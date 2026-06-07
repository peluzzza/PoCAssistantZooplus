# What's new — v1.0 → v1.4 (interview line)

**Baseline:** tag `v1.0` — stable PoC with OpenCode Go model ladder and hybrid RAG.  
**Current:** tag `v1.4` on `releases` — **live-loop streaming UX** is the official shopper experience.

This note is for **speaker prep** and deck updates. Frame changes as **new capabilities**, not a diff audit.

---

## Headline for the interview

> “Since v1.0 we kept the same five FRs and agentic core, and shipped a **live conversational loop**: the social agent talks to the shopper every few seconds while catalog search runs in parallel — like modern LLM streaming chunks, but with full sentences and real product grounding at the end.”

---

## New features (v1.4 — official UX)

| Feature | What the shopper sees | Why it matters |
|--------|------------------------|----------------|
| **Timed social chunks** | Short friendly messages every ~5s during catalog work | No blank wait; feels like a human assistant thinking aloud |
| **Parallel catalog** | Chunks appear while retrieve + rank + synthesis run | Latency hidden behind conversation |
| **Typing indicator** | `.` `..` `...` between bubbles | Familiar chat-app affordance |
| **Paced delivery** | Backend slots + UI queue — not burst messages | Avoids “wall of text” in one frame |
| **Persistent bubbles** | Each chunk is its own bot message | Clear narrative arc before product cards |
| **Session turns** | New message cancels the previous stream | Safe interruption, like real chat |

**Key files:** `src/lanes/stream.py`, `src/agents/social_agent.py` (`social_chunk_reply`), `static/ui/app.js`, `src/cache/session_turn.py`

**Config (tunable):** `ZOOPLUS_CHUNK_INTERVAL_SECONDS`, `ZOOPLUS_CHUNK_MIN_TYPING_SECONDS`, `ZOOPLUS_CHUNK_MIN_PAUSE_SECONDS`

---

## Still the same (v1.0 foundation)

- Five FRs, hybrid RAG (Chroma + BM25 + business signals), max 4 products
- Conductor-first routing — classify before Chroma on social turns
- Per-agent OpenCode Go models, multilingual replies, `site_id` shop scope
- `POST /chat` + `POST /chat/stream` NDJSON contract
- Default-deny guardrails (FR4)

---

## Intermediate releases (optional mention)

| Tag | Theme |
|-----|--------|
| **v1.1** | Backend status phases in stream (stepping stone) |
| **v1.2** | Beat-based social loop experiments (superseded by v1.4) |
| **v1.4** | **Timed chunks + pacing — production UX** |

You can say: *“We iterated on progress feedback in v1.1–v1.2 and landed on v1.4 as the official pattern.”*

---

## Demo script (slide 9)

1. **Spain shop (15)** — *“hola qué tal”* → quick social, no products.
2. **Catalog loop** — *“opciones para perros y gatos no más de 20€”* → typing, 2–3 conversational bubbles, then answer + cards.
3. **Decline** — *“qué tiempo hace”* → polite boundary.

Hard refresh the UI (`Ctrl+Shift+R`) before demo if you patched the deck or pulled `releases`.

---

## Refresh the pro deck

```powershell
py -3 scripts/patch_interview_pptx_v14_live_loop.py
```

Slides **6–9** updated: RAG stream, live-loop architecture, social-agent chunks, demo talking points.

Speaker notes: [`PRESENTATION_15MIN.md`](PRESENTATION_15MIN.md)
