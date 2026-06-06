"""Unit tests — shopper answer normalization."""

import pytest
from src.llm.answer_sanitize import normalize_shopper_answer

pytestmark = pytest.mark.unit


def test_strips_json_answer_wrapper() -> None:
    raw = '{"answer": "Hello from the shop."}'
    assert normalize_shopper_answer(raw) == "Hello from the shop."


def test_strips_fenced_json() -> None:
    raw = '```json\n{"answer": "Plain text."}\n```'
    assert normalize_shopper_answer(raw) == "Plain text."


def test_plain_prose_unchanged() -> None:
    assert normalize_shopper_answer("Sure! Here are cat treats.") == "Sure! Here are cat treats."
