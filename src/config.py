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

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            log_level=os.environ.get("ZOOPLUS_LOG_LEVEL", "INFO").upper(),
            retrieval_mode=os.environ.get("ZOOPLUS_RETRIEVAL_MODE", "hybrid").lower(),
            chroma_path=os.environ.get("ZOOPLUS_CHROMA_PATH"),
            metrics_enabled=os.environ.get("ZOOPLUS_METRICS", "1") not in ("0", "false", "no"),
        )


def apply_settings(settings: Settings | None = None) -> Settings:
    """Apply env overrides used by RAG pipeline."""
    cfg = settings or Settings.from_env()
    if cfg.chroma_path:
        os.environ["ZOOPLUS_CHROMA_PATH"] = cfg.chroma_path
    os.environ["ZOOPLUS_RETRIEVAL_MODE"] = cfg.retrieval_mode
    return cfg
