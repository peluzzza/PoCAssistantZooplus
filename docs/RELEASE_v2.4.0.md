# Release v2.4.0 — Agentic social assistant (main)

**Date:** 2026-06-04  
**Git tag:** `v2.4.0`  
**Branch:** `main` @ `f2c5959` (and `dev`, aligned)

## Highlights

- **Agentic intent router** (`ZOOPLUS_INTENT_MODE=agentic`) — OpenCode classifies each message; no keyword routing in production.
- **Social agent** — greetings, `hello, who are you`, help/thanks: warm replies, **zero** `retrieved_products`.
- **Default-deny firewall** — traffic, weather, humans, etc. decline before RAG (no random cat-food cards).
- **114 automated use cases** + `intent_oracle` for CI; markers `agentic`, `social`, `security`.
- Chat UI: **http://127.0.0.1:8080/ui/** — status line shows intent/synthesis mode.

## Upgrade from v2.3.x

1. `git pull origin main`
2. `pip install -e ".[rag,dev]"`
3. Copy/update `.env` from `.env.example` (add `ZOOPLUS_INTENT_MODE=agentic`).
4. `.\scripts\setup_opencode_local.ps1` if not done.
5. **Restart** API (`.\scripts\run_dev.ps1`).

## Required environment (local UI)

```env
ZOOPLUS_INTENT_MODE=agentic
ZOOPLUS_SYNTHESIS_MODE=opencode
ZOOPLUS_OPENCODE_DATA_DIR=.opencode/data
ZOOPLUS_RETRIEVAL_MODE=hybrid
```

Fallback without OpenCode intent LLM: `ZOOPLUS_INTENT_MODE=oracle` (fixture from `docs/instructions` matrix).

## Quick verification

| Query | Products |
|-------|----------|
| `hello, who are you` | 0 |
| `how is the traffic today` | 0 |
| `best dry food for puppy` | 1–4 |

```bash
curl http://127.0.0.1:8080/health
curl -X POST http://127.0.0.1:8080/chat -H "Content-Type: application/json" \
  -d "{\"site_id\":3,\"query\":\"hello, who are you\"}"
```

## Docs

- `docs/instructions/AGENTIC_SOCIAL.md`
- `docs/instructions/USE_CASES.md` (regenerate: `python scripts/build_use_case_matrix.py`)
- `docs/CHAT_UI.md`
- `docs/TESTING_GUARDRAILS.md`

## Test gate

```bash
python scripts/build_use_case_matrix.py
python -m pytest tests/agentic tests/security tests/unit -q
```
