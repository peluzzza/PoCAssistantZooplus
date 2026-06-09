# 15-minute presentation — Coding Task.docx

**Deck (pro):** `zooplus-assistant-interview-15min-pro.pptx` — **14 slides**  
**FR** = Functional Requirement from `Coding Task.docx` — explain on **slide 2**.  
**Roadmap:** slides **11–13** (3 slides, ~2 min + Q&A).

Regenerate slides: `py -3 scripts/patch_interview_pptx_rag_slides.py` · FR1 async: `py -3 scripts/patch_interview_pptx_fr1_async.py` · **v2.0 conductor + FR code panels:** `py -3 scripts/patch_interview_pptx_v20_conductor.py` (includes slides 5–9 + FR2–FR5 code evidence) · optional: `py -3 scripts/patch_interview_pptx_fr_code_panels.py`

**Changelog v2.0 → v2.1:** [`CHANGELOG_v2.0_to_v2.1.md`](CHANGELOG_v2.0_to_v2.1.md) · **v1.4 → v2.0:** [`CHANGELOG_v1.4_to_v2.0.md`](CHANGELOG_v1.4_to_v2.0.md) · **v1.0 → v1.4:** [`CHANGELOG_v1.0_to_v1.4.md`](CHANGELOG_v1.0_to_v1.4.md)

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
| 14 | **Release progress** — v0.1.0 → v2.1.6 + **Q&A** | 1:00 |

*Total talk ~15 min; Q&A on slide 14.*

---

## Slide 3 — FR1 async FastAPI + evidence

> “FR1 asks for an async FastAPI backend. Our main handler is `async def chat` in `routes/chat.py`, it awaits the orchestrator, and blocking work — Chroma retrieval, intent classification — runs in `asyncio.to_thread` so we do not block the event loop. We ship with uvicorn ASGI in Docker, and acceptance test B1 asserts `inspect.iscoroutinefunction(chat)`. You can verify live in Swagger `/docs` with the mandatory brief query.”

---

## Slide 5 — Why hybrid retrieval?

> “We did not rely on vector search alone. Chroma gives semantic recall on product text, but shoppers also use exact tokens — brands, ‘grain-free’, SKUs. BM25 on the same candidate pool adds lexical precision without a second database. We fuse vector, keyword, and business signals — default **four** picks, or up to **twenty** when the shopper asks. The stream sends **product_batch** events so the UI reveals cards in chunks of four. Zero extra infra for the PoC; A/B vector-only with `ZOOPLUS_RETRIEVAL_MODE=vector`.”

---

## Slide 6 — RAG strategy end-to-end

> “FR3 is catalog-only RAG — same hybrid ingest as v1.0. **v2.1.6** adds an internal playbook plus a **social phrase index** (~90 curated ES/EN/DE/FR utterances, fast in-memory match; playbook auto-learns novel help/greeting lines). Social vs catalog probe before any ack — ‘can you help me’ never gets a catalog progress chunk. **Four picks by default**, but the shopper can ask for more (e.g. ten options, cap twenty); the stream emits **product_batch** events so cards appear in the UI in chunks of four. Dynamic species inference handles iguanas and unseen pets without a fixed list. Grounding unchanged: same `site_id`, polite decline off-topic.”

---

## Slide 7 — Agentic architecture (conductor playbook)

> “The shopper sees one assistant. The conductor owns `conductor_playbook.md` and updates it silently on repeats. **v2.1.3+** runs intent-agent and policy probes first for lower latency; conductor intent is opt-in. Social turns: one bubble, no re-intro mid-session. Catalog turns: ack from species, price, language, and requested count; progress chunks while RAG runs; final answer deduped against live chunks. `ZOOPLUS_STREAM_MODE=conductor` default.”

---

## Slide 8 — Agents + per-agent LLMs

> “**zooplus-conductor** maintains the playbook and stream — invisible in the UI. **social-agent** handles help and greetings without catalog boilerplate or redundant self-introduction intros. **phrase_index** matches help/greeting/thanks in milliseconds; learned rows merge at runtime. Catalog lane: intent, RAG, logic, synthesis. Reply language is agent-driven — no fixed locale whitelist.”

---

## Slide 9 — Guardrails + demo (v2.1.6 smart loop)

> “FR4: pet catalog only, default-deny. Demo on 8090, shop 15: (A) ‘can you help me’ — social help, **no** ‘Still searching the catalog’ chunk; (B) ‘and what about iguanas’ — scope reply without duplicate greeting intro; (C) ‘give me 10 dog food options’ — up to ten product cards arriving in batches. Hard refresh if you tested an older build.”

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

## Slide 14 — Release progress (v0.1.0 → v2.1.6) + Q&A

> “Same five FRs, iterated on `releases`. **v0.1.0–v1.4**: hybrid RAG, streaming, live-loop UX. **v2.0–v2.1**: invisible conductor, playbook MD, social/catalog probe, agent-multilingual. **v2.1.3**: fast intent-first stream. **v2.1.4–5**: dynamic species, help/greeting detection, greeting dedupe. **v2.1.6** (current): four picks by default but shopper can ask for more, `product_batch` chunked cards, and the social phrase index. Happy to dive into any milestone or run the demo.”

---

## One-minute pitch

> Five FRs delivered with hybrid RAG and conductor-led agentic UX: classify before search, stream real status to the UI, multilingual replies, per-agent LLMs, and catalog-derived lexicon — fast enough for live demo. Next: P0 security and filters, P1 fresh vectors and Redis at scale, then photo search, promos, and voice on the same `/chat` contract.
