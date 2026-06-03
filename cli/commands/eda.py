"""EDA command — writes summary to stdout and updates trace (T1)."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "product_catalog_dataset.json"


def run_eda() -> int:
    if not RAW.exists():
        print(f"Missing catalog: {RAW}", flush=True)
        return 1
    data = json.loads(RAW.read_text(encoding="utf-8"))
    sites = sorted({r["site_id"] for r in data})
    locales = sorted({r["locale"] for r in data})
    pets = Counter(r["pet_type"] for r in data)
    print(f"records={len(data)} sites={sites} locales={locales} pet_types={dict(pets)}")
    print(f"unique_product_id={len({r['product_id'] for r in data})}")
    print(f"unique_variant_id={len({r['variant_id'] for r in data})}")
    return 0
