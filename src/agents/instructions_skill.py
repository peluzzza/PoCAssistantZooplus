"""Internal skill: Coding Task instructions + order catalog (never shown to shopper)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from src.rag.catalog_lexicon import prompt_context as catalog_lexicon_prompt

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "docs" / "instructions" / "AGENT_BUNDLE.md"
ORDER_CATALOG = ROOT / "docs" / "instructions" / "order" / "product_catalog_dataset.json"
INSTRUCTIONS_CATALOG = ROOT / "docs" / "instructions" / "product_catalog_dataset.json"


@lru_cache(maxsize=1)
def _catalog_path() -> Path:
    return INSTRUCTIONS_CATALOG if INSTRUCTIONS_CATALOG.is_file() else ORDER_CATALOG


@lru_cache(maxsize=1)
def catalog_scope_summary() -> str:
    path = _catalog_path()
    if not path.is_file():
        return "Catalog missing."
    rows = json.loads(path.read_text(encoding="utf-8"))
    sites = sorted({int(r["site_id"]) for r in rows})
    return f"Catalog: {len(rows)} variants; sites {sites}; source={path.name}"


@lru_cache(maxsize=1)
def bundle_excerpt(max_chars: int = 3000) -> str:
    if not BUNDLE.is_file():
        return ""
    text = BUNDLE.read_text(encoding="utf-8")
    return text[:max_chars]


def instructions_skill_context(*, site_id: int) -> str:
    return "\n".join(
        [
            "[internal skill: instructions]",
            bundle_excerpt(),
            catalog_scope_summary(),
            catalog_lexicon_prompt(),
            f"active_site_id={site_id}",
            "Shopper-facing name: zooplus Assistant only.",
        ]
    )
