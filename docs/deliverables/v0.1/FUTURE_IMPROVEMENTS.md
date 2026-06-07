# Future improvements (presentation summary)

**Order:** **2 → 3 → 8 → 9 → 4 → 5 → 7 → 1 → 6** (full analysis on `main`)

| # | Topic | Priority | One line |
|---|--------|----------|----------|
| 2 | Constraints v2 + prompt-injection | **P0** | Versioned policy + layered scanner + security CI |
| 3 | Agent / intent structure for filtering | **P0** | Intent facets (pet_type, price) → deterministic RAG |
| 8 | RAG re-ingest & vector DB refresh | **P1** | Scheduled catalog sync; blue/green index; no stale SKUs |
| 9 | Scale & concurrency | **P1** | Stateless API, queues, rate limits, managed vector DB — **PoC:** optional Redis cache + lexicon mirror (`ZOOPLUS_CACHE_BACKEND=redis`) |
| 4 | LLM CLI provider evaluation | **P1** | `LLMProvider` port — OpenCode local, HTTP API in cloud |
| 5 | MCP server + ACP agent bus | **P1–P2** | MCP external; ACP internal orchestration |
| 7 | Image input (photo → search) | **P2** | Vision embedding + catalog-only multimodal RAG |
| 1 | Promo slots during long searches | **P2** | Stream promos while RAG runs |
| 6 | Voice for the assistant | **P3** | STT/TTS on same `/chat` contract |
| 10 | Multi-shop retrieval (UI + API) | **P2** | Optional all-shops or `site_ids[]`; Chroma `$in`, merge/dedup, locale-aware product cards |

**Interview line (45s):** Slide 11 = P0 trust · Slide 12 = P1 scale + fresh index · Slide 13 = photo/voice/promos + Q&A.

---

## Multi-shop search (deferred — item #10)

**Today:** one `site_id` per request (Coding Task B5 — hard shop isolation). UI shows Germany / UK / Spain; API always scopes retrieval to a single shop.

**Future option:** UI selector for **all shops** or a **subset** (e.g. Germany + Spain).

| Layer | Change |
|-------|--------|
| API | Extend contract with `site_ids: [1, 3, 15]` (backward-compatible: single `site_id` still works) |
| Chroma | `where site_id $in [...]` or parallel queries per shop + fused ranking |
| Retrieval | Global cap 4 after merge; dedupe same `article_id` across locales |
| UX | Show shop/locale on each product card; avoid mixing languages without labels |
| Tests | New acceptance profile for multi-shop; keep B5 suite on single-shop default |

**Why not in the PoC:** B5 and the interview demo emphasise per-shop catalog isolation; multi-shop is a product feature, not a brief requirement.

**Interview one-liner:** “We scope every query to one shop today. Multi-shop would be `site_ids[]`, vector filter `$in`, merge and dedup — planned as P2, same `/chat` contract.”
