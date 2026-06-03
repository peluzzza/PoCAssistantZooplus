#!/usr/bin/env python3
"""Measure topic guard latency (G1) — writes artifacts/load/topic_guard_latency.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.guardian.benchmark import run_topic_guard_benchmark  # noqa: E402

OUTPUT = ROOT / "artifacts" / "load" / "topic_guard_latency.json"


def main() -> int:
    report = run_topic_guard_benchmark(output_path=OUTPUT)
    print(json.dumps(report, indent=2))
    print(f"Wrote {OUTPUT}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
