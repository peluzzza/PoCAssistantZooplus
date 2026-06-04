"""Constraint-driven topic guard and response policy helpers."""

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

OFF_TOPIC_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bweather\b", re.IGNORECASE), "off_topic_weather"),
    (re.compile(r"\b(time|datetime|date)\b", re.IGNORECASE), "off_topic_datetime"),
    (re.compile(r"\bnews\b", re.IGNORECASE), "off_topic_news"),
    (
        re.compile(
            r"\b(who is|what is|capital of|history of|election|president|prime minister)\b",
            re.IGNORECASE,
        ),
        "off_topic_general_knowledge",
    ),
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
    ),
]

EXTERNAL_WEB_DECLINE = (
    "I'm the zooplus Assistant and can only use this shop's product catalog — "
    "I can't search the internet. Ask me about pet food, treats, or accessories "
    "available in your shop and I'll recommend options from our data."
)


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


def topic_check(query: str) -> TopicDecision:
    for pattern, reason_code in OFF_TOPIC_PATTERNS:
        if pattern.search(query):
            decline = DEFAULT_DECLINE
            if reason_code == "off_topic_external_web":
                decline = EXTERNAL_WEB_DECLINE
            return TopicDecision(
                decision="DECLINE",
                reason_code=reason_code,
                polite_decline=decline,
            )
    return TopicDecision(decision="ALLOW", reason_code="in_scope_pet_catalog", polite_decline=None)
