"""Chat UI static assets and public runtime config."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from src.config import apply_settings
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
    settings = apply_settings()
    return {
        "sites": [1, 3, 15],
        "site_labels": {
            1: "Shop 1 (100 variants · dogs & cats)",
            3: "Shop 3 (100 variants · dogs & cats)",
            15: "Shop 15 (100 variants · dogs & cats)",
        },
        "catalog_scope": "DOGS and CATS only — 300 variants across 3 site_id shops",
        "default_site_id": 3,
        "synthesis_mode": settings.synthesis_mode,
        "opencode_model": settings.opencode_model,
        "opencode_auth_configured": opencode_auth_present(settings),
        "chat_endpoint": "/chat",
        "stream_endpoint": "/chat/stream",
        "wait_phases": {
            "social": ["One moment…", "Reading message…", "Almost there…"],
            "catalog": ["One moment…", "Searching catalog…", "Picking matches…"],
            "decline": ["One moment…", "Checking scope…", "Almost there…"],
            "default": ["One moment…", "Working on it…", "Almost there…"],
        },
        "wait_phase_interval_ms": 2600,
        "wait_phase_max": 3,
    }
