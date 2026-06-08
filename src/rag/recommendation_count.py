"""Resolve how many catalog products to return — default 4, shopper can ask for more."""

from __future__ import annotations

import re

# ES / EN / DE / FR — "10 opciones", "show me 10 products", "top 5", etc.
_COUNT_NUM = r"(\d{1,2})"
_COUNT_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.I)
    for p in (
        rf"\b{_COUNT_NUM}\s*(?:opciones?|productos?|art[ií]culos?|sugerencias?|"
        rf"recomendaciones?|items?|picks?|options?|results?|choices?|ergebnisse?)\b",
        rf"\b(?:dame|mu[eé]strame|muestrame|ens[eé]ñame|quiero|necesito|"
        rf"show\s+me|give\s+me|list\s+me|fetch\s+me|bring\s+me)\s+{_COUNT_NUM}\b",
        rf"\b(?:top|los|las|die|les)\s+{_COUNT_NUM}\b",
        rf"\b{_COUNT_NUM}\s+(?:mejores|best|top|primera?s?)\b",
        rf"\b(?:at\s+least|al\s+menos|hasta)\s+{_COUNT_NUM}\b",
    )
)

_WORD_NUMBERS: dict[str, int] = {
    "uno": 1,
    "one": 1,
    "eins": 1,
    "un": 1,
    "dos": 2,
    "two": 2,
    "zwei": 2,
    "deux": 2,
    "tres": 3,
    "three": 3,
    "drei": 3,
    "trois": 3,
    "cuatro": 4,
    "four": 4,
    "vier": 4,
    "quatre": 4,
    "cinco": 5,
    "five": 5,
    "fünf": 5,
    "funf": 5,
    "cinq": 5,
    "seis": 6,
    "six": 6,
    "sechs": 6,
    "sieben": 7,
    "seven": 7,
    "ocho": 8,
    "eight": 8,
    "acht": 8,
    "neun": 9,
    "nine": 9,
    "nueve": 9,
    "diez": 10,
    "ten": 10,
    "zehn": 10,
    "dix": 10,
}


def parse_requested_product_count(query: str) -> int | None:
    """Extract shopper-requested result count from natural language, if any."""
    text = (query or "").strip()
    if not text:
        return None
    for pattern in _COUNT_PATTERNS:
        m = pattern.search(text)
        if m:
            try:
                return int(m.group(1))
            except (TypeError, ValueError):
                continue
    for word, value in _WORD_NUMBERS.items():
        if re.search(rf"\b{re.escape(word)}\s+(?:opciones?|productos?|options?)\b", text, re.I):
            return value
        if re.search(rf"\b(?:dame|show\s+me|give\s+me)\s+{re.escape(word)}\b", text, re.I):
            return value
    return None


def retrieval_pool_size(requested: int, *, has_price_band: bool) -> int:
    """Candidate pool before price filter and cap slice."""
    if has_price_band:
        return max(requested * 6, 24)
    if requested > 4:
        return max(requested * 3, 12)
    return requested
