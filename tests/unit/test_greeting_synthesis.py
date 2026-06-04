"""Unit tests — fast greeting path (no OpenCode hang)."""

import pytest
from src.llm.synthesis import synthesize_answer

pytestmark = pytest.mark.unit


def test_hello_skips_opencode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "opencode")
    answer = synthesize_answer("Hello", 3, [])
    assert "zooplus Assistant" in answer
    assert len(answer) < 300
