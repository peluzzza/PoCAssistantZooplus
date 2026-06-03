"""Integration tests — Chroma ingest + site-scoped search."""

import pytest
from src.rag.pipeline import run_ingest
from src.rag.retrieve import search_catalog

pytestmark = pytest.mark.integration


def test_ingest_manifest(indexed_catalog: dict) -> None:
    assert indexed_catalog["records_ingested"] == 300
    assert indexed_catalog["collection"] == "zooplus_variants"


def test_retrieval_respects_site_id(indexed_catalog: dict) -> None:
    hits = search_catalog("dry food puppy", site_id=3, n_results=5)
    assert len(hits) >= 1
    for hit in hits:
        assert hit["metadata"]["site_id"] == 3


def test_no_cross_site_leak(indexed_catalog: dict) -> None:
    for site in (1, 3, 15):
        hits = search_catalog("dog toy", site_id=site, n_results=3)
        assert all(h["metadata"]["site_id"] == site for h in hits)


def test_reingest_idempotent(indexed_catalog: dict) -> None:
    second = run_ingest()
    assert second["records_ingested"] == 300
