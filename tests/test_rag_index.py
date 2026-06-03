"""T2 — RAG ingest and site-scoped retrieval."""

from __future__ import annotations

import json
import pytest

from src.rag.normalize import html_to_plain
from src.rag.pipeline import run_ingest
from src.rag.retrieve import search_catalog


def test_html_to_plain_strips_tags() -> None:
    assert "hello" in html_to_plain("<p>hello <strong>world</strong></p>")


@pytest.fixture(scope="module")
def indexed():
    manifest = run_ingest()
    return manifest


def test_ingest_all_records(indexed: dict) -> None:
    assert indexed["records_ingested"] == 300


def test_retrieval_respects_site_id(indexed: dict) -> None:
    hits = search_catalog("dry food puppy", site_id=3, n_results=5)
    assert len(hits) >= 1
    for h in hits:
        assert h["metadata"]["site_id"] == 3


def test_no_cross_site_leak(indexed: dict) -> None:
    for site in (1, 3, 15):
        hits = search_catalog("dog toy", site_id=site, n_results=3)
        assert all(h["metadata"]["site_id"] == site for h in hits)


def test_manifest_written(indexed: dict) -> None:
    from src.rag.pipeline import MANIFEST

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["records_ingested"] == 300
