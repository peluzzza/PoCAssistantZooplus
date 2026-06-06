"""Integration — agentic mode when OpenCode intent fails must not spam help template."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.agents.intent_agent import classify_intent
from src.api.app import app

pytestmark = pytest.mark.integration


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_fallback_routes_internet_to_decline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_INTENT_MODE", "agentic")
    monkeypatch.setenv("ZOOPLUS_CONDUCTOR_INTENT", "0")
    monkeypatch.setattr(
        "src.agents.agent_cascade.run_opencode_agent",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "src.agents.intent_agent.run_opencode_agent",
        lambda *a, **k: None,
    )
    d = classify_intent("show me option to find in internet about dogs", 3)
    assert d.lane == "decline_off_topic"
    assert d.source == "topic_fallback"


def test_fallback_routes_greeting(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_INTENT_MODE", "agentic")
    monkeypatch.setenv("ZOOPLUS_CONDUCTOR_INTENT", "0")
    monkeypatch.setattr(
        "src.agents.agent_cascade.run_opencode_agent",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "src.agents.intent_agent.run_opencode_agent",
        lambda *a, **k: None,
    )
    d = classify_intent("hello??", 3)
    assert d.lane == "conversational"
    assert d.social_kind == "greeting"
    assert d.source == "topic_fallback"


def test_fallback_routes_catalog_products(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_INTENT_MODE", "agentic")
    monkeypatch.setenv("ZOOPLUS_CONDUCTOR_INTENT", "0")
    monkeypatch.setattr(
        "src.agents.agent_cascade.run_opencode_agent",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "src.agents.intent_agent.run_opencode_agent",
        lambda *a, **k: None,
    )
    d = classify_intent("show me products about dogs", 3)
    assert d.lane == "catalog_search"
    assert d.source == "topic_fallback"


def test_chat_no_repeated_help_template(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    indexed_catalog: dict,
) -> None:
    """Reproduces UI bug: same help blurb for every message when intent LLM fails."""
    monkeypatch.setenv("ZOOPLUS_INTENT_MODE", "agentic")
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
    monkeypatch.setenv("ZOOPLUS_FAST_INTENT", "1")
    monkeypatch.setenv("ZOOPLUS_CONDUCTOR_INTENT", "0")
    monkeypatch.setattr(
        "src.agents.agent_cascade.run_opencode_agent",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "src.agents.intent_agent.run_opencode_agent",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "src.agents.social_agent.social_reply",
        lambda q, sid, intent, handoff_brief=None, *, settings=None: (
            f"zooplus Assistant reply ({intent.lane})"
        ),
    )
    help_blurb = "I can recommend up to four products in plain language"

    r1 = client.post(
        "/chat",
        json={"site_id": 3, "query": "show me option to find in internet about dogs"},
    )
    assert r1.status_code == 200
    assert help_blurb not in r1.json()["answer"]
    assert r1.json()["retrieved_products"] == []

    r2 = client.post("/chat", json={"site_id": 3, "query": "hello??"})
    assert r2.status_code == 200
    assert help_blurb not in r2.json()["answer"]

    r3 = client.post("/chat", json={"site_id": 3, "query": "show me products about dogs"})
    assert r3.status_code == 200
    assert help_blurb not in r3.json()["answer"]
    assert len(r3.json()["retrieved_products"]) >= 1
