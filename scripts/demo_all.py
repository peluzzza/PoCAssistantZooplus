#!/usr/bin/env python3
"""End-to-end PoC demo — local verification (no Anthropic / no cloud required)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = "http://127.0.0.1:8080"


def _run(label: str, cmd: list[str], *, cwd: Path = ROOT) -> bool:
    print(f"\n=== {label} ===", flush=True)
    print("+", " ".join(cmd), flush=True)
    code = subprocess.call(cmd, cwd=str(cwd))
    if code != 0:
        print(f"FAIL: {label} (exit {code})", file=sys.stderr)
    return code == 0


def _http_samples(base: str) -> bool:
    from urllib import request

    print(f"\n=== HTTP samples @ {base} ===", flush=True)
    ok = True

    def get(path: str) -> None:
        nonlocal ok
        url = f"{base.rstrip('/')}{path}"
        try:
            with request.urlopen(url, timeout=30) as resp:
                body = resp.read().decode("utf-8")[:200]
                print(f"GET {path} -> {resp.status} {body[:120]}...")
        except Exception as exc:
            print(f"GET {path} FAIL: {exc}", file=sys.stderr)
            ok = False

    def post_chat(query: str, site_id: int = 3) -> None:
        nonlocal ok
        url = f"{base.rstrip('/')}/chat"
        payload = json.dumps({"site_id": site_id, "query": query}).encode("utf-8")
        req = request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                n = len(data.get("retrieved_products", []))
                print(f"POST /chat '{query[:40]}...' -> {n} products")
        except Exception as exc:
            print(f"POST /chat FAIL: {exc}", file=sys.stderr)
            ok = False

    get("/health")
    get("/ready")
    get("/metrics")
    post_chat("best dry food for puppy")
    post_chat("what is the weather today?")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full zooplus PoC demo checks")
    parser.add_argument("--base-url", default=DEFAULT_BASE, help="API base (server must be up)")
    parser.add_argument("--skip-gates", action="store_true", help="Skip pytest quality gates")
    parser.add_argument("--skip-ingest", action="store_true", help="Skip cli ingest")
    parser.add_argument("--with-gates", action="store_true", help="Run quality gates first")
    args = parser.parse_args()

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from scripts.resolve_python import preferred_python

    py = preferred_python()
    results: list[tuple[str, bool]] = []

    if args.with_gates and not args.skip_gates:
        results.append(
            (
                "quality_gates",
                _run("quality_gates", [py, "scripts/run_quality_gates.py"]),
            )
        )

    if not args.skip_ingest:
        results.append(("ingest", _run("ingest", [py, "-m", "cli", "ingest"])))

    results.append(("eda", _run("eda", [py, "-m", "cli", "eda"])))
    results.append(("evaluate", _run("evaluate", [py, "-m", "cli", "evaluate"])))
    results.append(
        (
            "topic_guard_load",
            _run("topic_guard_load", [py, "scripts/topic_guard_load_test.py"]),
        )
    )
    results.append(
        (
            "deploy_smoke",
            _run("deploy_smoke", [py, "scripts/deploy_smoke.py", args.base_url]),
        )
    )
    results.append(("http_samples", _http_samples(args.base_url)))

    print("\n=== Summary ===", flush=True)
    failed = [name for name, ok in results if not ok]
    for name, ok in results:
        print(f"{'PASS' if ok else 'FAIL'} {name}")
    if failed:
        print(
            f"\nDemo incomplete ({len(failed)} failed). "
            "Start API: uvicorn src.api.app:app --port 8080 "
            "or: docker compose up -d",
            file=sys.stderr,
        )
        return 1
    print("\nDemo ALL PASSED — PoC path verified locally.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
