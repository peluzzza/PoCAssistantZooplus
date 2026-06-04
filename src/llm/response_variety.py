"""Rotating copy pools — template fallback stays varied, not one fixed paragraph."""

from __future__ import annotations

import hashlib
from typing import TypeVar

T = TypeVar("T")


def style_seed(*parts: str) -> str:
    """Stable per-utterance seed so the same question gets the same variant, repeats can differ slightly."""
    blob = "|".join(p.strip().lower() for p in parts if p)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:8]


def pick_variant(key: str, options: tuple[str, ...]) -> str:
    if not options:
        return ""
    idx = int(hashlib.sha256(key.encode("utf-8")).hexdigest(), 16) % len(options)
    return options[idx]


def variation_directive(query: str, role: str) -> str:
    """Inject into agent prompts — discourage rigid repeated branding."""
    seed = style_seed(query, role)
    return (
        f"[variation seed={seed}] Write fresh, natural prose for THIS turn only. "
        "Do not copy example phrases from instructions verbatim. "
        "Avoid repeating 'I'm the zooplus Assistant for shop' unless the user asked who you are. "
        "2–5 sentences for social/decline; for catalog answers do not output numbered product lists "
        "(the UI shows product cards)."
    )
