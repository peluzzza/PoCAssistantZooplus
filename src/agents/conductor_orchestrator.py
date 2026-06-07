"""Invisible conductor — orchestrates stream ticks (shopper never sees this layer)."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Literal

from src.agents.agent_cascade import run_agent_cascade
from src.agents.prompts import CONDUCTOR_ORCHESTRATOR_SYSTEM
from src.agents.registry import agent_chain_for_role, cli_model_arg
from src.config import Settings, apply_settings
from src.llm.opencode import run_opencode_agent
from src.agents.agent_body import wrap_prompt_with_agent

logger = logging.getLogger(__name__)

ConductorAction = Literal["emit_message", "start_catalog", "wait", "complete"]

_ACTION_ALIASES: dict[str, ConductorAction] = {
    "emit_message": "emit_message",
    "message": "emit_message",
    "send_message": "emit_message",
    "start_catalog": "start_catalog",
    "catalog": "start_catalog",
    "invoke_catalog": "start_catalog",
    "wait": "wait",
    "complete": "complete",
    "finish": "complete",
    "done": "complete",
}

_PROGRESS_BRIEFS_ES = (
    "Sigue buscando en el catálogo, un momento más…",
    "Estoy afinando opciones dentro de tu rango de precio…",
    "Ya casi — preparo las mejores opciones para ti…",
)
_PROGRESS_BRIEFS_EN = (
    "Still searching the catalog — just a moment…",
    "Narrowing options to your price range…",
    "Almost ready — putting the best picks together…",
)


@dataclass(frozen=True)
class ConductorStep:
    action: ConductorAction
    message_brief: str | None = None
    wait_seconds: float = 5.0
    reason: str | None = None


@dataclass(frozen=True)
class ConductorState:
    query: str
    site_id: int
    lane: str
    tick_index: int
    elapsed_seconds: int
    messages_sent: tuple[str, ...]
    catalog_running: bool
    catalog_done: bool
    shopper_status: str | None = None


def _parse_step_json(raw: str) -> ConductorStep | None:
    text = (raw or "").strip()
    fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if fenced:
        text = fenced.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    action_raw = str(data.get("action", "wait")).strip().lower()
    action = _ACTION_ALIASES.get(action_raw)
    if not action:
        return None
    brief = data.get("message_brief") or data.get("brief") or data.get("text")
    brief_s = str(brief).strip() if brief else None
    wait = data.get("wait_seconds", 5)
    try:
        wait_f = max(0.0, min(30.0, float(wait)))
    except (TypeError, ValueError):
        wait_f = 5.0
    reason = data.get("reason")
    return ConductorStep(
        action=action,
        message_brief=brief_s,
        wait_seconds=wait_f,
        reason=str(reason) if reason else None,
    )


def _state_prompt(state: ConductorState) -> str:
    history = (
        "\n".join(f"  - {m}" for m in state.messages_sent)
        if state.messages_sent
        else "  (none yet)"
    )
    return (
        f"{CONDUCTOR_ORCHESTRATOR_SYSTEM}\n\n"
        f"site_id={state.site_id}\n"
        f"lane={state.lane}\n"
        f"tick_index={state.tick_index}\n"
        f"elapsed_seconds={state.elapsed_seconds}\n"
        f"catalog_running={str(state.catalog_running).lower()}\n"
        f"catalog_done={str(state.catalog_done).lower()}\n"
        f"shopper_status={state.shopper_status or ''}\n"
        f"messages_already_sent:\n{history}\n\n"
        f"Customer query: {state.query}\n"
        f"Return ONE JSON object only."
    )


def _heuristic_step(state: ConductorState) -> ConductorStep:
    """Deterministic fallback when conductor LLM fails."""
    if state.catalog_done and state.tick_index > 0:
        return ConductorStep(action="complete", reason="catalog_done_heuristic")
    if state.lane != "catalog_search":
        return ConductorStep(action="complete", reason="non_catalog_lane")
    if state.tick_index == 0:
        brief = state.shopper_status if state.shopper_status and len(state.shopper_status) > 10 else (
            "Warm ack — confirm you will help; ONE line on dog/cat scope only if non-catalog species asked."
        )
        return ConductorStep(action="emit_message", message_brief=brief, wait_seconds=5)
    if not state.catalog_running and state.tick_index == 1:
        return ConductorStep(action="start_catalog", wait_seconds=0, reason="start_catalog_heuristic")
    if state.catalog_done:
        return ConductorStep(action="complete")
    es = bool(re.search(r"[áéíóúñ¿¡]", state.query)) or "gato" in state.query.lower()
    pool = _PROGRESS_BRIEFS_ES if es else _PROGRESS_BRIEFS_EN
    idx = min(state.tick_index - 1, len(pool) - 1)
    return ConductorStep(
        action="emit_message",
        message_brief=pool[idx],
        wait_seconds=5,
        reason="progress_heuristic",
    )


def conductor_next_step(
    state: ConductorState,
    *,
    settings: Settings | None = None,
) -> ConductorStep:
    """Invisible conductor tick — decides next orchestration action."""
    cfg = settings or apply_settings()
    prompt = _state_prompt(state)

    def _ok(raw: str) -> ConductorStep | None:
        return _parse_step_json(raw)

    result = run_agent_cascade("conductor", prompt, settings=cfg, parse=_ok)
    if result.value:
        step = result.value
        if step.action == "emit_message" and not step.message_brief:
            step = ConductorStep(
                action="wait",
                wait_seconds=step.wait_seconds,
                reason="empty_brief",
            )
        return step

    chain = agent_chain_for_role("conductor")
    agent_id = chain[0] if chain else "zooplus-conductor"
    raw = run_opencode_agent(
        wrap_prompt_with_agent(agent_id, prompt),
        settings=cfg,
        agent_id=agent_id,
        timeout_seconds=12,
        model=cli_model_arg(agent_id, default=cfg.opencode_model),
    )
    parsed = _parse_step_json(raw or "")
    if parsed:
        return parsed

    logger.info("conductor orchestrator using heuristic tick=%s", state.tick_index)
    return _heuristic_step(state)
