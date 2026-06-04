"""Retry OpenCode calls across configured subagents before heuristic fallback."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

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


def _per_agent_timeout(settings: Settings, chain_len: int) -> int:
    total = max(10, settings.opencode_timeout_seconds)
    if chain_len <= 0:
        return total
    # Cap each attempt so we do not blackout the UI on serial timeouts
    return max(6, min(12, total // chain_len))


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

    from src.llm.response_variety import variation_directive

    full_prompt = prompt
    if attach_roster and role in ("intent", "conductor"):
        full_prompt = f"{prompt}\n\n{format_agent_roster()}\n"
    if role in ("social", "synthesis", "intent"):
        # Extract customer line for seed when present
        seed_q = prompt.split("Customer:")[-1].strip()[:200] if "Customer:" in prompt else prompt[:200]
        full_prompt = f"{variation_directive(seed_q, role)}\n\n{full_prompt}"

    timeout = _per_agent_timeout(settings, len(chain))
    tried: list[str] = []

    for agent_id in chain:
        tried.append(agent_id)
        logger.info("opencode cascade role=%s trying agent=%s", role, agent_id)
        raw = run_opencode_agent(
            full_prompt,
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
