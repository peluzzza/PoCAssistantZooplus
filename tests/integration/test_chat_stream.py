"""Integration tests — POST /chat/stream NDJSON."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

pytestmark = pytest.mark.integration


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _read_ndjson(response) -> list[dict]:
    lines = [ln for ln in response.iter_lines() if ln]
    return [json.loads(ln) for ln in lines]


def test_chat_stream_decline_emits_topic_and_done(client: TestClient) -> None:
    with client.stream(
        "POST",
        "/chat/stream",
        json={"site_id": 3, "query": "what is the weather today?"},
    ) as response:
        assert response.status_code == 200
        events = _read_ndjson(response)
    types = [e["type"] for e in events]
    assert types[0] == "topic"
    assert events[0]["decision"] == "DECLINE"
    assert "done" in types
    done = next(e for e in events if e["type"] == "done")
    assert done["retrieved_products"] == []


def test_chat_stream_in_scope_emits_products_and_answer(
    client: TestClient, indexed_catalog: dict
) -> None:
    with client.stream(
        "POST",
        "/chat/stream",
        json={"site_id": 3, "query": "best dry food for puppy"},
    ) as response:
        assert response.status_code == 200
        events = _read_ndjson(response)
    types = [e["type"] for e in events]
    assert events[0]["type"] == "topic"
    assert events[0]["decision"] == "ALLOW"
    assert "products" in types
    assert "answer_chunk" in types
    done = next(e for e in events if e["type"] == "done")
    assert done.get("answer")
    assert len(done.get("retrieved_products", [])) >= 1
