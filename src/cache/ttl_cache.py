"""In-process TTL cache with optional Redis mirror for multi-instance deploy."""

from __future__ import annotations

import os
import time
from collections import OrderedDict
from typing import Generic, TypeVar

from src.cache.redis_store import RedisTTLCache, redis_cache_enabled

T = TypeVar("T")


def cache_enabled() -> bool:
    return os.environ.get("ZOOPLUS_CACHE", "1").lower() not in ("0", "false", "no")


def cache_ttl_seconds() -> int:
    raw = os.environ.get("ZOOPLUS_CACHE_TTL_SECONDS", "600")
    try:
        return max(60, int(raw))
    except ValueError:
        return 600


def cache_max_entries() -> int:
    raw = os.environ.get("ZOOPLUS_CACHE_MAX_ENTRIES", "128")
    try:
        return max(16, int(raw))
    except ValueError:
        return 128


class TTLCache(Generic[T]):
    """Ordered TTL map with simple LRU eviction."""

    def __init__(self, *, max_entries: int, ttl_seconds: int) -> None:
        self._max = max_entries
        self._ttl = ttl_seconds
        self._data: OrderedDict[str, tuple[float, T]] = OrderedDict()

    def get(self, key: str) -> T | None:
        entry = self._data.get(key)
        if not entry:
            return None
        ts, value = entry
        if time.time() - ts > self._ttl:
            self._data.pop(key, None)
            return None
        self._data.move_to_end(key)
        return value

    def set(self, key: str, value: T) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = (time.time(), value)
        while len(self._data) > self._max:
            self._data.popitem(last=False)

    def clear(self) -> None:
        self._data.clear()


class HybridTTLCache(Generic[T]):
    """Memory-first cache; mirrors to Redis when ZOOPLUS_CACHE_BACKEND=redis."""

    def __init__(self, namespace: str) -> None:
        self._mem = TTLCache(max_entries=cache_max_entries(), ttl_seconds=cache_ttl_seconds())
        self._redis: RedisTTLCache[T] | None = None
        if redis_cache_enabled():
            self._redis = RedisTTLCache(
                namespace,
                ttl_seconds=cache_ttl_seconds(),
                max_entries=cache_max_entries(),
            )

    def get(self, key: str) -> T | None:
        if self._redis is not None:
            hit = self._redis.get(key)
            if hit is not None:
                return hit
        return self._mem.get(key)

    def set(self, key: str, value: T) -> None:
        self._mem.set(key, value)
        if self._redis is not None:
            self._redis.set(key, value)

    def clear(self) -> None:
        self._mem.clear()


def _make_cache(namespace: str) -> HybridTTLCache:
    return HybridTTLCache(namespace)


chat_cache: HybridTTLCache[dict] = _make_cache("chat")
intent_cache: HybridTTLCache[dict] = _make_cache("intent")
retrieval_cache: HybridTTLCache[list] = _make_cache("retrieval")
