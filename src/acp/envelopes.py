"""Typed envelopes and receipts for process-lane dispatch."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from uuid import uuid4

from src.models.chat import RetrievedProduct


@dataclass(frozen=True)
class ChatProcessEnvelope:
    site_id: int
    query: str
    dispatch_id: str = field(default_factory=lambda: str(uuid4()))
    source_surface: str = "api/chat"
    created_at: float = field(default_factory=time)


@dataclass(frozen=True)
class TopicDeclineEnvelope:
    site_id: int
    query: str
    reason_code: str
    polite_decline: str
    dispatch_id: str = field(default_factory=lambda: str(uuid4()))
    source_surface: str = "api/chat"
    created_at: float = field(default_factory=time)


@dataclass(frozen=True)
class ProcessLaneReceipt:
    dispatch_id: str
    dispatch_ok: bool
    status: str
    answer: str
    retrieved_products: list[RetrievedProduct]
    blocked_reason: str | None = None
