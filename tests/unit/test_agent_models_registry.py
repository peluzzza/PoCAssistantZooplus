"""Unit tests — per-agent model assignment from opencode.json."""

from __future__ import annotations

import pytest
from src.agents.registry import (
    agent_models_map,
    cli_model_arg,
    load_agent_catalog,
    resolved_agent_model,
)

pytestmark = pytest.mark.unit


def test_catalog_loads_per_agent_models() -> None:
    catalog = load_agent_catalog()
    assert "zooplus-conductor" in catalog
    assert catalog["zooplus-social-agent"].model == "opencode/mimo-v2.5-free"
    assert catalog["zooplus-logic-worker"].model == "opencode-go/qwen3.6-plus"


def test_cli_model_arg_omits_flag_when_agent_has_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ZOOPLUS_SOCIAL_MODEL", raising=False)
    from src.agents.request_context import request_llm_model

    token = request_llm_model.set(None)
    try:
        assert cli_model_arg("zooplus-social-agent", default="opencode/fallback") is None
    finally:
        request_llm_model.reset(token)


def test_resolved_agent_model_for_meta() -> None:
    model = resolved_agent_model("zooplus-topic-guard", default="opencode/fallback")
    assert model == "opencode-go/minimax-m2.5"


def test_agent_models_map_has_all_workers() -> None:
    models = agent_models_map()
    assert models["zooplus-conductor"] == "opencode/mimo-v2.5-free"
    assert models["zooplus-synthesis"] == "opencode/deepseek-v4-flash-free"
