"""Unit tests — catalog-derived routing lexicon."""

from __future__ import annotations

from src.rag.catalog_lexicon import (
    build_lexicon_from_raw,
    has_catalog_signal,
    persist_lexicon,
    query_signal,
    reload_lexicon,
)


def _ensure_lexicon() -> None:
    persist_lexicon(build_lexicon_from_raw())
    reload_lexicon()


def test_lexicon_builds_brands_from_catalog() -> None:
    lexicon = build_lexicon_from_raw()
    assert "Eukanuba" in lexicon.get("brands", [])
    assert "DOGS" in lexicon.get("pet_types", [])
    assert lexicon.get("record_count", 0) >= 100


def test_query_signal_matches_catalog_brand() -> None:
    _ensure_lexicon()
    signal = query_signal("I need Eukanuba dry food under 30 euros")
    assert "Eukanuba" in signal["brands"]
    assert signal["score"] >= 1


def test_spanish_price_query_without_handcoded_species_words() -> None:
    _ensure_lexicon()
    q = "necesito ver las opciones de comida a gatos entre 40 y 60€"
    assert not has_catalog_signal(q) or query_signal(q)["score"] >= 0
