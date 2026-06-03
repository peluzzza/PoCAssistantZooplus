"""Acceptance tests — Coding Task.docx + docs/instructions catalog (source of truth)."""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.api.routes import chat as chat_routes
from src.guardian.engine import max_recommendations

pytestmark = pytest.mark.acceptance

ROOT = Path(__file__).resolve().parents[2]
INSTRUCTIONS_CATALOG = ROOT / "docs" / "instructions" / "product_catalog_dataset.json"
RUNTIME_CATALOG = ROOT / "data" / "raw" / "product_catalog_dataset.json"
ACCEPTANCE_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "acceptance_queries.json"
_CATALOG_CACHE: list[dict] | None = None


def _instructions_catalog() -> list[dict]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE is None:
        _CATALOG_CACHE = json.loads(INSTRUCTIONS_CATALOG.read_text(encoding="utf-8"))
    return _CATALOG_CACHE


def _catalog_index() -> dict[tuple[int, int], dict]:
    index: dict[tuple[int, int], dict] = {}
    for row in _instructions_catalog():
        index[(int(row["site_id"]), int(row["article_id"]))] = row
    return index


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def catalog_index() -> dict[tuple[int, int], dict]:
    return _catalog_index()


@pytest.fixture
def acceptance_cases() -> list[dict]:
    return json.loads(ACCEPTANCE_FIXTURE.read_text(encoding="utf-8"))


# --- Static brief / submission requirements (B7–B9) ---


def test_instructions_catalog_record_count() -> None:
    records = _instructions_catalog()
    assert len(records) == 300
    assert {r["site_id"] for r in records} == {1, 3, 15}


def test_runtime_catalog_matches_instructions_bytes() -> None:
    assert RUNTIME_CATALOG.is_file()
    a = hashlib.sha256(INSTRUCTIONS_CATALOG.read_bytes()).hexdigest()
    b = hashlib.sha256(RUNTIME_CATALOG.read_bytes()).hexdigest()
    assert a == b


def test_repo_layout_brief() -> None:
    assert (ROOT / "src" / "api" / "app.py").is_file()
    assert (ROOT / "cli").is_dir()
    assert (ROOT / "docs" / "instructions" / "Coding Task.docx").is_file()


def test_readme_and_cli_entrypoints() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Setup" in readme or "setup" in readme.lower()
    assert (ROOT / "cli" / "__main__.py").is_file()


def test_evaluation_docs_present() -> None:
    assert (ROOT / "docs" / "instructions" / "ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "01-eda-report.md").is_file()


# --- B1 async FastAPI ---


def test_app_is_async_fastapi() -> None:
    assert inspect.iscoroutinefunction(chat_routes.chat)


# --- B2/B3 API contract ---


def test_chat_request_contract_valid(client: TestClient, indexed_catalog: dict) -> None:
    response = client.post(
        "/chat",
        json={
            "site_id": 3,
            "query": "What's the best dry food for a puppy with a sensitive stomach?",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["answer"], str) and payload["answer"].strip()
    assert isinstance(payload["retrieved_products"], list)


def test_chat_request_contract_rejects_empty_query(client: TestClient) -> None:
    response = client.post("/chat", json={"site_id": 3, "query": ""})
    assert response.status_code == 422


def test_chat_request_contract_rejects_missing_fields(client: TestClient) -> None:
    assert client.post("/chat", json={"query": "dog food"}).status_code == 422
    assert client.post("/chat", json={"site_id": 3}).status_code == 422


def test_response_schema_retrieved_product_fields(
    client: TestClient, indexed_catalog: dict
) -> None:
    response = client.post("/chat", json={"site_id": 3, "query": "puppy dry food"})
    assert response.status_code == 200
    for product in response.json()["retrieved_products"]:
        assert "article_id" in product
        assert "product_name" in product
        assert "price" in product
        assert "pet_type" in product


# --- B4 grounding / B5 site scoping / P1 max products ---


def test_retrieved_products_grounded_in_instructions_catalog(
    client: TestClient, indexed_catalog: dict, catalog_index: dict[tuple[int, int], dict]
) -> None:
    response = client.post("/chat", json={"site_id": 3, "query": "Eukanuba dog food"})
    assert response.status_code == 200
    for product in response.json()["retrieved_products"]:
        key = (3, int(product["article_id"]))
        assert key in catalog_index, f"hallucinated article_id {product['article_id']} for site 3"


def test_max_four_retrieved_products(client: TestClient, indexed_catalog: dict) -> None:
    limit = max_recommendations()
    assert limit <= 4
    response = client.post(
        "/chat",
        json={"site_id": 3, "query": "dog food treats toys accessories"},
    )
    assert response.status_code == 200
    assert len(response.json()["retrieved_products"]) <= limit


@pytest.mark.parametrize("site_id", [1, 3, 15])
def test_site_scoping_all_retrieved_match_site(
    client: TestClient, indexed_catalog: dict, site_id: int
) -> None:
    response = client.post(
        "/chat",
        json={"site_id": site_id, "query": "popular pet food"},
    )
    assert response.status_code == 200
    for product in response.json()["retrieved_products"]:
        key = (site_id, int(product["article_id"]))
        assert key in _catalog_index()


# --- B6 guardrails ---


@pytest.mark.parametrize(
    "query",
    [
        "What's the weather today?",
        "who is the president of france?",
    ],
)
def test_off_topic_politely_declined(client: TestClient, indexed_catalog: dict, query: str) -> None:
    response = client.post("/chat", json={"site_id": 3, "query": query})
    assert response.status_code == 200
    payload = response.json()
    assert payload["retrieved_products"] == []
    assert len(payload["answer"]) > 20
    assert "zooplus" in payload["answer"].lower() or "pet" in payload["answer"].lower()


_ACCEPTANCE_CASES = json.loads(ACCEPTANCE_FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", _ACCEPTANCE_CASES, ids=lambda c: c["id"])
def test_acceptance_query_matrix(
    case: dict,
    client: TestClient,
    indexed_catalog: dict,
    catalog_index: dict[tuple[int, int], dict],
) -> None:
    site_id = int(case["site_id"])
    response = client.post(
        "/chat",
        json={"site_id": site_id, "query": case["query"]},
    )
    assert response.status_code == 200
    payload = response.json()
    products = payload["retrieved_products"]
    answer = payload["answer"]

    if case.get("expect_decline"):
        assert products == []
        assert answer.strip()
        return

    if case.get("min_products"):
        assert len(products) >= case["min_products"]
    if case.get("max_products") is not None:
        assert len(products) <= case["max_products"]

    for product in products:
        key = (site_id, int(product["article_id"]))
        assert key in catalog_index
        assert product["product_name"] in answer or str(product["article_id"]) in answer
