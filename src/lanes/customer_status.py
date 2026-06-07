"""Customer-facing status copy — generic phases + agent shopper_status (no hard-coded species)."""

from __future__ import annotations

MAX_STATUS_MESSAGES = 7

_PHASE_COPY = {
    "received": "Thanks — I'll take a look and help you with that.",
    "reading": "Let me read what you're looking for…",
    "searching": "I'm browsing this shop for good matches…",
    "found": "I found some options — picking the best fits for you…",
    "found_empty": "I didn't spot a perfect match yet — I'll still try to suggest something close.",
    "narrowing": "Narrowing it down to my top recommendations…",
    "composing": "Almost ready — putting together your answer…",
    "composing_social": "Writing my reply…",
    "composing_decline": "I'll explain what I can help with…",
    "reading_social": "Thanks for your message — give me a second.",
}


def phases_for_lane(lane: str) -> list[str]:
    """Ordered phase ids emitted for a lane (1–7)."""
    if lane == "catalog_search":
        return [
            "received",
            "understood",
            "searching",
            "found",
            "narrowing",
            "composing",
        ]
    if lane == "conversational":
        return ["received", "composing"]
    if lane == "decline_off_topic":
        return ["received", "understood", "composing"]
    return ["received", "composing"]


def status_message(
    phase: str,
    *,
    lane: str,
    shopper_status: str | None = None,
    hit_count: int | None = None,
) -> str:
    """Non-technical English status line — agent summary preferred on 'understood'."""
    if phase == "understood":
        if shopper_status:
            return shopper_status
        if lane == "catalog_search":
            return "Got it — I'll search our catalog for you."
        return "Got your request…"
    if phase == "found":
        if hit_count is not None and hit_count <= 0:
            return _PHASE_COPY["found_empty"]
        return _PHASE_COPY["found"]
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
    hit_count: int | None = None,
) -> dict:
    return {
        "type": "status",
        "phase": phase,
        "text": status_message(
            phase,
            lane=lane,
            shopper_status=shopper_status,
            hit_count=hit_count,
        ),
    }
