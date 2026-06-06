"""Optional Redis backing for shared TTL caches (multi-instance PoC scale-out)."""

from __future__ import annotations

import json
import os
import time
from typing import Generic, TypeVar

T = TypeVar("T")


def redis_cache_enabled() -> bool:
    return os.environ.get("ZOOPLUS_CACHE_BACKEND", "memory").lower() == "redis"


def _client():
    url = os.environ.get("ZOOPLUS_REDIS_URL", "").strip()
    if not url:
        return None
    try:
        import redis
    except ImportError:
        return None
    return redis.from_url(url, decode_responses=True)


class RedisTTLCache(Generic[T]):
    """JSON-serialized TTL cache in Redis; falls back gracefully if Redis unavailable."""

    def __init__(self, namespace: str, *, ttl_seconds: int, max_entries: int) -> None:
        self._ns = namespace
        self._ttl = ttl_seconds
        self._max = max_entries

    def _key(self, key: str) -> str:
        return f"zooplus:cache:{self._ns}:{key}"

    def get(self, key: str) -> T | None:
        client = _client()
        if client is None:
            return None
        raw = client.get(self._key(key))
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def set(self, key: str, value: T) -> None:
        client = _client()
        if client is None:
            return
        client.setex(self._key(key), self._ttl, json.dumps(value, ensure_ascii=False))
        index_key = f"zooplus:cache:{self._ns}:__index__"
        now = time.time()
        client.zadd(index_key, {key: now})
        client.expire(index_key, self._ttl * 2)
        while client.zcard(index_key) > self._max:
            oldest = client.zpopmin(index_key, count=1)
            if not oldest:
                break
            old_key = oldest[0][0]
            client.delete(self._key(old_key))
