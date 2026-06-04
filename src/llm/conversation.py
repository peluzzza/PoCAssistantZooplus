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
    r"^(hi|hello|hey|hola|buenas|hi\s+there|good\s+(morning|afternoon|evening))[!?.\s]*$",
    re.I,
)
_THANKS = re.compile(r"^(thanks|thank\s+you|gracias|muchas\s+gracias|danke)[!?.\s]*$", re.I)
_BYE = re.compile(r"^(bye|goodbye|see\s+you|adios|hasta\s+luego)[!?.\s]*$", re.I)
_HELP = re.compile(r"^(help|\?|what\s+can\s+you\s+do|how\s+can\s+you\s+help)[!?.\s]*$", re.I)


def classify_conversation(query: str) -> ConvoKind:
    text = query.strip()
    if _GREETING.match(text):
        return ConvoKind.GREETING
    if _THANKS.match(text):
        return ConvoKind.THANKS
    if _BYE.match(text):
        return ConvoKind.BYE
    if _HELP.match(text):
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
