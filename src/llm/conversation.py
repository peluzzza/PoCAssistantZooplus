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


def _template_reply(kind: ConvoKind, site_id: int, *, query: str = "") -> str:
    from src.llm.response_variety import pick_variant, style_seed

    key = style_seed(query or str(site_id), kind.value, str(site_id))
    if kind == ConvoKind.GREETING:
        return pick_variant(
            key,
            (
                f"Hello! I help shoppers on site {site_id} pick dog and cat food, treats, and accessories. "
                "What should we look for first — puppy kibble, grain-free cat food, something else?",
                f"Hi — welcome to shop {site_id}. Tell me your pet (dog or cat) and what you need; "
                "I'll suggest a few items from this catalog.",
                "Hey there! I'm here to narrow down pet products in plain language. "
                "Dry food, treats, toys — what are you after?",
            ),
        )
    if kind == ConvoKind.THANKS:
        return pick_variant(
            key,
            (
                "Glad that helped! If you want more ideas, mention brand, budget, or dog vs cat.",
                "You're welcome — happy to dig deeper anytime. Just say what pet and product type you need.",
                "Anytime! I can refine suggestions with a bit more detail when you're ready.",
            ),
        )
    if kind == ConvoKind.BYE:
        return pick_variant(
            key,
            (
                f"See you later — shop {site_id} is here whenever you need pet product ideas.",
                "Bye for now! Come back with a dog or cat shopping question anytime.",
                "Take care — I'll be here for food, treats, and accessories in this catalog.",
            ),
        )
    if kind == ConvoKind.HELP:
        return pick_variant(
            key,
            (
                f"On site {site_id} I search this catalog in natural language and show up to four matches — "
                'try "grain-free adult cat food" or "dog treats on sale". Off-topic stuff gets a polite redirect.',
                "Ask like you're talking to a shop assistant: describe the pet and product. "
                "I'll return a few grounded picks from our dog/cat data (no web search or weather).",
                "I recommend from this shop's catalog only — dogs and cats. "
                "Describe what you want and I'll surface a short list you can refine.",
            ),
        )
    if kind == ConvoKind.IDENTITY:
        return pick_variant(
            key,
            (
                f"I'm the zooplus Assistant for shop {site_id} — catalog-only, dogs and cats. "
                "No general knowledge or internet; just product help for this store.",
                f"Shop assistant for site {site_id}: I use local product data for dogs and cats "
                "(food, treats, litter, toys). Ask what you'd like to buy.",
                "An AI helper tied to one pet catalog per site — I suggest real SKUs here, "
                "not traffic, news, or human products.",
            ),
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
    fallback = _template_reply(kind, site_id, query=query)
    if not fallback:
        return ""

    social_env = os.environ.get("ZOOPLUS_SOCIAL_SYNTHESIS", "auto").lower()
    synthesis_is_llm = (cfg.synthesis_mode or "").lower() == "opencode"
    use_llm = social_env == "opencode" or (social_env == "auto" and synthesis_is_llm)
    if not use_llm:
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
