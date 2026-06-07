"""Per-session turn counter — invalidate in-flight streams when the shopper sends a new message."""

from __future__ import annotations

import os
import threading
import time

_memory_lock = threading.Lock()
_memory_turns: dict[str, tuple[int, float]] = {}
_MEMORY_TTL_SECONDS = 600


def _redis_client():
    url = os.environ.get("ZOOPLUS_REDIS_URL", "").strip()
    if not url or os.environ.get("ZOOPLUS_CACHE_BACKEND", "memory").lower() != "redis":
        return None
    try:
        import redis
    except ImportError:
        return None
    return redis.from_url(url, decode_responses=True)


def _redis_key(session_id: str) -> str:
    return f"zooplus:session_turn:{session_id}"


def bump_session_turn(session_id: str) -> int:
    """New shopper message — previous stream for this session is stale."""
    sid = (session_id or "default").strip() or "default"
    client = _redis_client()
    if client is not None:
        try:
            return int(client.incr(_redis_key(sid)))
        except Exception:
            pass
    now = time.time()
    with _memory_lock:
        prev, _ = _memory_turns.get(sid, (0, now))
        nxt = prev + 1
        _memory_turns[sid] = (nxt, now)
        stale = [k for k, (_, ts) in _memory_turns.items() if now - ts > _MEMORY_TTL_SECONDS]
        for k in stale:
            _memory_turns.pop(k, None)
        return nxt


def is_current_turn(session_id: str, turn_id: int) -> bool:
    sid = (session_id or "default").strip() or "default"
    client = _redis_client()
    if client is not None:
        try:
            raw = client.get(_redis_key(sid))
            return raw is not None and int(raw) == turn_id
        except Exception:
            pass
    with _memory_lock:
        current, _ = _memory_turns.get(sid, (0, 0.0))
        return current == turn_id
