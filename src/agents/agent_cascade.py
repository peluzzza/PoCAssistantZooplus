"""Retry OpenCode calls across configured subagents before heuristic fallback."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from src.agents.agent_body import wrap_prompt_with_agent
from src.agents.registry import AgentRole, agent_chain_for_role, format_agent_roster
from src.config import Settings
from src.llm.opencode import run_opencode_agent

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass(frozen=True)
class CascadeResult:
    value: T | None
    raw: str | None
    agent_id: str | None
    attempts: tuple[str, ...]


def _per_agent_timeout(settings: Settings, chain_len: int, role: AgentRole) -> int:
    total = max(10, settings.opencode_timeout_seconds)
    if chain_len <= 0:
        return total
    role_caps: dict[AgentRole, int] = {
        "intent": 10,
        "social": 12,
        "synthesis": 14,
        "conductor": 12,
    }
    cap = role_caps.get(role, 12)
    if total > 40:
        cap = min(cap + 2, 16)
    per = min(cap, total // max(1, chain_len))
    return max(8, per)


def run_agent_cascade(
    role: AgentRole,
    prompt: str,
    *,
    settings: Settings,
    parse: Callable[[str], T | None],
    attach_roster: bool = False,
) -> CascadeResult[T]:
    """
    Try each subagent in role chain until parse() succeeds.

    parse() returns non-None when the agent output is usable (e.g. valid intent JSON).
    """
    chain = agent_chain_for_role(role)
    if not chain:
        logger.warning("no opencode agents configured for role=%s", role)
        return CascadeResult(None, None, None, ())

    full_prompt = prompt
    if attach_roster and role in ("intent", "conductor"):
        full_prompt = f"{prompt}\n\n{format_agent_roster()}\n"

    timeout = _per_agent_timeout(settings, len(chain), role)
    tried: list[str] = []

    for agent_id in chain:
        tried.append(agent_id)
        logger.info("opencode cascade role=%s trying agent=%s", role, agent_id)
        raw = run_opencode_agent(
            wrap_prompt_with_agent(agent_id, full_prompt),
            settings=settings,
            agent_id=agent_id,
            timeout_seconds=timeout,
        )
        if not raw:
            logger.warning("agent %s returned empty (role=%s)", agent_id, role)
            continue
        parsed = parse(raw)
        if parsed is not None:
            logger.info("opencode cascade success role=%s agent=%s", role, agent_id)
            return CascadeResult(parsed, raw, agent_id, tuple(tried))
        logger.warning("agent %s output not parseable (role=%s)", agent_id, role)

    logger.warning(
        "opencode cascade exhausted role=%s agents=%s",
        role,
        ",".join(tried),
    )
    return CascadeResult(None, None, None, tuple(tried))
