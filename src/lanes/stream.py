"""NDJSON stream — timed social chunks (Anthropic delta style) + parallel catalog."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator

from src.acp.dispatcher import dispatch_process
from src.acp.envelopes import ChatProcessEnvelope
from src.agents.conductor_orchestrator import (
    ConductorState,
    chunk_is_redundant,
    conductor_status_text,
    conductor_tick,
    dedupe_answer_against_chunks,
    stream_context_for_synthesis,
)
from src.agents.intent_agent import IntentDecision, try_obvious_social_intent
from src.agents.handoff import build_handoff
from src.agents.registry import resolved_agent_model
from src.agents.social_agent import social_chunk_reply, social_reply
from src.agents.stream_voice_registry import (
    format_catalog_opening,
    probe_instant_lane,
    progress_phrase,
)
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
    status_chunks: list[str],
    first_tick: int = 0,
) -> AsyncIterator[str]:
    """Conductor emits fast status chunks while catalog agents run in parallel."""
    started = time.monotonic()
    max_ticks = cfg.max_chunk_messages
    interval = cfg.chunk_interval_seconds
    min_typing = (
        min(cfg.chunk_min_typing_seconds, 0.6)
        if cfg.conductor_fast_status
        else cfg.chunk_min_typing_seconds
    )
    min_pause = cfg.chunk_min_pause_seconds

    for tick_index in range(first_tick, max_ticks):
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
            messages_sent=tuple(status_chunks),
            catalog_running=not catalog_task.done(),
            catalog_done=catalog_task.done(),
            shopper_status=shopper_status if tick_index == 0 else None,
        )
        step = await asyncio.to_thread(conductor_tick, state, settings=cfg)

        if step.action == "complete":
            return

        if step.action == "emit_message":
            text: str | None = None
            if cfg.conductor_fast_status:
                text = conductor_status_text(state)
            elif step.message_brief:
                yield _line(_typing_event(chunk=tick_index))
                llm_task = asyncio.create_task(
                    asyncio.to_thread(
                        social_chunk_reply,
                        request.query,
                        request.site_id,
                        chunk_index=tick_index,
                        elapsed_seconds=elapsed,
                        previous_chunks=tuple(status_chunks),
                        catalog_still_running=not catalog_task.done(),
                        shopper_status=shopper_status if tick_index == 0 else None,
                        conductor_brief=step.message_brief,
                        settings=cfg,
                    )
                )
                if min_typing > 0:
                    await asyncio.sleep(min_typing)
                text = await llm_task

            if not text or chunk_is_redundant(text, tuple(status_chunks)):
                if catalog_task.done():
                    return
                continue

            yield _line(_typing_event(chunk=tick_index))
            if min_typing > 0:
                await asyncio.sleep(min_typing)
            if not is_current_turn(session_id, turn_id):
                return
            yield _line(_chunk_event(text, chunk_index=tick_index, elapsed_s=elapsed))
            status_chunks.append(text)

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


def _probe_catalog_intent(query: str, site_id: int) -> IntentDecision:
    return IntentDecision(
        lane="catalog_search",
        confidence=0.9,
        reason="stream_probe_catalog",
        source="probe_catalog",
    )


async def _cancel_task(task: asyncio.Task) -> None:
    if task.done():
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def _emit_intent_wait_chunk(
    intent_task: asyncio.Task,
    *,
    request: ChatRequest,
    session_id: str,
    turn_id: int,
    cfg: Settings,
    chunk_index: int = 0,
) -> AsyncIterator[str]:
    """One progress bubble while agentic intent is still classifying."""
    if intent_task.done():
        return
    wait_s = min(2.0, max(0.6, cfg.chunk_min_typing_seconds))
    try:
        await asyncio.wait_for(asyncio.shield(intent_task), timeout=wait_s)
        return
    except TimeoutError:
        pass
    if not is_current_turn(session_id, turn_id) or intent_task.done():
        return
    text = progress_phrase(request.query, chunk_index, site_id=request.site_id)
    yield _line(_typing_event(chunk=chunk_index))
    if cfg.chunk_min_typing_seconds > 0:
        await asyncio.sleep(min(cfg.chunk_min_typing_seconds, 0.4))
    yield _line(_chunk_event(text, chunk_index=chunk_index, elapsed_s=0))


async def _yield_social_done(
    request: ChatRequest,
    intent: IntentDecision,
    *,
    session_id: str,
    turn_id: int,
    cfg: Settings,
) -> AsyncIterator[str]:
    handoff = build_handoff(
        query=request.query,
        site_id=request.site_id,
        lane=intent.lane,
        topic=intent.topic,
        social_kind=intent.social_kind,
        reason=intent.reason,
        source=intent.source,
    )
    if cfg.chunk_min_typing_seconds > 0:
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


async def _yield_catalog_finish(
    request: ChatRequest,
    intent: IntentDecision,
    catalog_task: asyncio.Task,
    status_chunks: list[str],
    *,
    session_id: str,
    turn_id: int,
    cfg: Settings,
) -> AsyncIterator[str]:
    if not is_current_turn(session_id, turn_id):
        catalog_task.cancel()
        return
    _hits, receipt = await catalog_task
    if cfg.chunk_min_typing_seconds > 0:
        yield _line(_typing_event(chunk=99))
        await asyncio.sleep(cfg.chunk_min_typing_seconds)
    products_payload = [p.model_dump() for p in receipt.retrieved_products]
    answer = normalize_shopper_answer(receipt.answer)
    if status_chunks:
        answer = dedupe_answer_against_chunks(answer, tuple(status_chunks))
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


async def stream_chat_events(request: ChatRequest) -> AsyncIterator[str]:
    """Yield NDJSON: typing/chunk* (timed) → topic → products+done."""
    from src.agents.request_context import request_llm_model

    model_token = request_llm_model.set(request.preferred_model)
    cfg = apply_settings()
    session_id = (request.session_id or "default").strip() or "default"
    turn_id = bump_session_turn(session_id)

    try:
        status_chunks: list[str] = []
        lane_probe = (
            probe_instant_lane(request.query, request.site_id)
            if cfg.stream_mode == "conductor"
            else "pending"
        )
        intent_task = asyncio.create_task(
            _classify_intent_bounded(request.query, request.site_id)
        )

        yield _line(_typing_event(chunk=0))

        # --- Fast social: reply without waiting for slow conductor intent ---
        if lane_probe == "social":
            obvious = try_obvious_social_intent(request.query)
            if obvious is not None:
                yield _line(_topic_event(obvious))
                async for line in _yield_social_done(
                    request,
                    obvious,
                    session_id=session_id,
                    turn_id=turn_id,
                    cfg=cfg,
                ):
                    yield line
                await _cancel_task(intent_task)
                return

        # --- Fast catalog: ack + parallel catalog while intent classifies ---
        if lane_probe == "catalog":
            if not status_chunks:
                opening = format_catalog_opening(request.query, request.site_id)
                yield _line(_chunk_event(opening, chunk_index=0, elapsed_s=0))
                status_chunks.append(opening)
            provisional = _probe_catalog_intent(request.query, request.site_id)
            yield _line(_topic_event(provisional))
            handoff = build_handoff(
                query=request.query,
                site_id=request.site_id,
                lane=provisional.lane,
                topic=provisional.topic,
                social_kind=provisional.social_kind,
                reason=provisional.reason,
                source=provisional.source,
            )
            handoff_brief = handoff.brief()
            if status_chunks:
                handoff_brief = (
                    f"{handoff_brief}\n\n{stream_context_for_synthesis(tuple(status_chunks))}"
                )
            catalog_task = asyncio.create_task(
                _run_catalog_pipeline(request, handoff_brief)
            )
            if cfg.stream_mode == "conductor":
                async for line in _emit_conductor_chunks(
                    request=request,
                    catalog_task=catalog_task,
                    lane=provisional.lane,
                    shopper_status=None,
                    session_id=session_id,
                    turn_id=turn_id,
                    cfg=cfg,
                    status_chunks=status_chunks,
                    first_tick=1 if status_chunks else 0,
                ):
                    yield line
            else:
                async for line in _emit_timed_chunks(
                    request=request,
                    catalog_task=catalog_task,
                    shopper_status=None,
                    session_id=session_id,
                    turn_id=turn_id,
                    cfg=cfg,
                ):
                    yield line
            intent = await intent_task
            if not is_current_turn(session_id, turn_id):
                await _cancel_task(catalog_task)
                return
            if intent.lane in ("decline_off_topic", "conversational"):
                await _cancel_task(catalog_task)
                status_chunks.clear()
                yield _line(_topic_event(intent))
                async for line in _yield_social_done(
                    request,
                    intent,
                    session_id=session_id,
                    turn_id=turn_id,
                    cfg=cfg,
                ):
                    yield line
                return
            async for line in _yield_catalog_finish(
                request,
                intent,
                catalog_task,
                status_chunks,
                session_id=session_id,
                turn_id=turn_id,
                cfg=cfg,
            ):
                yield line
            return

        # --- Pending: optional progress chunk while agentic intent runs ---
        async for line in _emit_intent_wait_chunk(
            intent_task,
            request=request,
            session_id=session_id,
            turn_id=turn_id,
            cfg=cfg,
            chunk_index=1 if status_chunks else 0,
        ):
            yield line

        intent = await intent_task

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
            status_chunks.clear()
            async for line in _yield_social_done(
                request,
                intent,
                session_id=session_id,
                turn_id=turn_id,
                cfg=cfg,
            ):
                yield line
            return

        if (
            cfg.stream_mode == "conductor"
            and not status_chunks
            and intent.lane == "catalog_search"
        ):
            opening = format_catalog_opening(request.query, request.site_id)
            yield _line(_chunk_event(opening, chunk_index=0, elapsed_s=0))
            status_chunks.append(opening)

        handoff_brief = handoff.brief()
        if status_chunks:
            handoff_brief = (
                f"{handoff_brief}\n\n{stream_context_for_synthesis(tuple(status_chunks))}"
            )
        catalog_task = asyncio.create_task(_run_catalog_pipeline(request, handoff_brief))
        if cfg.stream_mode == "conductor":
            async for line in _emit_conductor_chunks(
                request=request,
                catalog_task=catalog_task,
                lane=intent.lane,
                shopper_status=shopper_status,
                session_id=session_id,
                turn_id=turn_id,
                cfg=cfg,
                status_chunks=status_chunks,
                first_tick=1 if status_chunks else 0,
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

        async for line in _yield_catalog_finish(
            request,
            intent,
            catalog_task,
            status_chunks,
            session_id=session_id,
            turn_id=turn_id,
            cfg=cfg,
        ):
            yield line
    finally:
        request_llm_model.reset(model_token)
