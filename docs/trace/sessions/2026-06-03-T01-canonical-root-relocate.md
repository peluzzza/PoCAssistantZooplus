# Session 2026-06-03 — Canonical root relocation

| Field | Value |
|-------|-------|
| **Conductor** | Zeus (Composer) |
| **Goal** | Move all PoC work into `PoC chatbot zooplus/` only |
| **Bridges** | None (user correction — inline) |

---

## Problem

Planning artifacts lived under `project_temp/plans/zooplus-poc-chatbot/` while docs were started in `review_clones/.../docs/`. User required **single folder** for everything.

---

## Actions

1. Copied `zooplus-poc-chatbot-plan.md` → `docs/plans/`
2. Added `CANONICAL_LOCATION.md` in `project_temp` (pointer only)
3. Created full repo skeleton at PoC root: `cli/`, `src/`, `.opencode/`, `data/raw/`, `tests/`
4. Marked T0 DONE, P0 complete

---

## Rule going forward

**Edit only:** `d:\temp\review_clones\PoC chatbot zooplus\`
