"""System routes — health, metrics, readiness."""

from __future__ import annotations

from fastapi import APIRouter
from src.observability.metrics import snapshot
from src.rag.pipeline import index_dir

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> dict[str, str | bool]:
    """Readiness: Chroma index directory exists."""
    path = index_dir()
    ok = path.exists() and any(path.iterdir()) if path.exists() else False
    return {"status": "ready" if ok else "not_ready", "index_present": ok}


@router.get("/metrics")
async def metrics() -> dict:
    return snapshot()
