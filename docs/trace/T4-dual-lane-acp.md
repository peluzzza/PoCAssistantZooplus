# Step T4 — Dual-lane orchestration + ACP

| Field | Value |
|-------|-------|
| **Step** | T4 |
| **Phase** | P4 |
| **Status** | **DONE** |
| **Brief sections** | Production-oriented async design |

---

## Objective

Implement `src/lanes/` (Interactive vs Process), ACP envelopes, topic guard p95 target < 300ms.

## Evidence

- Added `src/acp/envelopes.py` and `src/acp/dispatcher.py`.
- Added `src/lanes/interactive.py` and `src/lanes/process.py`.
- Updated `src/lanes/orchestrator.py` to run fast topic guard and process lane in parallel with cancellation on decline.

---

## Next step

→ **T5** — API contract
