"""Unit tests — TTL cache and retrieval cache integration."""

from __future__ import annotations

import time

import pytest
from src.cache.ttl_cache import TTLCache, cache_enabled
from src.rag.retrieve import search_catalog

pytestmark = pytest.mark.unit


def test_ttl_cache_evicts_expired(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = TTLCache[str](max_entries=8, ttl_seconds=1)
    cache.set("a", "one")
    assert cache.get("a") == "one"
    time.sleep(1.1)
    assert cache.get("a") is None


def test_retrieval_cache_hit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_CACHE", "1")
    calls: list[str] = []

    def fake_hybrid(query_text: str, site_id: int, *, n_results: int, pet_type=None):
        calls.append(query_text)
        return [{"metadata": {"article_id": 1, "price": 9.0}}]

    monkeypatch.setattr("src.rag.retrieve.hybrid_search_catalog", fake_hybrid)
    monkeypatch.setattr("src.rag.retrieve.retrieval_mode", lambda: "hybrid")
    from src.cache.ttl_cache import retrieval_cache

    retrieval_cache.clear()

    first = search_catalog("cat food", 3, n_results=4)
    second = search_catalog("cat food", 3, n_results=4)
    assert first == second
    assert len(calls) == 1


def test_cache_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_CACHE", "0")
    assert not cache_enabled()
