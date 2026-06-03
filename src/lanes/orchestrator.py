"""Dual-lane orchestrator — Interactive (fast) + Process (RAG). Implemented in T4."""

from __future__ import annotations

from src.models.chat import ChatRequest, ChatResponse


async def handle_chat(request: ChatRequest) -> ChatResponse:
    raise NotImplementedError("Dual-lane orchestrator — trace step T4")
