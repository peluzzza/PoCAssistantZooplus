"""Social tests — template synthesis for deterministic matrix runs."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _fast_template_synthesis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_INTENT_MODE", "oracle")
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
    monkeypatch.setenv("ZOOPLUS_SOCIAL_SYNTHESIS", "template")
    monkeypatch.setenv("ZOOPLUS_AGENT_CASCADE", "0")
