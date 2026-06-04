# Coding Task validation (100+ use cases × instructions catalog)

**Sources of truth**

| Artifact | Path |
|----------|------|
| Brief | `docs/instructions/Coding Task.docx` |
| Catalog | `docs/instructions/product_catalog_dataset.json` (300 rows, sites 1/3/15) |

## Matrix

- **Fixture:** `tests/fixtures/use_cases_matrix.json` (generated)
- **Oracle:** `tests/fixtures/intent_oracle.json` (intent lanes for CI)
- **Build:** `python scripts/build_use_case_matrix.py`
- **Index:** `docs/instructions/USE_CASES.md`

Branches: guardrails (B6), conversational (B3), product search (B4+B5), site isolation (B5), catalog-backed sweep (`catalog_ref` per row), Coding Task.docx examples.

## Run full validation

```bash
python -m cli ingest
python scripts/build_use_case_matrix.py
python scripts/run_use_case_matrix.py
set ZOOPLUS_INTENT_MODE=oracle
set ZOOPLUS_SYNTHESIS_MODE=template
python -m pytest tests/acceptance/test_use_cases_matrix_catalog.py tests/social -q
python scripts/run_quality_gates.py
```

## What is checked

1. **≥100 cases** in the matrix (`test_matrix_at_least_100_cases`).
2. **B2–B6 coverage** in requirement tags.
3. **`catalog_ref` / `target_article_id`** exist in `product_catalog_dataset.json`.
4. **E2E** (`tests/social/test_use_cases_matrix.py`): HTTP `/chat`, grounded `article_id` ∈ catalog, max 4 products, declines empty.
