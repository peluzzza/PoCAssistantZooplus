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

DEFAULT_MODEL = "opencode-go/qwen3.6-plus"


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


def _build_prompt(query: str, site_id: int, products: list[RetrievedProduct]) -> str:
    payload = [p.model_dump() for p in products]
    catalog = json.dumps(payload, ensure_ascii=False, indent=2)
    return (
        "You are the zooplus Assistant for a pet-product shop.\n"
        f"Shop site_id: {site_id}\n"
        f"Customer question: {query}\n\n"
        "Retrieved catalog products (use ONLY these; do not invent SKUs or prices):\n"
        f"{catalog}\n\n"
        "Rules:\n"
        "- Ground every claim in the list above.\n"
        "- If the list is empty, say no matches were found and suggest rephrasing.\n"
        "- Mention at most 4 products.\n"
        "- Reply in the same language as the customer question when possible.\n"
        "- Be polite and concise.\n"
    )


def synthesize_opencode(
    query: str,
    site_id: int,
    products: list[RetrievedProduct],
    *,
    settings: Settings | None = None,
) -> str | None:
    """Return answer text, or None if OpenCode is unavailable or fails."""
    from src.config import Settings as SettingsCls

    cfg = settings or SettingsCls.from_env()
    model = cfg.opencode_model or DEFAULT_MODEL
    prompt = _build_prompt(query, site_id, products)
    cmd = ["opencode", "run", "--format", "json", "--model", model, prompt]

    try:
        result = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=cfg.opencode_timeout_seconds,
            env=_opencode_env(cfg),
            cwd=str(Path(__file__).resolve().parents[2]),
        )
    except FileNotFoundError:
        logger.warning("opencode CLI not found in PATH; falling back to template synthesis")
        return None
    except subprocess.TimeoutExpired:
        logger.warning("opencode synthesis timed out after %ss", cfg.opencode_timeout_seconds)
        return None

    if result.returncode != 0:
        logger.warning("opencode exit %s: %s", result.returncode, result.stderr[:500])
        return None

    text = _parse_opencode_json(result.stdout)
    return text if text else None


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
