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
from src.agents.agent_cascade import run_agent_cascade
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
    from src.llm.conversation import ConvoKind, classify_conversation

    conv = classify_conversation(query)
    kind = intent.social_kind or "greeting"
    if conv != ConvoKind.PRODUCT:
        kind = {
            ConvoKind.GREETING: "greeting",
            ConvoKind.IDENTITY: "identity",
            ConvoKind.THANKS: "thanks",
            ConvoKind.HELP: "help",
            ConvoKind.BYE: "bye",
        }.get(conv, kind)
    elif intent.topic == "shop_social" and any(
        w in query.lower() for w in ("service", "provide", "offer", "capabilities")
    ):
        kind = "help"
    handoff_line = f"{handoff_brief}\n\n" if handoff_brief else ""
    ctx = f"{SOCIAL_SYSTEM}\n\n{handoff_line}{_context_for_kind(kind, query, intent)}"

    social_env = os.environ.get("ZOOPLUS_SOCIAL_SYNTHESIS", "auto").lower()
    synthesis_is_llm = (cfg.synthesis_mode or "").lower() == "opencode"
    use_opencode_social = social_env == "opencode" or (social_env == "auto" and synthesis_is_llm)
    cascade_on = os.environ.get("ZOOPLUS_AGENT_CASCADE", "1").lower() not in ("0", "false", "no")
    if use_opencode_social and (cfg.synthesis_mode or "").lower() == "opencode":
        if cascade_on:

            def _social_ok(raw: str) -> str | None:
                t = raw.strip()
                return t if len(t) > 15 else None

            result = run_agent_cascade("social", f"{ctx}\n\nCustomer: {query}", settings=cfg, parse=_social_ok)
            if result.value:
                logger.info("social via opencode agent=%s", result.agent_id)
                return str(result.value).strip()
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
        social_kind=kind,
    )
