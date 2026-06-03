"""Unit tests — HTML normalization."""

import pytest
from src.rag.chunking import record_to_index_item
from src.rag.normalize import build_embed_text, html_to_plain

pytestmark = pytest.mark.unit


def test_html_to_plain_strips_tags() -> None:
    assert "world" in html_to_plain("<p>hello <strong>world</strong></p>")


def test_build_embed_text_includes_product_name(sample_record: dict) -> None:
    text = build_embed_text(sample_record)
    assert sample_record["product_name"] in text


def test_record_to_index_item_metadata(sample_record: dict) -> None:
    item = record_to_index_item(sample_record)
    assert item["metadata"]["site_id"] == sample_record["site_id"]
    assert ":" in item["id"]
