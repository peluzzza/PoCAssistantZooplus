"""Minimal MCP-like tool surface served by FastAPI routes."""

from __future__ import annotations

import asyncio

from src.guardian.engine import absolute_max_recommendations, default_recommendations, topic_check
from src.rag.retrieve import search_catalog


async def tool_topic_check(query: str) -> dict:
    decision = topic_check(query)
    return {
        "decision": decision.decision,
        "reason_code": decision.reason_code,
        "polite_decline": decision.polite_decline,
    }


async def tool_catalog_search(
    query_text: str,
    site_id: int,
    *,
    n_results: int | None = None,
    pet_type: str | None = None,
) -> dict:
    ceiling = absolute_max_recommendations()
    limit = min(n_results or default_recommendations(), ceiling)
    hits = await asyncio.to_thread(
        search_catalog,
        query_text,
        site_id,
        n_results=limit,
        pet_type=pet_type,
    )
    return {"hits": hits}
