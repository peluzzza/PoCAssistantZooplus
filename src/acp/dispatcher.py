"""Async dispatcher for process lane work."""

from __future__ import annotations

import asyncio

from src.acp.envelopes import ChatProcessEnvelope, ProcessLaneReceipt


async def dispatch_process(
    envelope: ChatProcessEnvelope,
    worker_coro,
    *,
    timeout_seconds: float = 15,
) -> ProcessLaneReceipt:
    task = asyncio.create_task(worker_coro(envelope))
    try:
        return await asyncio.wait_for(task, timeout=timeout_seconds)
    except TimeoutError:
        task.cancel()
        return ProcessLaneReceipt(
            dispatch_id=envelope.dispatch_id,
            dispatch_ok=False,
            status="timeout",
            answer="I'm still checking products for your request. Please try again.",
            retrieved_products=[],
            blocked_reason="process_timeout",
        )
