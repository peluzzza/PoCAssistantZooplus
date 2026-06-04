"""Unit tests — conversational fast path."""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.llm.conversation import conversational_reply, is_conversational_only

pytestmark = pytest.mark.unit


def test_conversational_only_detects_hello() -> None:
    assert is_conversational_only("Hello!")
    assert is_conversational_only("who are you")
    assert not is_conversational_only("best dry food for puppy")


def test_conversational_reply_template(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
    monkeypatch.setenv("ZOOPLUS_SOCIAL_SYNTHESIS", "template")
    answer = conversational_reply("Hello", 3)
    assert len(answer) > 20
    assert any(w in answer.lower() for w in ("shop", "catalog", "dog", "cat", "pet", "zooplus"))


def test_chat_identity_no_products(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
    monkeypatch.setenv("ZOOPLUS_SOCIAL_SYNTHESIS", "template")
    monkeypatch.setenv("ZOOPLUS_AGENT_CASCADE", "0")
    client = TestClient(app)
    response = client.post("/chat", json={"site_id": 3, "query": "who are you"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["retrieved_products"] == []
    assert len(payload["answer"]) > 20
    assert any(
        w in payload["answer"].lower()
        for w in ("zooplus", "assistant", "catalog", "dog", "cat", "shop")
    )


def test_chat_traffic_decline_no_products(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
    monkeypatch.setenv("ZOOPLUS_SOCIAL_SYNTHESIS", "template")
    monkeypatch.setenv("ZOOPLUS_AGENT_CASCADE", "0")
    client = TestClient(app)
    response = client.post("/chat", json={"site_id": 3, "query": "how it the traffic today"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["retrieved_products"] == []
    assert "traffic" in payload["answer"].lower() or "catalog" in payload["answer"].lower()


def test_chat_hello_fast_path_no_hang(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
    monkeypatch.setenv("ZOOPLUS_SOCIAL_SYNTHESIS", "template")
    monkeypatch.setenv("ZOOPLUS_AGENT_CASCADE", "0")
    client = TestClient(app)
    response = client.post("/chat", json={"site_id": 3, "query": "Hello"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["retrieved_products"] == []
    assert len(payload["answer"]) > 15
    assert "can't help with that topic" not in payload["answer"].lower()
