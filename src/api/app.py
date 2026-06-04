"""Async FastAPI application entrypoint."""

from __future__ import annotations

import logging
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api.routes.chat import router as chat_router
from src.api.routes.mcp import router as mcp_router
from src.api.routes.system import router as system_router
from src.api.routes.ui import router as ui_router
from src.config import apply_settings
from src.observability.middleware import ObservabilityMiddleware

try:
    _APP_VERSION = version("zooplus-assistant-poc")
except PackageNotFoundError:
    _APP_VERSION = "0.0.0"


def create_app() -> FastAPI:
    settings = apply_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))

    application = FastAPI(
        title="zooplus Assistant",
        description="PoC pet-product chat API (RAG + agent-first)",
        version=_APP_VERSION,
    )
    if settings.metrics_enabled:
        application.add_middleware(ObservabilityMiddleware)

    static_dir = Path(__file__).resolve().parents[2] / "static" / "ui"
    application.include_router(ui_router, tags=["ui"])
    application.include_router(system_router, tags=["system"])
    application.include_router(chat_router, tags=["chat"])
    application.include_router(mcp_router, tags=["mcp"])
    if static_dir.is_dir():
        application.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="ui")
    return application


app = create_app()
