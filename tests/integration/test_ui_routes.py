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


def test_ui_assets_served(client: TestClient) -> None:
    assert client.get("/ui/styles.css").status_code == 200
    assert client.get("/ui/app.js").status_code == 200
    assert "background" in client.get("/ui/styles.css").text


def test_ui_config_endpoint(client: TestClient) -> None:
    response = client.get("/api/ui/config")
    assert response.status_code == 200
    data = response.json()
    assert data["sites"] == [1, 3, 15]
    assert data["site_labels"]["1"] == "Germany (de-DE)"
    assert data["site_labels"]["3"] == "United Kingdom (en-GB)"
    assert data["site_labels"]["15"] == "Spain (es-ES)"
    assert data["chat_endpoint"] == "/chat/stream"
    assert "synthesis_mode" in data
