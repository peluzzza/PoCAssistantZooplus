"""Unit tests — BM25 lexical scoring."""

import pytest
from src.rag.lexical import bm25_scores, tokenize

pytestmark = pytest.mark.unit


def test_tokenize_lowercases() -> None:
    assert "dry" in tokenize("Dry Food Puppy")


def test_bm25_prefers_matching_document() -> None:
    scores = bm25_scores(
        "chuckit ball",
        ["chuckit ultra squeaker ball for dogs", "unrelated cat litter product"],
    )
    assert scores[0] > scores[1]
