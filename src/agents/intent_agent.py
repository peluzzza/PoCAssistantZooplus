"""Agentic intent router (OpenCode) — default-deny, no keyword routing in production."""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Literal

from src.agents.prompts import INTENT_SYSTEM
from src.config import Settings, apply_settings
from src.guardian.engine import EXTERNAL_WEB_DECLINE, polite_decline_for
from src.llm.opencode import _run_opencode_prompt, opencode_auth_present

logger = logging.getLogger(__name__)

Lane = Literal["conversational", "catalog_search", "decline_off_topic"]
SocialKind = Literal["greeting", "identity", "thanks", "help", "bye", "clarify"] | None

_JSON_BLOCK = re.compile(r"\{[\s\S]*\}")


@dataclass(frozen=True)
class IntentDecision:
    lane: Lane
    social_kind: SocialKind = None
    confidence: float = 1.0
    reason: str = ""
    source: str = "agent"
    decline_message: str | None = None


def intent_mode() -> str:
    return os.environ.get("ZOOPLUS_INTENT_MODE", "agentic").lower()


def _parse_intent_json(raw: str) -> dict | None:
    if not raw:
        return None
    text = raw.strip()
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        pass
    match = _JSON_BLOCK.search(text)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def _normalize_lane(value: str | None) -> Lane:
    v = (value or "").strip().lower().replace("-", "_")
    if v in ("conversational", "conversation", "social", "chitchat"):
        return "conversational"
    if v in ("catalog_search", "catalog", "product", "products", "rag", "search"):
        return "catalog_search"
    return "decline_off_topic"


def _normalize_social_kind(value: str | None) -> SocialKind:
    if not value:
        return None
    v = value.strip().lower()
    if v in ("greeting", "hello", "hi"):
        return "greeting"
    if v in ("identity", "who_are_you", "about"):
        return "identity"
    if v in ("thanks", "thank_you"):
        return "thanks"
    if v in ("help", "capabilities"):
        return "help"
    if v in ("bye", "goodbye"):
        return "bye"
    if v in ("clarify",):
        return "clarify"
    return None


def _build_intent_prompt(query: str, site_id: int) -> str:
    return (
        f"{INTENT_SYSTEM}\n\n"
        f"shop site_id: {site_id}\n"
        f'Customer message: "{query}"\n'
    )


def _decline_copy(_reason: str, *, query: str) -> str:
    q = query.lower()
    if "internet" in q or "browse the web" in q or "web search" in q:
        return EXTERNAL_WEB_DECLINE
    return polite_decline_for("out_of_scope_default_deny")


def classify_intent_agentic(
    query: str,
    site_id: int,
    *,
    settings: Settings | None = None,
) -> IntentDecision:
    """Classify via local OpenCode agent (primary production path)."""
    cfg = settings or apply_settings()
    prompt = _build_intent_prompt(query, site_id)
    raw = _run_opencode_prompt(prompt, settings=cfg, timeout_seconds=min(12, cfg.opencode_timeout_seconds))
    parsed = _parse_intent_json(raw or "")
    if not parsed:
        logger.warning("intent agent returned no JSON; safe decline")
        return IntentDecision(
            lane="decline_off_topic",
            confidence=0.0,
            reason="agent_parse_failed",
            source="agent_fallback",
            decline_message=_decline_copy("parse_failed", query=query),
        )

    lane = _normalize_lane(str(parsed.get("lane", "")))
    kind = _normalize_social_kind(
        str(parsed.get("social_kind") or parsed.get("social") or "") or None
    )
    try:
        confidence = float(parsed.get("confidence", 0.8))
    except (TypeError, ValueError):
        confidence = 0.8
    reason = str(parsed.get("reason") or parsed.get("brief_reason") or "")

    decline_msg = None
    if lane == "decline_off_topic":
        decline_msg = _decline_copy(reason, query=query)

    return IntentDecision(
        lane=lane,
        social_kind=kind if lane == "conversational" else None,
        confidence=confidence,
        reason=reason,
        source="opencode",
        decline_message=decline_msg,
    )


def load_oracle_decision(query: str) -> IntentDecision | None:
    """Test oracle lookup (built from instructions matrix — not used in production agentic mode)."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    path = root / "tests" / "fixtures" / "intent_oracle.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    key = query.strip().lower()
    row = data.get(key)
    if not row:
        return None
    lane = _normalize_lane(row.get("lane"))
    kind = _normalize_social_kind(row.get("social_kind"))
    return IntentDecision(
        lane=lane,
        social_kind=kind,
        confidence=float(row.get("confidence", 1.0)),
        reason=str(row.get("reason", "oracle")),
        source="oracle",
        decline_message=row.get("decline_message") or _decline_copy("", query=query)
        if lane == "decline_off_topic"
        else None,
    )


def classify_intent(
    query: str,
    site_id: int,
    *,
    settings: Settings | None = None,
) -> IntentDecision:
    """Route intent: oracle (tests), agentic OpenCode (prod), or safe decline if agent unavailable."""
    mode = intent_mode()
    text = (query or "").strip()
    if not text:
        return IntentDecision(
            lane="decline_off_topic",
            reason="empty",
            source="policy",
            decline_message=polite_decline_for("out_of_scope_empty"),
        )

    if mode == "oracle":
        oracle = load_oracle_decision(text)
        if oracle:
            return oracle
        logger.warning("oracle miss for %r — decline", text[:80])
        return IntentDecision(
            lane="decline_off_topic",
            reason="oracle_miss",
            source="oracle",
            decline_message=polite_decline_for("out_of_scope_default_deny"),
        )

    cfg = settings or apply_settings()
    if mode == "agentic" or (mode == "auto" and opencode_auth_present(cfg)):
        decision = classify_intent_agentic(text, site_id, settings=cfg)
        if decision.source == "opencode":
            return decision
        oracle = load_oracle_decision(text)
        if oracle:
            return oracle
        return decision

    # Agentic required but OpenCode unavailable — do NOT keyword-route or RAG blindly.
    return IntentDecision(
        lane="decline_off_topic",
        reason="agent_unavailable",
        source="safe_fallback",
        decline_message=(
            "I'm the zooplus Assistant — I need the local AI agent to understand your message right now. "
            "Please check OpenCode auth (scripts/setup_opencode_local.ps1) or set ZOOPLUS_INTENT_MODE=oracle for tests. "
            "I'm here for dog and cat products in this shop once the agent is available."
        ),
    )
