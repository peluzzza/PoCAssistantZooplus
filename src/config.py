"""Runtime configuration from environment (v2 production profile)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "zooplus Assistant"
    log_level: str = "INFO"
    retrieval_mode: str = "hybrid"
    chroma_path: str | None = None
    metrics_enabled: bool = True
    synthesis_mode: str = "template"
    opencode_model: str = "opencode-go/deepseek-v4-flash"
    opencode_timeout_seconds: int = 90
    opencode_data_dir: str | None = None
    opencode_config_dir: str | None = None

    @classmethod
    def from_env(cls) -> Settings:
        timeout_raw = os.environ.get("ZOOPLUS_OPENCODE_TIMEOUT", "90")
        try:
            timeout = max(10, int(timeout_raw))
        except ValueError:
            timeout = 90
        return cls(
            log_level=os.environ.get("ZOOPLUS_LOG_LEVEL", "INFO").upper(),
            retrieval_mode=os.environ.get("ZOOPLUS_RETRIEVAL_MODE", "hybrid").lower(),
            chroma_path=os.environ.get("ZOOPLUS_CHROMA_PATH"),
            metrics_enabled=os.environ.get("ZOOPLUS_METRICS", "1") not in ("0", "false", "no"),
            synthesis_mode=os.environ.get("ZOOPLUS_SYNTHESIS_MODE", "template").lower(),
            opencode_model=os.environ.get("ZOOPLUS_OPENCODE_MODEL", "opencode-go/deepseek-v4-flash"),
            opencode_timeout_seconds=timeout,
            opencode_data_dir=os.environ.get("ZOOPLUS_OPENCODE_DATA_DIR"),
            opencode_config_dir=os.environ.get("ZOOPLUS_OPENCODE_CONFIG_DIR"),
        )


def apply_settings(settings: Settings | None = None) -> Settings:
    """Apply env overrides used by RAG pipeline."""
    cfg = settings or Settings.from_env()
    if cfg.chroma_path:
        os.environ["ZOOPLUS_CHROMA_PATH"] = cfg.chroma_path
    os.environ["ZOOPLUS_RETRIEVAL_MODE"] = cfg.retrieval_mode
    return cfg
