# OpenCode agents — zooplus PoC

**Source of truth:** `docs/instructions/AGENT_BUNDLE.md` (read first).

Per-agent LLMs follow the [OpenCode agents docs](https://opencode.ai/docs/agents/): set `model` in `opencode.json` and/or agent markdown frontmatter.

| Agent | Role | Default model |
|-------|------|----------------|
| `zooplus-conductor` | Primary orchestrator (fast) | `opencode/mimo-v2.5-free` |
| `zooplus-intent-agent` | Intent routing | `opencode-go/deepseek-v4-flash` |
| `zooplus-social-agent` | Greeting, identity, decline (flash) | `opencode-go/deepseek-v4-flash` |
| `zooplus-topic-guard` | Topic / quality guard | `opencode-go/minimax-m2.5` |
| `zooplus-rag-worker` | Site-scoped retrieval | `opencode-go/deepseek-v4-flash` |
| `zooplus-logic-worker` | Rank + cap 4 | `opencode-go/qwen3.6-plus` |
| `zooplus-synthesis` | Natural grounded answer | `opencode/deepseek-v4-flash-free` |
| `zooplus-rag-pipeline` | Offline ingest only | (no live `/chat`) |

Runtime config: `.opencode/config-cli/opencode.json` (see `ZOOPLUS_OPENCODE_CONFIG_DIR`).

Override per agent via env: `ZOOPLUS_AGENT_MODEL_ZOOPLUS_SOCIAL_AGENT=...` or role env `ZOOPLUS_SOCIAL_MODEL=...`.

Python mirrors intent/social: `src/agents/intent_agent.py`, `src/agents/social_agent.py`, `src/agents/registry.py`.
