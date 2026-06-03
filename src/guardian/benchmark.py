"""Topic guard latency benchmark (G1) — importable from tests and CLI."""

from __future__ import annotations

import time
from pathlib import Path

from src.guardian.engine import topic_check

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

P95_BUDGET_MS = 300
DEFAULT_ITERATIONS = 500


def _percentile(sorted_ms: list[float], p: float) -> float:
    if not sorted_ms:
        return 0.0
    idx = int(round((p / 100.0) * (len(sorted_ms) - 1)))
    return sorted_ms[max(0, min(idx, len(sorted_ms) - 1))]


def run_topic_guard_benchmark(
    *,
    iterations: int = DEFAULT_ITERATIONS,
    output_path: Path | None = None,
) -> dict:
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
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        import json

        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
