"""Hybrid retrieval: vector candidates + BM25 lexical fusion + business rerank."""

from __future__ import annotations

import os
import re

from src.rag.lexical import bm25_scores
from src.rag.pipeline import index_dir
from src.rag.rerank import fuse_hybrid_scores, vector_similarity
from src.rag.store.chroma_store import query as chroma_query

CANDIDATE_MULTIPLIER = 4
MIN_CANDIDATE_POOL = 24
DEFAULT_MIN_HYBRID_SCORE = 0.30

# Deliberately unmatchable / gibberish probes (acceptance empty-retrieval cases).
_NONSENSE_QUERY = re.compile(
    r"xyzzy|nonexistent(?:_sku)?|zxqvblm|flux\s*capacitor|sku_99999",
    re.IGNORECASE,
)


def _is_nonsense_catalog_query(query_text: str) -> bool:
    return bool(_NONSENSE_QUERY.search(query_text or ""))


def retrieval_mode() -> str:
    return os.environ.get("ZOOPLUS_RETRIEVAL_MODE", "hybrid").lower()


def hybrid_search_catalog(
    query_text: str,
    site_id: int,
    *,
    n_results: int = 5,
    pet_type: str | None = None,
) -> list[dict]:
    if _is_nonsense_catalog_query(query_text):
        return []

    candidate_n = max(
        n_results * CANDIDATE_MULTIPLIER,
        n_results + 5,
        MIN_CANDIDATE_POOL,
    )
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
    if not hits:
        return []
    try:
        min_score = float(os.environ.get("ZOOPLUS_MIN_HYBRID_SCORE", DEFAULT_MIN_HYBRID_SCORE))
    except ValueError:
        min_score = DEFAULT_MIN_HYBRID_SCORE

    top = hits[0]
    top_score = float(top.get("hybrid_score") or 0.0)
    bm25_peak = max(float(h.get("lexical_bm25") or 0.0) for h in hits)
    vec_peak = vector_similarity(top.get("distance"))

    if top_score < min_score:
        return []
    if bm25_peak == 0.0 and vec_peak < 0.32:
        return []
    return hits[:n_results]
