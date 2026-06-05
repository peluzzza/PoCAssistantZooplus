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
            answer=(
                "That search took longer than expected. Please try again with a shorter "
                "question, or narrow to dog or cat and one product type (e.g. dry food under 20 EUR)."
            ),
            retrieved_products=[],
            blocked_reason="process_timeout",
        )
