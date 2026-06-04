"""E2E agentic social behaviors — no rigid product dump on chitchat."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

pytestmark = [pytest.mark.agentic, pytest.mark.integration, pytest.mark.e2e]

RIGID_PHRASES = (
    "based on what you asked",
    "i'd be happy to help! based on",
    "here's what i found in this shop",
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize(
    "query",
    [
        "hello, who are you",
        "hi, what are you?",
        "how it the traffic today",
        "what about for humans",
    ],
)
def test_agentic_chat_no_rigid_catalog_template(
    client: TestClient,
    indexed_catalog: dict,
    query: str,
) -> None:
    response = client.post("/chat", json={"site_id": 3, "query": query})
    assert response.status_code == 200
    payload = response.json()
    answer = (payload.get("answer") or "").lower()
    products = payload.get("retrieved_products") or []

    if "traffic" in query or "humans" in query:
        assert products == []
    if "who are you" in query or "what are you" in query or query.startswith("hi"):
        assert products == []
        assert "zooplus" in answer

    for phrase in RIGID_PHRASES:
        assert phrase not in answer, f"rigid template on {query!r}"
