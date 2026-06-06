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

**Interview line (45s):** Slide 11 = P0 trust · Slide 12 = P1 scale + fresh index · Slide 13 = photo/voice/promos + Q&A.
