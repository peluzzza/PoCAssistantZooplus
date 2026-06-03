# Dataset EDA report

**Status:** COMPLETE (T1)  
**Source:** `data/raw/product_catalog_dataset.json` (read-only, 300 records)  
**Artifact:** `artifacts/eda/summary.json`

---

## 1. Volume & keys

| Metric | Value |
|--------|-------|
| Records (variants) | 300 |
| Unique `product_id` | 154 |
| Unique `variant_id` | 287 |

---

## 2. Multi-shop (`site_id`) — mandatory filter for RAG

| site_id | records | locale(s) |
|---------|---------|-----------|
| 1 | 100 | de-DE |
| 3 | 100 | en-GB |
| 15 | 100 | es-ES |

**Implication:** Every retrieval and API call must filter `site_id == request.site_id` before vector ranking.

---

## 3. Pet type split

| pet_type | records |
|----------|---------|
| DOGS | 150 |
| CATS | 150 |

---

## 4. Field completeness

| Field | Non-empty rows | Notes |
|-------|----------------|-------|
| `ingredients` | 223 | Food/supplements |
| `feeding_recommendations` | 214 | Food/supplements |
| `discount_label` | 190 | Promotions |
| `summary` | 300 | Short HTML text |
| `description` | 300 | Long HTML text |

**Food-like rows** (ingredients or feeding populated): **223**

---

## 5. HTML in text fields

| Field | Avg. HTML tag density |
|-------|---------------------|
| `summary` | 18.1% |
| `description` | 21.7% |

**Implication:** Strip HTML in ingest (`skill_04_html_normalize`); embed plain text only.

---

## 6. Price distribution

| Stat | EUR |
|------|-----|
| min | 0.75 |
| max | 1000.0 |
| mean | 100.24 |

**Outliers flagged** (high price + small cat portion): 1 — document, do not mutate raw JSON.

---

## 7. Top brands (sample)

| Brand | Records |
|-------|---------|
| Eukanuba | 29 |
| Smilla | 21 |
| Purina One | 16 |
| Lucky Jim | 14 |
| 8in1 | 13 |
| Chuckit! | 12 |
| Hyper Pet | 12 |
| Schesir | 9 |
| Cosma | 9 |
| Canada Litter | 9 |
| Doppelherz | 8 |
| Simple Solution | 7 |
| Flamingo | 7 |
| Purizon | 7 |
| Whiskas | 6 |

---

## 8. RAG design decisions (from EDA)

1. **Chunk unit:** one document per **variant** (`variant_id`), metadata includes `site_id`, `article_id`, `pet_type`, `price`, `stock_units`.
2. **Filter-then-score:** hard `site_id` filter → optional `pet_type` → vector search on normalized text.
3. **Nutrition queries:** route to variants with non-empty `ingredients` / `feeding_recommendations`.
4. **Ranking signals:** `monthly_sales_units`, `rating_average`, `stock_units` available for logic agent.

---

## Trace

- Step log: [`trace/T1-eda-run.md`](trace/T1-eda-run.md)
- CLI: `python -m cli eda`
