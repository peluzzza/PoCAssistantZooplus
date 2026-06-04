"""Lightweight conversational intents — polite ask-and-respond without full RAG."""

from __future__ import annotations

import os
import re
from enum import StrEnum

from src.config import Settings, apply_settings
from src.llm.opencode import synthesize_opencode_chat


class ConvoKind(StrEnum):
    GREETING = "greeting"
    THANKS = "thanks"
    BYE = "bye"
    HELP = "help"
    IDENTITY = "identity"
    PRODUCT = "product"


_GREETING = re.compile(
    r"^(hi|hello|hey|hola|buenas|buenos\s+d[ií]as|hi\s+there|good\s+(morning|afternoon|evening))[!?.\s]*$",
    re.I,
)
_THANKS = re.compile(
    r"^(thanks|thank\s+you|gracias|muchas\s+gracias|danke)[!?.\s]*$",
    re.I,
)
_BYE = re.compile(
    r"^(bye|goodbye|see\s+you(\s+later)?|adios|hasta\s+luego|goodbye\s+for\s+now)[!?.\s]*$",
    re.I,
)
_HELP = re.compile(
    r"^(help|\?|what\s+can\s+you\s+do|how\s+can\s+you\s+help|what\s+do\s+you\s+do)[!?.\s]*$",
    re.I,
)
_HELP_PHRASE = re.compile(
    r"\b(help\s+me\s+understand|what\s+you\s+offer|what\s+can\s+you\s+do\s+for\s+me)\b",
    re.I,
)
_IDENTITY = re.compile(
    r"\b("
    r"who\s+are\s+you|what\s+are\s+you|who\s+is\s+this|what\s+is\s+this(\s+(bot|assistant))?|"
    r"introduce\s+yourself|tell\s+me\s+about\s+yourself|"
    r"cu[eé]ntame\s+qui[eé]n\s+eres|qui[eé]n\s+eres"
    r")\b",
    re.I,
)


def classify_conversation(query: str) -> ConvoKind:
    text = query.strip()
    if _IDENTITY.search(text):
        return ConvoKind.IDENTITY
    if _GREETING.match(text) or re.search(r"^(hi|hello|hey|hola|buenos)\b", text, re.I):
        return ConvoKind.GREETING
    if _THANKS.match(text):
        return ConvoKind.THANKS
    if _BYE.match(text) or re.search(r"\b(goodbye|see\s+you|adios|hasta\s+luego)\b", text, re.I):
        return ConvoKind.BYE
    if _HELP.match(text) or _HELP_PHRASE.search(text):
        return ConvoKind.HELP
    if _IDENTITY.match(text):
        return ConvoKind.IDENTITY
    return ConvoKind.PRODUCT


def is_conversational_only(query: str) -> bool:
    return classify_conversation(query) != ConvoKind.PRODUCT


def _template_reply(kind: ConvoKind, site_id: int) -> str:
    if kind == ConvoKind.GREETING:
        return (
            f"Hi there! I'm the zooplus Assistant for shop {site_id}. "
            "I help shoppers find pet food, treats, and accessories in this catalog. "
            "What are you looking for — maybe dry food for a puppy or grain-free cat food?"
        )
    if kind == ConvoKind.THANKS:
        return (
            "You're welcome! I'm the zooplus Assistant for this shop — happy to suggest more "
            "options or narrow things by brand, budget, or dog vs cat whenever you like."
        )
    if kind == ConvoKind.BYE:
        return (
            f"Take care! I'm the zooplus Assistant for shop {site_id} — come back anytime "
            "you need help choosing pet products in this catalog."
        )
    if kind == ConvoKind.HELP:
        return (
            f"I'm the zooplus Assistant for shop {site_id} — I can recommend up to four products "
            'in plain language (e.g. "sensitive puppy dry food" or "cat treats in stock"). '
            "Questions outside pets in this shop I'll answer briefly and point you back to the catalog."
        )
    if kind == ConvoKind.IDENTITY:
        return (
            f"I'm the zooplus Assistant for shop {site_id}. "
            "I only use this shop's product data — dog and cat food, treats, litter, toys, and similar. "
            "I'm not a general chatbot: no weather, traffic, or web search. "
            "Ask me what you'd like to buy for your pet and I'll suggest a few options."
        )
    return ""


_SOCIAL_KIND_TO_CONVO: dict[str, ConvoKind] = {
    "greeting": ConvoKind.GREETING,
    "identity": ConvoKind.IDENTITY,
    "thanks": ConvoKind.THANKS,
    "help": ConvoKind.HELP,
    "bye": ConvoKind.BYE,
}


def conversational_reply(
    query: str,
    site_id: int,
    *,
    settings: Settings | None = None,
    social_kind: str | None = None,
) -> str:
    """Polite short reply for greetings/thanks/help — optional OpenCode polish."""
    cfg = settings or apply_settings()
    kind = _SOCIAL_KIND_TO_CONVO.get(social_kind or "", classify_conversation(query))
    fallback = _template_reply(kind, site_id)
    if not fallback:
        return ""

    social_mode = os.environ.get("ZOOPLUS_SOCIAL_SYNTHESIS", "template").lower()
    if social_mode != "opencode" or (cfg.synthesis_mode or "").lower() != "opencode":
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
