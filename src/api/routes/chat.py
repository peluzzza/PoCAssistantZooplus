"""POST /chat endpoint wired to dual-lane orchestrator."""

from __future__ import annotations

from fastapi import APIRouter
from src.lanes.orchestrator import handle_chat
from src.models.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    return await handle_chat(body)
