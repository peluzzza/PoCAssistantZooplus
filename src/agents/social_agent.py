"""Agentic social replies — warm conversational lane (OpenCode + template fallback)."""

from __future__ import annotations

import logging
import os

from src.agents.intent_agent import IntentDecision, SocialKind
from src.agents.prompts import (
    SOCIAL_BYE_CONTEXT,
    SOCIAL_DECLINE_CONTEXT,
    SOCIAL_GREETING_CONTEXT,
    SOCIAL_HELP_CONTEXT,
    SOCIAL_IDENTITY_CONTEXT,
    SOCIAL_SYSTEM,
    SOCIAL_THANKS_CONTEXT,
)
from src.config import Settings, apply_settings
from src.llm.conversation import conversational_reply as template_conversational_reply
from src.llm.opencode import synthesize_opencode_chat

logger = logging.getLogger(__name__)


def _context_for_kind(kind: SocialKind, query: str, intent: IntentDecision) -> str:
    if intent.lane == "decline_off_topic":
        return SOCIAL_DECLINE_CONTEXT
    if kind == "identity":
        return SOCIAL_IDENTITY_CONTEXT
    if kind == "greeting":
        return SOCIAL_GREETING_CONTEXT
    if kind == "help":
        return SOCIAL_HELP_CONTEXT
    if kind == "thanks":
        return SOCIAL_THANKS_CONTEXT
    if kind == "bye":
        return SOCIAL_BYE_CONTEXT
    if "who" in query.lower() and "you" in query.lower():
        return SOCIAL_IDENTITY_CONTEXT
    if any(w in query.lower() for w in ("hello", "hi ", "hey", "hola")):
        return SOCIAL_GREETING_CONTEXT
    return SOCIAL_GREETING_CONTEXT


def social_reply(
    query: str,
    site_id: int,
    intent: IntentDecision,
    handoff_brief: str | None = None,
    *,
    settings: Settings | None = None,
) -> str:
    """Generate a sociable reply without product retrieval."""
    cfg = settings or apply_settings()
    kind = intent.social_kind or "greeting"
    if intent.topic == "shop_social" and kind == "greeting" and any(
        w in query.lower() for w in ("service", "provide", "offer", "capabilities")
    ):
        kind = "help"
    handoff_line = f"{handoff_brief}\n\n" if handoff_brief else ""
    ctx = f"{SOCIAL_SYSTEM}\n\n{handoff_line}{_context_for_kind(kind, query, intent)}"

    # Social lane: always template for sub-second UX (catalog synthesis still uses OpenCode).
    use_opencode_social = os.environ.get("ZOOPLUS_SOCIAL_SYNTHESIS", "template").lower() == "opencode"
    if use_opencode_social and (cfg.synthesis_mode or "").lower() == "opencode":
        llm = synthesize_opencode_chat(
            query=query,
            site_id=site_id,
            context=ctx,
            products=[],
            settings=cfg,
            timeout_seconds=min(8, cfg.opencode_timeout_seconds),
        )
        if llm:
            return llm.strip()

    return template_conversational_reply(
        query,
        site_id,
        settings=cfg,
        social_kind=intent.social_kind,
    )
