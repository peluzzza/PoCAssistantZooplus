"""NDJSON stream — same agentic routing as POST /chat (internal OpenCode)."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from src.acp.dispatcher import dispatch_process
from src.acp.envelopes import ChatProcessEnvelope
from src.agents.handoff import build_handoff
from src.agents.intent_agent import classify_intent
from src.agents.social_agent import social_reply
from src.guardian.engine import load_constraints
from src.lanes.process import run_process_lane
from src.llm.answer_sanitize import normalize_shopper_answer
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


def _topic_event(intent) -> dict:
    if intent.lane == "decline_off_topic":
        return {
            "type": "topic",
            "decision": "DECLINE",
            "reason_code": intent.reason or "off_topic",
        }
    if intent.lane == "conversational":
        return {
            "type": "topic",
            "decision": "ALLOW",
            "reason_code": "conversational",
        }
    return {
        "type": "topic",
        "decision": "ALLOW",
        "reason_code": intent.reason or "catalog_search",
    }


async def stream_chat_events(request: ChatRequest) -> AsyncIterator[str]:
    """Yield NDJSON: topic → social|products+answer_chunk* → done."""
    intent = await asyncio.to_thread(
        classify_intent,
        request.query,
        request.site_id,
    )
    handoff = build_handoff(
        query=request.query,
        site_id=request.site_id,
        lane=intent.lane,
        topic=intent.topic,
        social_kind=intent.social_kind,
        reason=intent.reason,
        source=intent.source,
    )
    yield _line(_topic_event(intent))

    if intent.lane in ("decline_off_topic", "conversational"):
        answer = normalize_shopper_answer(
            await asyncio.to_thread(
                social_reply,
                request.query,
                request.site_id,
                intent,
                handoff.brief(),
            )
        )
        for chunk in _answer_chunks(answer):
            yield _line({"type": "answer_chunk", "text": chunk})
        yield _line({"type": "done", "answer": answer, "retrieved_products": []})
        return

    constraints = load_constraints()
    process_cfg = constraints.get("process_lane", {})
    timeout_seconds = float(process_cfg.get("dispatch_timeout_seconds", 15))

    envelope = ChatProcessEnvelope(
        site_id=request.site_id,
        query=request.query,
        intent_handoff=handoff.brief(),
    )
    receipt = await dispatch_process(
        envelope,
        run_process_lane,
        timeout_seconds=timeout_seconds,
    )
    products_payload = [p.model_dump() for p in receipt.retrieved_products]
    yield _line({"type": "products", "retrieved_products": products_payload})

    answer = normalize_shopper_answer(receipt.answer)
    for chunk in _answer_chunks(answer):
        yield _line({"type": "answer_chunk", "text": chunk})

    yield _line(
        {
            "type": "done",
            "answer": answer,
            "retrieved_products": products_payload,
        }
    )
