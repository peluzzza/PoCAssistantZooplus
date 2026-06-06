"""Agentic intent router (OpenCode) — default-deny, no keyword routing in production."""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import asdict, dataclass
from typing import Literal

from src.agents.agent_body import wrap_prompt_with_agent
from src.agents.agent_cascade import run_agent_cascade
from src.agents.intent_hints import (
    looks_like_catalog_search,
    looks_like_help_about_shop,
    looks_like_non_catalog_species,
    looks_like_off_topic,
    looks_like_price_filtered_catalog,
    looks_like_product_browse,
)
from src.rag.catalog_lexicon import has_catalog_signal
from src.agents.prompts import INTENT_SYSTEM
from src.agents.registry import agent_chain_for_role, cli_model_arg
from src.config import Settings, apply_settings
from src.guardian.engine import polite_decline_for
from src.llm.opencode import opencode_auth_present, run_opencode_agent

logger = logging.getLogger(__name__)

Lane = Literal["conversational", "catalog_search", "decline_off_topic"]
SocialKind = Literal["greeting", "identity", "thanks", "help", "bye", "clarify"] | None

_JSON_BLOCK = re.compile(r"\{[\s\S]*\}")


@dataclass(frozen=True)
class IntentDecision:
    lane: Lane
    social_kind: SocialKind = None
    topic: str | None = None
    confidence: float = 1.0
    reason: str = ""
    source: str = "agent"
    decline_message: str | None = None
    shopper_status: str | None = None


def intent_mode() -> str:
    return os.environ.get("ZOOPLUS_INTENT_MODE", "agentic").lower()


def fast_intent_enabled() -> bool:
    """Regex fast-paths are opt-in only (tests/CI). Production uses agent interpretation."""
    return os.environ.get("ZOOPLUS_FAST_INTENT", "0").lower() in ("1", "true", "yes")


def conductor_intent_enabled() -> bool:
    """Conductor classifies lane first; catalog search only after green light."""
    return os.environ.get("ZOOPLUS_CONDUCTOR_INTENT", "1").lower() in ("1", "true", "yes")


def intent_repair_enabled() -> bool:
    """Opt-in lexicon repair when the agent mis-declines — off in production agentic mode."""
    return os.environ.get("ZOOPLUS_INTENT_REPAIR", "0").lower() in ("1", "true", "yes")


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


def try_fast_catalog_intent(query: str) -> IntentDecision | None:
    """Allow-list fast path for obvious in-scope product browse (before OpenCode)."""
    if not looks_like_catalog_search(query):
        return None
    return IntentDecision(
        lane="catalog_search",
        confidence=1.0,
        reason="fast_catalog",
        source="fast_catalog",
    )


def _repair_agentic_misroute(query: str, decision: IntentDecision) -> IntentDecision:
    """Opt-in repair using catalog-derived signals only (ZOOPLUS_INTENT_REPAIR=1)."""
    if not intent_repair_enabled() or decision.lane != "decline_off_topic":
        return decision
    if looks_like_help_about_shop(query):
        return IntentDecision(
            lane="conversational",
            social_kind="help",
            confidence=1.0,
            reason="repair_help",
            source="repair",
            shopper_status=decision.shopper_status,
        )
    if has_catalog_signal(query) or looks_like_price_filtered_catalog(query):
        return IntentDecision(
            lane="catalog_search",
            confidence=1.0,
            reason="repair_catalog",
            source="repair",
            shopper_status=decision.shopper_status,
        )
    return decision


def try_obvious_social_intent(query: str) -> IntentDecision | None:
    """Clear social turns — skip OpenCode intent; one LLM call for the reply only."""
    from src.agents.handoff import TOPIC_SHOP_SOCIAL
    from src.llm.conversation import ConvoKind, classify_conversation

    if looks_like_help_about_shop(query):
        return IntentDecision(
            lane="conversational",
            social_kind="help",
            topic=TOPIC_SHOP_SOCIAL,
            confidence=0.95,
            reason="obvious_help",
            source="conversation_classifier",
        )

    kind = classify_conversation(query)
    if kind == ConvoKind.PRODUCT:
        return None
    social_map: dict[ConvoKind, SocialKind] = {
        ConvoKind.GREETING: "greeting",
        ConvoKind.THANKS: "thanks",
        ConvoKind.HELP: "help",
        ConvoKind.BYE: "bye",
    }
    return IntentDecision(
        lane="conversational",
        social_kind=social_map.get(kind, "greeting"),
        topic=TOPIC_SHOP_SOCIAL,
        confidence=0.95,
        reason=f"obvious_{kind.value}",
        source="conversation_classifier",
    )


