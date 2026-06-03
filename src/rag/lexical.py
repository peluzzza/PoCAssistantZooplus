"""Lightweight lexical scoring (BM25-style, no extra dependencies)."""

from __future__ import annotations

import math
import re
from collections import Counter

_TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text or "")]


def bm25_scores(
    query: str,
    documents: list[str],
    *,
    k1: float = 1.2,
    b: float = 0.75,
) -> list[float]:
    """Okapi BM25 over a small candidate set (vector pre-filter)."""
    if not documents:
        return []
    query_tokens = tokenize(query)
    if not query_tokens:
        return [0.0] * len(documents)

    doc_tokens = [tokenize(doc) for doc in documents]
    doc_lens = [len(toks) for toks in doc_tokens]
    avg_dl = sum(doc_lens) / len(doc_lens) if doc_lens else 0.0

    df: Counter[str] = Counter()
    for toks in doc_tokens:
        for term in set(toks):
            df[term] += 1

    n_docs = len(documents)
    scores: list[float] = []
    for toks, dl in zip(doc_tokens, doc_lens, strict=True):
        tf = Counter(toks)
        total = 0.0
        for term in query_tokens:
            if term not in tf:
                continue
            idf = math.log(1 + (n_docs - df[term] + 0.5) / (df[term] + 0.5))
            freq = tf[term]
            denom = freq + k1 * (1 - b + b * dl / (avg_dl or 1.0))
            total += idf * (freq * (k1 + 1)) / (denom or 1.0)
        scores.append(total)
    return scores
