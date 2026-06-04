"""Interactive lane — agentic intent classification."""

from __future__ import annotations

import asyncio

from src.agents.intent_agent import IntentDecision, classify_intent
from src.guardian.engine import TopicDecision


def intent_to_topic_decision(intent: IntentDecision) -> TopicDecision:
    if intent.lane == "decline_off_topic":
        return TopicDecision(
            decision="DECLINE",
            reason_code=intent.reason or "agent_decline",
            polite_decline=intent.decline_message,
        )
    reason = "conversational" if intent.lane == "conversational" else "in_scope_pet_catalog"
    return TopicDecision(decision="ALLOW", reason_code=reason, polite_decline=None)


async def run_topic_guard(query: str, site_id: int = 3) -> TopicDecision:
    intent = await asyncio.to_thread(classify_intent, query, site_id)
    return intent_to_topic_decision(intent)
