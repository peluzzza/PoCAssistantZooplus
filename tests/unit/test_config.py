"""Unit tests — settings from environment."""

import os

import pytest
from src.config import Settings, apply_settings

pytestmark = pytest.mark.unit


def test_apply_settings_sets_retrieval_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.config._load_dotenv", lambda: None)
    monkeypatch.setenv("ZOOPLUS_RETRIEVAL_MODE", "vector")
    cfg = apply_settings()
    assert cfg.retrieval_mode == "vector"
    assert os.environ["ZOOPLUS_RETRIEVAL_MODE"] == "vector"


def test_settings_defaults() -> None:
    s = Settings()
    assert s.retrieval_mode == "hybrid"
    assert s.metrics_enabled is True
