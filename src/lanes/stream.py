"""NDJSON stream — agentic routing with customer-facing status events."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from src.acp.dispatcher import dispatch_process
from src.acp.envelopes import ChatProcessEnvelope
from src.agents.handoff import build_handoff
from src.agents.registry import resolved_agent_model
from src.agents.social_agent import social_reply
from src.config import apply_settings
from src.guardian.engine import load_constraints, max_recommendations
from src.lanes.customer_status import MAX_STATUS_MESSAGES, phases_for_lane, status_event
from src.lanes.orchestrator import _classify_intent_bounded
from src.lanes.process import run_process_lane
from src.llm.answer_sanitize import normalize_shopper_answer
from src.models.chat import ChatRequest, ChatRuntimeMeta
from src.rag.price_filter import parse_eur_price_range
from src.rag.retrieve import search_catalog


def _line(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False) + "\n"


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
    """Yield NDJSON: status* → topic → social|products+answer → done."""
    from src.agents.request_context import request_llm_model

    model_token = request_llm_model.set(request.preferred_model)
    status_count = 0

    shopper_status: str | None = None
    lane = "catalog_search"

    def _emit_status(
        phase: str,
        *,
        lane_name: str | None = None,
        hit_count: int | None = None,
    ) -> str | None:
        nonlocal status_count
        if status_count >= MAX_STATUS_MESSAGES:
            return None
        status_count += 1
        return _line(
            status_event(
                phase,
                lane=lane_name or lane,
                shopper_status=shopper_status,
                hit_count=hit_count,
            )
        )

    try:
        # Instant ack — do not wait for intent LLM (keeps the shopper from feeling blocked).
        if line := _emit_status("received", lane_name="catalog_search"):
            yield line

        intent = await _classify_intent_bounded(request.query, request.site_id)
        lane = intent.lane
        shopper_status = intent.shopper_status
        lane_phases = set(phases_for_lane(lane))

        if "understood" in lane_phases:
            if line := _emit_status("understood"):
                yield line

        yield _line(_topic_event(intent))

        handoff = build_handoff(
            query=request.query,
            site_id=request.site_id,
            lane=intent.lane,
            topic=intent.topic,
            social_kind=intent.social_kind,
            reason=intent.reason,
            source=intent.source,
        )

        if intent.lane in ("decline_off_topic", "conversational"):
            if "composing" in lane_phases:
                if line := _emit_status("composing"):
                    yield line
            answer, run_meta = await asyncio.to_thread(
                social_reply,
                request.query,
                request.site_id,
                intent,
                handoff.brief(),
            )
            answer = normalize_shopper_answer(answer)
            yield _line(
                {
                    "type": "done",
                    "answer": answer,
                    "retrieved_products": [],
                    "meta": {
                        "lane": run_meta.lane,
                        "intent_source": run_meta.intent_source,
                        "llm_agent": run_meta.llm_agent,
                        "llm_model": run_meta.llm_model,
                    },
                }
            )
            return

        if "searching" in lane_phases:
            if line := _emit_status("searching"):
                yield line

        cap = max_recommendations()
        pool_n = max(cap * 6, 24) if parse_eur_price_range(request.query) else cap
        prefetched_hits = tuple(
            await asyncio.to_thread(
                search_catalog,
                request.query,
                request.site_id,
                n_results=pool_n,
            )
        )

        if "found" in lane_phases:
            if line := _emit_status("found", hit_count=len(prefetched_hits)):
                yield line

        if "narrowing" in lane_phases:
            if line := _emit_status("narrowing"):
                yield line

        constraints = load_constraints()
        process_cfg = constraints.get("process_lane", {})
        timeout_seconds = float(process_cfg.get("dispatch_timeout_seconds", 20))

        if "composing" in lane_phases:
            if line := _emit_status("composing"):
                yield line

        envelope = ChatProcessEnvelope(
            site_id=request.site_id,
            query=request.query,
            intent_handoff=handoff.brief(),
            prefetched_hits=prefetched_hits,
        )
        receipt = await dispatch_process(
            envelope,
            run_process_lane,
            timeout_seconds=timeout_seconds,
        )
        products_payload = [p.model_dump() for p in receipt.retrieved_products]
        answer = normalize_shopper_answer(receipt.answer)
        cfg = apply_settings()
        meta = ChatRuntimeMeta(
            lane="catalog_search",
            intent_source=intent.source,
            llm_agent="zooplus-synthesis",
            llm_model=resolved_agent_model("zooplus-synthesis", default=cfg.opencode_model),
        )
        yield _line({"type": "products", "retrieved_products": products_payload})
        yield _line(
            {
                "type": "done",
                "answer": answer,
                "retrieved_products": products_payload,
                "meta": meta.model_dump(),
            }
        )
    finally:
        request_llm_model.reset(model_token)
