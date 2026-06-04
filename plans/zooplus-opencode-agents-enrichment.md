# Plan — OpenCode agents enrichment (Zeus / v2.4.1)

**Goal:** Agentic-first `.opencode/agents` aligned with `docs/instructions` + CUX best practices.

## Phase 1 — Source bundle ✅

- `docs/instructions/AGENT_BUNDLE.md` (sections A–G)
- Cross-ref: `ACCEPTANCE.md`, `constraints.yaml`, `AGENTIC_SOCIAL.md`

## Phase 2 — Agent rewrite ✅

| Agent | Change |
|-------|--------|
| `zooplus-intent-agent` | **New** — default-deny JSON router |
| `zooplus-social-agent` | **New** — sociable lane, no RAG |
| `zooplus-conductor` | Agentic pipeline order |
| `zooplus-topic-guard` | Compat + bundle ref |
| `zooplus-rag-worker` | B4/B5 grounding rules |
| `zooplus-logic-worker` | P1 cap + ranking |
| `zooplus-synthesis` | CUX prose, anti-template |
| `zooplus-rag-pipeline` | Offline-only scope |

## Phase 3 — Wiring ✅

- `opencode.json` permissions for new agents
- `src/agents/prompts.py` synced with bundle
- `social_agent.py` decline context

## Phase 4 — Verify

```bash
python -m pytest tests/agentic tests/social -q
# OpenCode: opencode run with zooplus-conductor (API on :8080)
```

## References (external CUX)

- Microsoft Copilot CUX principles (persona, chit-chat, emotional acknowledgment)
- ServiceNow Horizon conversation design (tone per situation)
- Wharton effective chatbots (transparency, interjections, competence over gimmicks)
