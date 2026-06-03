"""Retrieval API — vector-only or hybrid (v1.2)."""

from __future__ import annotations

from src.rag.hybrid import hybrid_search_catalog, retrieval_mode
from src.rag.pipeline import index_dir
from src.rag.store.chroma_store import query as chroma_query


def search_catalog(
    query_text: str,
    site_id: int,
    *,
    n_results: int = 5,
    pet_type: str | None = None,
) -> list[dict]:
    if retrieval_mode() == "vector":
        return chroma_query(
            index_dir(),
            query_text,
            site_id,
            n_results=n_results,
            pet_type=pet_type,
        )
    return hybrid_search_catalog(
        query_text,
        site_id,
        n_results=n_results,
        pet_type=pet_type,
    )
