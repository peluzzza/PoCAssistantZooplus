# Roadmap — release v0.1 → presentation (Coding Task)

## Done in v0.1.0 (`releases`)

- Agentic orchestration (intent → social | RAG+synthesis), OpenCode internal
- Chat UI `/ui/`, 3 shops, DOGS/CATS catalog only
- Tests: unit + integration + e2e + **agentic** + **social** (no mocks)
- `.\scripts\run_release_verify.ps1`

## Next deliverables (v0.1.1 on `releases`)

| Item | Source | Output |
|------|--------|--------|
| Coding Task checklist | `docs/instructions/Coding Task.docx` + `ACCEPTANCE.md` | `docs/deliverables/v0.1/CODING_TASK_CHECKLIST.md` |
| Architecture diagram | `docs/02-rag-architecture.md`, orchestrator | PPT slide + mermaid in deliverables |
| Demo screenshots | UI on :8090 | `docs/deliverables/v0.1/screenshots/` |
| Catalog stats | `product_catalog_dataset.json` | chart: 3×100 variants, DOGS/CATS |
| Code excerpts | `orchestrator.py`, `intent_agent.py`, UI | PPT appendix |

## Git promote path

`dev` → `releases` (v0.1.x) → `main` (when milestone signed off per `RELEASE_PLAN.md`)
