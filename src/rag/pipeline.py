"""Ingest pipeline: raw JSON → normalized docs → Chroma index."""

from __future__ import annotations

import json
from pathlib import Path

from src.rag.chunking import record_to_index_item
from src.rag.store.chroma_store import upsert_items

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "product_catalog_dataset.json"
INDEX_DIR = ROOT / "artifacts" / "index" / "chroma"
MANIFEST = ROOT / "artifacts" / "index" / "manifest.json"


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
    count = upsert_items(INDEX_DIR, items)
    manifest = {
        "records_ingested": count,
        "index_path": str(INDEX_DIR),
        "collection": "zooplus_variants",
        "chunk_unit": "catalog_row",
        "source_rows": len(records),
        "indexed_ids": count,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
