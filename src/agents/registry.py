"""OpenCode agent registry — discover configured subagents and retry chains."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

from src.agents.agent_models import AGENT_MODEL_DEFAULTS, AGENT_ROLE_BY_ID

AgentRole = Literal["intent", "social", "synthesis", "conductor"]

ROOT = Path(__file__).resolve().parents[2]

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
    model: str | None = None


def _config_path() -> Path:
    raw = os.environ.get("ZOOPLUS_OPENCODE_CONFIG_DIR", ".opencode")
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / raw
    return path.resolve()


def _agent_env_key(agent_id: str) -> str:
    slug = re.sub(r"[^A-Z0-9]", "_", agent_id.upper())
    return f"ZOOPLUS_AGENT_MODEL_{slug}"


def _catalog_model(agent_id: str, meta: dict) -> str | None:
    raw = meta.get("model")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return AGENT_MODEL_DEFAULTS.get(agent_id)


@lru_cache(maxsize=1)
def load_agent_catalog() -> dict[str, AgentSpec]:
    """Agents declared in opencode.json (source of truth for availability + model)."""
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
            model=_catalog_model(agent_id, meta),
        )
    return catalog


def list_available_agent_ids() -> list[str]:
    return sorted(load_agent_catalog().keys())


def agent_models_map() -> dict[str, str]:
    """Per-agent LLM ids for UI / observability."""
    catalog = load_agent_catalog()
    out: dict[str, str] = {}
    for agent_id, defaults in AGENT_MODEL_DEFAULTS.items():
        spec = catalog.get(agent_id)
        out[agent_id] = (spec.model if spec and spec.model else defaults) or defaults
    for agent_id, spec in catalog.items():
        if spec.model:
            out[agent_id] = spec.model
    return out


def _env_model_for_agent(agent_id: str) -> str | None:
    raw = os.environ.get(_agent_env_key(agent_id), "").strip()
    return raw or None


def _env_model_for_role(role: AgentRole) -> str | None:
    env_key = _ROLE_MODEL_ENV.get(role, "")
    if not env_key:
        return None
    raw = os.environ.get(env_key, "").strip()
    return raw or None


def resolved_agent_model(agent_id: str, *, default: str | None = None) -> str | None:
    """Model id used for this agent (UI meta + logging)."""
    from src.agents.request_context import request_llm_model

    picked = request_llm_model.get()
    if picked:
        return picked
    per_agent = _env_model_for_agent(agent_id)
    if per_agent:
        return per_agent
    role = AGENT_ROLE_BY_ID.get(agent_id)
    if role:
        role_model = _env_model_for_role(role)  # type: ignore[arg-type]
        if role_model:
            return role_model
    catalog = load_agent_catalog()
    spec = catalog.get(agent_id)
    if spec and spec.model:
        return spec.model
    return default


def cli_model_arg(agent_id: str | None, *, default: str | None = None) -> str | None:
    """
    Model for `opencode run --model`.

    Returns None when OpenCode should use the agent's own `model` from opencode.json
    (official per-agent assignment). See https://opencode.ai/docs/agents/
    """
    from src.agents.request_context import request_llm_model

    if request_llm_model.get():
        return request_llm_model.get()
    if agent_id:
        if _env_model_for_agent(agent_id):
            return _env_model_for_agent(agent_id)
        role = AGENT_ROLE_BY_ID.get(agent_id)
        if role and _env_model_for_role(role):  # type: ignore[arg-type]
            return _env_model_for_role(role)  # type: ignore[arg-type]
        catalog = load_agent_catalog()
        spec = catalog.get(agent_id)
        if spec and spec.model:
            return None
    return default


def model_for_role(role: AgentRole, *, default: str | None = None) -> str | None:
    """Backward-compatible role resolver (prefer agent-specific config)."""
    chain = agent_chain_for_role(role)
    if chain:
        return resolved_agent_model(chain[0], default=default)
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
        model = spec.model or "inherit"
        lines.append(f"- {spec.agent_id} ({spec.mode}, {model}): {spec.description[:60]}")
    return "\n".join(lines)
