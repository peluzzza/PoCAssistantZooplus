# Brief alignment checklist (Coding Task)

**Source:** `instructions/Coding Task.docx`  
**Updated:** 2026-06-03 (T3–T6 complete on `dev`)

Mark each row when evidence exists in `trace/` or tests.

| ID | Requirement | Trace step | Status | Evidence link |
|----|-------------|------------|--------|---------------|
| B1 | Async FastAPI backend | T5 | **DONE** | `src/api/app.py`, `async def chat` |
| B2 | `POST /chat` `{ site_id, query }` | T5 | **DONE** | `src/api/routes/chat.py`, `tests/integration/test_api.py` |
| B3 | Response `{ answer, retrieved_products }` | T5 | **DONE** | `src/models/chat.py` |
| B4 | RAG — knowledge only from dataset | T2, T5 | **DONE** | `src/rag/`, `src/lanes/process.py` |
| B5 | `site_id` shop scoping | T2, T5 | **DONE** | `tests/integration/test_rag_retrieval.py` |
| B6 | Guardrails — pet products only | T3–T5 | **DONE** | `src/guardian/engine.py`, `tests/unit/test_topic_guard.py` |
| B7 | Production-oriented structure | T0, T6 | **DONE** | `cli/`, `src/`, `.opencode/` |
| B8 | Git repo + README | T6 | **DONE** | `README.md`, GitHub remote |
| B9 | Evaluation: rigor, RAG, data, trade-offs | T1–T6 | **DONE** | `docs/trace/`, `docs/01-eda-report.md` |

---

## PoC extensions (proposal v2 — not in brief but traced)

| ID | Extension | Trace step | Status |
|----|-----------|------------|--------|
| X1 | Dual-lane latency | T4 | **DONE** |
| X2 | MCP on server | T3 | **DONE** |
| X3 | ACP dispatch | T4 | **DONE** |
| X4 | `.opencode/agents` | T3 | **DONE** |

---

## Pending for production (not blocking PoC)

| Item | Notes |
|------|-------|
| G1 p95 topic guard < 300ms | Rule-based guard is fast; no load test artifact yet |
| Merge `dev` → `main` | Requires explicit user authorization |
| `SONAR_TOKEN` | Optional SonarCloud import |
