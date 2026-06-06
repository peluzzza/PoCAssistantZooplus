"""Unit tests — fast intent hints and chat routing for help/catalog phrasing."""

import pytest
from fastapi.testclient import TestClient
from src.agents.intent_agent import (
    _repair_agentic_misroute,
    fast_intent_enabled,
    try_fast_catalog_intent,
    try_fast_conversational_intent,
    IntentDecision,
)
from src.agents.intent_hints import looks_like_catalog_search
from src.rag.catalog_lexicon import build_lexicon_from_raw, persist_lexicon, reload_lexicon
from src.api.app import app
from src.llm.conversation import classify_conversation

pytestmark = pytest.mark.unit


def test_fast_intent_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ZOOPLUS_FAST_INTENT", raising=False)
    assert not fast_intent_enabled()


def test_help_services_classified() -> None:
    q = "what can you tell me about your services"
    assert classify_conversation(q).value == "help"
    fast = try_fast_conversational_intent(q)
    assert fast is not None
    assert fast.lane == "conversational"
    assert fast.social_kind == "help"


def _ensure_lexicon() -> None:
    persist_lexicon(build_lexicon_from_raw())
    reload_lexicon()


def test_catalog_brand_signal_is_catalog() -> None:
    _ensure_lexicon()
    q = "show me Eukanuba options between 20 and 30 euros"
    assert looks_like_catalog_search(q)
    fast = try_fast_catalog_intent(q)
    assert fast is not None
    assert fast.lane == "catalog_search"


def test_repair_declined_brand_query_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    _ensure_lexicon()
    monkeypatch.setenv("ZOOPLUS_INTENT_REPAIR", "1")
    q = "Eukanuba puppy food under 25€"
    wrong = IntentDecision(lane="decline_off_topic", reason="llm_miss", source="conductor")
    fixed = _repair_agentic_misroute(q, wrong)
    assert fixed.lane == "catalog_search"
    assert fixed.source == "repair"


def test_catalog_browse_classified() -> None:
    q = "what products do you have available"
    assert try_fast_conversational_intent(q) is None
    fast = try_fast_catalog_intent(q)
    assert fast is not None
    assert fast.lane == "catalog_search"


def test_product_availability_not_declined(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_INTENT_MODE", "oracle")
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
    monkeypatch.setenv("ZOOPLUS_SOCIAL_SYNTHESIS", "agentic")
    client = TestClient(app)
    resp = client.post(
        "/chat",
        json={"site_id": 3, "query": "what products do you have available"},
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert "can't help with that topic" not in (payload.get("answer") or "").lower()


def test_chat_help_and_catalog_no_decline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_INTENT_MODE", "oracle")
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
    monkeypatch.setenv("ZOOPLUS_SOCIAL_SYNTHESIS", "agentic")
    from src.agents.run_meta import AgentRunMeta

    monkeypatch.setattr(
        "src.agents.social_agent.social_reply",
        lambda q, sid, intent, handoff_brief=None, *, settings=None: (
            f"I'm the zooplus Assistant for shop {sid} — describe dog or cat products you need.",
            AgentRunMeta(lane=intent.lane),
        ),
    )
    client = TestClient(app)

    for q in (
        "what can you tell me about your services",
        "hello, what services do you provide",
    ):
        help_resp = client.post("/chat", json={"site_id": 3, "query": q})
        assert help_resp.status_code == 200
        help_payload = help_resp.json()
        assert help_payload["retrieved_products"] == []
        assert "can't help with that topic" not in help_payload["answer"].lower()
        assert any(
            w in help_payload["answer"].lower()
            for w in ("zooplus", "catalog", "shop", "dog", "cat")
        )

    cat_resp = client.post(
        "/chat",
        json={"site_id": 3, "query": "show me some options about cats and dogs"},
    )
    assert cat_resp.status_code == 200
    cat_payload = cat_resp.json()
    assert "can't help with that topic" not in cat_payload["answer"].lower()
    assert len(cat_payload["retrieved_products"]) >= 1
