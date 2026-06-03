"""Integration tests — golden query fixture set."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

pytestmark = pytest.mark.integration

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "golden_queries.json"


@pytest.fixture
def golden_cases() -> list[dict]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


_GOLDEN = json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", _GOLDEN, ids=lambda c: c["id"])
def test_golden_query(case: dict, client: TestClient, indexed_catalog: dict) -> None:
    response = client.post(
        "/chat",
        json={"site_id": case["site_id"], "query": case["query"]},
    )
    assert response.status_code == case.get("expect_status", 200)
    payload = response.json()
    products = payload["retrieved_products"]
    answer = payload["answer"]
    if case.get("expect_decline"):
        assert products == []
        assert len(answer) > 10
    if case.get("min_products"):
        assert len(products) >= case["min_products"]
    if case.get("max_products") is not None:
        assert len(products) <= case["max_products"]
