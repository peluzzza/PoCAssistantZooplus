"""Per-request overrides (UI model picker, browser language for PoC)."""

from __future__ import annotations

from contextvars import ContextVar

request_llm_model: ContextVar[str | None] = ContextVar("request_llm_model", default=None)
request_accept_language: ContextVar[str | None] = ContextVar("request_accept_language", default=None)
request_shopper_language: ContextVar[str | None] = ContextVar("request_shopper_language", default=None)
