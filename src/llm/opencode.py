"""OpenCode CLI synthesis — uses your local auth.json (never committed)."""

from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path

from src.config import Settings
from src.models.chat import RetrievedProduct

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "opencode-go/deepseek-v4-flash"


def _opencode_env(settings: Settings) -> dict[str, str]:
    env = {**os.environ}
    env["CI"] = "true"
    env["NO_COLOR"] = "1"
    env["TERM"] = "dumb"
    env["OPENCODE_NON_INTERACTIVE"] = "1"
    if settings.opencode_data_dir:
        env["OPENCODE_DATA_DIR"] = str(Path(settings.opencode_data_dir).resolve())
    if settings.opencode_config_dir:
        env["OPENCODE_CONFIG_DIR"] = str(Path(settings.opencode_config_dir).resolve())
    return env


def _parse_opencode_json(raw: str) -> str:
    text_parts: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "text":
            part = event.get("part", {})
            if isinstance(part, dict) and part.get("text"):
                text_parts.append(str(part["text"]))
    return "".join(text_parts).strip() or raw.strip()


def _build_prompt(
    query: str,
    site_id: int,
    products: list[RetrievedProduct],
    *,
    extra_context: str = "",
) -> str:
    payload = [p.model_dump() for p in products]
    catalog = json.dumps(payload, ensure_ascii=False, indent=2)
    ctx = f"{extra_context}\n" if extra_context else ""
    return (
        "You are the zooplus Assistant — a friendly, professional pet-shop advisor.\n"
        "Style: natural ask-and-answer conversation (not a bullet dump). Be polite and helpful.\n"
        f"Shop site_id: {site_id}\n"
        f"Customer: {query}\n"
        f"{ctx}\n"
        "Retrieved catalog products (use ONLY these; never invent SKUs, brands, or prices):\n"
        f"{catalog}\n\n"
        "Rules:\n"
        "- Ground every product mention in the list above.\n"
        "- If the list is empty, apologise and suggest how to rephrase (dog/cat, food type).\n"
        "- Do NOT output a numbered or bulleted product list — the UI shows product cards separately.\n"
        "- Mention at most two product names in prose; prices live in the cards.\n"
        "- Vary wording each turn; avoid rigid template openings.\n"
        "- Match the customer's language when possible.\n"
        "- End with one short follow-up question when appropriate.\n"
    )


def _run_opencode_prompt(
    prompt: str,
    *,
    settings: Settings,
    timeout_seconds: int | None = None,
    agent_id: str | None = None,
    model: str | None = None,
) -> str | None:
    use_model = model or settings.opencode_model or DEFAULT_MODEL
    timeout = timeout_seconds if timeout_seconds is not None else settings.opencode_timeout_seconds
    cmd = ["opencode", "run", "--format", "json", "--model", use_model]
    if agent_id:
        cmd.extend(["--agent", agent_id])
    cmd.append(prompt)
    try:
        result = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            env=_opencode_env(settings),
            cwd=str(Path(__file__).resolve().parents[2]),
        )
    except FileNotFoundError:
        logger.warning("opencode CLI not found in PATH; falling back to template synthesis")
        return None
    except subprocess.TimeoutExpired:
        logger.warning("opencode synthesis timed out after %ss", timeout)
        return None
    if result.returncode != 0:
        logger.warning("opencode exit %s: %s", result.returncode, result.stderr[:500])
        return None
    text = _parse_opencode_json(result.stdout)
    return text if text else None


def run_opencode_agent(
    prompt: str,
    *,
    settings: Settings | None = None,
    agent_id: str,
    timeout_seconds: int | None = None,
    model: str | None = None,
) -> str | None:
    """Invoke a named OpenCode subagent from opencode.json."""
    from src.config import Settings as SettingsCls

    cfg = settings or SettingsCls.from_env()
    return _run_opencode_prompt(
        prompt,
        settings=cfg,
        timeout_seconds=timeout_seconds,
        agent_id=agent_id,
        model=model,
    )


def synthesize_opencode_chat(
    query: str,
    site_id: int,
    *,
    context: str,
    products: list[RetrievedProduct] | None = None,
    settings: Settings | None = None,
    timeout_seconds: int | None = None,
) -> str | None:
    """Short conversational turn via local OpenCode (your auth.json)."""
    from src.config import Settings as SettingsCls

    cfg = settings or SettingsCls.from_env()
    prompt = _build_prompt(
        query,
        site_id,
        products or [],
        extra_context=context,
    )
    return _run_opencode_prompt(prompt, settings=cfg, timeout_seconds=timeout_seconds)


def synthesize_opencode_with_agents(
    query: str,
    site_id: int,
    products: list[RetrievedProduct],
    *,
    settings: Settings | None = None,
    extra_context: str = "",
) -> tuple[str | None, str | None]:
    """Try synthesis subagents in chain; returns (answer, winning_agent_id)."""
    from src.agents.agent_cascade import run_agent_cascade
    from src.config import Settings as SettingsCls

    cfg = settings or SettingsCls.from_env()
    prompt = _build_prompt(query, site_id, products, extra_context=extra_context)

    def _ok(raw: str) -> str | None:
        text = raw.strip()
        return text if len(text) > 20 else None

    result = run_agent_cascade("synthesis", prompt, settings=cfg, parse=_ok)
    answer = result.value
    return (str(answer) if answer else None), result.agent_id


def synthesize_opencode(
    query: str,
    site_id: int,
    products: list[RetrievedProduct],
    *,
    settings: Settings | None = None,
    extra_context: str = "",
) -> str | None:
    """Return answer text, or None if OpenCode is unavailable or fails."""
    from src.config import Settings as SettingsCls

    cfg = settings or SettingsCls.from_env()
    prompt = _build_prompt(query, site_id, products, extra_context=extra_context)
    return _run_opencode_prompt(prompt, settings=cfg)


def opencode_auth_present(settings: Settings | None = None) -> bool:
    """True if a local or default auth.json exists (does not validate keys)."""
    from src.config import Settings as SettingsCls

    cfg = settings or SettingsCls.from_env()
    candidates: list[Path] = []
    if cfg.opencode_data_dir:
        candidates.append(Path(cfg.opencode_data_dir) / "auth.json")
    candidates.append(Path.home() / ".local" / "share" / "opencode" / "auth.json")
    candidates.append(Path(__file__).resolve().parents[2] / ".opencode" / "auth.json")
    return any(p.is_file() for p in candidates)
