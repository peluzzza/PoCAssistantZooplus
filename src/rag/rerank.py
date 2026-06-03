"""Business reranking on top of hybrid retrieval scores."""

from __future__ import annotations


def vector_similarity(distance: float | None) -> float:
    if distance is None:
        return 0.0
    return 1.0 / (1.0 + max(distance, 0.0))


def business_score(metadata: dict) -> float:
    rating = float(metadata.get("rating_average", 0.0) or 0.0) / 5.0
    sales = float(metadata.get("monthly_sales_units", 0) or 0)
    sales_norm = min(sales / 2000.0, 1.0)
    stock = 1.0 if int(metadata.get("stock_units", 0) or 0) > 0 else 0.0
    return 0.45 * rating + 0.35 * sales_norm + 0.20 * stock


def fuse_hybrid_scores(
    *,
    vector_distance: float | None,
    lexical_norm: float,
    metadata: dict,
    lexical_weight: float = 0.35,
    business_weight: float = 0.15,
) -> float:
    vec = vector_similarity(vector_distance)
    lex = min(max(lexical_norm, 0.0), 1.0)
    biz = business_score(metadata)
    vector_weight = 1.0 - lexical_weight - business_weight
    return vector_weight * vec + lexical_weight * lex + business_weight * biz


def recommendation_reason(metadata: dict, *, hybrid: bool) -> str:
    parts = ["Matches your request in this catalog"]
    if hybrid:
        parts.append("hybrid vector+keyword rank")
    rating = metadata.get("rating_average")
    if rating:
        parts.append(f"rating {float(rating):.1f}/5")
    if int(metadata.get("stock_units", 0) or 0) > 0:
        parts.append("in stock")
    return "; ".join(parts) + "."
