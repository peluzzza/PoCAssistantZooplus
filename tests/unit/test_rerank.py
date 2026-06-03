"""Unit tests — business rerank helpers."""

import pytest
from src.rag.rerank import business_score, fuse_hybrid_scores

pytestmark = pytest.mark.unit


def test_business_score_favors_stock_and_rating() -> None:
    high = business_score({"rating_average": 4.5, "monthly_sales_units": 1500, "stock_units": 100})
    low = business_score({"rating_average": 2.0, "monthly_sales_units": 0, "stock_units": 0})
    assert high > low


def test_fuse_hybrid_scores_increases_with_lexical_match() -> None:
    base = fuse_hybrid_scores(
        vector_distance=0.5,
        lexical_norm=0.1,
        metadata={"rating_average": 4.0, "monthly_sales_units": 100, "stock_units": 10},
    )
    boosted = fuse_hybrid_scores(
        vector_distance=0.5,
        lexical_norm=0.9,
        metadata={"rating_average": 4.0, "monthly_sales_units": 100, "stock_units": 10},
    )
    assert boosted > base
