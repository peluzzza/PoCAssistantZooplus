"""Shared pytest fixtures."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

# Agentic routing oracle (from instructions matrix) — no keyword guard in CI.
os.environ["ZOOPLUS_INTENT_MODE"] = "oracle"
os.environ["ZOOPLUS_SYNTHESIS_MODE"] = "template"

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "product_catalog_dataset.json"


@pytest.fixture(scope="session")
def catalog_records() -> list[dict]:
    return json.loads(RAW.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def sample_record(catalog_records: list[dict]) -> dict:
    return catalog_records[0]


@pytest.fixture(scope="module")
def indexed_catalog(tmp_path_factory):
    """Build an isolated Chroma index for integration tests."""
    import os

    index_dir = tmp_path_factory.mktemp("chroma") / "chroma"
    os.environ["ZOOPLUS_CHROMA_PATH"] = str(index_dir)
    from src.rag.pipeline import run_ingest

    manifest = run_ingest()
    yield manifest
    os.environ.pop("ZOOPLUS_CHROMA_PATH", None)
