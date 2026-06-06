"""Positive intent hints for fast routing (allow-list only — not off-topic deny lists)."""

from __future__ import annotations

import re

_HELP_ABOUT = re.compile(
    r"\b("
    r"your\s+services?|what\s+services?|services?\s+do\s+you\s+provide|"
    r"what\s+can\s+you\s+(tell|do)|what\s+do\s+you\s+offer|"
    r"about\s+your(\s+services?|\s+shop)?|capabilities|how\s+do\s+you\s+work|"
    r"help\s+me\s+understand\s+what\s+you\s+offer"
    r")\b",
    re.I,
)

_CATALOG_ACTION = re.compile(
    r"\b(show\s+me|options?|recommend|suggest|find|browse|looking\s+for|"
    r"best\s+\w+|need\s+\w+\s+food|in\s+stock|on\s+sale|discount)\b",
    re.I,
)

_PET_PRODUCT = re.compile(
    r"\b(cat|cats|dog|dogs|puppy|puppies|kitten|kittens|pet|"
    r"food|treats?|toys?|litter|chew|grain|eukanuba|royal\s+canin)\b",
    re.I,
)

_PRODUCT_BROWSE = re.compile(
    r"\b("
    r"what\s+products?|products?\s+(do\s+you\s+)?(have|sell|carry|stock)|"
    r"what\s+do\s+you\s+sell|what'?s?\s+available|show\s+me\s+(something|anything)|"
    r"browse\s+(the\s+)?(shop|catalog)|anything\s+in\s+stock"
    r")\b",
    re.I,
)

_SHOW_PET_TOPIC = re.compile(
    r"\bshow\s+me\b.*\b(about\s+)?(dogs?|cats?|pupp(?:y|ies)|kitt(?:en|ens)?)\b",
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
    text = query.strip()
    if not text or _OFF_TOPIC_HARD.search(text) or looks_like_non_catalog_species(text):
        return False
    if _PRODUCT_BROWSE.search(text):
        return True
    if _SHOW_PET_TOPIC.search(text):
        return True
    return False


def looks_like_catalog_search(query: str) -> bool:
    text = query.strip()
    if not text or _OFF_TOPIC_HARD.search(text):
        return False
    if looks_like_non_catalog_species(text):
        return False
    if looks_like_product_browse(text):
        return True
    if _CATALOG_ACTION.search(text) and _PET_PRODUCT.search(text):
        return True
    if re.search(
        r"\b(dry|wet|grain[- ]?free|sensitive|puppy|kitten|adult)\b.*\b(food|treats?)\b",
        text,
        re.I,
    ):
        return True
    if re.search(r"\b(cat|dog)\s+food\b", text, re.I):
        return True
    if re.search(
        r"\b(dog|cat|puppy|kitten)s?\s+(product|toy|chew|food|treats?|snack|litter)\b",
        text,
        re.I,
    ):
        return True
    return False
