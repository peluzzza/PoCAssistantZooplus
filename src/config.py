"""Runtime configuration from environment (v2 production profile)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _bounded_float(key: str, default: float, lo: float, hi: float) -> float:
    raw = os.environ.get(key, str(default))
    try:
        val = float(raw)
    except ValueError:
        return default
    return max(lo, min(hi, val))


def _bounded_int(key: str, default: int, lo: int, hi: int) -> int:
    raw = os.environ.get(key, str(default))
    try:
        val = int(raw)
    except ValueError:
        return default
    return max(lo, min(hi, val))


def _load_dotenv() -> None:
    """Load repo `.env` into os.environ (file is gitignored)."""
    env_file = ROOT / ".env"
    if not env_file.is_file():
        return
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    app_name: str = "zooplus Assistant"
    log_level: str = "INFO"
    retrieval_mode: str = "hybrid"
    chroma_path: str | None = None
    metrics_enabled: bool = True
    synthesis_mode: str = "opencode"
    opencode_model: str = "opencode-go/deepseek-v4-flash"
    opencode_timeout_seconds: int = 25
    opencode_data_dir: str | None = None
    opencode_config_dir: str | None = None
    chunk_interval_seconds: int = 5
    max_chunk_messages: int = 5
    stream_mode: str = "conductor"
    chunk_min_typing_seconds: float = 1.4
    chunk_min_pause_seconds: float = 0.9

    @classmethod
    def from_env(cls) -> Settings:
        timeout_raw = os.environ.get("ZOOPLUS_OPENCODE_TIMEOUT", "25")
        try:
            timeout = max(10, int(timeout_raw))
        except ValueError:
            timeout = 90
        return cls(
            log_level=os.environ.get("ZOOPLUS_LOG_LEVEL", "INFO").upper(),
            retrieval_mode=os.environ.get("ZOOPLUS_RETRIEVAL_MODE", "hybrid").lower(),
            chroma_path=os.environ.get("ZOOPLUS_CHROMA_PATH"),
            metrics_enabled=os.environ.get("ZOOPLUS_METRICS", "1") not in ("0", "false", "no"),
            synthesis_mode=os.environ.get("ZOOPLUS_SYNTHESIS_MODE", "opencode").lower(),
            opencode_model=os.environ.get(
                "ZOOPLUS_OPENCODE_MODEL",
                "opencode/deepseek-v4-flash-free",
            ),
            opencode_timeout_seconds=timeout,
            opencode_data_dir=os.environ.get("ZOOPLUS_OPENCODE_DATA_DIR"),
            opencode_config_dir=os.environ.get("ZOOPLUS_OPENCODE_CONFIG_DIR"),
            chunk_interval_seconds=_bounded_int("ZOOPLUS_CHUNK_INTERVAL_SECONDS", 5, 2, 30),
            max_chunk_messages=_bounded_int("ZOOPLUS_MAX_CHUNK_MESSAGES", 5, 1, 8),
            stream_mode=os.environ.get("ZOOPLUS_STREAM_MODE", "conductor").strip().lower()
            or "conductor",
            chunk_min_typing_seconds=_bounded_float(
                "ZOOPLUS_CHUNK_MIN_TYPING_SECONDS", 1.4, 0.0, 5.0
            ),
            chunk_min_pause_seconds=_bounded_float(
                "ZOOPLUS_CHUNK_MIN_PAUSE_SECONDS", 0.9, 0.0, 5.0
            ),
        )


def apply_settings(settings: Settings | None = None) -> Settings:
    """Apply env overrides used by RAG pipeline."""
    _load_dotenv()
    cfg = settings or Settings.from_env()
    if cfg.chroma_path:
        os.environ["ZOOPLUS_CHROMA_PATH"] = cfg.chroma_path
    os.environ["ZOOPLUS_RETRIEVAL_MODE"] = cfg.retrieval_mode
    if cfg.opencode_data_dir:
        data = str((ROOT / cfg.opencode_data_dir).resolve())
        os.environ.setdefault("ZOOPLUS_OPENCODE_DATA_DIR", data)
        os.environ.setdefault("OPENCODE_DATA_DIR", data)
    if cfg.opencode_config_dir:
        conf = str((ROOT / cfg.opencode_config_dir).resolve())
        os.environ.setdefault("ZOOPLUS_OPENCODE_CONFIG_DIR", conf)
        os.environ.setdefault("OPENCODE_CONFIG_DIR", conf)
    return cfg
