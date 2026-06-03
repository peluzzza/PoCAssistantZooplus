"""Integration tests — FastAPI app."""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

pytestmark = pytest.mark.integration


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_valid_body_returns_200(client: TestClient, indexed_catalog: dict) -> None:
    response = client.post(
        "/chat",
        json={"site_id": 3, "query": "best dry food for puppy"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["answer"], str)
    assert isinstance(payload["retrieved_products"], list)
    if payload["retrieved_products"]:
        first = payload["retrieved_products"][0]
        assert "article_id" in first
        assert "product_name" in first


def test_chat_invalid_body_returns_422(client: TestClient) -> None:
    response = client.post("/chat", json={"site_id": 3, "query": ""})
    assert response.status_code == 422
