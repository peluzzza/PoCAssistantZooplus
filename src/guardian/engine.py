"""Constraint-driven topic guard — default-deny firewall (allow pet catalog only)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONSTRAINTS_PATH = ROOT / "src" / "guardian" / "constraints.yaml"
DEFAULT_DECLINE = (
    "I'm the zooplus Assistant and can help with pet products for your shop. "
    "I can't help with that topic, but I'd be happy to find food, treats, or "
    "accessories for your dog or cat."
)

# Out-of-catalog consumer / competitor (deny before allow-list — avoids dog+cat token bypass).
_FORBIDDEN_CONSUMER = re.compile(
    r"\b("
    r"humans?|for\s+humans?|people(?:\s+food)?|human\s+food|"
    r"amazon\.com|compare\s+prices\s+on\s+amazon|"
    r"medicine\s+should\s+i\s+take|headache\s+pill|take\s+for\s+my\s+headache|"
    r"cryptocurrency|bitcoin|invest\s+in\s+2026|"
    r"spaghetti\s+carbonara|recipe\s+for\s+(?!dog|cat|pet)|"
    r"hack\s+a\s+website|write\s+python\s+code\s+to\s+hack"
    r")\b",
    re.IGNORECASE,
)

# Hard blocks with tailored copy (security / catalog-only policy).
_POLICY_BLOCKS: list[tuple[re.Pattern[str], str, str | None]] = [
    (
        re.compile(
            r"\b("
            r"search\s+(in\s+)?(the\s+)?internet|internet\s+search|search\s+online|"
            r"browse\s+the\s+web|google\s+it|look\s+up\s+online|web\s+search|"
            r"search\s+the\s+web|use\s+the\s+internet"
            r")\b",
            re.IGNORECASE,
        ),
        "off_topic_external_web",
        None,  # filled below
    ),
    (
        re.compile(
            r"(ignore\s+(all\s+)?(previous|prior)\s+instructions|"
            r"disregard\s+(your\s+)?(rules|instructions)|"
            r"you\s+are\s+now\s+(a|an)|system\s*:\s*|"
            r"<\s*/?\s*system\s*>|jailbreak|DAN\s+mode)",
            re.IGNORECASE,
        ),
        "off_topic_prompt_injection",
        None,
    ),
]

EXTERNAL_WEB_DECLINE = (
    "I'm the zooplus Assistant and can only use this shop's product catalog — "
    "I can't search the internet. Ask me about pet food, treats, or accessories "
    "available in your shop and I'll recommend options from our data."
)

# Allowed scope: dogs/cats catalog shopping (see constraints.yaml allowed_intents).
_PET_ANIMALS = re.compile(
    r"\b("
    r"dogs?|pupp(?:y|ies)|cats?|kitt(?:ens?)|pets?|"
    r"perros?|gatos?|hund(?:e)?|katzen?|welpen?|chats?|chatons?"
    r")\b",
    re.IGNORECASE,
)
_PET_BRANDS = re.compile(
    r"\b("
    r"eukanuba|royal\s+canin|purizon|wild\s+freedom|cosma|chuckit|"
    r"lucky\s+jim|wolf\s+of\s+wilderness|smiileyz|feringa|rocco"
    r")\b",
    re.IGNORECASE,
)
_PET_PRODUCTS = re.compile(
    r"\b("
    r"foods?|treats?|toys?|snacks?|litter|collars?|leashes?|leads?|"
    r"bowls?|beds?|futter|trockenfutter|nassfutter|comida|croquettes?|alimento|"
    r"chew|squeaker|balls?|meatcubies|cubies|accessories?"
    r")\b",
    re.IGNORECASE,
)
_PET_NUTRITION = re.compile(
    r"\b("
    r"ingredients?|feeding|nutrition|recommend(?:ation)?s?|popular|discount|"
    r"stock|grain|sensitive|overweight|veterinary|vet\s+diet|diets?"
    r")\b",
    re.IGNORECASE,
)
# Species outside catalog pet_type (DOGS/CATS only).
_OUT_OF_CATALOG_SPECIES = re.compile(r"\bbird\s+food\b", re.IGNORECASE)


@dataclass(frozen=True)
class TopicDecision:
    decision: str
    reason_code: str
    polite_decline: str | None


@lru_cache(maxsize=1)
def load_constraints() -> dict[str, Any]:
    data = CONSTRAINTS_PATH.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        parsed = yaml.safe_load(data)
        if isinstance(parsed, dict):
            return parsed
    except ModuleNotFoundError:
        pass
    return {
        "response_policy": {
            "max_recommendations": 4,
            "must_ground_in_retrieval": True,
            "empty_retrieval_message": (
                "I couldn't find matching products in this shop. Could you rephrase "
                "or specify dog/cat and product type?"
            ),
        }
    }


def max_recommendations() -> int:
    policy = load_constraints().get("response_policy", {})
    value = policy.get("max_recommendations", 4)
    try:
        return min(max(int(value), 1), 4)
    except (TypeError, ValueError):
        return 4


def empty_retrieval_message() -> str:
    policy = load_constraints().get("response_policy", {})
    message = policy.get("empty_retrieval_message")
    if isinstance(message, str) and message.strip():
        return message.strip()
    return "I couldn't find matching products in this shop. Could you rephrase your request?"


def must_ground_in_retrieval() -> bool:
    policy = load_constraints().get("response_policy", {})
    return bool(policy.get("must_ground_in_retrieval", True))


def _is_conversational_turn(query: str) -> bool:
    from src.llm.conversation import is_conversational_only

    return is_conversational_only(query)


def is_pet_catalog_in_scope(query: str) -> bool:
    """True when the query targets in-catalog dog/cat product assistance."""
    text = query or ""
    if _OUT_OF_CATALOG_SPECIES.search(text):
        return False
    if _PET_ANIMALS.search(text) or _PET_BRANDS.search(text):
        return True
    has_product = bool(_PET_PRODUCTS.search(text))
    has_nutrition = bool(_PET_NUTRITION.search(text))
    if has_product and has_nutrition:
        return True
    if has_product and re.search(
        r"\b(show|find|search|looking|options|best|need|want|recommend)\b",
        text,
        re.IGNORECASE,
    ):
        return True
    return False


def topic_check(query: str) -> TopicDecision:
    """Default-deny: allow only conversational turns or pet-catalog intents."""
    text = (query or "").strip()
    if not text:
        return TopicDecision(
            decision="DECLINE",
            reason_code="out_of_scope_empty",
            polite_decline=DEFAULT_DECLINE,
        )

    if _FORBIDDEN_CONSUMER.search(text):
        return TopicDecision(
            decision="DECLINE",
            reason_code="off_topic_non_pet_consumer",
            polite_decline=DEFAULT_DECLINE,
        )

    for pattern, reason_code, _ in _POLICY_BLOCKS:
        if pattern.search(text):
            decline = DEFAULT_DECLINE
            if reason_code == "off_topic_external_web":
                decline = EXTERNAL_WEB_DECLINE
            return TopicDecision(
                decision="DECLINE",
                reason_code=reason_code,
                polite_decline=decline,
            )

    if _OUT_OF_CATALOG_SPECIES.search(text):
        return TopicDecision(
            decision="DECLINE",
            reason_code="off_topic_non_pet_species",
            polite_decline=DEFAULT_DECLINE,
        )

    if _is_conversational_turn(text):
        return TopicDecision(
            decision="ALLOW",
            reason_code="conversational",
            polite_decline=None,
        )

    if is_pet_catalog_in_scope(text):
        return TopicDecision(
            decision="ALLOW",
            reason_code="in_scope_pet_catalog",
            polite_decline=None,
        )

    return TopicDecision(
        decision="DECLINE",
        reason_code="out_of_scope_default_deny",
        polite_decline=DEFAULT_DECLINE,
    )
