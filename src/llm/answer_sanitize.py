"""Strip accidental JSON / markdown wrappers from LLM answer text."""

from __future__ import annotations

import json
import re

_JSON_ANSWER = re.compile(
    r'^\s*\{\s*"answer"\s*:\s*"(?P<body>(?:\\.|[^"\\])*)"\s*\}\s*$',
    re.DOTALL,
)
_FENCED_JSON = re.compile(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE)


def _unescape_json_string(s: str) -> str:
    try:
        return json.loads(f'"{s}"')
    except json.JSONDecodeError:
        return s.replace('\\"', '"').replace("\\n", "\n")


def normalize_shopper_answer(text: str | None) -> str:
    """Return plain prose for the chat UI (never raw JSON blobs)."""
    if not text:
        return ""
    raw = text.strip()
    if not raw:
        return ""

    fenced = _FENCED_JSON.search(raw)
    if fenced:
        raw = fenced.group(1).strip()

    if raw.startswith("{"):
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                if isinstance(data.get("answer"), str):
                    return data["answer"].strip()
                if isinstance(data.get("text"), str):
                    return data["text"].strip()
        except json.JSONDecodeError:
            pass
        m = _JSON_ANSWER.match(raw)
        if m:
            return _unescape_json_string(m.group("body")).strip()

    return raw
