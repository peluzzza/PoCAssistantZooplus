"""Catalog-derived routing lexicon — built at ingest, no hand-maintained pet/product words."""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "product_catalog_dataset.json"
LEXICON_PATH = ROOT / "artifacts" / "index" / "routing_lexicon.json"
_REDIS_KEY = "zooplus:lexicon:v1"

_TOKEN = re.compile(r"[a-zA-ZÀ-ÿ0-9][a-zA-ZÀ-ÿ0-9'-]{2,}")
_STOP = frozenset(
    {
        "the",
        "and",
        "for",
        "with",
        "from",
        "this",
        "that",
        "your",
        "para",
        "con",
        "por",
        "una",
        "uno",
        "los",
        "las",
        "del",
        "der",
        "die",
        "und",
        "für",
        "mit",
        "des",
        "les",
        "une",
    }
)


def _tokenize(text: str) -> list[str]:
    if not text:
        return []
    clean = re.sub(r"<[^>]+>", " ", text)
    return [m.group(0).lower() for m in _TOKEN.finditer(clean)]


def build_lexicon(records: list[dict]) -> dict:
    """Derive brands, pet types, and frequent catalog tokens from indexed data."""
    brands: set[str] = set()
    pet_types: set[str] = set()
    product_names: set[str] = set()
    token_freq: Counter[str] = Counter()

    for row in records:
        brand = (row.get("brands") or "").strip()
        if brand:
            brands.add(brand)
        pet = (row.get("pet_type") or "").strip()
        if pet:
            pet_types.add(pet)
        name = (row.get("product_name") or "").strip()
        if name:
            product_names.add(name)
        for field in ("product_name", "summary", "brands"):
            for tok in _tokenize(str(row.get(field) or "")):
                if tok not in _STOP and not tok.isdigit():
                    token_freq[tok] += 1

    tokens = [t for t, _ in token_freq.most_common(120) if len(t) >= 4]
    sites = sorted({int(r["site_id"]) for r in records if r.get("site_id") is not None})

    return {
        "version": 1,
        "brands": sorted(brands),
        "pet_types": sorted(pet_types),
        "product_tokens": tokens[:80],
        "sample_product_names": sorted(product_names)[:24],
        "sites": sites,
        "record_count": len(records),
    }


def persist_lexicon(lexicon: dict) -> Path:
    LEXICON_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEXICON_PATH.write_text(json.dumps(lexicon, ensure_ascii=False, indent=2), encoding="utf-8")
    _publish_redis(lexicon)
    return LEXICON_PATH


def _redis_client():
    url = os.environ.get("ZOOPLUS_REDIS_URL", "").strip()
    if not url:
        return None
    try:
        import redis
    except ImportError:
        return None
    return redis.from_url(url, decode_responses=True)


def redis_enabled() -> bool:
    return os.environ.get("ZOOPLUS_CACHE_BACKEND", "memory").lower() == "redis"


def _publish_redis(lexicon: dict) -> None:
    if not redis_enabled():
        return
    client = _redis_client()
    if client is None:
        return
    client.set(_REDIS_KEY, json.dumps(lexicon, ensure_ascii=False))


def _load_from_redis() -> dict | None:
    if not redis_enabled():
        return None
    client = _redis_client()
    if client is None:
        return None
    raw = client.get(_REDIS_KEY)
    if not raw:
        return None
    data = json.loads(raw)
    return data if isinstance(data, dict) else None


def build_lexicon_from_raw() -> dict:
    if not RAW.is_file():
        return {"version": 1, "brands": [], "pet_types": [], "product_tokens": [], "sites": []}
    records = json.loads(RAW.read_text(encoding="utf-8"))
    return build_lexicon(records)


@lru_cache(maxsize=1)
def load_lexicon() -> dict:
    cached = _load_from_redis()
    if cached:
        return cached
    if LEXICON_PATH.is_file():
        return json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
    lexicon = build_lexicon_from_raw()
    if lexicon.get("record_count"):
        persist_lexicon(lexicon)
    return lexicon


def reload_lexicon() -> dict:
    load_lexicon.cache_clear()
    return load_lexicon()


def prompt_context(*, max_brands: int = 18, max_tokens: int = 24) -> str:
    """Compact lexicon slice for agentic intent prompts (catalog facts, not routing rules)."""
    lex = load_lexicon()
    brands = ", ".join(lex.get("brands", [])[:max_brands])
    tokens = ", ".join(lex.get("product_tokens", [])[:max_tokens])
    pets = ", ".join(lex.get("pet_types", []))
    sites = lex.get("sites", [])
    return (
        f"Indexed catalog: {lex.get('record_count', 0)} variants; sites {sites}; "
        f"pet_types={pets or 'n/a'}; brands include: {brands or 'n/a'}; "
        f"common product terms: {tokens or 'n/a'}. "
        "Classify by shopper TOPIC in any language — do not rely on fixed keyword lists."
    )


def _query_tokens(query: str) -> set[str]:
    return set(_tokenize(query.lower()))


def query_signal(query: str) -> dict:
    """Match query tokens against catalog-derived brands/tokens (not hand-coded species)."""
    text = (query or "").strip()
    if not text:
        return {"score": 0, "brands": [], "tokens": []}
    lex = load_lexicon()
    q_lower = text.lower()
    matched_brands = [b for b in lex.get("brands", []) if b.lower() in q_lower]
    q_tokens = _query_tokens(text)
    catalog_tokens = set(lex.get("product_tokens", []))
    matched_tokens = sorted(q_tokens & catalog_tokens)
    score = len(matched_brands) + min(len(matched_tokens), 3)
    return {"score": score, "brands": matched_brands, "tokens": matched_tokens}


def has_catalog_signal(query: str, *, min_score: int = 1) -> bool:
    return query_signal(query)["score"] >= min_score
