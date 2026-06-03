# Agent flows & prompts

**Status:** DONE — implemented T3–T5 (see trace + `.opencode/agents/`)  
**Proposal reference:** [`plans/PROPOSAL.md`](plans/PROPOSAL.md) §9, §18

---

## Flows (to document)

| Flow | Description | Trace |
|------|-------------|-------|
| A | Discovery + clarifying question | T5 |
| B | Nutrition / ingredients | T5 |
| C | Off-topic polite decline | T4 |

---

## Prompt sources

- `.opencode/agents/*.md` (source of truth when created)
- Mirrored under `src/agents/prompts/` (when created)

**Evidence:** `trace/T3-opencode-mcp-agents.md`
