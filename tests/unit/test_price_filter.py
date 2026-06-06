"""Unit tests — EUR price range parsing and hit filtering."""

from __future__ import annotations

from src.rag.price_filter import apply_price_range_filter, parse_eur_price_range


def test_parse_reversed_range() -> None:
    assert parse_eur_price_range("prices between 20 and 10 €") == (10.0, 20.0)


def test_parse_eur_suffix() -> None:
    assert parse_eur_price_range("from 10 to 20 euros") == (10.0, 20.0)


def test_parse_spanish_eur_amounts_without_keywords() -> None:
    assert parse_eur_price_range("dame lo que tengas entre 30 y 50€ para perros") == (
        30.0,
        50.0,
    )


def test_filter_hits_in_band() -> None:
    hits = [
        {"metadata": {"price": 9.5}},
        {"metadata": {"price": 15.0}},
        {"metadata": {"price": 25.0}},
    ]
    out = apply_price_range_filter("between 10 and 20 €", hits)
    prices = [h["metadata"]["price"] for h in out]
    assert prices == [15.0]
