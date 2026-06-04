# Release v2.5.0 — Agentic cascade, OpenCode social, matrix 173/173

**Date:** 2026-06-04  
**Git tag:** `v2.5.0`  
**Branch:** `main` @ `3a59e53` (`dev` aligned)

## Highlights

- **OpenCode agent cascade** — intent, social, and synthesis retry across subagents (`zooplus-intent-agent` → `zooplus-topic-guard` → `zooplus-conductor`) before heuristic fallback; `ZOOPLUS_AGENT_CASCADE=1`.
- **Agentic social lane** — greetings, help, thanks, declines via `zooplus-social-agent` (no fixed dialog pools in `conversation.py`; only hints + emergency fallback).
- **Smarter topic fallback** — product browse, species (horses), shop help; no repeated help template on OpenCode timeout.
- **Catalog UX** — synthesis prose without numbered duplicate lists (cards in UI).
- **173/173 use-case matrix** — Coding Task + instructions catalog; smoke script `scripts/smoke_minimal.ps1`.
- **CI determinism** — `.env` uses `setdefault` so pytest oracle mode is not overridden.

## Upgrade from v2.4.0

1. `git pull origin main && git checkout main`
2. `pip install -e ".[rag,dev]"`
3. Update `.env` from `.env.example`:
   ```env
   ZOOPLUS_INTENT_MODE=agentic
   ZOOPLUS_SYNTHESIS_MODE=opencode
   ZOOPLUS_SOCIAL_SYNTHESIS=agentic
   ZOOPLUS_AGENT_CASCADE=1
   ```
4. `.\scripts\setup_opencode_local.ps1` (if needed)
5. `python -m cli ingest` (first time or after catalog change)
6. `.\scripts\run_dev.ps1` → **http://127.0.0.1:8080/ui/**

## Quick verification

```powershell
.\scripts\smoke_minimal.ps1
py -3 scripts/run_use_case_matrix.py
```

| Query | Expected |
|-------|----------|
| `hello, what can you tell me about your services` | Help, 0 products |
| `what products do you have available` | ≥1 product |
| `do you have product about horses?` | Decline, 0 products |
| `how is the traffic today` | Decline, 0 products |

## Docs

- `docs/MINIMAL_FUNCTIONAL.md`
- `docs/CODING_TASK_VALIDATION.md`
- `docs/instructions/USE_CASES.md`
- `docs/instructions/AGENTIC_SOCIAL.md`

## Test gate

```bash
python scripts/build_use_case_matrix.py
python scripts/run_use_case_matrix.py
python -m pytest tests/unit tests/integration tests/social -q -m "not slow"
```
