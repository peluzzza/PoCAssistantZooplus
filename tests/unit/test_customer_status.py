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


def test_catalog_status_mentions_price_band() -> None:
    text = status_message(
        "understood",
        lane="catalog_search",
        query="dog food between 20 and 30 €",
    )
    assert "20" in text and "30" in text
    assert "dog" in text.lower()


def test_social_lane_short_phases() -> None:
    phases = phases_for_lane("conversational")
    assert phases == ["reading", "composing"]
    assert "searching" not in phases


def test_decline_understood_message() -> None:
    text = status_message(
        "understood",
        lane="decline_off_topic",
        query="what is the weather?",
    )
    assert "outside" in text.lower()
