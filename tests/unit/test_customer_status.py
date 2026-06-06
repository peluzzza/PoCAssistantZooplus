"""Unit tests — customer-facing status copy."""

from __future__ import annotations

from src.lanes.customer_status import (
    MAX_STATUS_MESSAGES,
    phases_for_lane,
    status_message,
)


def test_phases_for_catalog_lane() -> None:
    phases = phases_for_lane("catalog_search")
    assert phases[0] == "reading"
    assert "searching" in phases
    assert len(phases) <= MAX_STATUS_MESSAGES


def test_understood_uses_agent_shopper_status() -> None:
    text = status_message(
        "understood",
        lane="catalog_search",
        shopper_status="Cat food options in a 40–60 € range.",
    )
    assert "40" in text and "60" in text
    assert "gato" not in text.lower()


def test_understood_without_agent_status_falls_back_to_phase_copy() -> None:
    text = status_message("understood", lane="catalog_search", shopper_status=None)
    assert text == "Got your request…"


def test_social_lane_short_phases() -> None:
    phases = phases_for_lane("conversational")
    assert phases == ["reading", "composing"]
    assert "searching" not in phases


def test_decline_composing_generic() -> None:
    text = status_message("composing", lane="decline_off_topic")
    assert "help" in text.lower()
