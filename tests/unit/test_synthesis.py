"""Unit tests — synthesis router and template."""

import pytest
from src.llm.synthesis import synthesize_answer
from src.llm.template import synthesize_template
from src.models.chat import RetrievedProduct

pytestmark = pytest.mark.unit


def _sample_product() -> RetrievedProduct:
    return RetrievedProduct(
        article_id=100,
        product_id=10,
        variant_id="v1",
        product_name="Test Kibble",
        price=12.5,
        pet_type="DOGS",
        brands="TestBrand",
    )


def test_template_synthesis_lists_products() -> None:
    text = synthesize_template("dog food", [_sample_product()])
    assert "Test Kibble" in text
    assert "found in this shop" in text.lower()


def test_synthesis_router_template_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
    answer = synthesize_answer("dog food", 3, [_sample_product()])
    assert "Test Kibble" in answer


def test_synthesis_router_opencode_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "opencode")
    monkeypatch.setenv("ZOOPLUS_OPENCODE_TIMEOUT", "3")
    answer = synthesize_answer("dog food", 3, [])
    assert isinstance(answer, str)
    assert len(answer) > 5
