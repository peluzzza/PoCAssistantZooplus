"""Retrieval API for agents (filter-then-score via Chroma where clause)."""

from __future__ import annotations

from src.rag.pipeline import index_dir
from src.rag.store.chroma_store import query


def search_catalog(
    query_text: str,
    site_id: int,
    *,
    n_results: int = 5,
    pet_type: str | None = None,
) -> list[dict]:
    return query(index_dir(), query_text, site_id, n_results=n_results, pet_type=pet_type)
