# 15-minute presentation — Coding Task.docx

**Deck (pro):** `zooplus-assistant-interview-15min-pro.pptx` — **11 slides**  
**FR** = Functional Requirement from `Coding Task.docx` — explain on **slide 2**.  
**Roadmap:** slides **9–11** (3 slides, ~2 min + Q&A).

---

## Timing (pro)

| Slide | Topic | Min |
|-------|--------|-----|
| 1 | Title | 0:30 |
| 2 | FR1–FR5 overview | 0:45 |
| 3 | FR1 + Swagger | 1:00 |
| 4 | FR2 + FR3 | 2:00 |
| 5 | Agentic architecture | 1:15 |
| 6 | Agents — who responds | 1:15 |
| 7 | FR4 + live demo | 4:00 |
| 8 | FR5 + README | 1:00 |
| 9 | **Roadmap Phase 1** — trust & quality (P0) | 0:45 |
| 10 | **Roadmap Phase 2** — scale & fresh catalog (P1) | 0:45 |
| 11 | **Roadmap Phase 3** — photo, voice, promos + **Q&A** | 1:30 |

*Total talk ~15 min; Q&A on slide 11.*

---

## Slide 9 — Roadmap Phase 1 (P0)

> “First I would harden FR4: versioned constraints, injection defense, and structured intent filters so RAG respects pet type and price before we scale traffic.”

Graphic: `diag-06-quality-pyramid.png`

---

## Slide 10 — Roadmap Phase 2 (P1)

> “Operations: automated catalog re-ingest so the vector index never serves stale SKUs; horizontal API, queues, and managed vector DB for concurrency; HTTP LLM and MCP/ACP for production agents.”

Graphic: `diag-07-deployment.png`

---

## Slide 11 — Roadmap Phase 3 (P2–P3) + Q&A

> “Product channels on the **same** `/chat` contract: search by photo grounded in catalog, optional promos during long streams, and later voice. Order: 2→3→8→9→4→5→7→1→6.”

Graphic: `diag-01-containers.png`  
Full doc: [`FUTURE_IMPROVEMENTS.md`](FUTURE_IMPROVEMENTS.md)

---

## One-minute pitch

> Five FRs delivered with agentic RAG inside and one assistant outside. Next: P0 security and filters, P1 fresh vectors and scale, then multimodal photo search, promos, and voice — without breaking the API contract.
