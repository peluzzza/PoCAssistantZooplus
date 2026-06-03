"""HTTP middleware — structured access logs + metrics."""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.observability.metrics import record_request

logger = logging.getLogger("zooplus.access")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000.0
        path = request.url.path
        record_request(path, response.status_code, duration_ms)
        logger.info(
            "request path=%s method=%s status=%s duration_ms=%.2f",
            path,
            request.method,
            response.status_code,
            duration_ms,
        )
        return response
