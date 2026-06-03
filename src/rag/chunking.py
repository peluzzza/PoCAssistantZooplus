"""Map raw catalog records to index-ready documents + metadata."""

from __future__ import annotations

from src.rag.normalize import build_embed_text


def record_to_index_item(record: dict) -> dict:
    """One Chroma row per variant."""
    return {
        "id": f"{record['site_id']}:{record['locale']}:{record['article_id']}:{record['variant_id']}",
        "document": build_embed_text(record),
        "metadata": {
            "site_id": int(record["site_id"]),
            "article_id": int(record["article_id"]),
            "product_id": int(record["product_id"]),
            "variant_id": str(record["variant_id"]),
            "locale": str(record["locale"]),
            "pet_type": str(record["pet_type"]),
            "brands": str(record["brands"])[:200],
            "product_name": str(record["product_name"])[:300],
            "price": float(record["price"]),
            "stock_units": int(record["stock_units"]),
            "has_ingredients": bool((record.get("ingredients") or "").strip()),
        },
    }
