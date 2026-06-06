"""Per-request overrides (UI model picker for PoC)."""

from __future__ import annotations

from contextvars import ContextVar

request_llm_model: ContextVar[str | None] = ContextVar("request_llm_model", default=None)
