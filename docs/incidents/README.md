# Incidents — zooplus Assistant PoC

Track defects found during guardrail / acceptance testing. Each incident links to a fix branch and verification.

| ID | Severity | Summary | Branch | Status |
|----|----------|---------|--------|--------|
| [INC-001](INC-001-synthesis-500.md) | **P0** | HTTP 500 on product search — wrong `synthesize_template()` call on timeout | `bugfix/INC-001-synthesis-500` | **FIXED** |
| [INC-002](INC-002-external-search-guard.md) | P1 | “Search internet” allowed → should decline (catalog-only) | `bugfix/INC-002-external-search-guard` | **FIXED** |

**Source of truth:** `docs/instructions/Coding Task.docx`, `docs/instructions/product_catalog_dataset.json`

**Test suite:** `tests/security/test_guardrails.py`, `tests/fixtures/guardrail_queries.json`
