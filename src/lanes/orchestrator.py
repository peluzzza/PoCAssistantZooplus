"""Dual-lane orchestrator — agentic intent + social / catalog process."""

from __future__ import annotations

import asyncio

from src.acp.dispatcher import dispatch_process
from src.acp.envelopes import ChatProcessEnvelope
from src.agents.intent_agent import classify_intent
from src.agents.social_agent import social_reply
from src.guardian.engine import load_constraints
from src.lanes.process import run_process_lane
from src.models.chat import ChatRequest, ChatResponse
from src.observability.metrics import record_chat_outcome


async def handle_chat(request: ChatRequest) -> ChatResponse:
    intent = await asyncio.to_thread(
        classify_intent,
        request.query,
        request.site_id,
    )

    if intent.lane == "decline_off_topic":
        record_chat_outcome(declined=True)
        return ChatResponse(
            answer=intent.decline_message or "",
            retrieved_products=[],
        )

    if intent.lane == "conversational":
        answer = await asyncio.to_thread(
            social_reply,
            request.query,
            request.site_id,
            intent,
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
    return ChatResponse(
        answer=receipt.answer,
        retrieved_products=receipt.retrieved_products,
    )
