"""Unit tests — Pydantic API contracts."""

import pytest
from pydantic import ValidationError
from src.models.chat import ChatRequest, ChatResponse, RetrievedProduct

pytestmark = pytest.mark.unit


def test_chat_request_valid() -> None:
    req = ChatRequest(site_id=3, query="dry food for puppy")
    assert req.site_id == 3


def test_chat_request_rejects_empty_query() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(site_id=1, query="")


def test_chat_response_schema() -> None:
    resp = ChatResponse(
        answer="Here are some options.",
        retrieved_products=[
            RetrievedProduct(
                article_id=1,
                product_id=2,
                variant_id="2.0",
                product_name="Test",
                price=9.99,
                pet_type="DOGS",
                brands="Brand",
            )
        ],
    )
    assert len(resp.retrieved_products) == 1
