"""Unit tests — internal instructions skill."""

import pytest
from src.agents.agent_body import wrap_prompt_with_agent
from src.agents.instructions_skill import catalog_scope_summary, instructions_skill_context

pytestmark = pytest.mark.unit


def test_catalog_scope_summary() -> None:
    text = catalog_scope_summary()
    assert "Catalog:" in text
    assert "300" in text


def test_instructions_skill_context_includes_site() -> None:
    ctx = instructions_skill_context(site_id=3)
    assert "active_site_id=3" in ctx
    assert "zooplus Assistant" in ctx


def test_wrap_prompt_with_agent() -> None:
    out = wrap_prompt_with_agent("zooplus-intent", "classify this")
    assert "classify this" in out
