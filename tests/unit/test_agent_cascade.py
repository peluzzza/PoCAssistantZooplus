"""Unit tests — OpenCode agent registry and cascade retries."""

from __future__ import annotations

import json

import pytest
from src.agents.agent_cascade import run_agent_cascade
from src.agents.registry import agent_chain_for_role, list_available_agent_ids, load_agent_catalog

pytestmark = pytest.mark.unit


def test_load_agent_catalog_from_opencode_json() -> None:
    catalog = load_agent_catalog()
    assert "zooplus-intent-agent" in catalog
    assert "zooplus-conductor" in catalog
    assert len(list_available_agent_ids()) >= 5


def test_intent_chain_order() -> None:
    chain = agent_chain_for_role("intent")
    assert chain[0] == "zooplus-intent-agent"
    assert "zooplus-conductor" in chain


def test_cascade_tries_second_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_run(prompt: str, *, settings, agent_id: str, timeout_seconds=None, model=None):
        calls.append(agent_id)
        if agent_id == "zooplus-topic-guard":
            return json.dumps({"lane": "conversational", "topic": "shop_social", "social_kind": "greeting"})
        return None

    monkeypatch.setattr("src.agents.agent_cascade.run_opencode_agent", fake_run)
    from src.config import Settings

    cfg = Settings.from_env()

    def parse(raw: str) -> dict | None:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    result = run_agent_cascade("intent", "hello", settings=cfg, parse=parse)
    assert result.agent_id == "zooplus-topic-guard"
    assert result.value is not None
    assert "zooplus-intent-agent" in calls


def test_cascade_exhausted_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.agents.agent_cascade.run_opencode_agent",
        lambda *a, **k: None,
    )
    from src.config import Settings

    result = run_agent_cascade(
        "intent",
        "test",
        settings=Settings.from_env(),
        parse=lambda r: None,
    )
    assert result.value is None
    assert len(result.attempts) >= 1
