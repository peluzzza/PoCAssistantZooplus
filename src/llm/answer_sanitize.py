"""Strip accidental JSON / markdown wrappers from LLM answer text."""

from __future__ import annotations

import json
import re

_JSON_ANSWER = re.compile(
    r'^\s*\{\s*"answer"\s*:\s*"(?P<body>(?:\\.|[^"\\])*)"\s*\}\s*$',
    re.DOTALL,
)
_FENCED_JSON = re.compile(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE)
_TOOL_EVENT = re.compile(r'"type"\s*:\s*"tool_', re.IGNORECASE)
_INTERNAL_EVENT_TYPES = frozenset(
    {"tool_use", "tool_result", "tool_call", "tool_output", "step", "thinking"}
)


def _unescape_json_string(s: str) -> str:
    try:
        return json.loads(f'"{s}"')
    except json.JSONDecodeError:
        return s.replace('\\"', '"').replace("\\n", "\n")


def extract_opencode_stdout(text: str) -> str:
    """Keep shopper-facing text from OpenCode --format json stdout; drop tool events."""
    if not text or not text.strip():
        return ""
    parts: list[str] = []
    saw_tool = False
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            if not line.startswith("{") and not _TOOL_EVENT.search(line):
                parts.append(line)
            continue
        if not isinstance(event, dict):
            continue
        etype = str(event.get("type") or "")
        if etype in _INTERNAL_EVENT_TYPES or etype.startswith("tool"):
            saw_tool = True
            continue
        if etype == "text":
            part = event.get("part", {})
            if isinstance(part, dict) and part.get("text"):
                parts.append(str(part["text"]))
        elif isinstance(event.get("text"), str):
            parts.append(str(event["text"]))
    joined = "".join(parts).strip()
    if joined:
        return joined
    if saw_tool or _TOOL_EVENT.search(text):
        return ""
    return ""


def normalize_shopper_answer(text: str | None) -> str:
    """Return plain prose for the chat UI (never raw JSON blobs)."""
    if not text:
        return ""
    raw = text.strip()
    if not raw:
        return ""

    if _TOOL_EVENT.search(raw) or (raw.count('{"type"') > 1 and raw.startswith("{")):
        extracted = extract_opencode_stdout(raw)
        if not extracted:
            return ""
        raw = extracted

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
