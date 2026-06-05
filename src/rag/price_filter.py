"""Parse EUR price ranges from shopper queries and filter retrieval hits."""

from __future__ import annotations

import re

_EUR_RANGE = re.compile(
    r"(?:between|from|price[s]?\s+(?:between|from)?)\s*"
    r"€?\s*(\d+(?:[.,]\d+)?)\s*€?\s*"
    r"(?:and|to|-|–)\s*"
    r"€?\s*(\d+(?:[.,]\d+)?)\s*€?",
    re.IGNORECASE,
)
_EUR_RANGE_ALT = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(?:€|eur(?:os?)?)\s*(?:and|to|-|–)\s*(\d+(?:[.,]\d+)?)\s*(?:€|eur(?:os?)?)?",
    re.IGNORECASE,
)


def parse_eur_price_range(query: str) -> tuple[float, float] | None:
    """Return (min_eur, max_eur) if the query mentions a numeric band."""
    text = (query or "").strip()
    if not text:
        return None
    m = _EUR_RANGE.search(text) or _EUR_RANGE_ALT.search(text)
    if not m:
        return None
    a = float(m.group(1).replace(",", "."))
    b = float(m.group(2).replace(",", "."))
    return (min(a, b), max(a, b))


def apply_price_range_filter(query: str, hits: list[dict]) -> list[dict]:
    """Keep hits whose catalog price falls inside the parsed EUR band."""
    band = parse_eur_price_range(query)
    if not band or not hits:
        return hits
    lo, hi = band
    filtered: list[dict] = []
    for hit in hits:
        meta = hit.get("metadata") or {}
        try:
            price = float(meta.get("price", 0))
        except (TypeError, ValueError):
            continue
        if lo <= price <= hi:
            filtered.append(hit)
    return filtered if filtered else hits
