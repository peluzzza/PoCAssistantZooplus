# Coding Task — requirement checklist (v0.1 deliverable)

**Sources:** `docs/instructions/ACCEPTANCE.md`, `product_catalog_dataset.json`, `Coding Task.docx` (add to `docs/instructions/`).

## Catalog facts (demo)

| Fact | Value |
|------|--------|
| Shops | `site_id` **1**, **3**, **15** |
| Rows | **300** variants (100 per shop) |
| Pets | **DOGS**, **CATS** only |

## B1–B9 — functional (tick when demonstrated)

| ID | Requirement | Demo / evidence |
|----|-------------|-----------------|
| **B1** | Async FastAPI | Show `async` routes; `/docs` OpenAPI |
| **B2** | `POST /chat` `{ site_id, query }` | UI or curl with site 3 |
| **B3** | Response `{ answer, retrieved_products }` | JSON in UI network tab |
| **B4** | RAG only from dataset | Explain Chroma index; no web in path |
| **B5** | `site_id` scoping | Same query on site 1 vs 3 → different products |
| **B6** | Pet-only; off-topic declined | “weather” / “humans” → decline, no cards |
| **B7** | Production layout | `cli/`, `src/`, tests, `.opencode/` |
| **B8** | README + runnable | `run_dev.ps1`, ingest, `/ui/` |
| **B9** | Evaluation & trade-offs | Slide: hybrid RAG, agentic intent, limits |

## Policies (P1–P3)

| ID | Policy | Demo |
|----|--------|------|
| **P1** | Max 4 products | Catalog query → ≤4 cards |
| **P2** | Decline → answer, empty products | Off-topic turn |
| **P3** | 300 variants ingested | `python -m cli ingest` / `/ready` |

## Suggested live demo script (5–7 min)

1. **Hello** (site 3) — social, no product cards.
2. **“options for cats”** — prose answer + ≤4 cat products.
3. **Switch site 15** — repeat; different SKUs.
4. **“products for humans”** — polite decline.
5. **Brief example** — `best dry food for puppy` (site 3).

## Automated proof

```powershell
py -3 -m pytest tests/acceptance -m acceptance -q
py -3 -m pytest tests/integration -m agentic -q
py -3 -m pytest tests/social -m social -q
```
