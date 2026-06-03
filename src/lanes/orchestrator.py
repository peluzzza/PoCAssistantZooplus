"""Dual-lane orchestrator — Interactive (fast) + Process (RAG)."""

from __future__ import annotations

import asyncio

from src.acp.dispatcher import dispatch_process
from src.acp.envelopes import ChatProcessEnvelope
from src.guardian.engine import load_constraints
from src.lanes.interactive import run_topic_guard
from src.lanes.process import run_process_lane
from src.models.chat import ChatRequest, ChatResponse
from src.observability.metrics import record_chat_outcome


async def handle_chat(request: ChatRequest) -> ChatResponse:
    constraints = load_constraints()
    process_cfg = constraints.get("process_lane", {})
    timeout_seconds = float(process_cfg.get("dispatch_timeout_seconds", 15))

    envelope = ChatProcessEnvelope(site_id=request.site_id, query=request.query)
    process_task = asyncio.create_task(
        dispatch_process(envelope, run_process_lane, timeout_seconds=timeout_seconds)
    )
    topic = await run_topic_guard(request.query)
    if topic.decision == "DECLINE":
        process_task.cancel()
        record_chat_outcome(declined=True)
        return ChatResponse(answer=topic.polite_decline or "", retrieved_products=[])

    receipt = await process_task
    record_chat_outcome(declined=False)
    return ChatResponse(answer=receipt.answer, retrieved_products=receipt.retrieved_products)
