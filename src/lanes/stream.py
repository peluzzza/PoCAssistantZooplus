"""NDJSON stream events for POST /chat/stream."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from src.acp.dispatcher import dispatch_process
from src.acp.envelopes import ChatProcessEnvelope
from src.guardian.engine import load_constraints
from src.lanes.interactive import run_topic_guard
from src.lanes.process import run_process_lane
from src.models.chat import ChatRequest


def _line(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False) + "\n"


def _answer_chunks(answer: str, *, max_chunk: int = 120) -> list[str]:
    if len(answer) <= max_chunk:
        return [answer]
    chunks: list[str] = []
    rest = answer
    while rest:
        if len(rest) <= max_chunk:
            chunks.append(rest)
            break
        split_at = rest.rfind(". ", 0, max_chunk)
        if split_at < 40:
            split_at = max_chunk
        else:
            split_at += 1
        chunks.append(rest[:split_at])
        rest = rest[split_at:].lstrip()
    return chunks


async def stream_chat_events(request: ChatRequest) -> AsyncIterator[str]:
    """Yield NDJSON: topic → decline|products+answer_chunk* → done."""
    constraints = load_constraints()
    process_cfg = constraints.get("process_lane", {})
    timeout_seconds = float(process_cfg.get("dispatch_timeout_seconds", 15))

    envelope = ChatProcessEnvelope(site_id=request.site_id, query=request.query)
    process_task = asyncio.create_task(
        dispatch_process(envelope, run_process_lane, timeout_seconds=timeout_seconds)
    )

    topic = await run_topic_guard(request.query)
    yield _line(
        {
            "type": "topic",
            "decision": topic.decision,
            "reason_code": topic.reason_code,
        }
    )

    if topic.decision == "DECLINE":
        process_task.cancel()
        answer = topic.polite_decline or ""
        yield _line({"type": "answer_chunk", "text": answer})
        yield _line({"type": "done", "answer": answer, "retrieved_products": []})
        return

    receipt = await process_task
    products_payload = [p.model_dump() for p in receipt.retrieved_products]
    yield _line({"type": "products", "retrieved_products": products_payload})

    for chunk in _answer_chunks(receipt.answer):
        yield _line({"type": "answer_chunk", "text": chunk})

    yield _line(
        {
            "type": "done",
            "answer": receipt.answer,
            "retrieved_products": products_payload,
        }
    )
