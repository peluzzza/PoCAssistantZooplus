"""E2E smoke — CLI + RAG path (no external LLM)."""

import subprocess
import sys

import pytest
from src.rag.retrieve import search_catalog

pytestmark = pytest.mark.e2e


def test_cli_eda_exits_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "cli", "eda"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "records=300" in result.stdout


def test_e2e_ingest_then_search(indexed_catalog: dict) -> None:
    """Full local path: index built in fixture → query returns scoped hits."""
    hits = search_catalog("cat food", site_id=1, n_results=3, pet_type="CATS")
    assert len(hits) >= 1
    assert hits[0]["metadata"]["pet_type"] == "CATS"
    assert hits[0]["metadata"]["site_id"] == 1
