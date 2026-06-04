"""Integration — real OpenCode agents (no mocks)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

pytestmark = [pytest.mark.integration, pytest.mark.agentic]


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_chat_greeting_agentic(
    client: TestClient,
    indexed_catalog: dict,
    require_opencode: None,
) -> None:
    response = client.post("/chat", json={"site_id": 3, "query": "Hello"})
    assert response.status_code == 200
    answer = response.json()["answer"]
    assert len(answer) > 10
    assert response.json()["retrieved_products"] == []


def test_chat_catalog_agentic(
    client: TestClient,
    indexed_catalog: dict,
    require_opencode: None,
) -> None:
    response = client.post(
        "/chat",
        json={"site_id": 3, "query": "dry dog food for puppies"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["answer"]) > 10
    assert len(payload["retrieved_products"]) >= 1


def test_chat_decline_then_social(
    client: TestClient,
    require_opencode: None,
) -> None:
    response = client.post(
        "/chat",
        json={"site_id": 3, "query": "book me a flight to Paris"},
    )
    assert response.status_code == 200
    answer = response.json()["answer"]
    assert len(answer) > 15
    assert response.json()["retrieved_products"] == []
