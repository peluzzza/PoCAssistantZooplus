"""Social tests — template synthesis for deterministic matrix runs."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _fast_template_synthesis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
