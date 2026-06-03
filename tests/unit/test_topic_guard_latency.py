"""Unit tests — G1 topic guard latency budget."""

from __future__ import annotations

import pytest
from scripts.topic_guard_load_test import run

pytestmark = pytest.mark.unit


def test_topic_guard_p95_under_300ms() -> None:
    report = run(iterations=200)
    assert report["pass"] is True
    assert report["p95_ms"] < 300
