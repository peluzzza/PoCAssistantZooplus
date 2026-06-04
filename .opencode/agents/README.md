# OpenCode agents — zooplus PoC

**Source of truth:** `docs/instructions/AGENT_BUNDLE.md` (read first).

| Agent | Role |
|-------|------|
| `zooplus-conductor` | Primary orchestrator |
| `zooplus-intent-agent` | Agentic default-deny routing |
| `zooplus-social-agent` | Greeting, identity, decline (no RAG) |
| `zooplus-topic-guard` | MCP compat / legacy alias |
| `zooplus-rag-worker` | Site-scoped retrieval |
| `zooplus-logic-worker` | Rank + cap 4 |
| `zooplus-synthesis` | Natural grounded answer |
| `zooplus-rag-pipeline` | Offline ingest only |

Python runtime mirrors intent/social: `src/agents/intent_agent.py`, `src/agents/social_agent.py`.
