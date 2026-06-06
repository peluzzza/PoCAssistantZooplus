"""Social lane — internal OpenCode; shopper sees zooplus Assistant only."""

from __future__ import annotations

import logging

from src.agents.agent_cascade import run_agent_cascade
from src.agents.instructions_skill import instructions_skill_context
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
    return SOCIAL_GREETING_CONTEXT


def social_reply(
    query: str,
    site_id: int,
    intent: IntentDecision,
    handoff_brief: str | None = None,
    *,
    settings: Settings | None = None,
) -> str:
    cfg = settings or apply_settings()
    kind: SocialKind = intent.social_kind or "greeting"  # type: ignore[assignment]
    skill = instructions_skill_context(site_id=site_id)
    handoff = f"{handoff_brief}\n\n" if handoff_brief else ""
    ctx = f"{skill}\n\n{SOCIAL_SYSTEM}\n\n{handoff}{_context_for_kind(kind, query, intent)}"
    prompt = (
        f"{ctx}\n\nsite_id={site_id}\nCustomer: {query}\n"
        "Reply as zooplus Assistant (2-5 sentences). Match the customer's language when clear."
    )

    def _ok(raw: str) -> str | None:
        t = raw.strip()
        return t if len(t) > 15 else None

    result = run_agent_cascade("social", prompt, settings=cfg, parse=_ok)
    if result.value:
        return str(result.value).strip()

    llm = synthesize_opencode_chat(
        query=query,
        site_id=site_id,
        context=ctx,
        products=[],
        settings=cfg,
        timeout_seconds=min(14, cfg.opencode_timeout_seconds),
    )
    if llm:
        return llm.strip()

    fb = run_agent_cascade("conductor", prompt, settings=cfg, parse=_ok)
    if fb.value:
        return str(fb.value).strip()

    return (
        "I'm the zooplus Assistant for this shop. I'm having trouble responding — "
        "please try again or ask about dog or cat products."
    )
