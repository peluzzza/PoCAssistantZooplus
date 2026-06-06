"""Retrieval API — vector-only or hybrid (v1.2)."""

from __future__ import annotations

import logging

from src.cache.ttl_cache import cache_enabled, retrieval_cache
from src.rag.hybrid import hybrid_search_catalog, retrieval_mode
from src.rag.pipeline import index_dir
from src.rag.store.chroma_store import query as chroma_query

logger = logging.getLogger(__name__)


def _retrieval_cache_key(
    query_text: str,
    site_id: int,
    *,
    n_results: int,
    pet_type: str | None,
) -> str:
    mode = retrieval_mode()
    pet = pet_type or ""
    return f"{mode}:{site_id}:{n_results}:{pet}:{query_text.strip().lower()}"


def search_catalog(
    query_text: str,
    site_id: int,
    *,
    n_results: int = 5,
    pet_type: str | None = None,
) -> list[dict]:
    key = _retrieval_cache_key(query_text, site_id, n_results=n_results, pet_type=pet_type)
    if cache_enabled():
        cached = retrieval_cache.get(key)
        if cached is not None:
            logger.debug("retrieval cache hit site=%s n=%s", site_id, n_results)
            return list(cached)

    if retrieval_mode() == "vector":
        hits = chroma_query(
            index_dir(),
            query_text,
            site_id,
            n_results=n_results,
            pet_type=pet_type,
        )
    else:
        hits = hybrid_search_catalog(
            query_text,
            site_id,
            n_results=n_results,
            pet_type=pet_type,
        )

    if cache_enabled():
        retrieval_cache.set(key, hits)
    return hits
