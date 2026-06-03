"""Build vector index from data/raw/ (T2)."""

from __future__ import annotations

from src.rag.pipeline import run_ingest


def run() -> int:
    manifest = run_ingest()
    print(f"ingested={manifest['records_ingested']} index={manifest['index_path']}")
    return 0
