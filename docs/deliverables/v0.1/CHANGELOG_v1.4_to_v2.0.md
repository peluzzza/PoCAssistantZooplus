# What's new — v1.4 → v2.0 (interview line)

**Baseline:** tag `v1.4` on `releases` — timed social chunks + parallel catalog (live-loop UX).  
**Current:** tag `v2.0` on `releases` — **invisible conductor orchestrator** decides each stream tick.

Frame this as **smarter orchestration behind the same shopper shell**, not a new API or UI redesign.

---

## Headline for the interview

> “v1.4 gave shoppers a live conversational loop while catalog work ran in parallel. v2.0 adds an **invisible conductor** — a stronger LLM that decides *when* to speak, *what* to say next, and *when* to finish — so the social agent never repeats the same disclaimer and each bubble advances the story.”

---

## New features (v2.0 — official stream mode)

| Feature | What the shopper sees | Why it matters |
|--------|------------------------|----------------|
| **Invisible conductor** | Same bubbles + typing as v1.4 | System admin is hidden; only zooplus Assistant voice |
| **Brief-driven chunks** | Each message follows a fresh conductor brief | Fixes repeated “solo perros y gatos / no tortugas” loops |
| **JSON step loop** | `emit_message` → `wait` → `complete` per tick | Explicit orchestration instead of fixed timer-only chunks |
| **Anti-repeat rules** | Scope disclaimer once per turn; later ticks = progress | Natural dialogue arc before product cards |
| **Mode switch** | `ZOOPLUS_STREAM_MODE=conductor` (default) · `timed` = v1.4 fallback | Safe rollback without touching v1.0 tag |

**Key files:** `src/agents/conductor_orchestrator.py`, `src/lanes/stream.py`, `src/agents/prompts.py`, `src/agents/social_agent.py`

**Model:** conductor → `opencode-go/minimax-m2.7` (`.opencode/agents/zooplus-conductor.md`)

---

## Carried forward from v1.4 (unchanged UX shell)

- Timed typing indicator (`. .. ...`) and paced chunk queue in UI
- `ZOOPLUS_CHUNK_MIN_TYPING_SECONDS` / `ZOOPLUS_CHUNK_MIN_PAUSE_SECONDS`
- Parallel catalog pipeline (retrieve → process → synthesis)
- Session turn cancellation on new shopper message
- Five FRs, hybrid RAG, FR4 default-deny, per-agent OpenCode models

---

## Demo script (slide 9)

1. **A:** `hola` → fast social, no catalog
2. **B:** `gatos y tortugas 20–50€` → 2–3 **different** bubbles; scope said once; then progress
3. **C:** `what is the weather` → polite decline, empty `retrieved_products`

**URL:** `http://127.0.0.1:8090/ui/` · shop Spain (`site_id` 15)

---

## Regenerate deck

```bash
py -3 scripts/patch_interview_pptx_v20_conductor.py
```
