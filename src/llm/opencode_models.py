"""Discover OpenCode models from CLI — cached for UI selector."""

from __future__ import annotations

import logging
import subprocess
import time

from src.config import ROOT, Settings, apply_settings
from src.llm.opencode import _opencode_env

logger = logging.getLogger(__name__)

# PoC defaults — fast free / flash models first
RECOMMENDED_MODEL_IDS: tuple[str, ...] = (
    "opencode/mimo-v2.5-free",
    "opencode/deepseek-v4-flash-free",
    "opencode-go/deepseek-v4-flash",
    "github-copilot/gemini-3.5-flash",
    "github-copilot/gpt-5.4-mini",
    "opencode-go/minimax-m2.5",
)

_CACHE_AT: float = 0.0
_CACHE_MODELS: list[str] = []
_CACHE_TTL_SECONDS = 300


def _parse_models_stdout(raw: str) -> list[str]:
    models: list[str] = []
    for line in raw.splitlines():
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        if "/" in text and " " not in text:
            models.append(text)
    return sorted(set(models))


def list_opencode_models(
    *,
    settings: Settings | None = None,
    force_refresh: bool = False,
) -> list[str]:
    """Run `opencode models` and return sorted model ids."""
    global _CACHE_AT, _CACHE_MODELS
    now = time.time()
    if not force_refresh and _CACHE_MODELS and (now - _CACHE_AT) < _CACHE_TTL_SECONDS:
        return list(_CACHE_MODELS)

    cfg = settings or apply_settings()
    cmd = ["opencode", "models"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=45,
            env=_opencode_env(cfg),
            cwd=str(ROOT),
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        logger.warning("opencode models failed: %s", exc)
        return list(_CACHE_MODELS) if _CACHE_MODELS else list(RECOMMENDED_MODEL_IDS)

    if result.returncode != 0:
        logger.warning("opencode models exit %s: %s", result.returncode, result.stderr[:300])
        return list(_CACHE_MODELS) if _CACHE_MODELS else list(RECOMMENDED_MODEL_IDS)

    parsed = _parse_models_stdout(result.stdout)
    if parsed:
        _CACHE_MODELS = parsed
        _CACHE_AT = now
    return list(_CACHE_MODELS) if _CACHE_MODELS else list(RECOMMENDED_MODEL_IDS)


def models_for_ui(*, settings: Settings | None = None) -> dict:
    """Models list + recommended subset for the chat UI."""
    all_models = list_opencode_models(settings=settings)
    recommended = [m for m in RECOMMENDED_MODEL_IDS if m in all_models]
    if not recommended:
        recommended = all_models[:8] if all_models else list(RECOMMENDED_MODEL_IDS)
    cfg = settings or apply_settings()
    current = cfg.opencode_model or RECOMMENDED_MODEL_IDS[0]
    if current not in recommended and current in all_models:
        recommended = [current, *recommended[:7]]
    return {
        "all": all_models,
        "recommended": recommended,
        "default": current,
    }
