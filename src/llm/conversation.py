"""Conversation hints — classify social shape only; replies come from OpenCode agents."""

from __future__ import annotations

import re
from enum import StrEnum


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
    r"\b("
    r"help\s+me\s+understand|what\s+you\s+offer|what\s+can\s+you\s+do\s+for\s+me|"
    r"your\s+services?|what\s+can\s+you\s+tell\s+me|about\s+your|capabilities"
    r")\b",
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

_KIND_MAP: dict[ConvoKind, str] = {
    ConvoKind.GREETING: "greeting",
    ConvoKind.IDENTITY: "identity",
    ConvoKind.THANKS: "thanks",
    ConvoKind.HELP: "help",
    ConvoKind.BYE: "bye",
}


def classify_conversation(query: str) -> ConvoKind:
    """Lightweight hint when intent agent did not set social_kind (fallback paths only)."""
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
    return ConvoKind.PRODUCT


def is_conversational_only(query: str) -> bool:
    return classify_conversation(query) != ConvoKind.PRODUCT


def social_kind_hint(query: str, *, intent_social_kind: str | None = None) -> str:
    """Prefer intent agent social_kind; regex hint only when missing."""
    if intent_social_kind:
        return intent_social_kind
    conv = classify_conversation(query)
    return _KIND_MAP.get(conv, "greeting")


def emergency_social_fallback(site_id: int) -> str:
    """Last resort when OpenCode social agents are unavailable (not a scripted dialog tree)."""
    return (
        f"I'm the zooplus Assistant for shop {site_id}. "
        "Social agents are temporarily unavailable — please retry, or ask about dog or cat products in this catalog."
    )
