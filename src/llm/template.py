"""Template-based grounded answer (no external API) — conversational tone."""

from __future__ import annotations

from src.guardian.engine import empty_retrieval_message
from src.models.chat import RetrievedProduct


def synthesize_template(query: str, products: list[RetrievedProduct]) -> str:
    if not products:
        return empty_retrieval_message()
    names = ", ".join(f"{p.product_name} ({p.brands})" for p in products[:4])
    return (
        "I'd be happy to help! Based on what you asked, I found options in this shop — "
        f"see the product cards below: {names}. "
        "Would you like me to narrow by budget, brand, or dog vs cat?"
    )
