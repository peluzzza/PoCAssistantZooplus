"""Unit tests — G1 topic guard latency budget."""

from __future__ import annotations

import pytest
from src.guardian.benchmark import run_topic_guard_benchmark

pytestmark = pytest.mark.unit


def test_topic_guard_p95_under_300ms() -> None:
    report = run_topic_guard_benchmark(iterations=200, output_path=None)
    assert report["pass"] is True
    assert report["p95_ms"] < 300
