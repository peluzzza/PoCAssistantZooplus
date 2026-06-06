# 15-minute presentation — Coding Task.docx

**Deck (pro):** `zooplus-assistant-interview-15min-pro.pptx` — **13 slides**  
**FR** = Functional Requirement from `Coding Task.docx` — explain on **slide 2**.  
**Roadmap:** slides **11–13** (3 slides, ~2 min + Q&A).

Regenerate slides: `py -3 scripts/patch_interview_pptx_rag_slides.py` · FR1 async: `py -3 scripts/patch_interview_pptx_fr1_async.py` · **Agentic UX (v0.1.3):** `py -3 scripts/patch_interview_pptx_agentic_ux.py`

**Changelog since last PPT (v0.1.2):** [`CHANGELOG_v0.1.2_to_v0.1.3.md`](CHANGELOG_v0.1.2_to_v0.1.3.md)

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
| 13 | **Roadmap Phase 3** — photo, voice, promos + **Q&A** | 1:30 |

*Total talk ~15 min; Q&A on slide 13.*

---

## Slide 3 — FR1 async FastAPI + evidence

> “FR1 asks for an async FastAPI backend. Our main handler is `async def chat` in `routes/chat.py`, it awaits the orchestrator, and blocking work — Chroma retrieval, intent classification — runs in `asyncio.to_thread` so we do not block the event loop. We ship with uvicorn ASGI in Docker, and acceptance test B1 asserts `inspect.iscoroutinefunction(chat)`. You can verify live in Swagger `/docs` with the mandatory brief query.”

---

## Slide 5 — Why hybrid retrieval?

> “We did not rely on vector search alone. Chroma gives semantic recall on product text, but shoppers also use exact tokens — brands, ‘grain-free’, SKUs. BM25 on the same candidate pool adds lexical precision without a second database. We fuse vector, keyword, and business signals — rating, sales, stock — then return the top four. For the PoC that means zero extra infra: local Chroma plus in-memory BM25. You can still A/B vector-only with `ZOOPLUS_RETRIEVAL_MODE=vector`.”

---

## Slide 6 — RAG strategy end-to-end

> “FR3 is catalog-only RAG. Offline: the instructions JSON is normalized — HTML stripped — one embedding per variant, with `site_id` and commerce metadata in Chroma; ingest also builds `routing_lexicon.json` for agentic prompts. Online: after the conductor allows catalog lane, we search with hybrid retrieval, optional EUR price-band filter, cap at four products, and return grounded `retrieved_products`. The UI uses `/chat/stream`: real status phases, then products and answer. Off-topic never hits the index. Optional Redis mirrors lexicon and caches for scale-out.”

---

## Slide 7 — Agentic architecture (v0.1.3)

> “Not a separate FR — this is how we made the PoC fast and shopper-friendly. Conductor-first routing classifies topic before any Chroma call, so greetings do not trigger RAG. The orchestrator prefetches catalog hits only on catalog lane. Vocabulary in prompts comes from the indexed catalog, not hardcoded dog/cat lists. TTL caches and optional Redis cut repeat latency. The shopper still sees one assistant and one `/chat` contract.”

---

## Slide 8 — Agents + per-agent LLMs

> “OpenCode subprocesses per role. Conductor returns lane plus a short `shopper_status` for the UI bubble. Social agent answers in the shopper’s language while static UI copy stays English. Each agent has its own model in `opencode.json` — fast models for routing and social, stronger models for synthesis. The UI badge shows the real model from response metadata, not a hardcoded label.”

---

## Slide 9 — Guardrails + demo

> “FR4: pet catalog only, default-deny. Live demo on port 8090: ‘hola que tal’ — social in seconds; Spanish cat food with a EUR band — stream status, then product cards; weather — polite decline. Enter sends, one transient status line, abort if the user types again. Pick shop 1, 3, or 15 before chatting.”

---

## Slide 11 — Roadmap Phase 1 (P0)

> “First I would harden FR4: versioned constraints, injection defense, and structured intent filters so RAG respects pet type and price before we scale traffic.”

---

## Slide 12 — Roadmap Phase 2 (P1)

> “Operations: automated catalog re-ingest so the vector index never serves stale SKUs; horizontal API, queues, and managed vector DB for concurrency; HTTP LLM and MCP/ACP for production agents.”

---

## Slide 13 — Roadmap Phase 3 (P2–P3) + Q&A

> “Product channels on the **same** `/chat` contract: search by photo grounded in catalog, optional promos during long streams, and later voice. Order: 2→3→8→9→4→5→7→1→6.”

Full doc: [`FUTURE_IMPROVEMENTS.md`](FUTURE_IMPROVEMENTS.md)

---

## One-minute pitch

> Five FRs delivered with hybrid RAG and conductor-led agentic UX: classify before search, stream real status to the UI, multilingual replies, per-agent LLMs, and catalog-derived lexicon — fast enough for live demo. Next: P0 security and filters, P1 fresh vectors and Redis at scale, then photo search, promos, and voice on the same `/chat` contract.
