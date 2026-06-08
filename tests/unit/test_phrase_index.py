"""Unit tests — YAML social phrase index."""

from __future__ import annotations

import pytest
from src.agents.phrase_index import (
    classify_social_kind,
    index_stats,
    match_social_help,
    phrase_categories,
)

pytestmark = pytest.mark.unit


def test_index_loads_categories() -> None:
    cats = phrase_categories()
    assert "greeting" in cats
    assert "help" in cats
    assert index_stats()["total_seed_phrases"] >= 50


def test_match_help_spanish() -> None:
    assert match_social_help("me puedes ayudar")
    assert classify_social_kind("me puedes ayudar") == "help"


def test_match_greeting_multilingual() -> None:
    assert classify_social_kind("hola que tal") == "greeting"
    assert classify_social_kind("bonjour") == "greeting"
    assert classify_social_kind("guten tag") == "greeting"


def test_catalog_query_not_social() -> None:
    assert classify_social_kind("best dry food for puppy") is None
