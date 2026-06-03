# Zooplus PoC Chatbot — Phased Implementation Plan

**Generated:** 2026-06-03  
**Source:** `product_catalog_dataset.json` (300 variant records). `Coding Task.docx` (extracted 2026-06-03 via Zeus).  
**Constraint:** No Anthropic models. Catalog is multilingual (de-DE, en-GB, es-ES).

---

## Task summary (from Coding Task.docx)

**Deliverable:** Take-home PoC (~4–6 h) — **zooplus Assistant** chatbot API for Senior AI Engineer (Agentic Commerce).

| Area | Requirement |
|------|-------------|
| **API** | Async **FastAPI**; `POST /chat` with `{ "site_id": int, "query": string }` |
| **Multi-shop** | `site_id` required; only products for that shop |
| **Response** | `{ "answer": string, "retrieved_products": {...} }` — conversational + structured articles used as context |
| **RAG** | Knowledge **only** from provided JSON catalog |
| **Guardrails** | Pet-product questions only; politely decline off-topic |
| **Production mindset** | PoC but scalable API contract and code layout |
| **Submission** | Git repo: runnable code, indexing/embed scripts if any, **README** (architecture diagram, setup, trade-offs, 3–5 production next steps) |
| **Evaluation** | Engineering rigor, RAG reasoning, dataset leverage, transparent trade-offs (not feature count) |

---

## UNRESOLVED GAPS (before implementation)

| ID | Gap | Risk | Resolution |
|----|-----|------|------------|
| GAP-01 | ~~DOCX unread~~ | — | **Resolved** — spec captured above |
| GAP-02 | LLM provider not mandated in brief | Medium | Pick one (OpenAI-compatible or local Ollama); document in README |
| GAP-03 | No UI required — API only | Low | Optional demo page; not in acceptance criteria |
| GAP-04 | Shape of `retrieved_products` not fully specified | Medium | Define stable schema (e.g. list of article_id + key fields) in spec |
| GAP-05 | ~~Record count unknown~~ | — | **Resolved:** 300 records, 154 products, 287 variants |

---

## Data Model — Confirmed from JSON

### Entity: `ProductVariant` (one JSON object per article/variant)

| Field | Type | Notes |
|-------|------|-------|
| `product_id` | int | Groups variants belonging to same product |
| `article_id` | int | Unique SKU identifier |
| `variant_id` | string | `"{product_id}.{index}"` |
| `site_id` | int | **1, 3, 15** (multi-shop — must filter per request) |
| `locale` | string | **de-DE, en-GB, es-ES** (aligned with sites) |
| `pet_type` | enum | `DOGS` or `CATS` confirmed |
| `brands` | string | Single brand per record (Chuckit!, KONG, Hyper Pet, Simple Solution, Flamingo, Doppelherz, Schesir, …) |
| `product_name` | string | Product title |
| `variant_name` | string | Size/flavor/color descriptor |
| `summary` | HTML string | Short bullet-point description |
| `description` | HTML string | Long rich-text description |
| `ingredients` | HTML string | Non-empty for food/supplement products only |
| `feeding_recommendations` | HTML string | Non-empty for food/supplement products only |
| `price` | float | EUR |
| `currency` | string | Always `"EUR"` |
| `discount_label` | string\|null | e.g. `"-30%"`, `null` if no discount |
| `rating_average` | float | 0–5, `0.0` means no ratings |
| `rating_count` | int | Number of reviews |
| `stock_units` | int | Current inventory |
| `margin_pct` | float | Gross margin percentage |
| `monthly_sales_units` | int | Last 30d unit sales |
| `revenue_last_30d` | float | EUR revenue last 30 days |

**Key observations:**
- Products span: toys, accessories, care items, supplements, wet/dry food
- Food/supplement products have `ingredients` and `feeding_recommendations` populated (HTML with tables)
- Business metrics (`margin_pct`, `monthly_sales_units`, `revenue_last_30d`) enable ranking/recommendation logic
- All text content is in German; chatbot must handle German queries or do lang detection

---

## Suggested Stack (no Anthropic)

| Layer | Choice | Rationale |
|-------|--------|-----------|
| LLM | OpenAI GPT-4o (or Ollama + Mistral/LLaMA3) | German fluency, function calling; Ollama for fully local |
| Embedding | `text-embedding-3-small` (OpenAI) or `nomic-embed-text` (Ollama) | Semantic search over product descriptions |
| Vector store | ChromaDB (in-process) or FAISS | Simple, no external infra for PoC |
| Orchestration | LangChain or bare Python with tool-calling | Thin enough for PoC |
| API | FastAPI | Lightweight REST + streaming |
| Data ingest | Python + `json` + `html.parser` / `BeautifulSoup` | Strip HTML tags before embedding |
| Interface | Simple HTML/JS chat widget OR Jupyter notebook | Sufficient for PoC demo |

---

## Phases

### Phase 0 — Scout & Gap Resolution *(done)*

**Goal:** Understand brief + data before coding.

**Tasks:**
- [x] Extract `Coding Task.docx` (Zeus)
- [x] Profile `product_catalog_dataset.json` (300 rows, sites 1/3/15, DOGS/CATS 50/50)
- [ ] Choose LLM + embedding provider; document env vars
- [ ] Freeze `retrieved_products` JSON schema in spec

**Exit gate:** GAP-02/04 closed → Phase 1.

---

### Phase 1 — Spec & Architecture *(Hera gate)*

**Goal:** Finalise architecture and write acceptance tests before coding.

