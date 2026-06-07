"""POST /chat and /chat/stream — dual-lane orchestrator."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from src.lanes.orchestrator import handle_chat
from src.lanes.stream import stream_chat_events
from src.llm.language_context import bind_shopper_language_async
from src.models.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    accept_language = request.headers.get("accept-language")
    async with bind_shopper_language_async(body.query, accept_language, site_id=body.site_id):
        return await handle_chat(body)


@router.post("/chat/stream")
async def chat_stream(body: ChatRequest, request: Request) -> StreamingResponse:
    accept_language = request.headers.get("accept-language")

    async def _events():
        async with bind_shopper_language_async(body.query, accept_language, site_id=body.site_id):
            async for line in stream_chat_events(body):
                yield line

    return StreamingResponse(
        _events(),
        media_type="application/x-ndjson",
    )