def try_fast_conversational_intent(query: str) -> IntentDecision | None:
    """Skip OpenCode for obvious social turns (latency); policy routing stays agentic for catalog/decline."""
    from src.llm.conversation import ConvoKind, classify_conversation

    if looks_like_help_about_shop(query):
        return IntentDecision(
            lane="conversational",
            social_kind="help",
            confidence=1.0,
            reason="fast_help",
            source="fast_social",
        )

    kind = classify_conversation(query)
    if kind == ConvoKind.PRODUCT:
        return None
    social_map: dict[ConvoKind, SocialKind] = {
        ConvoKind.GREETING: "greeting",
        ConvoKind.THANKS: "thanks",
        ConvoKind.HELP: "help",
        ConvoKind.BYE: "bye",
    }
    return IntentDecision(
        lane="conversational",
        social_kind=social_map.get(kind, "greeting"),
        confidence=1.0,
        reason=f"fast_{kind.value}",
        source="fast_social",
    )


def _build_intent_prompt(query: str, site_id: int) -> str:
    from src.agents.instructions_skill import instructions_skill_context

    skill = instructions_skill_context(site_id=site_id)
    return (
        f"{skill}\n\n{INTENT_SYSTEM}\n\n"
        f"shop site_id: {site_id}\n"
        f'Customer message: "{query}"\n'
        "Classify by TOPIC (what they are talking about), not single keywords.\n"
        "Combined messages: use the dominant topic (e.g. hello + services → shop_social/help).\n"
        "Reply with JSON only: lane, topic, social_kind, confidence, reason.\n"
    )


def _fallback_intent_decision(query: str, *, site_id: int, reason: str) -> IntentDecision:
    """Topic-based routing when OpenCode intent agent fails — never repeat generic help."""
    from src.agents.handoff import TOPIC_OFF_TOPIC, TOPIC_PET_CATALOG, TOPIC_SHOP_SOCIAL
    from src.llm.conversation import ConvoKind, classify_conversation

    text = query.strip()
    if looks_like_non_catalog_species(text):
        return IntentDecision(
            lane="decline_off_topic",
            topic=TOPIC_OFF_TOPIC,
            confidence=0.5,
            reason=f"{reason}_non_catalog_species",
            source="topic_fallback",
            decline_message=_decline_copy("off_topic_non_pet_species", query=text),
        )

    if looks_like_off_topic(text):
        return IntentDecision(
            lane="decline_off_topic",
            topic=TOPIC_OFF_TOPIC,
            confidence=0.5,
            reason=reason,
            source="topic_fallback",
            decline_message=_decline_copy(reason, query=text),
        )

    if (
        looks_like_catalog_search(text)
        or looks_like_product_browse(text)
        or looks_like_price_filtered_catalog(text)
    ):
        return IntentDecision(
            lane="catalog_search",
            topic=TOPIC_PET_CATALOG,
            confidence=0.5,
            reason=reason,
            source="topic_fallback",
        )

    conv = classify_conversation(text)
    if conv != ConvoKind.PRODUCT:
        social_map = {
            ConvoKind.GREETING: "greeting",
            ConvoKind.THANKS: "thanks",
            ConvoKind.HELP: "help",
            ConvoKind.BYE: "bye",
        }
        kind = social_map.get(conv, "greeting")
        return IntentDecision(
            lane="conversational",
            social_kind=kind or "greeting",
            topic=TOPIC_SHOP_SOCIAL,
            confidence=0.5,
            reason=reason,
            source="topic_fallback",
        )

    if looks_like_help_about_shop(text):
        return IntentDecision(
            lane="conversational",
            social_kind="help",
            topic=TOPIC_SHOP_SOCIAL,
            confidence=0.5,
            reason=reason,
            source="topic_fallback",
        )

    return IntentDecision(
        lane="decline_off_topic",
        topic=TOPIC_OFF_TOPIC,
        confidence=0.3,
        reason=f"{reason}_ambiguous",
        source="topic_fallback",
        decline_message=polite_decline_for("out_of_scope_default_deny", query=text),
    )


