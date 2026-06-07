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

DEFAULT_MODEL = "opencode/deepseek-v4-flash-free"


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
    from src.llm.answer_sanitize import extract_opencode_stdout

    return extract_opencode_stdout(raw)


def _build_prompt(
    query: str,
    site_id: int,
    products: list[RetrievedProduct],
    *,
    extra_context: str = "",
) -> str:
    payload = [
        {
            "article_id": p.article_id,
            "name": p.product_name,
            "brand": p.brands,
            "pet": p.pet_type,
            "price_eur": p.price,
        }
        for p in products
    ]
    from src.llm.language_context import current_reply_language_instruction

    catalog = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    ctx = f"{extra_context}\n" if extra_context else ""
    lang_line = current_reply_language_instruction(query, site_id=site_id)
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
        "- If extra_context says conversation is in progress or follow-up: "
        "do NOT greet or re-introduce yourself.\n"
        f"- {lang_line}\n"
        "- End with one short follow-up question when appropriate.\n"
        "- Reply in plain text only — never wrap the answer in JSON or markdown code fences.\n"
    )


def _run_opencode_prompt(
    prompt: str,
    *,
    settings: Settings,
    timeout_seconds: int | None = None,
    agent_id: str | None = None,
    model: str | None = None,
) -> str | None:
    from src.agents.registry import cli_model_arg

    if model is None:
        use_model = cli_model_arg(agent_id, default=settings.opencode_model or DEFAULT_MODEL)
    else:
        use_model = model
    timeout = timeout_seconds if timeout_seconds is not None else settings.opencode_timeout_seconds
    cmd = ["opencode", "run", "--format", "json"]
    if use_model:
        cmd.extend(["--model", use_model])
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


def opencode_auth_paths(settings: Settings | None = None) -> list[Path]:
    """Auth.json locations checked in order (project-local first)."""
    from src.config import ROOT, apply_settings

    cfg = settings or apply_settings()
    candidates: list[Path] = []
    if cfg.opencode_data_dir:
        data = Path(cfg.opencode_data_dir)
        if not data.is_absolute():
            data = (ROOT / data).resolve()
        candidates.append(data / "auth.json")
    candidates.append((ROOT / ".opencode" / "data" / "auth.json").resolve())
    candidates.append(Path.home() / ".local" / "share" / "opencode" / "auth.json")
    return candidates


def opencode_auth_present(settings: Settings | None = None) -> bool:
    """True if a local or default auth.json exists (does not validate keys)."""
    return any(p.is_file() and p.stat().st_size > 2 for p in opencode_auth_paths(settings))
