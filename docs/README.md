# zooplus Assistant — PoC Documentation

**Canonical repo root:** `PoC chatbot zooplus/` (this tree only — not `project_temp`).

**Language:** English  
**Spec inputs:** [`instructions/Coding Task.docx`](instructions/Coding%20Task.docx) · [`instructions/product_catalog_dataset.json`](instructions/product_catalog_dataset.json)  
**Immutable catalog copy:** [`../data/raw/product_catalog_dataset.json`](../data/raw/product_catalog_dataset.json)  
**Master proposal (v2):** [`plans/PROPOSAL.md`](plans/PROPOSAL.md)

---

## Documentation map

| Path | Purpose |
|------|---------|
| [`00-brief-alignment.md`](00-brief-alignment.md) | Living checklist vs Coding Task |
| [`01-eda-report.md`](01-eda-report.md) | Dataset EDA (filled in T1) |
| [`02-rag-architecture.md`](02-rag-architecture.md) | RAG + index design |
| [`03-agent-flows-and-prompts.md`](03-agent-flows-and-prompts.md) | Conversation flows |
| [`constraints/`](constraints/) | Topic boundary + machine-readable rules |
| [`plans/PROPOSAL.md`](plans/PROPOSAL.md) | Full architecture proposal (Zeus v2) |
| [`trace/`](trace/) | **Step-by-step implementation progress** (PoC journal) |

---

## How to use the trace journal

1. Open [`trace/PROGRESS.md`](trace/PROGRESS.md) for current phase and status.
2. Each step `T0`–`T6` has its own file under [`trace/`](trace/).
3. When a step finishes, add a `trace/phases/*-complete.md` artifact (same style as `project_temp/plans/*-complete.md`).
4. Session logs go under [`trace/sessions/`](trace/sessions/) for Zeus/CLI orchestration notes.

**Rule:** No loose notes — every decision lands in `trace/` or the numbered spec docs above.
