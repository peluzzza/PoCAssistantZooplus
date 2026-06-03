"""Unit tests — deploy smoke helpers via TestClient (no live server)."""

import pytest
from fastapi.testclient import TestClient
from scripts.deploy_smoke import run_smoke
from src.api.app import app

pytestmark = pytest.mark.unit


def test_run_smoke_against_testclient_server(indexed_catalog: dict) -> None:
    """Use TestClient in-process; smoke script needs real URL — test via direct client."""
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json()["index_present"] is True
    chat = client.post("/chat", json={"site_id": 3, "query": "puppy food"})
    assert chat.status_code == 200
    assert client.get("/metrics").status_code == 200


def test_run_smoke_returns_nonzero_when_health_bad() -> None:
    assert run_smoke("http://127.0.0.1:59999") == 1
