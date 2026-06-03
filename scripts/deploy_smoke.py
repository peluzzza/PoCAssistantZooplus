#!/usr/bin/env python3
"""Post-deploy smoke checks (health, ready, chat, metrics)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = "http://127.0.0.1:8080"


def _get(path: str, base: str) -> tuple[int, dict | str]:
    url = f"{base.rstrip('/')}{path}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            body = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except urllib.error.URLError:
        return 0, "connection_error"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, body


def _post_chat(base: str) -> tuple[int, dict]:
    url = f"{base.rstrip('/')}/chat"
    payload = json.dumps({"site_id": 3, "query": "best dry food for puppy"}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def run_smoke(base: str = DEFAULT_BASE) -> int:
    checks: list[tuple[str, bool, str]] = []

    code, health = _get("/health", base)
    checks.append(("health", code == 200 and health == {"status": "ok"}, f"status={code}"))

    code, ready = _get("/ready", base)
    ready_ok = code == 200 and isinstance(ready, dict) and ready.get("index_present") is True
    checks.append(("ready", ready_ok, f"{ready}"))

    try:
        code, chat = _post_chat(base)
        chat_ok = code == 200 and isinstance(chat, dict) and "answer" in chat
        checks.append(("chat", chat_ok, f"status={code}"))
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        checks.append(("chat", False, str(exc)))

    code, metrics = _get("/metrics", base)
    metrics_ok = code == 200 and isinstance(metrics, dict) and "routes" in metrics
    checks.append(("metrics", metrics_ok, f"status={code}"))

    failed = [name for name, ok, _ in checks if not ok]
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        print(f"{status} {name}: {detail}")

    if failed:
        print(f"Deploy smoke FAILED ({len(failed)} checks)", file=sys.stderr)
        return 1
    print("Deploy smoke PASSED")
    return 0


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE
    return run_smoke(base)


if __name__ == "__main__":
    raise SystemExit(main())
