# 15-minute presentation — Coding Task.docx

**Deck (pro):** `zooplus-assistant-interview-15min-pro.pptx` — **13 slides**  
**FR** = Functional Requirement from `Coding Task.docx` — explain on **slide 2**.  
**Roadmap:** slides **11–13** (3 slides, ~2 min + Q&A).

Regenerate slides: `py -3 scripts/patch_interview_pptx_rag_slides.py` · FR1 async: `py -3 scripts/patch_interview_pptx_fr1_async.py` · **v1.4 live loop:** `py -3 scripts/patch_interview_pptx_v14_live_loop.py` · **v2.0 conductor:** `py -3 scripts/patch_interview_pptx_v20_conductor.py`

**Changelog v1.4 → v2.0:** [`CHANGELOG_v1.4_to_v2.0.md`](CHANGELOG_v1.4_to_v2.0.md) · **v1.0 → v1.4:** [`CHANGELOG_v1.0_to_v1.4.md`](CHANGELOG_v1.0_to_v1.4.md)  
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

> “FR3 is catalog-only RAG — same ingest and hybrid retrieval as v1.0. What changed in v2.0 is *when* we run it: the invisible conductor starts the catalog pipeline in parallel while the social agent keeps the shopper engaged. Grounding rules are unchanged — `retrieved_products[]` from the same `site_id` only, synthesis never invents SKUs, off-topic gets an empty list and a polite decline.”

---

## Slide 7 — Agentic architecture (v2.0 invisible conductor)

> “v1.4 timed chunks every five seconds. v2.0 replaces the fixed timer with an **invisible conductor** — minimax-m2.7 — that returns JSON each tick: emit a new message brief, wait, or complete. The social agent is the only voice the shopper hears. Anti-repeat: shop scope (dogs and cats only) is stated once; later bubbles are progress only. `ZOOPLUS_STREAM_MODE=conductor` is default; `timed` is the v1.4 fallback.”

---

## Slide 8 — Agents + per-agent LLMs

> “OpenCode subprocesses per role. **zooplus-conductor** is the invisible stream orchestrator — not shown in the UI. **social-agent** turns conductor briefs into shopper language. intent/topic-guard, RAG, logic, and synthesis run when the catalog lane needs them. Conductor and logic use minimax-m2.7; social and intent use fast flash models. The UI badge still shows the real model from response metadata.”

---

## Slide 9 — Guardrails + demo (v2.0 live loop)

> “FR4: pet catalog only, default-deny. Demo on 8090: (A) ‘hola’ — fast social; (B) ‘gatos y tortugas 20–50€’ — two or three **different** bubbles, scope disclaimer once, no tortuga loop; (C) weather — decline. Typing dots and paced chunks like v1.4. Pick shop 15 (Spain) before chatting.”

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