**Deliverables:**
1. `spec/data-model.md` — canonical field definitions, HTML-stripping rules
2. `spec/query-types.md` — list of supported intents with example Q&A pairs (German)
3. `spec/architecture.md` — component diagram (ingest → embed → retrieve → LLM → response)
4. `spec/acceptance-tests.md` — ≥10 test cases covering:
   - Product lookup by name/brand/pet_type
   - Ingredient query for food products
   - Feeding recommendation lookup
   - Price/discount query
   - Stock availability check
   - Top-selling product recommendation
   - Multi-variant selection (e.g. "size M vs size L")

**Acceptance criteria:**
- Architecture decision documented with rationale for each component choice
- All known query types covered by at least one test case
- HTML-stripping strategy defined (avoid feeding raw `<strong>` tags to LLM)

---

### Phase 2 — Implement: Data Ingestion & Embedding *(Sisyphus)*

**Goal:** Load JSON, clean HTML, embed product variants, persist to vector store.

**Tasks:**
1. Parse `product_catalog_dataset.json` — group by `product_id` / `article_id`
2. Strip HTML from `summary`, `description`, `ingredients`, `feeding_recommendations`
3. Build embedding document per variant: concatenate key text fields
4. Embed and upsert into ChromaDB with metadata (all structured fields as filters)
5. Smoke-test: retrieve top-3 semantically similar products for 3 test queries

**Acceptance criteria:**
- All records ingested without error
- Metadata filters work for `pet_type`, `brands`, `price` range
- Retrieval returns relevant results for German-language queries
- Ingest script is idempotent (re-run safe)

---

### Phase 3 — Implement: Chatbot Core *(Sisyphus)*

**Goal:** Implement conversational agent with retrieval-augmented generation.

**Tasks:**
1. Define tool set:
   - `search_products(query, pet_type?, brand?, max_price?)` → top-k variants
   - `get_product_detail(article_id)` → full record
   - `get_feeding_recommendation(article_id)` → feeding info
   - `recommend_top_sellers(pet_type, category?)` → ranked by `monthly_sales_units` / `revenue_last_30d`
2. Implement RAG loop: user message → tool call → context injection → LLM response
3. System prompt in German or bilingual (de/en) supporting German user queries
4. Handle multi-turn context (conversation history)
5. Expose as FastAPI `POST /chat` with `{site_id, query}` → `{answer, retrieved_products}` (per brief)

**Acceptance criteria:**
- All tools callable and return correct data
- Agent correctly routes to `get_feeding_recommendation` for nutrition queries
- Agent uses `recommend_top_sellers` for "what's popular" queries
- Handles unknown products gracefully (no hallucination of fake products)
- Response latency < 10s for typical query

---

### Phase 4 — Implement: Interface *(Sisyphus)*

**Goal:** Demo-ready chat UI or notebook.

**Tasks (choose based on DOCX spec):**
- **Option A (REST API demo):** Simple HTML/JS chat widget served from FastAPI static files
- **Option B (Jupyter):** Notebook with inline chat widget and product card rendering
- Both: render product cards (name, brand, price, discount, rating, stock status)

**Acceptance criteria:**
- Demo runs with single command (`uvicorn` or `jupyter notebook`)
- Product results include structured card, not just raw text
- At least one multi-turn conversation works end-to-end

---

### Phase 5 — Test & Validate *(Argus)*

**Goal:** Run acceptance tests from Phase 1 spec, identify gaps.

**Tasks:**
1. Run all 10+ test cases from `spec/acceptance-tests.md`
2. Check for hallucinations (product names/specs not in dataset)
3. Check edge cases: out-of-stock, zero-rating products, food vs non-food routing
4. Check data quality anomalies (e.g. `price: 950.0` on cat food — likely data error)

**Acceptance criteria:**
- ≥80% test cases pass
- No hallucinated product data
- Data anomalies documented (not necessarily fixed — this is a PoC)

---

## Known Data Anomalies (flag for DOCX confirmation)

| Anomaly | Example | Likely cause |
|---------|---------|--------------|
| `price: 950.0` on 70g cat food portion | `Schesir Complements in Gelee` variants | Data error or bulk/pallet price |
| `rating_average: 0.0, rating_count: 0` | Several new SKUs | No reviews yet — normal |
| `ingredients` / `feeding_recommendations` empty for non-food | Toys, accessories | Correct by design |

---

## Dependency Order

```
Phase 0 (Scout) → Phase 1 (Spec) → Phase 2 (Ingest) → Phase 3 (Chatbot) → Phase 4 (UI) → Phase 5 (Test)
                                                        [Phase 3 + Phase 4 can run in parallel after Phase 2]
```

**Next action:** Phase 1 spec (Hera gate) — define `retrieved_products` contract + guardrail prompts + site_id filter tests.

## Orchestration trace (this session)

| Agent | Route | Result |
|-------|-------|--------|
| Prometheus | Claude Code Sonnet 4.6 | Wrote this plan |
| Hermes | Claude Code Haiku 4.5 | Greenfield: docs + JSON only |
| Oracle | Claude Code Sonnet 4.6 | RAG stack trade-offs (embed + Chroma/FAISS) |
| Zeus | Composer (parent) | DOCX extract, dataset profile, plan corrections |
| Hera | Claude Code Sonnet 4.6 | **APPROVED** phase sequence (0→5); original BLOCKER on DOCX superseded by Zeus extract |

**Hera gate (2026-06-03):** Proposed phases (requirements → data → architecture → FastAPI+RAG → README → test) align with Prometheus plan. Proceed to **Phase 1** after freezing `retrieved_products` schema and LLM choice.
