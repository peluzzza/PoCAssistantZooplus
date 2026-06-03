"""Async FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from src.api.routes.chat import router as chat_router
from src.api.routes.mcp import router as mcp_router

app = FastAPI(
    title="zooplus Assistant",
    description="PoC pet-product chat API (RAG + agent-first)",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(chat_router, tags=["chat"])
app.include_router(mcp_router, tags=["mcp"])
