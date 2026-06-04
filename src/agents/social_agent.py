"""Agentic social replies — OpenCode subagents first; no fixed conversation scripts."""

from __future__ import annotations

import logging
import os

from src.agents.agent_cascade import run_agent_cascade
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
from src.llm.conversation import emergency_social_fallback, social_kind_hint
from src.llm.opencode import opencode_auth_present, synthesize_opencode_chat

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
    return SOCIAL_GREETING_CONTEXT


def _social_synthesis_mode(cfg: Settings) -> str:
    """agentic (default) | opencode | template (CI: skip agents, emergency only)."""
    raw = os.environ.get("ZOOPLUS_SOCIAL_SYNTHESIS", "agentic").lower()
    if raw == "auto":
        if (cfg.synthesis_mode or "").lower() == "opencode" or opencode_auth_present(cfg):
            return "agentic"
        return "template"
    return raw


def _run_social_agents(
    query: str,
    site_id: int,
    ctx: str,
    *,
    settings: Settings,
) -> str | None:
    prompt = (
        f"{ctx}\n\n"
        f"shop site_id: {site_id}\n"
        f"Customer: {query}\n"
        "Reply in natural prose (2–5 sentences). Interpret intent from the message; do not use a fixed template."
    )

    def _ok(raw: str) -> str | None:
        t = raw.strip()
        return t if len(t) > 15 else None

    cascade_on = os.environ.get("ZOOPLUS_AGENT_CASCADE", "1").lower() not in ("0", "false", "no")
    if cascade_on:
        result = run_agent_cascade("social", prompt, settings=settings, parse=_ok)
        if result.value:
            logger.info("social via opencode agent=%s", result.agent_id)
            return str(result.value).strip()

    return synthesize_opencode_chat(
        query=query,
        site_id=site_id,
        context=ctx,
        products=[],
        settings=settings,
        timeout_seconds=min(12, settings.opencode_timeout_seconds),
    )


def social_reply(
    query: str,
    site_id: int,
    intent: IntentDecision,
    handoff_brief: str | None = None,
    *,
    settings: Settings | None = None,
) -> str:
    """Generate sociable text via OpenCode social subagents (agentic-first)."""
    cfg = settings or apply_settings()
    mode = _social_synthesis_mode(cfg)

    kind: SocialKind = social_kind_hint(query, intent_social_kind=intent.social_kind)  # type: ignore[assignment]
    handoff_line = f"{handoff_brief}\n\n" if handoff_brief else ""
    ctx = f"{SOCIAL_SYSTEM}\n\n{handoff_line}{_context_for_kind(kind, query, intent)}"

    if intent.lane == "decline_off_topic" and intent.decline_message and mode == "template":
        return intent.decline_message

    if mode == "agentic":
        agent_text = _run_social_agents(query, site_id, ctx, settings=cfg)
        if agent_text:
            return agent_text
        if intent.lane == "decline_off_topic" and intent.decline_message:
            return intent.decline_message
        logger.warning("social agents unavailable; emergency fallback site=%s", site_id)
        return emergency_social_fallback(site_id)

    # template mode = CI fast path: still try agents once if auth exists, else emergency only
    if opencode_auth_present(cfg):
        agent_text = _run_social_agents(query, site_id, ctx, settings=cfg)
        if agent_text:
            return agent_text

    if intent.lane == "decline_off_topic":
        if intent.decline_message:
            return intent.decline_message
        from src.guardian.engine import polite_decline_for

        code = "off_topic_life"
        q = query.lower()
        if any(w in q for w in ("internet", "web search", "browse the web")):
            code = "off_topic_external_web"
        elif any(w in q for w in ("horse", "horses", "bird", "birds")):
            code = "off_topic_non_pet_species"
        return polite_decline_for(code, query=query)

    return emergency_social_fallback(site_id)
