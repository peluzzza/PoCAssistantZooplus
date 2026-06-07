"""Lightweight conversational intents — polite ask-and-respond without full RAG."""

from __future__ import annotations

import re
from enum import StrEnum

from src.config import Settings, apply_settings
from src.llm.opencode import synthesize_opencode_chat


class ConvoKind(StrEnum):
    GREETING = "greeting"
    THANKS = "thanks"
    BYE = "bye"
    HELP = "help"
    PRODUCT = "product"


_GREETING = re.compile(
    r"^(hi|hello|hey|hola|buenas|good\s+(morning|afternoon|evening))[!?.\s]*$",
    re.I,
)
_GREETING_CASUAL = re.compile(
    r"^(hola\s+que\s+tal|qué\s+tal|que\s+tal|how\s+are\s+you|how'?s\s+it\s+going|"
    r"hi\s+there|hey\s+there|buenos\s+días|buenas\s+tardes|buenas\s+noches|"
    r"bonjour|salut|bonsoir|ça\s+va|comment\s+ça\s+va|comment\s+allez-vous|"
    r"guten\s+tag|hallo\s+wie\s+geht|wie\s+geht'?s)[!?.\s]*$",
    re.I,
)
_SHORT_SOCIAL_OPENER = re.compile(
    r"^(hola|hi|hey|hello|buenas|good\s+(morning|afternoon|evening))\b",
    re.I,
)
_PET_SHOP_WORD = re.compile(
    r"\b(dog|cat|food|product|toy|puppy|kitten|treat|litter|collar|eur|€|price)\b",
    re.I,
)
_THANKS = re.compile(r"^(thanks|thank\s+you|gracias|muchas\s+gracias|danke)[!?.\s]*$", re.I)
_BYE = re.compile(r"^(bye|goodbye|see\s+you|adios|hasta\s+luego)[!?.\s]*$", re.I)
_HELP = re.compile(r"^(help|\?|what\s+can\s+you\s+do|how\s+can\s+you\s+help)[!?.\s]*$", re.I)
_HELP_PHRASES = re.compile(
    r"(what\s+can\s+you\s+tell\s+me\s+about\s+(your\s+)?services|"
    r"what\s+services\s+do\s+you\s+provide|hello,?\s+what\s+services)",
    re.I,
)


def classify_conversation(query: str) -> ConvoKind:
    text = query.strip()
    if _GREETING.match(text) or _GREETING_CASUAL.match(text):
        return ConvoKind.GREETING
    if (
        len(text.split()) <= 5
        and _SHORT_SOCIAL_OPENER.search(text)
        and not _PET_SHOP_WORD.search(text)
    ):
        return ConvoKind.GREETING
    if _THANKS.match(text):
        return ConvoKind.THANKS
    if _BYE.match(text):
        return ConvoKind.BYE
    if _HELP.match(text) or _HELP_PHRASES.search(text):
        return ConvoKind.HELP
    return ConvoKind.PRODUCT


def is_conversational_only(query: str) -> bool:
    return classify_conversation(query) != ConvoKind.PRODUCT


def _template_reply(kind: ConvoKind, site_id: int) -> str:
    if kind == ConvoKind.GREETING:
        return (
            f"Hello! I'm the zooplus Assistant for shop {site_id}. "
            "I'm here to help you find pet food, treats, and accessories. "
            "What are you looking for today — e.g. dry food for a puppy or grain-free cat food?"
        )
    if kind == ConvoKind.THANKS:
        return (
            "You're very welcome! If you'd like, I can suggest more options or narrow "
            "by brand, budget, or pet type."
        )
    if kind == ConvoKind.BYE:
        return "Goodbye! Come back anytime you need help choosing pet products for your shop."
    if kind == ConvoKind.HELP:
        return (
            "I can search this shop's catalog and recommend up to four products. "
            'Ask in natural language — e.g. "best dry food for a sensitive puppy" or '
            '"popular cat treats in stock". Off-topic questions (weather, news, etc.) '
            "I'll politely decline."
        )
    return ""


def conversational_reply(
    query: str,
    site_id: int,
    *,
    settings: Settings | None = None,
) -> str:
    """Polite short reply for greetings/thanks/help — optional OpenCode polish."""
    cfg = settings or apply_settings()
    kind = classify_conversation(query)
    fallback = _template_reply(kind, site_id)

    if (cfg.synthesis_mode or "").lower() != "opencode":
        return fallback

    llm = synthesize_opencode_chat(
        query=query,
        site_id=site_id,
        context=(
            f"Intent: {kind.value}. Reply in 2-4 short sentences. Be warm and professional. "
            "Stay within pet-product shopping assistance for zooplus."
        ),
        products=[],
        settings=cfg,
        timeout_seconds=min(10, cfg.opencode_timeout_seconds),
    )
    return llm or fallback


def social_kind_hint(query: str, *, intent_social_kind: str | None = None) -> str:
    """Resolve social intent — intent agent wins over regex (unit-test contract)."""
    if intent_social_kind:
        return intent_social_kind
    kind = classify_conversation(query)
    if kind == ConvoKind.PRODUCT:
        return "product"
    return kind.value


def emergency_social_fallback(site_id: int) -> str:
    """Short grounded message when agentic social path fails."""
    return (
        f"I'm the zooplus Assistant for shop {site_id}. "
        "I can help you find pet food, treats, and accessories in this catalog."
    )
