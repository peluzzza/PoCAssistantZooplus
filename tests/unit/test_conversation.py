"""Unit tests — conversation hints only (replies are agentic via social_agent)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.agents.social_agent import social_reply
from src.agents.intent_agent import IntentDecision
from src.llm.conversation import classify_conversation, is_conversational_only, social_kind_hint

pytestmark = pytest.mark.unit


def test_conversational_only_detects_hello() -> None:
    assert is_conversational_only("Hello!")
    assert is_conversational_only("who are you")
    assert not is_conversational_only("best dry food for puppy")


def test_social_kind_prefers_intent_agent() -> None:
    assert social_kind_hint("hello", intent_social_kind="help") == "help"
    assert social_kind_hint("thanks", intent_social_kind="thanks") == "thanks"


def test_social_reply_uses_agent_when_mocked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_SOCIAL_SYNTHESIS", "agentic")
    monkeypatch.setenv("ZOOPLUS_AGENT_CASCADE", "0")

    def fake_agents(*a, **k):
        return "Hi! I'm the zooplus Assistant — ask me about dog or cat food anytime."

    monkeypatch.setattr("src.agents.social_agent._run_social_agents", fake_agents)
    intent = IntentDecision(
        lane="conversational",
        social_kind="greeting",
        topic="shop_social",
        source="test",
    )
    text = social_reply("hello", 3, intent)
    assert "zooplus" in text.lower()
    assert "dog" in text.lower() or "cat" in text.lower()


def test_chat_identity_no_products(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_INTENT_MODE", "oracle")
    monkeypatch.setenv("ZOOPLUS_SOCIAL_SYNTHESIS", "agentic")
    monkeypatch.setenv("ZOOPLUS_AGENT_CASCADE", "0")
    monkeypatch.setattr(
        "src.agents.social_agent._run_social_agents",
        lambda *a, **k: "I'm the zooplus Assistant for this shop — dogs and cats only.",
    )
    client = TestClient(app)
    response = client.post("/chat", json={"site_id": 3, "query": "who are you"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["retrieved_products"] == []
    assert "zooplus" in payload["answer"].lower()


def test_chat_traffic_decline_no_products(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_INTENT_MODE", "oracle")
    monkeypatch.setenv("ZOOPLUS_SOCIAL_SYNTHESIS", "agentic")
    monkeypatch.setenv("ZOOPLUS_AGENT_CASCADE", "0")
    monkeypatch.setattr(
        "src.agents.social_agent._run_social_agents",
        lambda *a, **k: "I can't help with traffic — zooplus Assistant, pet catalog only.",
    )
    client = TestClient(app)
    response = client.post("/chat", json={"site_id": 3, "query": "how it the traffic today"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["retrieved_products"] == []
    assert "zooplus" in payload["answer"].lower()


def test_chat_hello_agentic_no_hang(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_INTENT_MODE", "oracle")
    monkeypatch.setenv("ZOOPLUS_SOCIAL_SYNTHESIS", "agentic")
    monkeypatch.setattr(
        "src.agents.social_agent._run_social_agents",
        lambda *a, **k: "Hello! zooplus Assistant here — what pet product can I find for you?",
    )
    client = TestClient(app)
    response = client.post("/chat", json={"site_id": 3, "query": "Hello"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["retrieved_products"] == []
    assert "can't help with that topic" not in payload["answer"].lower()
