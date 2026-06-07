"""Per-agent LLM defaults — mirrors OpenCode opencode.json `agent.<id>.model`."""

from __future__ import annotations

# OpenCode Go speed ladder (official req/5h, https://opencode.ai/docs/go/):
#  1 deepseek-v4-flash 31,650   2 mimo-v2.5 30,100   3 minimax-m2.5 6,300
#  4 qwen3.7-plus 4,300   5 deepseek-v4-pro 3,450   6 minimax-m2.7 3,400
#  7 qwen3.6-plus 3,300   8 mimo-v2.5-pro 3,250   9 kimi-k2.5 1,850 …
# Agents below are assigned rank #1 → #7 by latency sensitivity (social first).
AGENT_MODEL_DEFAULTS: dict[str, str] = {
    "zooplus-social-agent": "opencode-go/deepseek-v4-flash",
    "zooplus-intent-agent": "opencode-go/mimo-v2.5",
    "zooplus-conductor": "opencode-go/minimax-m2.7",
    "zooplus-topic-guard": "opencode-go/qwen3.7-plus",
    "zooplus-rag-worker": "opencode-go/deepseek-v4-pro",
    "zooplus-logic-worker": "opencode-go/minimax-m2.7",
    "zooplus-synthesis": "opencode-go/qwen3.6-plus",
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
