"""Security tests — fast template synthesis (no OpenCode subprocess)."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _template_synthesis_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
