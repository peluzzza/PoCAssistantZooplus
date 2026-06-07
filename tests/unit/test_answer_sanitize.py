"""Unit tests — shopper answer normalization."""

import pytest
from src.llm.answer_sanitize import extract_opencode_stdout, normalize_shopper_answer

pytestmark = pytest.mark.unit


def test_strips_json_answer_wrapper() -> None:
    raw = '{"answer": "Hello from the shop."}'
    assert normalize_shopper_answer(raw) == "Hello from the shop."


def test_strips_fenced_json() -> None:
    raw = '```json\n{"answer": "Plain text."}\n```'
    assert normalize_shopper_answer(raw) == "Plain text."


def test_plain_prose_unchanged() -> None:
    assert normalize_shopper_answer("Sure! Here are cat treats.") == "Sure! Here are cat treats."


def test_strips_opencode_tool_use_ndjson() -> None:
    raw = (
        '{"type":"tool_use","name":"glob","input":{"glob_pattern":"*"}}\n'
        '{"type":"tool_use","name":"glob","output":"zooplus\\\\tests\\\\unit\\\\foo.py"}\n'
    )
    assert extract_opencode_stdout(raw) == ""
    assert normalize_shopper_answer(raw) == ""


def test_keeps_opencode_text_events_only() -> None:
    raw = (
        '{"type":"tool_use","name":"glob"}\n'
        '{"type":"text","part":{"text":"Of course — I will reply in English."}}\n'
    )
    assert extract_opencode_stdout(raw) == "Of course — I will reply in English."
    assert normalize_shopper_answer(raw) == "Of course — I will reply in English."
