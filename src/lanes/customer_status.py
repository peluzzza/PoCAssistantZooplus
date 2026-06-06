"""Customer-facing status copy — generic phases + agent shopper_status (no hard-coded species)."""

from __future__ import annotations

MAX_STATUS_MESSAGES = 5

_PHASE_COPY = {
    "reading": "Let me read what you're looking for…",
    "searching": "I'm browsing this shop for good matches…",
    "narrowing": "Narrowing down the best options…",
    "composing": "Almost ready with your answer…",
    "composing_social": "Writing my reply…",
    "composing_decline": "I'll explain what I can help with…",
    "reading_social": "Thanks for your message — give me a second.",
}


def phases_for_lane(lane: str) -> list[str]:
    """Ordered phase ids emitted for a lane (1–5)."""
    if lane == "catalog_search":
        return ["reading", "understood", "searching", "narrowing", "composing"]
    if lane == "conversational":
        return ["reading", "composing"]
    if lane == "decline_off_topic":
        return ["reading", "understood", "composing"]
    return ["reading", "composing"]


def status_message(
    phase: str,
    *,
    lane: str,
    shopper_status: str | None = None,
) -> str:
    """Non-technical English status line — agent summary preferred on 'understood'."""
    if phase == "understood":
        if shopper_status:
            return shopper_status
        return "Got your request…"
    if phase == "reading" and lane == "conversational":
        return _PHASE_COPY["reading_social"]
    if phase == "composing":
        if lane == "decline_off_topic":
            return _PHASE_COPY["composing_decline"]
        if lane == "conversational":
            return _PHASE_COPY["composing_social"]
        return _PHASE_COPY["composing"]
    return _PHASE_COPY.get(phase, "One moment…")


def status_event(
    phase: str,
    *,
    lane: str,
    shopper_status: str | None = None,
) -> dict:
    return {
        "type": "status",
        "phase": phase,
        "text": status_message(phase, lane=lane, shopper_status=shopper_status),
    }
