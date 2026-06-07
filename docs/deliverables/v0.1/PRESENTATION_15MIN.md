# 15-minute presentation — Coding Task.docx

**Deck (pro):** `zooplus-assistant-interview-15min-pro.pptx` — **14 slides**  
**FR** = Functional Requirement from `Coding Task.docx` — explain on **slide 2**.  
**Roadmap:** slides **11–13** (3 slides, ~2 min + Q&A).

Regenerate slides: `py -3 scripts/patch_interview_pptx_rag_slides.py` · FR1 async: `py -3 scripts/patch_interview_pptx_fr1_async.py` · **v1.4 live loop:** `py -3 scripts/patch_interview_pptx_v14_live_loop.py` · **v2.0 conductor:** `py -3 scripts/patch_interview_pptx_v20_conductor.py`

**Changelog v2.0 → v2.1:** [`CHANGELOG_v2.0_to_v2.1.md`](CHANGELOG_v2.0_to_v2.1.md) · **v1.4 → v2.0:** [`CHANGELOG_v1.4_to_v2.0.md`](CHANGELOG_v1.4_to_v2.0.md) · **v1.0 → v1.4:** [`CHANGELOG_v1.0_to_v1.4.md`](CHANGELOG_v1.0_to_v1.4.md)  
**Interview Q&A:** [`QA_FOR_POC.md`](QA_FOR_POC.md)

---

## Timing (pro)

| Slide | Topic | Min |
|-------|--------|-----|
| 1 | Title | 0:30 |
| 2 | FR1–FR5 overview | 0:45 |
| 3 | FR1 + Swagger + **async evidence (B1)** | 1:15 |
| 4 | FR2 + FR3 (overview) | 1:15 |
| 5 | **Why hybrid retrieval** (Chroma + BM25 + rerank) | 1:00 |
| 6 | **RAG strategy end-to-end** (ingest → ground → synthesize) | 1:00 |
| 7 | Agentic architecture | 1:00 |
| 8 | Agents — who responds | 1:00 |
| 9 | FR4 + live demo | 3:30 |
| 10 | FR5 + README | 1:00 |
| 11 | **Roadmap Phase 1** — trust & quality (P0) | 0:45 |
| 12 | **Roadmap Phase 2** — scale & fresh catalog (P1) | 0:45 |
| 13 | **Roadmap Phase 3** — photo, voice, promos | 0:45 |
| 14 | **Release progress** — v0.1.0 → v2.1 + **Q&A** | 1:00 |

*Total talk ~15 min; Q&A on slide 14.*

---

## Slide 3 — FR1 async FastAPI + evidence

> “FR1 asks for an async FastAPI backend. Our main handler is `async def chat` in `routes/chat.py`, it awaits the orchestrator, and blocking work — Chroma retrieval, intent classification — runs in `asyncio.to_thread` so we do not block the event loop. We ship with uvicorn ASGI in Docker, and acceptance test B1 asserts `inspect.iscoroutinefunction(chat)`. You can verify live in Swagger `/docs` with the mandatory brief query.”

---

## Slide 5 — Why hybrid retrieval?

> “We did not rely on vector search alone. Chroma gives semantic recall on product text, but shoppers also use exact tokens — brands, ‘grain-free’, SKUs. BM25 on the same candidate pool adds lexical precision without a second database. We fuse vector, keyword, and business signals — rating, sales, stock — then return the top four. For the PoC that means zero extra infra: local Chroma plus in-memory BM25. You can still A/B vector-only with `ZOOPLUS_RETRIEVAL_MODE=vector`.”

---

## Slide 6 — RAG strategy end-to-end

> “FR3 is catalog-only RAG — same hybrid ingest as v1.0. v2.1 adds an **internal conductor playbook** (Markdown): species out of scope, opening templates, forbidden repeat phrases. The conductor probes social vs catalog before any ack — a greeting never gets a catalog template. On catalog lane, contextual ack runs in parallel with RAG. Grounding unchanged: same `site_id`, max four products, polite decline off-topic.”

---

## Slide 7 — Agentic architecture (conductor playbook)

> “The shopper sees one assistant. Behind the scenes the conductor owns `conductor_playbook.md` — it updates silently when dedupe catches a bad repeat. Social turns: one natural bubble via social-agent. Catalog turns: protocol ack parsed from the query (species, EUR band, language), then progress chunks while RAG runs. `ZOOPLUS_STREAM_MODE=conductor` default; `timed` is the v1.4 fallback.”

---

## Slide 8 — Agents + per-agent LLMs

> “**zooplus-conductor** maintains the internal playbook and orchestrates the stream — invisible in the UI. **social-agent** handles greetings and social turns without catalog boilerplate. Catalog lane still uses intent, RAG, logic, synthesis. Reply language follows the shopper: Spanish, English, German, or French from query or shop locale. UI badge shows the real model from response metadata.”

---

## Slide 9 — Guardrails + demo (v2.1 smart loop)

> “FR4: pet catalog only, default-deny. Demo on 8090, shop 15: (A) ‘hola que tal’ — **one** social reply, no ‘reviso el catálogo’ chunk; (B) hamsters/tortugas/perros hasta 50€ — scoped ack, progress, products; (C) ‘hello’ or ‘bonjour’ — reply in the same language. Hard refresh if you tested an older build.”

---

## Slide 11 — Roadmap Phase 1 (P0)

> “First I would harden FR4: versioned constraints, injection defense, and structured intent filters so RAG respects pet type and price before we scale traffic.”

---

## Slide 12 — Roadmap Phase 2 (P1)

> “Operations: automated catalog re-ingest so the vector index never serves stale SKUs; horizontal API, queues, and managed vector DB for concurrency; HTTP LLM and MCP/ACP for production agents.”

---

## Slide 13 — Roadmap Phase 3 (P2–P3)

> “Product channels on the **same** `/chat` contract: search by photo grounded in catalog, optional promos during long streams, and later voice. Order: 2→3→8→9→4→5→7→1→6.”

Full doc: [`FUTURE_IMPROVEMENTS.md`](FUTURE_IMPROVEMENTS.md)

---

## Slide 14 — Release progress (v0.1.0 → v2.1) + Q&A

> “We kept the same five FRs from the Coding Task and iterated on `releases`. **v0.1.0** delivered the PoC baseline — hybrid RAG and guardrails. **v0.1.3 / v1.0** added conductor-first routing, streaming status, and per-agent OpenCode models. **v1.4** shipped the live-loop UX shoppers feel today — timed chunks while catalog runs in parallel. **v2.0** introduced the invisible conductor so disclaimers are not repeated. **v2.1**, our current tag, adds the internal playbook, smart social-vs-catalog ack, and four shopper languages. Happy to dive into any milestone or run the demo again.”

---

## One-minute pitch

> Five FRs delivered with hybrid RAG and conductor-led agentic UX: classify before search, stream real status to the UI, multilingual replies, per-agent LLMs, and catalog-derived lexicon — fast enough for live demo. Next: P0 security and filters, P1 fresh vectors and Redis at scale, then photo search, promos, and voice on the same `/chat` contract.
