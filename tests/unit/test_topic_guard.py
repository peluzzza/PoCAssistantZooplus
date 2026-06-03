"""Unit tests for topic guard engine."""

import pytest
from src.guardian.engine import max_recommendations, must_ground_in_retrieval, topic_check

pytestmark = pytest.mark.unit


def test_topic_guard_declines_weather_queries() -> None:
    decision = topic_check("what is the weather in berlin?")
    assert decision.decision == "DECLINE"
    assert decision.reason_code == "off_topic_weather"
    assert decision.polite_decline is not None


def test_topic_guard_declines_general_knowledge_queries() -> None:
    decision = topic_check("who is the president of france?")
    assert decision.decision == "DECLINE"
    assert decision.reason_code == "off_topic_general_knowledge"


def test_topic_guard_allows_catalog_queries() -> None:
    decision = topic_check("best dry food for adult dogs")
    assert decision.decision == "ALLOW"
    assert decision.reason_code == "in_scope_pet_catalog"
    assert decision.polite_decline is None


def test_constraints_enforce_recommendation_cap() -> None:
    assert max_recommendations() == 4
    assert must_ground_in_retrieval() is True
