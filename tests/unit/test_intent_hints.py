"""Unit tests — fast intent hints and chat routing for help/catalog phrasing."""

import pytest
from fastapi.testclient import TestClient
from src.agents.intent_agent import (
    classify_intent,
    try_fast_catalog_intent,
    try_fast_conversational_intent,
)
from src.api.app import app
from src.llm.conversation import classify_conversation

pytestmark = pytest.mark.unit


def test_help_services_classified() -> None:
    q = "what can you tell me about your services"
    assert classify_conversation(q).value == "help"
    fast = try_fast_conversational_intent(q)
    assert fast is not None
    assert fast.lane == "conversational"
    assert fast.social_kind == "help"


def test_catalog_browse_classified() -> None:
    q = "show me some options about cats and dogs"
    assert try_fast_conversational_intent(q) is None
    fast = try_fast_catalog_intent(q)
    assert fast is not None
    assert fast.lane == "catalog_search"


def test_chat_help_and_catalog_no_decline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_INTENT_MODE", "agentic")
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
    client = TestClient(app)

    help_resp = client.post(
        "/chat",
        json={"site_id": 3, "query": "what can you tell me about your services"},
    )
    assert help_resp.status_code == 200
    help_payload = help_resp.json()
    assert help_payload["retrieved_products"] == []
    assert "can't help with that topic" not in help_payload["answer"].lower()
    assert "zooplus" in help_payload["answer"].lower()

    cat_resp = client.post(
        "/chat",
        json={"site_id": 3, "query": "show me some options about cats and dogs"},
    )
    assert cat_resp.status_code == 200
    cat_payload = cat_resp.json()
    assert "can't help with that topic" not in cat_payload["answer"].lower()
    assert len(cat_payload["retrieved_products"]) >= 1
