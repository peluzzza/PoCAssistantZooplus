"""Social / conversational turns via POST /chat — real LLM, no mocks."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.llm.answer_sanitize import normalize_shopper_answer

pytestmark = [pytest.mark.social, pytest.mark.agentic]


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize(
    "query",
    ["hello", "hola", "danke", "who are you?", "what can you do?"],
)
def test_social_greetings_and_help(
    client: TestClient,
    require_opencode: None,
    query: str,
) -> None:
    r = client.post("/chat", json={"site_id": 3, "query": query})
    assert r.status_code == 200
    answer = normalize_shopper_answer(r.json()["answer"])
    assert len(answer) > 12
    assert r.json()["retrieved_products"] == []
    assert "{" not in answer[:5]


def test_social_decline_humans(
    client: TestClient,
    require_opencode: None,
) -> None:
    r = client.post("/chat", json={"site_id": 3, "query": "products for humans"})
    assert r.status_code == 200
    answer = normalize_shopper_answer(r.json()["answer"]).lower()
    assert r.json()["retrieved_products"] == []
    assert "dog" in answer or "cat" in answer or "pet" in answer


def test_catalog_respects_site_id(
    client: TestClient,
    indexed_catalog: dict,
    require_opencode: None,
) -> None:
    for site_id in (1, 3, 15):
        r = client.post(
            "/chat",
            json={"site_id": site_id, "query": "cat food options"},
        )
        assert r.status_code == 200
        products = r.json()["retrieved_products"]
        assert len(products) >= 1
        for p in products:
            assert p["pet_type"] == "CATS"
