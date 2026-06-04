"""Chat UI static assets and public runtime config."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from src.config import Settings
from src.llm.opencode import opencode_auth_present

router = APIRouter()


@router.get("/")
async def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/ui/", status_code=302)


@router.get("/api/ui/config")
async def ui_config() -> dict:
    settings = Settings.from_env()
    return {
        "sites": [1, 3, 15],
        "default_site_id": 3,
        "synthesis_mode": settings.synthesis_mode,
        "opencode_model": settings.opencode_model,
        "opencode_auth_configured": opencode_auth_present(settings),
        "chat_endpoint": "/chat",
        "stream_endpoint": "/chat/stream",
    }
