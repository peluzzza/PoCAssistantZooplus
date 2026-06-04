"""Social E2E — oracle intent + agentic social (mocked agents when OpenCode unavailable)."""

from __future__ import annotations

import pytest


def _matrix_social_agent_stub(query: str, site_id: int, ctx: str, *, settings) -> str:
    """Simulates zooplus-social-agent interpretation for deterministic matrix (no script tree)."""
    q = query.lower()
    if "decline_off_topic" in ctx or "lane=decline" in ctx.lower():
        if any(w in q for w in ("internet", "browse the web", "web for", "search online", "google")):
            return (
                "I'm the zooplus Assistant — I only use this shop's product catalog, not the internet. "
                "Ask about dog or cat products here."
            )
        return (
            "I'm the zooplus Assistant — I can't help with that topic. "
            "This shop's catalog is for dog and cat products only."
        )
    if any(w in q for w in ("traffic", "weather", "wetter", "news", "president", "time is it")):
        return (
            "I'm the zooplus Assistant — I can't help with that. "
            "This shop's catalog is for dog and cat products only."
        )
    if any(w in q for w in ("thank", "danke", "gracias")):
        return "You're welcome! I'm the zooplus Assistant — happy to suggest more pet products."
    if any(w in q for w in ("who are you", "who is this", "introduce", "quién eres", "what are you")):
        return (
            f"I'm the zooplus Assistant for shop {site_id} — "
            "I help with dog and cat food, treats, and accessories from this catalog."
        )
    if any(w in q for w in ("service", "provide", "offer", "capabilities", "help me understand")):
        return (
            f"I'm the zooplus Assistant for shop {site_id}. "
            "Describe what you need in plain language and I'll find up to four products."
        )
    if any(w in q for w in ("bye", "goodbye", "see you", "adios", "hasta")):
        return "Take care! zooplus Assistant here whenever you need pet product help."
    return (
        f"Hi! I'm the zooplus Assistant for shop {site_id}. "
        "What dog or cat product can I help you find?"
    )


@pytest.fixture(autouse=True)
def _agentic_social_matrix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOPLUS_INTENT_MODE", "oracle")
    monkeypatch.setenv("ZOOPLUS_SYNTHESIS_MODE", "template")
    monkeypatch.setenv("ZOOPLUS_SOCIAL_SYNTHESIS", "agentic")
    monkeypatch.setenv("ZOOPLUS_AGENT_CASCADE", "0")
    monkeypatch.setattr(
        "src.agents.social_agent._run_social_agents",
        _matrix_social_agent_stub,
    )
