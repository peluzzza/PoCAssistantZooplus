"""Chat UI static assets and public runtime config."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from src.agents.registry import agent_models_map, model_for_role
from src.config import apply_settings
from src.llm.opencode import opencode_auth_present
from src.llm.opencode_models import models_for_ui

router = APIRouter()

# Dataset shops (EDA): site_id → locale — display only; API still sends numeric site_id.
SITE_LABELS: dict[int, str] = {
    1: "Germany (de-DE)",
    3: "United Kingdom (en-GB)",
    15: "Spain (es-ES)",
}

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
    settings = apply_settings()
    return {
        "sites": [1, 3, 15],
        "site_labels": {str(k): v for k, v in SITE_LABELS.items()},
        "catalog_scope": "DOGS and CATS only — 300 variants across Germany, UK, and Spain shops",
        "default_site_id": 3,
        "synthesis_mode": settings.synthesis_mode,
        "opencode_model": settings.opencode_model,
        "opencode_models_by_role": {
            "default": settings.opencode_model,
            "social": model_for_role("social", default=settings.opencode_model),
            "intent": model_for_role("intent", default=settings.opencode_model),
            "conductor": model_for_role("conductor", default=settings.opencode_model),
            "synthesis": model_for_role("synthesis", default=settings.opencode_model),
        },
        "opencode_auth_configured": opencode_auth_present(settings),
        "chat_endpoint": "/chat/stream",
        "stream_endpoint": "/chat/stream",
        "status_messages_from_server": True,
        "models": models_for_ui(settings=settings),
        "agent_models": agent_models_map(),
    }


@router.get("/api/ui/models")
async def ui_models(refresh: bool = False) -> dict:
    from src.llm.opencode_models import list_opencode_models

    settings = apply_settings()
    if refresh:
        list_opencode_models(settings=settings, force_refresh=True)
    return models_for_ui(settings=settings)
