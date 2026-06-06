"""Social lane — internal OpenCode; shopper sees zooplus Assistant only."""

from __future__ import annotations

import logging

from src.agents.agent_body import wrap_prompt_with_agent
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
from src.agents.registry import agent_chain_for_role, cli_model_arg, resolved_agent_model
from src.agents.run_meta import AgentRunMeta
from src.config import Settings, apply_settings
from src.llm.opencode import run_opencode_agent

logger = logging.getLogger(__name__)

_SOCIAL_FAST_TIMEOUT = 10


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
) -> tuple[str, AgentRunMeta]:
    cfg = settings or apply_settings()
    kind: SocialKind = intent.social_kind or "greeting"  # type: ignore[assignment]

    if intent.source == "conversation_classifier":
        chain = agent_chain_for_role("social")
        agent_id = chain[0] if chain else "zooplus-social-agent"
        agent_model = cli_model_arg(agent_id, default=cfg.opencode_model)
        display_model = resolved_agent_model(agent_id, default=cfg.opencode_model)
        fast_prompt = (
            f"{SOCIAL_SYSTEM}\n\n{_context_for_kind(kind, query, intent)}\n\n"
            f"site_id={site_id}\nCustomer: {query}\n"
            "Reply as zooplus Assistant in 2-3 short sentences. Match the customer's language."
        )
        raw = run_opencode_agent(
            wrap_prompt_with_agent(agent_id, fast_prompt),
            settings=cfg,
            agent_id=agent_id,
            timeout_seconds=_SOCIAL_FAST_TIMEOUT,
            model=agent_model,
        )
        if raw and len(raw.strip()) > 12:
            return raw.strip(), AgentRunMeta(
                lane=intent.lane,
                intent_source=intent.source,
                llm_agent=agent_id,
                llm_model=display_model,
            )

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
        answer = str(result.value).strip()
        return answer, AgentRunMeta(
            lane=intent.lane,
            intent_source=intent.source,
            llm_agent=result.agent_id,
            llm_model=result.model,
        )

    return (
        "I'm the zooplus Assistant for this shop. I'm having trouble responding — "
        "please try again or ask about dog or cat products.",
        AgentRunMeta(lane=intent.lane, intent_source=intent.source),
    )
