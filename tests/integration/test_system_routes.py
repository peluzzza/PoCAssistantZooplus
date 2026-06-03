"""Integration tests — health, ready, metrics."""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.observability.metrics import reset_for_tests

pytestmark = pytest.mark.integration


@pytest.fixture
def client() -> TestClient:
    reset_for_tests()
    return TestClient(app)


def test_ready_reports_index(indexed_catalog: dict, client: TestClient) -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["index_present"] is True
    assert payload["status"] == "ready"


def test_metrics_after_chat(indexed_catalog: dict, client: TestClient) -> None:
    client.post("/chat", json={"site_id": 3, "query": "dog food"})
    response = client.get("/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert payload["chat_total"] >= 1
    assert isinstance(payload["routes"], list)
