"""Unit tests — dynamic recommendation count from shopper query."""

from __future__ import annotations

import pytest
from src.guardian.engine import (
    absolute_max_recommendations,
    default_recommendations,
    resolve_recommendation_count,
)
from src.rag.recommendation_count import parse_requested_product_count, retrieval_pool_size

pytestmark = pytest.mark.unit


def test_default_count_without_request() -> None:
    assert default_recommendations() == 4
    assert resolve_recommendation_count("best dry food for puppy") == 4


def test_parse_ten_options_spanish() -> None:
    assert parse_requested_product_count("dame 10 opciones para gatos") == 10
    assert resolve_recommendation_count("dame 10 opciones para gatos") == 10


def test_parse_show_me_ten_english() -> None:
    assert parse_requested_product_count("show me 10 products for dogs") == 10


def test_ceiling_at_absolute_max() -> None:
    ceiling = absolute_max_recommendations()
    assert resolve_recommendation_count("give me 99 options") == ceiling


def test_retrieval_pool_scales_with_request() -> None:
    assert retrieval_pool_size(10, has_price_band=False) >= 12
    assert retrieval_pool_size(4, has_price_band=False) == 4
