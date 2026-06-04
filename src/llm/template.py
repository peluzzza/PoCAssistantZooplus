"""Template-based grounded answer (no external API) — conversational tone."""

from __future__ import annotations

from src.guardian.engine import empty_retrieval_message
from src.models.chat import RetrievedProduct


def synthesize_template(query: str, products: list[RetrievedProduct]) -> str:
    if not products:
        return empty_retrieval_message()
    lines = ["Here's what I found in this shop that could fit your question:"]
    for i, product in enumerate(products, start=1):
        lines.append(f"{i}. {product.product_name} ({product.brands}) — EUR {product.price:.2f}")
    lines.append(
        "\nHappy to narrow this down — just mention budget, brand, or whether it's for a dog or cat."
    )
    return "\n".join(lines)
