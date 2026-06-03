#!/usr/bin/env python3
"""Measure topic guard latency (G1) — writes artifacts/load/topic_guard_latency.json."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.guardian.engine import topic_check  # noqa: E402

SAMPLES = [
    "best dry food for puppy",
    "grain free cat food",
    "dog chew toys",
    "what is the weather in berlin?",
    "who is the president of france?",
    "what time is it now?",
    "latest news headlines",
    "sensitive stomach wet food for senior dog",
]

OUTPUT = ROOT / "artifacts" / "load" / "topic_guard_latency.json"
P95_BUDGET_MS = 300
ITERATIONS = 500


def _percentile(sorted_ms: list[float], p: float) -> float:
    if not sorted_ms:
        return 0.0
    idx = int(round((p / 100.0) * (len(sorted_ms) - 1)))
    return sorted_ms[max(0, min(idx, len(sorted_ms) - 1))]


def run(iterations: int = ITERATIONS) -> dict:
    latencies_ms: list[float] = []
    for i in range(iterations):
        query = SAMPLES[i % len(SAMPLES)]
        start = time.perf_counter()
        topic_check(query)
        latencies_ms.append((time.perf_counter() - start) * 1000.0)

    latencies_ms.sort()
    p95 = _percentile(latencies_ms, 95)
    report = {
        "iterations": iterations,
        "p50_ms": round(_percentile(latencies_ms, 50), 3),
        "p95_ms": round(p95, 3),
        "p99_ms": round(_percentile(latencies_ms, 99), 3),
        "max_ms": round(latencies_ms[-1], 3),
        "budget_p95_ms": P95_BUDGET_MS,
        "pass": p95 < P95_BUDGET_MS,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> int:
    report = run()
    print(json.dumps(report, indent=2))
    print(f"Wrote {OUTPUT}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
