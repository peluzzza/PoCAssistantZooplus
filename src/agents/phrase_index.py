"""Fast in-memory social phrase index — YAML seed + playbook learned rows."""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_DATA_PATH = Path(__file__).resolve().parent / "data" / "social_phrases.yaml"
_NORM_RE = re.compile(r"[^\w\s']+", re.UNICODE)


def _normalize(text: str) -> str:
    raw = unicodedata.normalize("NFKD", (text or "").strip().lower())
    raw = "".join(ch for ch in raw if not unicodedata.combining(ch))
    raw = _NORM_RE.sub(" ", raw)
    return " ".join(raw.split())


@lru_cache(maxsize=1)
def _load_seed() -> dict[str, tuple[str, ...]]:
    if not _DATA_PATH.is_file():
        return {}
    data = yaml.safe_load(_DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    out: dict[str, tuple[str, ...]] = {}
    for category, rows in data.items():
        if not isinstance(rows, list):
            continue
        phrases = tuple(
            dict.fromkeys(_normalize(str(row)) for row in rows if str(row).strip())
        )
        out[str(category).lower()] = phrases
    return out


def reload_phrase_index() -> None:
    _load_seed.cache_clear()
    _merged_index.cache_clear()


@lru_cache(maxsize=8)
def _merged_index(category: str) -> tuple[str, ...]:
    seed = _load_seed().get(category, ())
    learned: tuple[str, ...] = ()
    try:
        from src.agents.stream_voice_registry import social_help_phrases

        if category == "help":
            learned = social_help_phrases()
    except Exception:
        learned = ()
    merged = tuple(dict.fromkeys([*(_normalize(p) for p in seed), *(_normalize(p) for p in learned)]))
    return merged


def phrase_categories() -> tuple[str, ...]:
    return tuple(_load_seed().keys())


def match_phrase_category(query: str, category: str) -> bool:
    """Substring match on normalized query — O(n) over ~30–80 phrases per category."""
    norm_q = _normalize(query)
    if not norm_q:
        return False
    for phrase in _merged_index(category):
        if not phrase:
            continue
        if norm_q == phrase or phrase in norm_q:
            return True
    return False


def match_social_help(query: str) -> bool:
    return match_phrase_category(query, "help")


def classify_social_kind(query: str) -> str | None:
    """Return greeting|thanks|bye|help|identity or None."""
    order = ("help", "identity", "thanks", "bye", "greeting")
    for kind in order:
        if match_phrase_category(query, kind):
            return kind
    return None


def index_stats() -> dict[str, Any]:
    seed = _load_seed()
    return {
        "source": str(_DATA_PATH),
        "categories": {k: len(v) for k, v in seed.items()},
        "total_seed_phrases": sum(len(v) for v in seed.values()),
    }
