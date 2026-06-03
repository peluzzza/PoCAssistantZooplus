# PoC progress dashboard

**Last updated:** 2026-06-03 (Zeus / Composer)  
**Repo root:** `d:\temp\review_clones\PoC chatbot zooplus\` (**only** location for this PoC)  
**Current phase:** P6 done — T3 to T6 implemented  
**Current step:** v2.0.0 production profile released on `main`  
**Git:** `main` tag `v2.0.0`  

---

## Phase overview

| Phase | Name | Status | Complete artifact |
|-------|------|--------|-------------------|
| P0 | Bootstrap repo + docs trace | **DONE** | [`phases/P0-bootstrap-complete.md`](phases/P0-bootstrap-complete.md) |
| P1 | EDA + constraints | **DONE** (EDA) | `trace/T1-eda-run.md` |
| P2 | RAG index | **DONE** | `trace/T2-rag-index.md`, `phases/P2-rag-index-complete.md` |
| P3 | OpenCode agents + MCP on server | **DONE** | `trace/T3-opencode-mcp-agents.md` |
| P4 | Dual-lane + ACP | **DONE** | `trace/T4-dual-lane-acp.md` |
| P5 | Async `/chat` + tests | **DONE** | `trace/T5-api-contract.md` |
| P6 | README + submission | **DONE** | `trace/T6-readme-submission.md` |

---

## Step checklist (brief gates)

| Gate | Description | Status |
|------|-------------|--------|
| G0 | Trace journal structure exists | **DONE** |
| G0b | All code under PoC folder only | **DONE** |
| G0c | Quality gates (Ruff + 38 tests) local + CI | **DONE** |
| G1 | Topic guard p95 < 300ms | **DONE** (`scripts/topic_guard_load_test.py`) |
| G2 | Zero cross-`site_id` retrieval | **DONE** (T2 tests) |
| G3 | MCP tools on server | **DONE** |
| G4 | ACP receipt per `/chat` | **DONE** |
| G5 | Answers grounded in `retrieved_products` | **DONE** |
| G6 | Off-topic → polite decline | **DONE** |

---

## Latest session

| Date | Log |
|------|-----|
| 2026-06-03 | [`sessions/2026-06-03-T01-canonical-root-relocate.md`](sessions/2026-06-03-T01-canonical-root-relocate.md) |
| 2026-06-03 | [`sessions/2026-06-03-T00-zeus-trace-scaffold.md`](sessions/2026-06-03-T00-zeus-trace-scaffold.md) |
| 2026-06-03 | [`sessions/2026-06-03-T04-zeus-quality-gates-run.md`](sessions/2026-06-03-T04-zeus-quality-gates-run.md) |
| 2026-06-03 | [`sessions/2026-06-03-T05-T3-T6-implementation.md`](sessions/2026-06-03-T05-T3-T6-implementation.md) |
| 2026-06-03 | [`sessions/2026-06-03-release-v1.0.0.md`](sessions/2026-06-03-release-v1.0.0.md) |
| 2026-06-03 | [`sessions/2026-06-03-release-v1.1.0.md`](sessions/2026-06-03-release-v1.1.0.md) |
| 2026-06-03 | [`sessions/2026-06-03-release-v1.2.0.md`](sessions/2026-06-03-release-v1.2.0.md) |

---

## Next actions

1. PoC plan complete through v2.0.0 — optional hardening (Sonar token, hosted Chroma).
2. Optional: `SONAR_TOKEN` for SonarCloud.
3. Production hardening per README roadmap.
