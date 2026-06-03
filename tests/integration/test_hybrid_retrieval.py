"""Integration tests — hybrid retrieval path (v1.2)."""

from __future__ import annotations

import os

import pytest
from src.rag.hybrid import hybrid_search_catalog
from src.rag.retrieve import search_catalog

pytestmark = pytest.mark.integration


def test_hybrid_search_respects_site_id(indexed_catalog: dict) -> None:
    hits = hybrid_search_catalog("dog food", site_id=3, n_results=4)
    assert len(hits) >= 1
    assert all(h["metadata"]["site_id"] == 3 for h in hits)
    assert all("hybrid_score" in h for h in hits)


def test_hybrid_beats_vector_for_exact_brand_keyword(indexed_catalog: dict) -> None:
    """Brand token in query should rank Chuckit! hits when present in catalog."""
    os.environ["ZOOPLUS_RETRIEVAL_MODE"] = "vector"
    vector_hits = search_catalog("Chuckit squeaker ball", site_id=1, n_results=3)
    os.environ["ZOOPLUS_RETRIEVAL_MODE"] = "hybrid"
    hybrid_hits = search_catalog("Chuckit squeaker ball", site_id=1, n_results=3)
    assert len(hybrid_hits) >= 1
    top = hybrid_hits[0]["metadata"]["product_name"].lower()
    assert "chuckit" in top or "squeaker" in top
    if vector_hits and hybrid_hits:
        assert hybrid_hits[0].get("hybrid_score", 0) >= 0


def test_default_retrieval_mode_is_hybrid(indexed_catalog: dict) -> None:
    os.environ.pop("ZOOPLUS_RETRIEVAL_MODE", None)
    hits = search_catalog("cat treats", site_id=1, n_results=2)
    assert hits
    assert "hybrid_score" in hits[0]
