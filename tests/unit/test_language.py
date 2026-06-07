"""Unit tests — shopper language resolution."""

import pytest
from src.llm.language import (
    detect_query_language,
    has_strange_characters,
    parse_accept_language,
    resolve_shopper_language,
)

pytestmark = pytest.mark.unit


def test_parse_accept_language_spanish() -> None:
    assert parse_accept_language("es-ES,es;q=0.9,en;q=0.8") == "es"


def test_parse_accept_language_german() -> None:
    assert parse_accept_language("de-DE,de;q=0.9,en;q=0.8") == "de"


def test_detect_spanish_from_query() -> None:
    code, confident = detect_query_language("necesito comida para gatos")
    assert code == "es"
    assert confident is True


def test_detect_english_from_query() -> None:
    code, confident = detect_query_language("write to me in english please")
    assert code == "en"
    assert confident is True


def test_ambiguous_query_uses_accept_language() -> None:
    code, source = resolve_shopper_language("???", "es-ES,es;q=0.9", site_id=3)
    assert code == "es"
    assert source == "accept-language"


def test_strange_chars_use_accept_language() -> None:
    assert has_strange_characters("???###") is True
    code, source = resolve_shopper_language("???###", "es-ES,es;q=0.9", site_id=3)
    assert code == "es"
    assert source == "accept-language"


def test_confident_query_beats_accept_language() -> None:
    code, source = resolve_shopper_language(
        "hello I need dog food",
        "es-ES,es;q=0.9",
        site_id=15,
    )
    assert code == "en"
    assert source == "query"
