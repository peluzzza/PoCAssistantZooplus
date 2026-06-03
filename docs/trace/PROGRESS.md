# PoC progress dashboard

**Last updated:** 2026-06-03 (Zeus / Composer)  
**Repo root:** `d:\temp\review_clones\PoC chatbot zooplus\` (**only** location for this PoC)  
**Current phase:** P0 — bootstrap  
**Current step:** T0 — repo scaffold **DONE** → T1 EDA next  

---

## Phase overview

| Phase | Name | Status | Complete artifact |
|-------|------|--------|-------------------|
| P0 | Bootstrap repo + docs trace | **DONE** | [`phases/P0-bootstrap-complete.md`](phases/P0-bootstrap-complete.md) |
| P1 | EDA + constraints | PENDING | — |
| P2 | RAG index | PENDING | — |
| P3 | OpenCode agents + MCP on server | PENDING | — |
| P4 | Dual-lane + ACP | PENDING | — |
| P5 | Async `/chat` + tests | PENDING | — |
| P6 | README + submission | PENDING | — |

---

## Step checklist (brief gates)

| Gate | Description | Status |
|------|-------------|--------|
| G0 | Trace journal structure exists | **DONE** |
| G0b | All code under PoC folder only | **DONE** |
| G1 | Topic guard p95 < 300ms | PENDING |
| G2 | Zero cross-`site_id` retrieval | PENDING |
| G3 | MCP tools on server | PENDING |
| G4 | ACP receipt per `/chat` | PENDING |
| G5 | Answers grounded in `retrieved_products` | PENDING |
| G6 | Off-topic → polite decline | PENDING |

---

## Latest session

| Date | Log |
|------|-----|
| 2026-06-03 | [`sessions/2026-06-03-T01-canonical-root-relocate.md`](sessions/2026-06-03-T01-canonical-root-relocate.md) |
| 2026-06-03 | [`sessions/2026-06-03-T00-zeus-trace-scaffold.md`](sessions/2026-06-03-T00-zeus-trace-scaffold.md) |

---

## Next actions

1. **T1:** Run `python -m cli eda` → fill `docs/01-eda-report.md`
2. Copy `docs/constraints/constraints.yaml` → `src/guardian/constraints.yaml` (T3)
3. **T2:** Implement `cli ingest`
