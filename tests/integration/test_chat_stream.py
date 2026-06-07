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


@pytest.fixture(autouse=True)
def _mock_social_chunks(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_chunk(
        query: str,
        site_id: int,
        *,
        chunk_index: int,
        elapsed_seconds: int,
        previous_chunks: tuple[str, ...],
        catalog_still_running: bool,
        shopper_status: str | None = None,
        settings=None,
    ) -> str:
        _ = (
            query,
            site_id,
            elapsed_seconds,
            previous_chunks,
            catalog_still_running,
            shopper_status,
            settings,
        )
        return f"Timed chunk {chunk_index}: keeping you in the loop."

    monkeypatch.setattr("src.lanes.stream.social_chunk_reply", _fake_chunk)


def _read_ndjson(response) -> list[dict]:
    lines = [ln for ln in response.iter_lines() if ln]
    return [json.loads(ln) for ln in lines]


def test_chat_stream_decline_emits_topic_and_done(client: TestClient) -> None:
    with client.stream(
        "POST",
        "/chat/stream",
        json={"site_id": 3, "query": "what is the weather today?", "session_id": "s-dec"},
    ) as response:
        assert response.status_code == 200
        events = _read_ndjson(response)
    types = [e["type"] for e in events]
    assert "topic" in types
    topic = next(e for e in events if e["type"] == "topic")
    assert topic["decision"] == "DECLINE"
    assert "done" in types
    done = next(e for e in events if e["type"] == "done")
    assert done["retrieved_products"] == []
    assert not [e for e in events if e["type"] == "chunk"]


def test_chat_stream_catalog_emits_timed_chunks(
    client: TestClient, indexed_catalog: dict
) -> None:
    with client.stream(
        "POST",
        "/chat/stream",
        json={
            "site_id": 3,
            "query": "best dry food for puppy",
            "session_id": "s-cat",
        },
    ) as response:
        assert response.status_code == 200
        events = _read_ndjson(response)
    chunks = [e for e in events if e["type"] == "chunk"]
    assert len(chunks) >= 1
    assert all("Timed chunk" in c["text"] for c in chunks)
    typing = [e for e in events if e["type"] == "typing"]
    assert any(t.get("active") for t in typing)
    topic = next(e for e in events if e["type"] == "topic")
    assert topic["decision"] == "ALLOW"
    assert "products" in [e["type"] for e in events]
    done = next(e for e in events if e["type"] == "done")
    assert done.get("answer")
    assert len(done.get("retrieved_products", [])) >= 1
