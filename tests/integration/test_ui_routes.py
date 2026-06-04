"""Integration tests — chat UI static mount."""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

pytestmark = pytest.mark.integration


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_root_redirects_to_ui(client: TestClient) -> None:
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/ui/"


def test_ui_index_served(client: TestClient) -> None:
    response = client.get("/ui/")
    assert response.status_code == 200
    assert "zooplus Assistant" in response.text


def test_ui_config_endpoint(client: TestClient) -> None:
    response = client.get("/api/ui/config")
    assert response.status_code == 200
    data = response.json()
    assert data["sites"] == [1, 3, 15]
    assert data["chat_endpoint"] == "/chat"
    assert "synthesis_mode" in data
