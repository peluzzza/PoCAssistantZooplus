"""OpenCode agent registry — discover configured subagents and retry chains."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

AgentRole = Literal["intent", "social", "synthesis", "conductor"]

ROOT = Path(__file__).resolve().parents[2]

# Matches .opencode/opencode.json + conductor handoff graph
DEFAULT_CHAINS: dict[AgentRole, tuple[str, ...]] = {
    "intent": (
        "zooplus-intent-agent",
        "zooplus-topic-guard",
        "zooplus-conductor",
    ),
    "social": ("zooplus-social-agent",),
    "synthesis": (
        "zooplus-synthesis",
        "zooplus-logic-worker",
        "zooplus-conductor",
    ),
    "conductor": ("zooplus-conductor",),
}

_ROLE_ENV: dict[AgentRole, str] = {
    "intent": "ZOOPLUS_INTENT_AGENT_CHAIN",
    "social": "ZOOPLUS_SOCIAL_AGENT_CHAIN",
    "synthesis": "ZOOPLUS_SYNTHESIS_AGENT_CHAIN",
    "conductor": "ZOOPLUS_CONDUCTOR_AGENT_CHAIN",
}

_ROLE_MODEL_ENV: dict[AgentRole, str] = {
    "intent": "ZOOPLUS_INTENT_MODEL",
    "social": "ZOOPLUS_SOCIAL_MODEL",
    "synthesis": "ZOOPLUS_SYNTHESIS_MODEL",
    "conductor": "ZOOPLUS_CONDUCTOR_MODEL",
}


@dataclass(frozen=True)
class AgentSpec:
    agent_id: str
    mode: str
    description: str


def _config_path() -> Path:
    raw = os.environ.get("ZOOPLUS_OPENCODE_CONFIG_DIR", ".opencode")
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / raw
    return path.resolve()


@lru_cache(maxsize=1)
def load_agent_catalog() -> dict[str, AgentSpec]:
    """Agents declared in opencode.json (source of truth for availability)."""
    cfg_file = _config_path() / "opencode.json"
    if not cfg_file.is_file():
        return {}
    data = json.loads(cfg_file.read_text(encoding="utf-8"))
    block = data.get("agent") or {}
    catalog: dict[str, AgentSpec] = {}
    for agent_id, meta in block.items():
        if not isinstance(meta, dict):
            continue
        catalog[agent_id] = AgentSpec(
            agent_id=agent_id,
            mode=str(meta.get("mode") or "subagent"),
            description=str(meta.get("description") or ""),
        )
    return catalog


def list_available_agent_ids() -> list[str]:
    return sorted(load_agent_catalog().keys())


def model_for_role(role: AgentRole, *, default: str | None = None) -> str | None:
    """Per-role OpenCode model override (flash models for social/intent)."""
    from src.agents.request_context import request_llm_model

    picked = request_llm_model.get()
    if picked:
        return picked
    env_key = _ROLE_MODEL_ENV.get(role, "")
    raw = os.environ.get(env_key, "").strip() if env_key else ""
    if raw:
        return raw
    return default


def agent_chain_for_role(role: AgentRole) -> tuple[str, ...]:
    """Resolve retry order: env override → defaults, filtered to configured agents only."""
    env_key = _ROLE_ENV.get(role, "")
    raw = os.environ.get(env_key, "").strip()
    if raw:
        requested = tuple(a.strip() for a in raw.split(",") if a.strip())
    else:
        requested = DEFAULT_CHAINS[role]
    catalog = load_agent_catalog()
    chain = tuple(a for a in requested if a in catalog)
    if role == "social" and chain:
        allow_fb = os.environ.get("ZOOPLUS_SOCIAL_ALLOW_FALLBACK", "0").lower() in (
            "1",
            "true",
            "yes",
        )
        if not allow_fb:
            chain = chain[:1]
    if chain:
        return chain
    if "zooplus-conductor" in catalog:
        return ("zooplus-conductor",)
    return tuple(catalog.keys())[:1]


def format_agent_roster() -> str:
    """Brief roster for prompts — which subagents exist in this workspace."""
    lines = ["Available OpenCode subagents (from opencode.json):"]
    for spec in load_agent_catalog().values():
        lines.append(f"- {spec.agent_id} ({spec.mode}): {spec.description[:80]}")
    return "\n".join(lines)
