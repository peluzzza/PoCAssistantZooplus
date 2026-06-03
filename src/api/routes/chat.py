"""POST /chat and /chat/stream — dual-lane orchestrator."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.lanes.orchestrator import handle_chat
from src.lanes.stream import stream_chat_events
from src.models.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    return await handle_chat(body)


@router.post("/chat/stream")
async def chat_stream(body: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_chat_events(body),
        media_type="application/x-ndjson",
    )
