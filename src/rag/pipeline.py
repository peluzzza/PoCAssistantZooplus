"""Ingest pipeline: raw JSON → normalized docs → Chroma index."""

from __future__ import annotations

import json
import os
from pathlib import Path

from src.rag.catalog_lexicon import build_lexicon, persist_lexicon
from src.rag.chunking import record_to_index_item
from src.rag.store.chroma_store import upsert_items

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "product_catalog_dataset.json"
MANIFEST = ROOT / "artifacts" / "index" / "manifest.json"


def index_dir() -> Path:
    override = os.environ.get("ZOOPLUS_CHROMA_PATH")
    if override:
        return Path(override)
    return ROOT / "artifacts" / "index" / "chroma"


def run_ingest() -> dict:
    if not RAW.exists():
        raise FileNotFoundError(f"Missing catalog: {RAW}")
    records = json.loads(RAW.read_text(encoding="utf-8"))
    # Deduplicate by Chroma id (dataset has duplicate SKU rows per site/locale)
    by_id: dict[str, dict] = {}
    for idx, record in enumerate(records):
        item = record_to_index_item(record)
        key = item["id"]
        if key in by_id:
            item["id"] = f"{key}:dup{idx}"
        by_id[item["id"]] = item
    items = list(by_id.values())
    path = index_dir()
    count = upsert_items(path, items)
    manifest = {
        "records_ingested": count,
        "index_path": str(path),
        "collection": "zooplus_variants",
        "chunk_unit": "catalog_row",
        "source_rows": len(records),
        "indexed_ids": count,
    }
    lexicon = build_lexicon(records)
    lexicon_path = persist_lexicon(lexicon)
    manifest["routing_lexicon"] = str(lexicon_path)
    manifest["lexicon_brands"] = len(lexicon.get("brands", []))
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
