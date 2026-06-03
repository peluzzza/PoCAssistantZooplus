"""Hybrid retrieval: vector candidates + BM25 lexical fusion + business rerank."""

from __future__ import annotations

import os

from src.rag.lexical import bm25_scores
from src.rag.pipeline import index_dir
from src.rag.rerank import fuse_hybrid_scores
from src.rag.store.chroma_store import query as chroma_query

CANDIDATE_MULTIPLIER = 4


def retrieval_mode() -> str:
    return os.environ.get("ZOOPLUS_RETRIEVAL_MODE", "hybrid").lower()


def hybrid_search_catalog(
    query_text: str,
    site_id: int,
    *,
    n_results: int = 5,
    pet_type: str | None = None,
) -> list[dict]:
    candidate_n = max(n_results * CANDIDATE_MULTIPLIER, n_results + 5)
    hits = chroma_query(
        index_dir(),
        query_text,
        site_id,
        n_results=candidate_n,
        pet_type=pet_type,
    )
    if not hits:
        return []

    documents = [h.get("document", "") or "" for h in hits]
    bm25 = bm25_scores(query_text, documents)
    max_bm25 = max(bm25) if bm25 else 1.0

    for hit, raw_bm25 in zip(hits, bm25, strict=True):
        norm_lex = (raw_bm25 / max_bm25) if max_bm25 > 0 else 0.0
        hit["lexical_bm25"] = raw_bm25
        hit["hybrid_score"] = fuse_hybrid_scores(
            vector_distance=hit.get("distance"),
            lexical_norm=norm_lex,
            metadata=hit.get("metadata", {}),
        )

    hits.sort(key=lambda h: h.get("hybrid_score", 0.0), reverse=True)
    return hits[:n_results]
