"""POST /chat — stub until T5."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.models.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    raise HTTPException(
        status_code=501,
        detail="Chat pipeline not wired yet. See docs/trace/T5-api-contract.md",
    )
