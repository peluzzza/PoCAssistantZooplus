"""NDJSON stream — timed social chunks (Anthropic delta style) + parallel catalog."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator

from src.acp.dispatcher import dispatch_process
from src.acp.envelopes import ChatProcessEnvelope
from src.agents.conductor_orchestrator import ConductorState, conductor_next_step
from src.agents.handoff import build_handoff
from src.agents.registry import resolved_agent_model
from src.agents.social_agent import social_chunk_reply, social_reply
from src.cache.session_turn import bump_session_turn, is_current_turn
from src.config import Settings, apply_settings
from src.guardian.engine import load_constraints, max_recommendations
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


def _typing_event(*, chunk: int, active: bool = True) -> dict:
    return {"type": "typing", "chunk": chunk, "active": active}


def _chunk_event(text: str, *, chunk_index: int, elapsed_s: int) -> dict:
    return {
        "type": "chunk",
        "chunk": chunk_index,
        "elapsed_s": elapsed_s,
        "text": text,
    }


async def _sleep_until(deadline: float) -> None:
    wait = deadline - time.monotonic()
    if wait > 0:
        await asyncio.sleep(wait)


async def _run_catalog_pipeline(
    request: ChatRequest,
    handoff_brief: str,
) -> tuple[tuple[dict, ...], object]:
    cap = max_recommendations()
    pool_n = max(cap * 6, 24) if parse_eur_price_range(request.query) else cap
    hits = tuple(
        await asyncio.to_thread(
            search_catalog,
            request.query,
            request.site_id,
            n_results=pool_n,
        )
    )
    constraints = load_constraints()
    process_cfg = constraints.get("process_lane", {})
    timeout_seconds = float(process_cfg.get("dispatch_timeout_seconds", 20))
    envelope = ChatProcessEnvelope(
        site_id=request.site_id,
        query=request.query,
        intent_handoff=handoff_brief,
        prefetched_hits=hits,
    )
    receipt = await dispatch_process(
        envelope,
        run_process_lane,
        timeout_seconds=timeout_seconds,
    )
    return hits, receipt


async def _emit_conductor_chunks(
    *,
    request: ChatRequest,
    catalog_task: asyncio.Task,
    lane: str,
    shopper_status: str | None,
    session_id: str,
    turn_id: int,
    cfg: Settings,
) -> AsyncIterator[str]:
    """Invisible conductor decides each tick; social agent voices messages."""
    messages: list[str] = []
    started = time.monotonic()
    max_ticks = cfg.max_chunk_messages
    interval = cfg.chunk_interval_seconds
    min_typing = cfg.chunk_min_typing_seconds
    min_pause = cfg.chunk_min_pause_seconds

    for tick_index in range(max_ticks):
        if not is_current_turn(session_id, turn_id):
            return

        await _sleep_until(started + tick_index * interval)
        elapsed = int(time.monotonic() - started)
        state = ConductorState(
            query=request.query,
            site_id=request.site_id,
            lane=lane,
            tick_index=tick_index,
            elapsed_seconds=elapsed,
            messages_sent=tuple(messages),
            catalog_running=not catalog_task.done(),
            catalog_done=catalog_task.done(),
            shopper_status=shopper_status if tick_index == 0 else None,
        )
        step = await asyncio.to_thread(conductor_next_step, state, settings=cfg)

        if step.action == "complete":
            return

        if step.action == "emit_message" and step.message_brief:
            yield _line(_typing_event(chunk=tick_index))
            llm_task = asyncio.create_task(
                asyncio.to_thread(
                    social_chunk_reply,
                    request.query,
                    request.site_id,
                    chunk_index=tick_index,
                    elapsed_seconds=elapsed,
                    previous_chunks=tuple(messages),
                    catalog_still_running=not catalog_task.done(),
                    shopper_status=shopper_status if tick_index == 0 else None,
                    conductor_brief=step.message_brief,
                    settings=cfg,
                )
            )
            if min_typing > 0:
                await asyncio.sleep(min_typing)
            text = await llm_task
            if not is_current_turn(session_id, turn_id):
                return
            yield _line(_chunk_event(text, chunk_index=tick_index, elapsed_s=elapsed))
            messages.append(text)

        if catalog_task.done():
            return
        if tick_index + 1 >= max_ticks:
            return
        if min_pause > 0:
            await asyncio.sleep(min_pause)


async def _emit_timed_chunks(
    *,
    request: ChatRequest,
    catalog_task: asyncio.Task,
    shopper_status: str | None,
    session_id: str,
    turn_id: int,
    cfg: Settings,
) -> AsyncIterator[str]:
    """Emit one social chunk per time slot; typing visible before each message."""
    interval = cfg.chunk_interval_seconds
    max_chunks = cfg.max_chunk_messages
    min_typing = cfg.chunk_min_typing_seconds
    min_pause = cfg.chunk_min_pause_seconds
    prior: list[str] = []
    started = time.monotonic()

    for chunk_index in range(max_chunks):
        if not is_current_turn(session_id, turn_id):
            return
        await _sleep_until(started + chunk_index * interval)
        yield _line(_typing_event(chunk=chunk_index))
        llm_task = asyncio.create_task(
            asyncio.to_thread(
                social_chunk_reply,
                request.query,
                request.site_id,
                chunk_index=chunk_index,
                elapsed_seconds=int(time.monotonic() - started),
                previous_chunks=tuple(prior),
                catalog_still_running=not catalog_task.done(),
                shopper_status=shopper_status,
                settings=cfg,
            )
        )
        if min_typing > 0:
            await asyncio.sleep(min_typing)
        text = await llm_task
        if not is_current_turn(session_id, turn_id):
            return
        elapsed_s = int(time.monotonic() - started)
        yield _line(_chunk_event(text, chunk_index=chunk_index, elapsed_s=elapsed_s))
        prior.append(text)
        if catalog_task.done():
            return
        if chunk_index + 1 >= max_chunks:
            return
        if min_pause > 0:
            await asyncio.sleep(min_pause)


async def stream_chat_events(request: ChatRequest) -> AsyncIterator[str]:
    """Yield NDJSON: typing/chunk* (timed) → topic → products+done."""
    from src.agents.request_context import request_llm_model

    model_token = request_llm_model.set(request.preferred_model)
    cfg = apply_settings()
    session_id = (request.session_id or "default").strip() or "default"
    turn_id = bump_session_turn(session_id)

    try:
        intent = await _classify_intent_bounded(request.query, request.site_id)

        if not is_current_turn(session_id, turn_id):
            return

        shopper_status = intent.shopper_status
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
            if cfg.chunk_min_typing_seconds > 0:
                yield _line(_typing_event(chunk=0))
                await asyncio.sleep(cfg.chunk_min_typing_seconds)
            answer, run_meta = await asyncio.to_thread(
                social_reply,
                request.query,
                request.site_id,
                intent,
                handoff.brief(),
            )
            if not is_current_turn(session_id, turn_id):
                return
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

        catalog_task = asyncio.create_task(_run_catalog_pipeline(request, handoff.brief()))
        if cfg.stream_mode == "conductor":
            async for line in _emit_conductor_chunks(
                request=request,
                catalog_task=catalog_task,
                lane=intent.lane,
                shopper_status=shopper_status,
                session_id=session_id,
                turn_id=turn_id,
                cfg=cfg,
            ):
                yield line
        else:
            async for line in _emit_timed_chunks(
                request=request,
                catalog_task=catalog_task,
                shopper_status=shopper_status,
                session_id=session_id,
                turn_id=turn_id,
                cfg=cfg,
            ):
                yield line

        if not is_current_turn(session_id, turn_id):
            catalog_task.cancel()
            return

        _hits, receipt = await catalog_task
        if cfg.chunk_min_typing_seconds > 0:
            yield _line(_typing_event(chunk=99))
            await asyncio.sleep(cfg.chunk_min_typing_seconds)
        products_payload = [p.model_dump() for p in receipt.retrieved_products]
        answer = normalize_shopper_answer(receipt.answer)
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
