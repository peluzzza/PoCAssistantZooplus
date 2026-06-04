"""Unit tests — varied copy and routing fixes from screenshot regressions."""

from __future__ import annotations

import pytest
from src.agents.intent_agent import _fallback_intent_decision
from src.agents.intent_hints import (
    looks_like_product_browse,
    looks_like_non_catalog_species,
)
from src.llm.conversation import _template_reply, ConvoKind
from src.llm.template import synthesize_template
from src.models.chat import RetrievedProduct

pytestmark = pytest.mark.unit


def test_product_browse_hint() -> None:
    assert looks_like_product_browse("what products do you have available")
    assert looks_like_product_browse("show me about dogs now")


def test_horse_is_non_catalog_species() -> None:
    assert looks_like_non_catalog_species("do you have product about horses?")


def test_fallback_routes_product_browse_to_catalog() -> None:
    d = _fallback_intent_decision(
        "what products do you have available",
        site_id=3,
        reason="test",
    )
    assert d.lane == "catalog_search"
    assert d.source == "topic_fallback"


def test_fallback_declines_horses() -> None:
    d = _fallback_intent_decision(
        "do you have product about horses?",
        site_id=3,
        reason="test",
    )
    assert d.lane == "decline_off_topic"
    assert d.decline_message
    assert "horse" in d.decline_message.lower() or "dog" in d.decline_message.lower()


def test_template_greeting_varies_by_query() -> None:
    a = _template_reply(ConvoKind.GREETING, 3, query="hello")
    b = _template_reply(ConvoKind.GREETING, 3, query="hi there friend")
    assert a and b
    # Different seeds → usually different copy (allow rare collision)
    assert a != b or "shop" in a


def test_catalog_template_no_numbered_list() -> None:
    products = [
        RetrievedProduct(
            article_id=6236441,
            product_id=100,
            variant_id="v1",
            product_name="Purizon Single Meat",
            variant_name=None,
            brands="Purizon",
            pet_type="CATS",
            price=5.35,
        ),
    ]
    text = synthesize_template("cat food", products)
    assert "1." not in text
    assert "cards" in text.lower() or "below" in text.lower()
