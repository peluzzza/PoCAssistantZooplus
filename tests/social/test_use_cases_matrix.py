"""100+ use cases from Coding Task + instructions catalog (social/chat E2E)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

pytestmark = [pytest.mark.social, pytest.mark.integration]

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "use_cases_matrix.json"
_CATALOG = (
    Path(__file__).resolve().parents[2] / "docs" / "instructions" / "product_catalog_dataset.json"
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def catalog_index() -> dict[tuple[int, int], dict]:
    records = json.loads(_CATALOG.read_text(encoding="utf-8"))
    return {(int(r["site_id"]), int(r["article_id"])): r for r in records}


_CASES = json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", _CASES, ids=lambda c: c["id"])
def test_use_case_matrix(
    case: dict,
    client: TestClient,
    indexed_catalog: dict,
    catalog_index: dict[tuple[int, int], dict],
) -> None:
    site_id = int(case["site_id"])
    expect = case["expect"]
    response = client.post("/chat", json={"site_id": site_id, "query": case["query"]})
    assert response.status_code == expect.get("status", 200), response.text[:400]

    payload = response.json()
    assert "answer" in payload and isinstance(payload["answer"], str)
    assert "retrieved_products" in payload and isinstance(payload["retrieved_products"], list)

    products = payload["retrieved_products"]
    answer = payload["answer"]

    if expect.get("decline"):
        assert products == []
        assert len(answer) > 10
    if expect.get("max_products") is not None:
        assert len(products) <= expect["max_products"]
    if expect.get("min_products"):
        assert len(products) >= expect["min_products"]

    if expect.get("products_grounded") and products:
        for product in products:
            key = (site_id, int(product["article_id"]))
            assert key in catalog_index, (
                f"{case['id']}: hallucinated article_id {product['article_id']} for site {site_id}"
            )
            assert product["product_name"]

    for fragment in expect.get("answer_contains") or []:
        assert fragment.lower() in answer.lower(), f"{case['id']}: missing '{fragment}' in answer"

    for forbidden in expect.get("forbid_answer") or []:
        assert forbidden.lower() not in answer.lower(), (
            f"{case['id']}: rigid catalog template leaked '{forbidden}'"
        )

    lane = expect.get("intent_lane")
    if lane == "conversational":
        assert products == [], f"{case['id']}: conversational must not return products"
    if lane == "decline_off_topic":
        assert products == [], f"{case['id']}: decline must not return products"

    # target_article_id is a catalog hint only — semantic search may return siblings
