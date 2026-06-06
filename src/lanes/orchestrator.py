"""Dual-lane orchestrator — agentic intent + social / catalog process."""

from __future__ import annotations

import asyncio
import logging

from src.acp.dispatcher import dispatch_process
from src.acp.envelopes import ChatProcessEnvelope
from src.agents.handoff import build_handoff
from src.agents.intent_agent import (
    _fallback_intent_decision,
    classify_intent,
)
from src.agents.registry import resolved_agent_model
from src.agents.social_agent import social_reply
from src.cache.ttl_cache import cache_enabled, chat_cache
from src.config import apply_settings
from src.guardian.engine import load_constraints, max_recommendations
from src.lanes.process import run_process_lane
from src.llm.answer_sanitize import normalize_shopper_answer
from src.models.chat import ChatRequest, ChatResponse, ChatRuntimeMeta
from src.observability.metrics import record_chat_outcome
from src.rag.price_filter import parse_eur_price_range
from src.rag.retrieve import search_catalog

logger = logging.getLogger(__name__)


def _chat_cache_key(site_id: int, query: str) -> str:
    return f"{site_id}:{query.strip().lower()}"


async def _classify_intent_bounded(query: str, site_id: int):
    constraints = load_constraints()
    lane_cfg = constraints.get("interactive_lane", {})
    intent_timeout = float(lane_cfg.get("intent_timeout_seconds", 22))
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(classify_intent, query, site_id),
            timeout=intent_timeout,
        )
    except TimeoutError:
        logger.warning(
            "intent lane exceeded %.0fs; topic fallback (no extra OpenCode)",
            intent_timeout,
        )
        return await asyncio.to_thread(
            _fallback_intent_decision,
            query,
            site_id=site_id,
            reason="intent_lane_timeout",
        )


async def handle_chat(request: ChatRequest) -> ChatResponse:
    from src.agents.request_context import request_llm_model

    model_token = request_llm_model.set(request.preferred_model)
    try:
        return await _handle_chat_inner(request)
    finally:
        request_llm_model.reset(model_token)


async def _handle_chat_inner(request: ChatRequest) -> ChatResponse:
    cache_key = _chat_cache_key(request.site_id, request.query)
    if cache_enabled():
        cached = chat_cache.get(cache_key)
        if cached is not None:
            logger.info("chat cache hit site=%s", request.site_id)
            return ChatResponse.model_validate(cached)

    intent = await _classify_intent_bounded(request.query, request.site_id)

    prefetched_hits: tuple[dict, ...] | None = None
    if intent.lane == "catalog_search":
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

    handoff = build_handoff(
        query=request.query,
        site_id=request.site_id,
        lane=intent.lane,
        topic=intent.topic,
        social_kind=intent.social_kind,
        reason=intent.reason,
        source=intent.source,
    )

    if intent.lane == "decline_off_topic":
        answer, run_meta = await asyncio.to_thread(
            social_reply,
            request.query,
            request.site_id,
            intent,
            handoff.brief(),
        )
        record_chat_outcome(declined=True)
        response = ChatResponse(
            answer=normalize_shopper_answer(answer),
            retrieved_products=[],
            meta=ChatRuntimeMeta(
                lane=run_meta.lane,
                intent_source=run_meta.intent_source,
                llm_agent=run_meta.llm_agent,
                llm_model=run_meta.llm_model,
            ),
        )
        if cache_enabled():
            chat_cache.set(cache_key, response.model_dump())
        return response

    if intent.lane == "conversational":
        answer, run_meta = await asyncio.to_thread(
            social_reply,
            request.query,
            request.site_id,
            intent,
            handoff.brief(),
        )
        record_chat_outcome(declined=False)
        response = ChatResponse(
            answer=normalize_shopper_answer(answer),
            retrieved_products=[],
            meta=ChatRuntimeMeta(
                lane=run_meta.lane,
                intent_source=run_meta.intent_source,
                llm_agent=run_meta.llm_agent,
                llm_model=run_meta.llm_model,
            ),
        )
        if cache_enabled():
            chat_cache.set(cache_key, response.model_dump())
        return response

    constraints = load_constraints()
    process_cfg = constraints.get("process_lane", {})
    timeout_seconds = float(process_cfg.get("dispatch_timeout_seconds", 20))

    envelope = ChatProcessEnvelope(
        site_id=request.site_id,
        query=request.query,
        intent_handoff=handoff.brief(),
        prefetched_hits=prefetched_hits,
    )
    process_task = asyncio.create_task(
        dispatch_process(envelope, run_process_lane, timeout_seconds=timeout_seconds)
    )
    receipt = await process_task
    record_chat_outcome(declined=False)
    cfg = apply_settings()
    response = ChatResponse(
        answer=normalize_shopper_answer(receipt.answer),
        retrieved_products=receipt.retrieved_products,
        meta=ChatRuntimeMeta(
            lane="catalog_search",
            intent_source=intent.source,
            llm_agent="zooplus-synthesis",
            llm_model=resolved_agent_model("zooplus-synthesis", default=cfg.opencode_model),
        ),
    )
    if cache_enabled():
        chat_cache.set(cache_key, response.model_dump())
    return response
