"""Social lane — internal OpenCode; shopper sees zooplus Assistant only."""

from __future__ import annotations

import logging
import re

from src.agents.agent_body import wrap_prompt_with_agent
from src.agents.agent_cascade import run_agent_cascade
from src.agents.instructions_skill import instructions_skill_context
from src.agents.intent_agent import IntentDecision, SocialKind
from src.agents.prompts import (
    SOCIAL_BYE_CONTEXT,
    SOCIAL_CHUNK_STREAM,
    SOCIAL_DECLINE_CONTEXT,
    SOCIAL_GREETING_CONTEXT,
    SOCIAL_HELP_CONTEXT,
    SOCIAL_IDENTITY_CONTEXT,
    SOCIAL_SYSTEM,
    SOCIAL_THANKS_CONTEXT,
)
from src.agents.registry import agent_chain_for_role, cli_model_arg, resolved_agent_model
from src.agents.run_meta import AgentRunMeta
from src.agents.stream_voice_registry import strip_leading_assistant_intro
from src.config import Settings, apply_settings
from src.llm.answer_sanitize import normalize_shopper_answer
from src.llm.language_context import current_reply_language_instruction
from src.llm.opencode import run_opencode_agent

logger = logging.getLogger(__name__)

_SOCIAL_FAST_TIMEOUT = 6
_SOCIAL_CHUNK_TIMEOUT = 8
_SPANISH_HINT = re.compile(r"[áéíóúñ¿¡]", re.I)


def _chunk_fallback(
    chunk_index: int,
    query: str,
    *,
    shopper_status: str | None,
) -> str:
    es = bool(_SPANISH_HINT.search(query)) or any(
        w in query.lower() for w in ("hola", "gracias", "perro", "gato", "opciones", "buscar")
    )
    if chunk_index == 0 and shopper_status and len(shopper_status) > 12:
        return shopper_status
    if es:
        fallbacks = (
            "¡Claro! Con gusto te ayudo con tu pedido.",
            "Estoy revisando el catálogo de esta tienda, un momento…",
            "Sigo buscando opciones que encajen con lo que pediste…",
            "Ya tengo buenas coincidencias, las estoy ordenando…",
            "Casi listo — te muestro las mejores opciones enseguida…",
        )
        return fallbacks[min(chunk_index, len(fallbacks) - 1)]
    fallbacks = (
        "Of course — happy to help with that.",
        "I'm checking this shop's catalog — just a moment…",
        "Still narrowing options to match your request…",
        "Found some good matches — putting the best ones together…",
        "Almost ready — I'll show you the top picks shortly…",
    )
    return fallbacks[min(chunk_index, len(fallbacks) - 1)]


def social_chunk_reply(
    query: str,
    site_id: int,
    *,
    chunk_index: int,
    elapsed_seconds: int,
    previous_chunks: tuple[str, ...],
    catalog_still_running: bool,
    shopper_status: str | None = None,
    conductor_brief: str | None = None,
    settings: Settings | None = None,
) -> str:
    """One timed streaming chunk (social LLM + cascade), Anthropic delta style."""
    cfg = settings or apply_settings()
    history = "\n".join(f"- {c}" for c in previous_chunks) if previous_chunks else "(none yet)"
    brief_line = (
        f"Conductor brief (write ONLY this idea, do not repeat prior lines): {conductor_brief}\n"
        if conductor_brief
        else ""
    )
    ctx = SOCIAL_CHUNK_STREAM.format(
        chunk_index=chunk_index,
        elapsed_seconds=elapsed_seconds,
        catalog_still_running=str(catalog_still_running).lower(),
        previous_chunks=history,
    )
    lang_line = current_reply_language_instruction(query, site_id=site_id)
    understood = f"What they want: {shopper_status}\n" if shopper_status else ""
    prompt = (
        f"{SOCIAL_SYSTEM}\n\n{ctx}\n\n"
        f"site_id={site_id}\n{understood}{brief_line}Customer: {query}\n"
        f"One chunk only. Never repeat text from previous_chunks. {lang_line}"
    )

    def _ok(raw: str) -> str | None:
        t = normalize_shopper_answer(raw)
        return t if t and len(t) > 8 else None

    result = run_agent_cascade("social", prompt, settings=cfg, parse=_ok)
    if result.value:
        return str(result.value).strip()

    chain = agent_chain_for_role("social")
    agent_id = chain[0] if chain else "zooplus-social-agent"
    raw = run_opencode_agent(
        wrap_prompt_with_agent(agent_id, prompt),
        settings=cfg,
        agent_id=agent_id,
        timeout_seconds=_SOCIAL_CHUNK_TIMEOUT,
        model=cli_model_arg(agent_id, default=cfg.opencode_model),
    )
    answer = normalize_shopper_answer(raw)
    if answer and len(answer) > 8:
        return answer

    logger.info("social chunk index=%s using fallback (LLM empty/timeout)", chunk_index)
    return _chunk_fallback(chunk_index, query, shopper_status=shopper_status)


def _finalize_social_answer(raw: str, *, kind: SocialKind) -> str:
    text = normalize_shopper_answer(raw) or ""
    if kind == "greeting":
        return text.strip()
    return strip_leading_assistant_intro(text)


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
        lang_line = current_reply_language_instruction(query, site_id=site_id)
        no_intro = (
            " Mid-conversation: no Hola/hello, no 'Soy el zooplus Assistant' intro."
            if kind == "help"
            else ""
        )
        greet_hint = " Open with a warm hello." if kind == "greeting" else ""
        help_hint = (
            " No system manual — just invite their pet/product question."
            if kind == "help"
            else ""
        )
        fast_prompt = (
            f"{SOCIAL_SYSTEM}\n\n{_context_for_kind(kind, query, intent)}\n\n"
            f"site_id={site_id}\nCustomer: {query}\n"
            f"Reply as zooplus Assistant in 2-3 short sentences.{greet_hint}{help_hint}{no_intro} {lang_line}"
        )
        raw = run_opencode_agent(
            wrap_prompt_with_agent(agent_id, fast_prompt),
            settings=cfg,
            agent_id=agent_id,
            timeout_seconds=_SOCIAL_FAST_TIMEOUT,
            model=agent_model,
        )
        answer = _finalize_social_answer(raw, kind=kind)
        if answer and len(answer) > 12:
            return answer, AgentRunMeta(
                lane=intent.lane,
                intent_source=intent.source,
                llm_agent=agent_id,
                llm_model=display_model,
            )

    skill = instructions_skill_context(site_id=site_id)
    handoff = f"{handoff_brief}\n\n" if handoff_brief else ""
    ctx = f"{skill}\n\n{SOCIAL_SYSTEM}\n\n{handoff}{_context_for_kind(kind, query, intent)}"
    lang_line = current_reply_language_instruction(query, site_id=site_id)
    prompt = (
        f"{ctx}\n\nsite_id={site_id}\nCustomer: {query}\n"
        f"Reply as zooplus Assistant (2-4 sentences, professional and polite). {lang_line}"
    )

    def _ok(raw: str) -> str | None:
        t = normalize_shopper_answer(raw)
        return t if len(t) > 15 else None

    result = run_agent_cascade("social", prompt, settings=cfg, parse=_ok)
    if result.value:
        answer = _finalize_social_answer(str(result.value), kind=kind)
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