def _decline_copy(reason: str, *, query: str) -> str:
    q = query.lower()
    if "internet" in q or "browse the web" in q or "web search" in q:
        return polite_decline_for("off_topic_external_web", query=query)
    if looks_like_non_catalog_species(query):
        return polite_decline_for("off_topic_non_pet_species", query=query)
    code = reason if reason.startswith("off_topic") else "out_of_scope_default_deny"
    return polite_decline_for(code, query=query)


def classify_intent_conductor_first(
    query: str,
    site_id: int,
    *,
    settings: Settings | None = None,
) -> IntentDecision | None:
    """One-shot conductor routing — skips catalog/RAG unless lane is catalog_search."""
    cfg = settings or apply_settings()
    prompt = _build_intent_prompt(query, site_id)
    cascade = run_agent_cascade(
        "conductor",
        prompt,
        settings=cfg,
        parse=_parse_intent_json,
        attach_roster=False,
    )
    parsed = cascade.value
    if not parsed:
        return None
    agent_source = f"conductor:{cascade.agent_id or 'conductor'}"
    decision = _intent_decision_from_parsed(query, parsed, source=agent_source)
    return _repair_agentic_misroute(query, decision)


def classify_intent_single_agent(
    query: str,
    site_id: int,
    *,
    settings: Settings | None = None,
) -> IntentDecision | None:
    """One intent subagent attempt — avoids full multi-agent cascade latency."""
    cfg = settings or apply_settings()
    prompt = _build_intent_prompt(query, site_id)

    def _parse_intent(raw: str) -> dict | None:
        return _parse_intent_json(raw)

    chain = agent_chain_for_role("intent")
    if not chain:
        return None
    agent_id = chain[0]
    timeout = min(8, max(6, cfg.opencode_timeout_seconds // 4))
    raw = run_opencode_agent(
        wrap_prompt_with_agent(agent_id, prompt),
        settings=cfg,
        agent_id=agent_id,
        timeout_seconds=timeout,
        model=cli_model_arg(agent_id, default=cfg.opencode_model),
    )
    parsed = _parse_intent(raw or "")
    if not parsed:
        return None
    decision = _intent_decision_from_parsed(query, parsed, source=f"opencode:{agent_id}")
    return _repair_agentic_misroute(query, decision)


def classify_intent_agentic(
    query: str,
    site_id: int,
    *,
    settings: Settings | None = None,
) -> IntentDecision:
    """Classify via OpenCode subagent cascade (intent → topic-guard → conductor)."""
    cfg = settings or apply_settings()
    prompt = _build_intent_prompt(query, site_id)

    def _parse_intent(raw: str) -> dict | None:
        return _parse_intent_json(raw)

    cascade = run_agent_cascade(
        "intent",
        prompt,
        settings=cfg,
        parse=_parse_intent,
        attach_roster=False,
    )
    parsed = cascade.value
    agent_source = f"opencode:{cascade.agent_id}" if cascade.agent_id else "opencode"
    if not parsed:
        logger.warning(
            "intent cascade exhausted agents=%s; using topic fallback",
            ",".join(cascade.attempts),
        )
        return _fallback_intent_decision(
            query,
            site_id=site_id,
            reason="agent_cascade_failed",
        )

    decision = _intent_decision_from_parsed(query, parsed, source=agent_source)
    if os.environ.get("ZOOPLUS_INTENT_REPAIR", "0").lower() in ("1", "true", "yes"):
        return _repair_agentic_misroute(query, decision)
    return decision


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


def _intent_decision_from_parsed(
    query: str,
    parsed: dict,
    *,
    source: str,
) -> IntentDecision:
    """Build IntentDecision from agent JSON (shared by agentic + timeout fallback)."""
    from src.agents.handoff import normalize_topic

    topic_raw = str(parsed.get("topic") or parsed.get("theme") or "")
    lane = _normalize_lane(str(parsed.get("lane", "")))
    if topic_raw:
        topic = normalize_topic(topic_raw, lane=lane)
        if topic == "pet_catalog" and lane == "conversational":
            lane = "catalog_search"
        if topic == "shop_social" and lane == "decline_off_topic":
            lane = "conversational"
        if topic == "off_topic":
            lane = "decline_off_topic"
    topic = normalize_topic(topic_raw or None, lane=lane)
    kind = _normalize_social_kind(
        str(parsed.get("social_kind") or parsed.get("social") or "") or None
    )
    try:
        confidence = float(parsed.get("confidence", 0.8))
    except (TypeError, ValueError):
        confidence = 0.8
    reason = str(parsed.get("reason") or parsed.get("brief_reason") or "")
    raw_status = str(parsed.get("shopper_status") or parsed.get("status_hint") or "").strip()
    shopper_status = raw_status[:140] if raw_status else None
    decline_msg = _decline_copy(reason, query=query) if lane == "decline_off_topic" else None
    if lane == "conversational" and not kind:
        if topic == "shop_social" and any(
            w in query.lower() for w in ("service", "provide", "offer", "capabilities", "help")
        ):
            kind = "help"
    return IntentDecision(
        lane=lane,
        social_kind=kind if lane == "conversational" else None,
        topic=topic,
        confidence=confidence,
        reason=reason,
        source=source,
        decline_message=decline_msg,
        shopper_status=shopper_status,
    )


def classify_intent_conductor_fallback(
    query: str,
    site_id: int,
    *,
    settings: Settings | None = None,
) -> IntentDecision:
    """One-shot agentic intent when the full cascade exceeds the lane time budget."""
    cfg = settings or apply_settings()
    prompt = _build_intent_prompt(query, site_id)

    cascade = run_agent_cascade(
        "conductor",
        prompt,
        settings=cfg,
        parse=_parse_intent_json,
        attach_roster=False,
    )
    parsed = cascade.value
    if parsed:
        agent_source = f"opencode_timeout:{cascade.agent_id or 'conductor'}"
        return _intent_decision_from_parsed(query, parsed, source=agent_source)
    logger.warning(
        "intent timeout fallback exhausted; topic fallback (decline still agentic in social lane)"
    )
    return _fallback_intent_decision(query, site_id=site_id, reason="intent_lane_timeout")


def _store_intent_cache(site_id: int, query: str, decision: IntentDecision) -> None:
    from src.cache.ttl_cache import cache_enabled, intent_cache

    if cache_enabled():
        intent_cache.set(_intent_cache_key(site_id, query), asdict(decision))


def _intent_cache_key(site_id: int, query: str) -> str:
    return f"{site_id}:{query.strip().lower()}"


def _intent_from_cache_row(row: dict) -> IntentDecision:
    return IntentDecision(**row)


def classify_intent(
    query: str,
    site_id: int,
    *,
    settings: Settings | None = None,
) -> IntentDecision:
    """Route intent: oracle (tests), agentic OpenCode (prod), or safe decline if agent unavailable."""
    from src.cache.ttl_cache import cache_enabled, intent_cache

    mode = intent_mode()
    text = (query or "").strip()
    if cache_enabled() and mode in ("agentic", "auto"):
        cached = intent_cache.get(_intent_cache_key(site_id, text))
        if cached:
            logger.debug("intent cache hit site=%s", site_id)
            return _intent_from_cache_row(cached)

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
        obvious = try_obvious_social_intent(text)
        if obvious is not None:
            _store_intent_cache(site_id, text, obvious)
            return obvious
        if fast_intent_enabled():
            fast_catalog = try_fast_catalog_intent(text)
            if fast_catalog:
                _store_intent_cache(site_id, text, fast_catalog)
                return fast_catalog
            fast = try_fast_conversational_intent(text)
            if fast:
                _store_intent_cache(site_id, text, fast)
                return fast
        if conductor_intent_enabled():
            led = classify_intent_conductor_first(text, site_id, settings=cfg)
            if led is not None:
                _store_intent_cache(site_id, text, led)
                return led
            single = classify_intent_single_agent(text, site_id, settings=cfg)
            if single is not None:
                _store_intent_cache(site_id, text, single)
                return single
            decision = _fallback_intent_decision(text, site_id=site_id, reason="conductor_led_fallback")
            _store_intent_cache(site_id, text, decision)
            return decision
        decision = classify_intent_agentic(text, site_id, settings=cfg)
        _store_intent_cache(site_id, text, decision)
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
