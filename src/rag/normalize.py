"""Strip HTML from catalog text fields (non-destructive on raw JSON)."""

from __future__ import annotations

import re
from html import unescape

_HTML_TAG = re.compile(r"<[^>]+>")


def html_to_plain(text: str) -> str:
    """Convert HTML-ish catalog text to plain text for embedding."""
    if not text:
        return ""
    plain = _HTML_TAG.sub(" ", text)
    plain = unescape(plain)
    plain = re.sub(r"\s+", " ", plain).strip()
    return plain


def build_embed_text(record: dict) -> str:
    """Single embedding document per variant."""
    parts = [
        record.get("product_name") or "",
        record.get("variant_name") or "",
        record.get("brands") or "",
        record.get("pet_type") or "",
        html_to_plain(record.get("summary") or ""),
        html_to_plain(record.get("description") or ""),
        html_to_plain(record.get("ingredients") or ""),
        html_to_plain(record.get("feeding_recommendations") or ""),
    ]
    return "\n".join(p.strip() for p in parts if p.strip())
