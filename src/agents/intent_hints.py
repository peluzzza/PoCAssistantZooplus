"""Policy-only hints and catalog-derived signals — production routing stays agentic."""

from __future__ import annotations

import re

from src.rag.catalog_lexicon import has_catalog_signal
from src.rag.price_filter import parse_eur_price_range

_HELP_ABOUT = re.compile(
    r"\b("
    r"your\s+services?|what\s+services?|services?\s+do\s+you\s+provide|"
    r"what\s+can\s+you\s+(tell|do)|what\s+do\s+you\s+offer|"
    r"about\s+your(\s+services?|\s+shop)?|capabilities|how\s+do\s+you\s+work|"
    r"help\s+me\s+understand\s+what\s+you\s+offer"
    r")\b",
    re.I,
)

_NON_CATALOG_SPECIES = re.compile(
    r"\b(horse|horses|pony|ponies|bird|birds|fish|reptile|hamster|guinea\s+pig)\b",
    re.I,
)

_OFF_TOPIC_HARD = re.compile(
    r"\b(weather|traffic|president|news\s+headline|bitcoin|crypto|"
    r"for\s+humans|human\s+food|search\s+the\s+internet|ignore\s+all\s+previous|"
    r"find\s+in\s+internet|on\s+the\s+internet|browse\s+the\s+web|web\s+search|"
    r"on\s+amazon|google\s+search)\b",
    re.I,
)


def looks_like_off_topic(query: str) -> bool:
    text = query.strip()
    if not text:
        return True
    if _OFF_TOPIC_HARD.search(text):
        return True
    if re.search(r"\binternet\b", text, re.I):
        return True
    return False


def looks_like_help_about_shop(query: str) -> bool:
    return bool(_HELP_ABOUT.search(query.strip()))


def looks_like_non_catalog_species(query: str) -> bool:
    return bool(_NON_CATALOG_SPECIES.search(query.strip()))


def looks_like_product_browse(query: str) -> bool:
    """English browse phrasing — opt-in fast path only (ZOOPLUS_FAST_INTENT)."""
    text = query.strip()
    if not text or _OFF_TOPIC_HARD.search(text) or looks_like_non_catalog_species(text):
        return False
    if re.search(
        r"\b(what\s+products?|products?\s+(do\s+you\s+)?(have|sell|carry|stock)|"
        r"what\s+do\s+you\s+sell|what'?s?\s+available|show\s+me\s+(something|anything)|"
        r"browse\s+(the\s+)?(shop|catalog)|anything\s+in\s+stock)\b",
        text,
        re.I,
    ):
        return True
    return False


def looks_like_catalog_search(query: str) -> bool:
    """Catalog signal from indexed brands/tokens — not hand-maintained species words."""
    text = query.strip()
    if not text or _OFF_TOPIC_HARD.search(text) or looks_like_non_catalog_species(text):
        return False
    if looks_like_product_browse(text):
        return True
    return has_catalog_signal(text)


def looks_like_price_filtered_catalog(query: str) -> bool:
    """EUR band plus catalog-derived vocabulary hit (fallback safety net only)."""
    if not parse_eur_price_range(query):
        return False
    return has_catalog_signal(query, min_score=1)
