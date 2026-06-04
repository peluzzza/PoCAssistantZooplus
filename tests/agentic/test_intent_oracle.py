"""Agentic intent oracle coverage (instructions-derived)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from src.agents.intent_agent import classify_intent

pytestmark = [pytest.mark.agentic, pytest.mark.unit]

ORACLE = Path(__file__).resolve().parents[1] / "fixtures" / "intent_oracle.json"
MATRIX = Path(__file__).resolve().parents[1] / "fixtures" / "use_cases_matrix.json"


def test_oracle_has_100_plus_entries() -> None:
    data = json.loads(ORACLE.read_text(encoding="utf-8"))
    assert len(data) >= 100


@pytest.mark.parametrize(
    "query,expected_lane",
    [
        ("hello, who are you", "conversational"),
        ("how it the traffic today", "decline_off_topic"),
        ("best dry food for puppy", "catalog_search"),
        ("what about for humans", "decline_off_topic"),
    ],
)
def test_oracle_routes_key_social_cases(query: str, expected_lane: str) -> None:
    decision = classify_intent(query, 3)
    assert decision.lane == expected_lane
    assert decision.source == "oracle"


def test_matrix_cases_all_in_oracle() -> None:
    cases = json.loads(MATRIX.read_text(encoding="utf-8"))
    oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
    missing = [c["id"] for c in cases if c["query"].strip().lower() not in oracle]
    assert not missing, f"oracle missing: {missing[:5]}"
