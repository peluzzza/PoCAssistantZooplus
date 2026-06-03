# Brief alignment checklist (Coding Task)

**Source:** `instructions/Coding Task.docx`  
**Updated:** 2026-06-03  

Mark each row when evidence exists in `trace/` or tests.

| ID | Requirement | Trace step | Status | Evidence link |
|----|-------------|------------|--------|---------------|
| B1 | Async FastAPI backend | T5 | PENDING | — |
| B2 | `POST /chat` `{ site_id, query }` | T5 | PENDING | — |
| B3 | Response `{ answer, retrieved_products }` | T5 | PENDING | — |
| B4 | RAG — knowledge only from dataset | T2, T5 | PENDING | — |
| B5 | `site_id` shop scoping | T2, T5 | PENDING | — |
| B6 | Guardrails — pet products only | T3, T4, T5 | PENDING | — |
| B7 | Production-oriented structure | T0, T6 | IN_PROGRESS | `cli/`, `src/`, `.opencode/` at repo root |
| B8 | Git repo + README | T6 | PENDING | — |
| B9 | Evaluation: rigor, RAG, data, trade-offs | T1–T6 | IN_PROGRESS | `trace/PROGRESS.md` |

---

## PoC extensions (proposal v2 — not in brief but traced)

| ID | Extension | Trace step | Status |
|----|-----------|------------|--------|
| X1 | Dual-lane latency | T4 | PENDING |
| X2 | MCP on server | T3 | PENDING |
| X3 | ACP dispatch | T4 | PENDING |
| X4 | `.opencode/agents` | T3 | PENDING |
