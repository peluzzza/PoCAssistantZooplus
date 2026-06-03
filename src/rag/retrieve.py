"""Retrieval API for agents (filter-then-score via Chroma where clause)."""

from __future__ import annotations

from pathlib import Path

from src.rag.store.chroma_store import query

ROOT = Path(__file__).resolve().parents[2]
INDEX_DIR = ROOT / "artifacts" / "index" / "chroma"


def search_catalog(
    query_text: str,
    site_id: int,
    *,
    n_results: int = 5,
    pet_type: str | None = None,
) -> list[dict]:
    return query(INDEX_DIR, query_text, site_id, n_results=n_results, pet_type=pet_type)
