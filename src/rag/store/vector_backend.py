"""Vector store backend selection (local Chroma vs future managed)."""

from __future__ import annotations

import os
from enum import StrEnum
from typing import Protocol


class VectorBackend(StrEnum):
    CHROMA_LOCAL = "chroma_local"
    MANAGED = "managed"  # placeholder for hosted vector DB


class VectorStore(Protocol):
    def query(
        self,
        query_text: str,
        site_id: int,
        *,
        n_results: int = 5,
        pet_type: str | None = None,
    ) -> list[dict]: ...


def active_backend() -> VectorBackend:
    raw = os.environ.get("ZOOPLUS_VECTOR_BACKEND", VectorBackend.CHROMA_LOCAL.value).lower()
    try:
        return VectorBackend(raw)
    except ValueError:
        return VectorBackend.CHROMA_LOCAL


def backend_label() -> str:
    """Human-readable backend for metrics and runbook."""
    backend = active_backend()
    if backend == VectorBackend.MANAGED:
        return "managed (not wired in PoC — set ZOOPLUS_VECTOR_BACKEND=chroma_local)"
    return "chroma_local"
