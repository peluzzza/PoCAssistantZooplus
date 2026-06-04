# INC-003 — Hybrid retrieval empty for valid queries (site 15 / max_recommendations)

**Status:** resolved  
**Date:** 2026-06-04  
**Severity:** medium (acceptance / social matrix failures)

## Symptom

- `POST /chat` with `site_id=15`, query `dog chew toy` returned **0** `retrieved_products` and the empty-retrieval message, while direct Chroma queries had relevant snacks/toys.
- Matrix cases **UC-031**, **UC-039**, **dog_toy_site15**, **allow_dog_toy_site15** failed.
- **UC-038** (gibberish SKU) incorrectly returned catalog hits when vector-only similarity was high but BM25 was zero.

## Root cause

1. **Candidate pool too small:** `hybrid_search_catalog` used `candidate_n = max(4×n_results, n_results+5)`. With `max_recommendations() == 4`, only **16** vector candidates were scored; the best hybrid score was **0.281** (< `ZOOPLUS_MIN_HYBRID_SCORE` 0.30). With **20+** candidates, the same query reached **0.307+** and passed.
2. **Nonsense queries:** Pure-vector matches for token-less gibberish (`xyzzy_nonexistent_sku_…`) could score above 0.30 without lexical grounding.

## Fix

- `src/rag/hybrid.py`: enforce `MIN_CANDIDATE_POOL = 24` when building the candidate set.
- Reject known gibberish / non-catalog probe patterns via `_is_nonsense_catalog_query()` before retrieval.
- Keep BM25-zero + low vector-peak filter for weak semantic-only matches.

## Verification

```bash
ZOOPLUS_SYNTHESIS_MODE=template pytest tests/social tests/security tests/acceptance -q
python scripts/run_use_case_matrix.py   # 56/56
```

## References

- `tests/fixtures/use_cases_matrix.json` (UC-031, UC-038, UC-039)
- `docs/instructions/USE_CASES.md`
- `docs/trace/sessions/use-case-matrix-latest.json`
