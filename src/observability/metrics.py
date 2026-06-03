"""In-process request metrics (Prometheus-style JSON for PoC)."""

from __future__ import annotations

import threading
import time
from collections import defaultdict

_lock = threading.Lock()
_request_count: defaultdict[str, int] = defaultdict(int)
_latency_ms_sum: defaultdict[str, float] = defaultdict(float)
_latency_ms_max: defaultdict[str, float] = defaultdict(float)
_decline_count = 0
_chat_count = 0


def record_request(path: str, status_code: int, duration_ms: float) -> None:
    key = f"{path}:{status_code}"
    with _lock:
        _request_count[key] += 1
        _latency_ms_sum[key] += duration_ms
        _latency_ms_max[key] = max(_latency_ms_max[key], duration_ms)


def record_chat_outcome(*, declined: bool) -> None:
    global _decline_count, _chat_count
    with _lock:
        _chat_count += 1
        if declined:
            _decline_count += 1


def snapshot() -> dict:
    with _lock:
        routes = []
        for key, count in sorted(_request_count.items()):
            path, _, code = key.rpartition(":")
            avg = _latency_ms_sum[key] / count if count else 0.0
            routes.append(
                {
                    "route": path,
                    "status_code": int(code),
                    "count": count,
                    "latency_ms_avg": round(avg, 2),
                    "latency_ms_max": round(_latency_ms_max[key], 2),
                }
            )
        return {
            "timestamp": time.time(),
            "chat_total": _chat_count,
            "chat_declines": _decline_count,
            "routes": routes,
        }


def reset_for_tests() -> None:
    global _decline_count, _chat_count
    with _lock:
        _request_count.clear()
        _latency_ms_sum.clear()
        _latency_ms_max.clear()
        _decline_count = 0
        _chat_count = 0
