"""Chat UI static assets and public runtime config."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from src.config import Settings
from src.llm.opencode import opencode_auth_present

router = APIRouter()

UI_DIR = Path(__file__).resolve().parents[3] / "static" / "ui"
UI_ASSETS = frozenset({"styles.css", "app.js"})


def ui_directory() -> Path:
    """Resolve static/ui from package layout or cwd (editable install / Docker)."""
    candidates = [
        UI_DIR,
        Path.cwd() / "static" / "ui",
    ]
    for path in candidates:
        if (path / "index.html").is_file():
            return path
    return UI_DIR


@router.get("/")
async def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/ui/", status_code=302)


@router.get("/ui")
async def ui_redirect_trailing_slash() -> RedirectResponse:
    return RedirectResponse(url="/ui/", status_code=302)


@router.get("/ui/")
async def ui_index() -> FileResponse:
    index = ui_directory() / "index.html"
    if not index.is_file():
        raise HTTPException(status_code=503, detail="Chat UI not found (missing static/ui)")
    return FileResponse(index, media_type="text/html; charset=utf-8")


@router.get("/ui/{asset}")
async def ui_asset(asset: str) -> FileResponse:
    if asset not in UI_ASSETS:
        raise HTTPException(status_code=404, detail="Not found")
    path = ui_directory() / asset
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    media = "text/css" if asset.endswith(".css") else "application/javascript"
    return FileResponse(path, media_type=f"{media}; charset=utf-8")


@router.get("/api/ui/config")
async def ui_config() -> dict:
    settings = Settings.from_env()
    timeout_ms = int(os.environ.get("ZOOPLUS_CHAT_CLIENT_TIMEOUT_MS", "0"))
    if timeout_ms <= 0:
        # Intent + RAG + synthesis can stack; default above single OpenCode timeout.
        timeout_ms = max(45000, settings.opencode_timeout_seconds * 2000 + 15000)
    from src.agents.registry import agent_chain_for_role, list_available_agent_ids

    return {
        "sites": [1, 3, 15],
        "default_site_id": 3,
        "synthesis_mode": settings.synthesis_mode,
        "opencode_model": settings.opencode_model,
        "opencode_auth_configured": opencode_auth_present(settings),
        "chat_timeout_ms": timeout_ms,
        "agent_cascade_enabled": os.environ.get("ZOOPLUS_AGENT_CASCADE", "1").lower()
        not in ("0", "false", "no"),
        "available_agents": list_available_agent_ids(),
        "intent_agent_chain": list(agent_chain_for_role("intent")),
        "chat_endpoint": "/chat",
        "stream_endpoint": "/chat/stream",
    }
