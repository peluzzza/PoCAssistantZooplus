"""Dual-lane orchestrator — Interactive (fast) + Process (RAG)."""

from __future__ import annotations

import asyncio

from src.acp.dispatcher import dispatch_process
from src.acp.envelopes import ChatProcessEnvelope
from src.guardian.engine import load_constraints
from src.lanes.interactive import run_topic_guard
from src.lanes.process import run_process_lane
from src.llm.conversation import conversational_reply, is_conversational_only
from src.models.chat import ChatRequest, ChatResponse
from src.observability.metrics import record_chat_outcome


async def handle_chat(request: ChatRequest) -> ChatResponse:
    topic = await run_topic_guard(request.query)
    if topic.decision == "DECLINE":
        record_chat_outcome(declined=True)
        return ChatResponse(answer=topic.polite_decline or "", retrieved_products=[])

    if is_conversational_only(request.query):
        answer = await asyncio.to_thread(
            conversational_reply,
            request.query,
            request.site_id,
        )
        record_chat_outcome(declined=False)
        return ChatResponse(answer=answer, retrieved_products=[])

    constraints = load_constraints()
    process_cfg = constraints.get("process_lane", {})
    timeout_seconds = float(process_cfg.get("dispatch_timeout_seconds", 20))

    envelope = ChatProcessEnvelope(site_id=request.site_id, query=request.query)
    process_task = asyncio.create_task(
        dispatch_process(envelope, run_process_lane, timeout_seconds=timeout_seconds)
    )
    receipt = await process_task
    record_chat_outcome(declined=False)
    return ChatResponse(answer=receipt.answer, retrieved_products=receipt.retrieved_products)
