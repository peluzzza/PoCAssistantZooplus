"""Load `.opencode/agents/*.md` bodies for internal OpenCode calls only."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / ".opencode" / "agents"
_FM = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


@lru_cache(maxsize=32)
def load_agent_body(agent_id: str) -> str:
    path = AGENTS_DIR / f"{agent_id}.md"
    if not path.is_file():
        return ""
    return _FM.sub("", path.read_text(encoding="utf-8"), count=1).strip()


def wrap_prompt_with_agent(agent_id: str, task: str) -> str:
    body = load_agent_body(agent_id)
    return (
        f"{body}\n\n---\nTurn task:\n{task}\n\n"
        "Reply to the customer as zooplus Assistant. Do not mention internal roles."
    )
