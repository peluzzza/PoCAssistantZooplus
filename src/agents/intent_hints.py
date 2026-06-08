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

_SOCIAL_HELP = re.compile(
    r"(?:^|\b)("
    r"me\s+puedes\s+ayudar|puedes\s+ayudarme|me\s+ayudas|podr[ií]as\s+ayudarme|"
    r"ay[uú]dame|necesito\s+ayuda|"
    r"can\s+you\s+help(?:\s+me)?|could\s+you\s+help|help\s+me|"
    r"how\s+can\s+you\s+help|what\s+can\s+you\s+do|"
    r"kannst\s+du\s+mir\s+helfen|k[öo]nnen\s+sie\s+mir\s+helfen|"
    r"pouvez[- ]vous\s+m[''']aider|peux[- ]tu\s+m[''']aider"
    r")(?:\s|$|[?.!])",
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


def looks_like_social_help_request(query: str) -> bool:
    """Help / capabilities ask — social lane, never catalog."""
    text = (query or "").strip()
    if not text:
        return False
    from src.agents.phrase_index import match_social_help
    from src.agents.stream_voice_registry import learn_social_help_phrase, matches_playbook_social_help

    if (
        match_social_help(text)
        or _SOCIAL_HELP.search(text)
        or _HELP_ABOUT.search(text)
        or matches_playbook_social_help(text)
    ):
        learn_social_help_phrase(text)
        return True
    return False


def looks_like_help_about_shop(query: str) -> bool:
    return looks_like_social_help_request(query)


def looks_like_non_catalog_species(query: str, site_id: int = 3) -> bool:
    """Playbook + dynamic pet-noun inference (not a fixed species list)."""
    from src.agents.stream_voice_registry import mentions_non_catalog_species

    return mentions_non_catalog_species(query, site_id)


def looks_like_product_browse(query: str) -> bool:
    """English browse phrasing — opt-in fast path only (ZOOPLUS_FAST_INTENT)."""
    text = query.strip()
    if not text or _OFF_TOPIC_HARD.search(text) or looks_like_non_catalog_species(text):
        return False
    if re.search(
        r"\b(what\s+products?|products?\s+(do\s+you\s+)?(have|sell|carry|stock)|"
        r"what\s+do\s+you\s+sell|what'?s?\s+available|show\s+me\s+(something|anything|about)|"
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
