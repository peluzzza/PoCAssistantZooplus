"""Template-based grounded answer (no external API) — conversational tone."""

from __future__ import annotations

from src.guardian.engine import empty_retrieval_message
from src.models.chat import RetrievedProduct


def synthesize_template(query: str, products: list[RetrievedProduct]) -> str:
    if not products:
        return empty_retrieval_message()
    lines = ["I'd be happy to help! Based on what you asked, here are some options from this shop:"]
    for i, product in enumerate(products, start=1):
        lines.append(f"{i}. {product.product_name} ({product.brands}) — EUR {product.price:.2f}")
    lines.append("\nWould you like me to narrow by budget, brand, or dog vs cat?")
    return "\n".join(lines)
