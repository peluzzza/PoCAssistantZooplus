"""Customer-facing status copy — tied to real orchestration phases (English UI)."""

from __future__ import annotations

import re

from src.rag.price_filter import parse_eur_price_range

MAX_STATUS_MESSAGES = 5

_PET_LABEL = (
    (re.compile(r"\b(pupp(?:y|ies))\b", re.I), "puppy"),
    (re.compile(r"\b(kitt(?:en|ens))\b", re.I), "kitten"),
    (re.compile(r"\b(perros?)\b", re.I), "dog"),
    (re.compile(r"\b(gatos?)\b", re.I), "cat"),
    (re.compile(r"\bdogs?\b", re.I), "dog"),
    (re.compile(r"\bcats?\b", re.I), "cat"),
)

_PRODUCT_LABEL = (
    (re.compile(r"\b(treats?|snacks?)\b", re.I), "treats"),
    (re.compile(r"\b(food|comida|alimento|futter|nourriture)\b", re.I), "food"),
    (re.compile(r"\b(toys?)\b", re.I), "toys"),
    (re.compile(r"\b(litter)\b", re.I), "litter"),
)


def phases_for_lane(lane: str) -> list[str]:
    """Ordered phase ids emitted for a lane (1–5)."""
    if lane == "catalog_search":
        return ["reading", "understood", "searching", "narrowing", "composing"]
    if lane == "conversational":
        return ["reading", "composing"]
    if lane == "decline_off_topic":
        return ["reading", "understood", "composing"]
    return ["reading", "composing"]


def _pet_product_hint(query: str) -> str:
    text = (query or "").strip()
    pet = "pet"
    for pattern, label in _PET_LABEL:
        if pattern.search(text):
            pet = label
            break
    product = "products"
    for pattern, label in _PRODUCT_LABEL:
        if pattern.search(text):
            product = label
            break
    if product == "products" and pet != "pet":
        return f"{pet} products"
    if pet == "pet":
        return product
    return f"{pet} {product}"


def _price_hint(query: str) -> str | None:
    band = parse_eur_price_range(query)
    if not band:
        return None
    lo, hi = band
    lo_s = f"{lo:g}"
    hi_s = f"{hi:g}"
    return f"around {lo_s}–{hi_s} €"


def status_message(phase: str, *, lane: str, query: str) -> str:
    """Non-technical English status line for one orchestration phase."""
    hint = _pet_product_hint(query)
    price = _price_hint(query)

    if phase == "reading":
        if lane == "conversational":
            return "Thanks for your message — give me a second."
        return "Let me read what you're looking for…"

    if phase == "understood":
        if lane == "decline_off_topic":
            return "I see — that's a bit outside what I cover here."
        if lane == "catalog_search":
            if price:
                return f"Got it — {hint} {price}."
            return f"Got it — you're after {hint}."
        return "Understood."

    if phase == "searching":
        return "I'm browsing this shop for good matches…"

    if phase == "narrowing":
        if price:
            return "Narrowing to options in your price range…"
        return "Picking a few that fit nicely…"

    if phase == "composing":
        if lane == "decline_off_topic":
            return "I'll explain what I can help with…"
        if lane == "conversational":
            return "Writing my reply…"
        return "Almost ready with a short list for you…"

    return "One moment…"


def status_event(phase: str, *, lane: str, query: str) -> dict:
    return {
        "type": "status",
        "phase": phase,
        "text": status_message(phase, lane=lane, query=query),
    }
