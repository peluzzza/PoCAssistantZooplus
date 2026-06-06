"""Unit tests — conductor-first intent and deferred catalog search."""

from __future__ import annotations

import pytest
from src.agents.intent_agent import (
    IntentDecision,
    classify_intent_conductor_first,
    conductor_intent_enabled,
)
from src.lanes.orchestrator import handle_chat
from src.models.chat import ChatRequest

pytestmark = pytest.mark.unit


def test_conductor_intent_enabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ZOOPLUS_CONDUCTOR_INTENT", raising=False)
    assert conductor_intent_enabled()


def test_conductor_intent_can_be_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_CONDUCTOR_INTENT", "0")
    assert not conductor_intent_enabled()


def test_conductor_first_parses_lane_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.agents.intent_agent.run_agent_cascade",
        lambda role, prompt, *, settings, parse, attach_roster=False: type(
            "R",
            (),
            {
                "value": {
                    "lane": "conversational",
                    "social_kind": "greeting",
                    "confidence": 0.9,
                    "reason": "greeting",
                },
                "agent_id": "zooplus-conductor",
            },
        )(),
    )
    decision = classify_intent_conductor_first("hola", 3)
    assert decision is not None
    assert decision.lane == "conversational"
    assert decision.social_kind == "greeting"
    assert decision.source.startswith("conductor:")


@pytest.mark.asyncio
async def test_orchestrator_skips_catalog_on_social(monkeypatch: pytest.MonkeyPatch) -> None:
    search_calls: list[tuple] = []

    def fake_search(query: str, site_id: int, *, n_results: int = 4):
        search_calls.append((query, site_id, n_results))
        return []

    async def fake_classify(query: str, site_id: int):
        return IntentDecision(lane="conversational", social_kind="greeting", source="test")

    monkeypatch.setattr("src.lanes.orchestrator.search_catalog", fake_search)
    monkeypatch.setattr("src.lanes.orchestrator._classify_intent_bounded", fake_classify)
    monkeypatch.setattr(
        "src.lanes.orchestrator.social_reply",
        lambda q, sid, intent, handoff_brief=None: "Hi there!",
    )
    monkeypatch.setattr("src.cache.ttl_cache.cache_enabled", lambda: False)

    response = await handle_chat(ChatRequest(site_id=3, query="hello"))
    assert response.answer
    assert search_calls == []
