"""Per-agent LLM defaults — mirrors OpenCode opencode.json `agent.<id>.model`."""

from __future__ import annotations

# Official OpenCode pattern: fast orchestration, flash intent/social, stronger logic/quality.
AGENT_MODEL_DEFAULTS: dict[str, str] = {
    "zooplus-conductor": "opencode/mimo-v2.5-free",
    "zooplus-intent-agent": "opencode-go/deepseek-v4-flash",
    "zooplus-social-agent": "opencode-go/deepseek-v4-flash",
    "zooplus-topic-guard": "opencode-go/minimax-m2.5",
    "zooplus-rag-worker": "opencode-go/deepseek-v4-flash",
    "zooplus-logic-worker": "opencode-go/qwen3.6-plus",
    "zooplus-synthesis": "opencode/deepseek-v4-flash-free",
}

AGENT_ROLE_BY_ID: dict[str, str] = {
    "zooplus-conductor": "conductor",
    "zooplus-intent-agent": "intent",
    "zooplus-social-agent": "social",
    "zooplus-topic-guard": "intent",
    "zooplus-rag-worker": "synthesis",
    "zooplus-logic-worker": "synthesis",
    "zooplus-synthesis": "synthesis",
}
