# Step T5 — Async API contract

| Field | Value |
|-------|-------|
| **Step** | T5 |
| **Phase** | P5 |
| **Status** | **DONE** |
| **Brief sections** | POST /chat, response schema, guardrails |

---

## Objective

`POST /chat` (and optional `/chat/stream`) with `{ site_id, query }` → `{ answer, retrieved_products }`; golden tests green.

## Evidence

- Wired `src/api/routes/chat.py` to orchestrator.
- Added retrieval mapping to `RetrievedProduct` with max-4 cap.
- Added off-topic decline flow returning empty products.
- Updated `tests/integration/test_api.py` to expect `200` for valid request.

---

## Next step

→ **T6** — README submission
