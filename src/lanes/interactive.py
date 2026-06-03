"""Interactive lane for fast topic decisions."""

from __future__ import annotations

import asyncio

from src.guardian.engine import TopicDecision, topic_check


async def run_topic_guard(query: str) -> TopicDecision:
    return await asyncio.to_thread(topic_check, query)
