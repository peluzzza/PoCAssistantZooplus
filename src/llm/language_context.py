"""Bind shopper language for the current async request."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager

from src.agents.request_context import request_accept_language, request_shopper_language
from src.llm.language import resolve_shopper_language


@contextmanager
def bind_shopper_language(
    query: str,
    accept_language: str | None,
    *,
    site_id: int | None = None,
) -> Iterator[None]:
    code, _ = resolve_shopper_language(query, accept_language, site_id=site_id)
    accept_token = request_accept_language.set(accept_language)
    lang_token = request_shopper_language.set(code)
    try:
        yield
    finally:
        request_accept_language.reset(accept_token)
        request_shopper_language.reset(lang_token)


@asynccontextmanager
async def bind_shopper_language_async(
    query: str,
    accept_language: str | None,
    *,
    site_id: int | None = None,
) -> AsyncIterator[None]:
    with bind_shopper_language(query, accept_language, site_id=site_id):
        yield


def current_reply_language_instruction(query: str, *, site_id: int | None = None) -> str:
    from src.llm.language import reply_language_instruction

    return reply_language_instruction(
        query,
        request_accept_language.get(),
        site_id=site_id,
    )
