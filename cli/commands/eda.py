"""EDA command — analyzes data/raw catalog and writes docs/01-eda-report.md."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "product_catalog_dataset.json"
REPORT = ROOT / "docs" / "01-eda-report.md"
ARTIFACT = ROOT / "artifacts" / "eda" / "summary.json"

HTML_TAG = re.compile(r"<[^>]+>")


def _html_ratio(text: str) -> float:
    if not text:
        return 0.0
    stripped = HTML_TAG.sub("", text)
    return 1.0 - (len(stripped) / max(len(text), 1))


def run_eda() -> int:
    if not RAW.exists():
        print(f"Missing catalog: {RAW}", flush=True)
        return 1

    data = json.loads(RAW.read_text(encoding="utf-8"))
    n = len(data)

    by_site = Counter(r["site_id"] for r in data)
    by_locale = Counter(r["locale"] for r in data)
    by_pet = Counter(r["pet_type"] for r in data)
    by_brand = Counter(r["brands"] for r in data).most_common(15)

    field_nonempty = {}
    for field in (
        "ingredients",
        "feeding_recommendations",
        "discount_label",
        "summary",
        "description",
    ):
        field_nonempty[field] = sum(1 for r in data if (r.get(field) or "").strip())

    food_like = sum(
        1
        for r in data
        if (r.get("ingredients") or "").strip() or (r.get("feeding_recommendations") or "").strip()
    )

    prices = [r["price"] for r in data]
    price_outliers = [
        r
        for r in data
        if r["price"] > 200 and r.get("pet_type") == "CATS" and "70 g" in (r.get("variant_name") or "")
    ]

    html_ratios = {
        "summary": mean(_html_ratio(r.get("summary") or "") for r in data),
        "description": mean(_html_ratio(r.get("description") or "") for r in data),
    }

    site_locale = defaultdict(set)
    for r in data:
        site_locale[r["site_id"]].add(r["locale"])

    summary = {
        "records": n,
        "unique_product_id": len({r["product_id"] for r in data}),
        "unique_variant_id": len({r["variant_id"] for r in data}),
        "by_site": dict(by_site),
        "by_locale": dict(by_locale),
        "by_pet": dict(by_pet),
        "field_nonempty": field_nonempty,
        "food_like_records": food_like,
        "price_min": min(prices),
        "price_max": max(prices),
        "price_mean": round(mean(prices), 2),
        "price_outlier_count": len(price_outliers),
        "html_tag_density": html_ratios,
        "site_to_locales": {str(k): sorted(v) for k, v in site_locale.items()},
    }

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = f"""# Dataset EDA report

**Status:** COMPLETE (T1)  
**Source:** `data/raw/product_catalog_dataset.json` (read-only, {n} records)  
**Artifact:** `artifacts/eda/summary.json`

---

## 1. Volume & keys

| Metric | Value |
|--------|-------|
| Records (variants) | {n} |
| Unique `product_id` | {summary['unique_product_id']} |
| Unique `variant_id` | {summary['unique_variant_id']} |

---

## 2. Multi-shop (`site_id`) — mandatory filter for RAG

| site_id | records | locale(s) |
|---------|---------|-----------|
"""
    for sid in sorted(by_site):
        locs = ", ".join(sorted(site_locale[sid]))
        report += f"| {sid} | {by_site[sid]} | {locs} |\n"

    report += f"""
**Implication:** Every retrieval and API call must filter `site_id == request.site_id` before vector ranking.

---

## 3. Pet type split

| pet_type | records |
|----------|---------|
| DOGS | {by_pet.get('DOGS', 0)} |
| CATS | {by_pet.get('CATS', 0)} |

---

## 4. Field completeness

| Field | Non-empty rows | Notes |
|-------|----------------|-------|
| `ingredients` | {field_nonempty['ingredients']} | Food/supplements |
| `feeding_recommendations` | {field_nonempty['feeding_recommendations']} | Food/supplements |
| `discount_label` | {field_nonempty['discount_label']} | Promotions |
| `summary` | {field_nonempty['summary']} | Short HTML text |
| `description` | {field_nonempty['description']} | Long HTML text |

**Food-like rows** (ingredients or feeding populated): **{food_like}**

---

## 5. HTML in text fields

| Field | Avg. HTML tag density |
|-------|---------------------|
| `summary` | {html_ratios['summary']:.1%} |
| `description` | {html_ratios['description']:.1%} |

**Implication:** Strip HTML in ingest (`skill_04_html_normalize`); embed plain text only.

---

## 6. Price distribution

| Stat | EUR |
|------|-----|
| min | {summary['price_min']} |
| max | {summary['price_max']} |
| mean | {summary['price_mean']} |

**Outliers flagged** (high price + small cat portion): {len(price_outliers)} — document, do not mutate raw JSON.

---

## 7. Top brands (sample)

| Brand | Records |
|-------|---------|
"""
    for brand, count in by_brand:
        report += f"| {brand} | {count} |\n"

    report += """
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
"""

    REPORT.write_text(report, encoding="utf-8")

    print(f"records={n} sites={sorted(by_site)} locales={sorted(by_locale)}")
    print(f"report={REPORT}")
    print(f"artifact={ARTIFACT}")
    return 0
