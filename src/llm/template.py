"""Template-based grounded answer (no external API)."""

from __future__ import annotations

from src.guardian.engine import empty_retrieval_message
from src.models.chat import RetrievedProduct


def synthesize_template(products: list[RetrievedProduct]) -> str:
    if not products:
        return empty_retrieval_message()
    lines = ["I found these options in your shop catalog:"]
    for product in products:
        lines.append(
            f"- {product.product_name} ({product.brands}) - EUR {product.price:.2f} "
            f"[article_id: {product.article_id}]"
        )
    lines.append("Tell me if you want a narrower budget, brand, or pet-type filter.")
    return "\n".join(lines)
