# Evidence snapshot (auto-generated)

**Generated:** 2026-06-04 11:27 UTC
**Repo:** `PoC chatbot zooplus`

## Catalog (`instructions/order` or instructions copy)

| Metric | Value |
|--------|-------|
| Records | 300 |
| Sites | {1: 100, 3: 100, 15: 100} |
| Pet types | {'DOGS': 150, 'CATS': 150} |
| Locales | {'de-DE': 100, 'en-GB': 100, 'es-ES': 100} |

## Test suite

- Pytest collect: `463 tests collected in 0.46s`

## Use-case matrix

- Fixture cases: **170**

- Last E2E run: **2026-06-04T11:14:56.510692+00:00**
- Cases in run: **170**
- Pytest exit code: **0**

## Regenerate

```bash
python scripts/build_use_case_matrix.py
python scripts/run_use_case_matrix.py
python scripts/export_interview_evidence.py
```

See also: [`docs/INTERVIEW_DEFENSE.md`](../INTERVIEW_DEFENSE.md)
