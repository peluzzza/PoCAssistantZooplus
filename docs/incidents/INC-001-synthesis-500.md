# INC-001 — HTTP 500 on catalog product queries

**Severity:** P0  
**Found:** 2026-06-04 (UI manual test)  
**Status:** FIXED on `bugfix/INC-001-synthesis-500`

## Symptom

`POST /chat` with queries such as “can you search about cat food” returned **500 Internal Server Error** in the chat UI.

## Root cause

`src/lanes/process.py` timeout fallback called `synthesize_template(products)` but the function signature is `synthesize_template(query, products)` → `TypeError` bubbled to FastAPI.

OpenCode synthesis often timed out (25s), triggering this path on every product query when `ZOOPLUS_SYNTHESIS_MODE=opencode`.

## Fix

- Pass `envelope.query` to `synthesize_template` in the `TimeoutError` handler.
- Broaden `except` to catch synthesis failures and always fall back safely.
- Default UI/API path: template-first for product answers when OpenCode exceeds budget.

## Verification

```bash
pytest tests/security/test_guardrails.py -q
pytest tests/acceptance -q -m acceptance
```
