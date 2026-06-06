"""Runtime metadata from agent / OpenCode invocations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRunMeta:
    lane: str | None = None
    intent_source: str | None = None
    llm_agent: str | None = None
    llm_model: str | None = None
