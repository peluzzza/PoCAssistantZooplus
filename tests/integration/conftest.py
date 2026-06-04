"""Integration fixtures — agentic mode with real OpenCode (no mocks)."""

from __future__ import annotations

import os
import shutil

import pytest
from src.config import ROOT, apply_settings
from src.llm.opencode import opencode_auth_paths, opencode_auth_present


def pytest_configure(config: pytest.Config) -> None:
    apply_settings()
    # Force agentic (do not use setdefault — shell may still have oracle from CI)
    os.environ["ZOOPLUS_INTENT_MODE"] = "agentic"
    os.environ["ZOOPLUS_SYNTHESIS_MODE"] = "opencode"
    os.environ["ZOOPLUS_SOCIAL_SYNTHESIS"] = "agentic"
    os.environ["ZOOPLUS_AGENT_CASCADE"] = "1"
    os.environ["ZOOPLUS_FAST_INTENT"] = "0"
    os.environ["ZOOPLUS_OPENCODE_TIMEOUT"] = "60"
    os.environ["ZOOPLUS_OPENCODE_DATA_DIR"] = ".opencode/data"
    os.environ["ZOOPLUS_OPENCODE_CONFIG_DIR"] = ".opencode/config-cli"
    os.environ["ZOOPLUS_OPENCODE_MODEL"] = "opencode/deepseek-v4-flash-free"


@pytest.fixture(scope="session", autouse=True)
def _ensure_project_opencode_auth() -> None:
    """Copy global auth into gitignored .opencode/data so CLI + tests share one profile."""
    local_auth = ROOT / ".opencode" / "data" / "auth.json"
    if local_auth.is_file() and local_auth.stat().st_size > 2:
        return
    for src in opencode_auth_paths():
        if src.is_file() and src != local_auth:
            local_auth.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, local_auth)
            return


@pytest.fixture(scope="session")
def require_opencode() -> None:
    apply_settings()
    if shutil.which("opencode") is None:
        pytest.fail("opencode CLI not on PATH — install OpenCode and retry")
    if not opencode_auth_present():
        tried = ", ".join(str(p) for p in opencode_auth_paths())
        pytest.fail(
            f"OpenCode auth.json not found (checked: {tried}). "
            "Run: .\\scripts\\setup_opencode_local.ps1"
        )
    from src.llm.opencode import _run_opencode_prompt

    cfg = apply_settings()
    probe = _run_opencode_prompt("Reply with exactly: OK", settings=cfg, timeout_seconds=60)
    if not probe or "OK" not in probe.upper():
        pytest.fail(
            "OpenCode auth present but `opencode run` returned no text. "
            "Check ZOOPLUS_OPENCODE_MODEL and .opencode/config-cli (no MCP)."
        )
