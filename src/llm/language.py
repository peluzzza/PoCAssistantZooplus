"""Shopper reply language — query-first, Accept-Language fallback."""

from __future__ import annotations

import re

_LANGUAGE_LABELS: dict[str, str] = {
    "en": "English",
    "es": "Spanish",
    "de": "German",
}

_ACCEPT_LANG = re.compile(
    r"^\s*([a-zA-Z]{2,3})(?:-[a-zA-Z0-9]+)?(?:\s*;\s*q=[0-9.]+)?",
    re.IGNORECASE,
)
_CONTROL_OR_WEIRD = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ufffd\u200b-\u200f]")
_SYMBOL_HEAVY = re.compile(r"[^\w\s]", re.UNICODE)

_ES_MARKERS = re.compile(
    r"[ñ¿¡]|\b(hola|gracias|perro|gato|comida|necesito|quiero|busco|entre|para)\b",
    re.IGNORECASE,
)
_DE_MARKERS = re.compile(
    r"[äöüß]|\b(hallo|danke|hund|katze|futter|bitte|zwischen|für)\b",
    re.IGNORECASE,
)
_EN_MARKERS = re.compile(
    r"\b(hello|hi|thanks|please|dog|cat|food|puppy|kitten|between|write|english)\b",
    re.IGNORECASE,
)


def parse_accept_language(header: str | None) -> str | None:
    """Primary browser locale tag → short code (es-ES → es)."""
    if not header or not header.strip():
        return None
    for part in header.split(","):
        part = part.strip()
        if not part:
            continue
        m = _ACCEPT_LANG.match(part)
        if m:
            code = m.group(1).lower()
            if code in _LANGUAGE_LABELS:
                return code
            if code.startswith("es"):
                return "es"
            if code.startswith("en"):
                return "en"
            if code.startswith("de"):
                return "de"
    return None


def has_strange_characters(text: str) -> bool:
    """True when the query is not reliable for language detection."""
    if not text or not text.strip():
        return True
    if _CONTROL_OR_WEIRD.search(text):
        return True
    letters = sum(1 for c in text if c.isalpha())
    if letters == 0:
        return True
    symbols = len(_SYMBOL_HEAVY.findall(text))
    if symbols > max(6, len(text) // 2):
        return True
    return False


def detect_query_language(query: str) -> tuple[str | None, bool]:
    """
    Detect language from shopper text.
    Returns (code, confident). confident=False → use Accept-Language.
    """
    text = query.strip()
    if not text or has_strange_characters(text):
        return None, False

    if _ES_MARKERS.search(text):
        return "es", True
    if _DE_MARKERS.search(text):
        return "de", True
    if _EN_MARKERS.search(text):
        return "en", True

    non_ascii = sum(1 for c in text if ord(c) > 127)
    if non_ascii > 0:
        return None, False

    if len(text) >= 12 and re.search(r"[a-zA-Z]{3,}", text):
        return "en", True

    if len(text.split()) <= 2 and text.isascii():
        return None, False

    return None, False


def resolve_shopper_language(
    query: str,
    accept_language: str | None,
    *,
    site_id: int | None = None,
) -> tuple[str, str]:
    """
    Pick reply language code and source label.
    Priority: confident query → Accept-Language → shop locale → English.
    """
    code, confident = detect_query_language(query)
    if confident and code:
        return code, "query"

    browser = parse_accept_language(accept_language)
    if browser:
        return browser, "accept-language"

    if site_id == 1:
        return "de", "site"
    if site_id == 15:
        return "es", "site"
    if site_id == 3:
        return "en", "site"

    return "en", "default"


def language_label(code: str) -> str:
    return _LANGUAGE_LABELS.get(code, "English")


def reply_language_instruction(
    query: str,
    accept_language: str | None,
    *,
    site_id: int | None = None,
) -> str:
    """Prompt line for OpenCode agents."""
    code, source = resolve_shopper_language(query, accept_language, site_id=site_id)
    label = language_label(code)
    if source == "query":
        return f"Reply in {label} (match the customer's language)."
    if source == "accept-language":
        return (
            f"Reply in {label} (shopper browser preference Accept-Language; "
            "the message text was ambiguous)."
        )
    if source == "site":
        return f"Reply in {label} (default for this shop locale)."
    return f"Reply in {label}."
