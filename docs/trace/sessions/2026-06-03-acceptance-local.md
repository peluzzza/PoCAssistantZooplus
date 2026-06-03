# Local acceptance run — 2026-06-03

**Source of truth:** `docs/instructions/Coding Task.docx`, `docs/instructions/product_catalog_dataset.json`  
**Runtime catalog:** `data/raw/product_catalog_dataset.json` (SHA256 match verified in tests)

## Commands

```bash
py -3 scripts/run_quality_gates.py
py -3 -m pytest tests/acceptance -q -m acceptance
```

## Results (Python 3.13 local; CI uses 3.11)

| Suite | Passed |
|-------|--------|
| unit | 21 |
| integration | 18 |
| acceptance | 29 |
| e2e | 2 |
| **Total** | **70** |

## Brief mapping

All B1–B9 rows covered by `tests/acceptance/test_coding_task_brief.py` and `docs/instructions/ACCEPTANCE.md`.

## Notes

- No contradictions found vs Coding Task functional requirements.
- `retrieved_products` implemented as JSON array of article objects (brief shows `{ ... }` placeholder).
- RAG uses template synthesis (no external LLM API); grounded in Chroma index built from instructions catalog.
