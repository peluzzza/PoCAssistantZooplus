"""Template-based grounded answer (no external API) — conversational tone."""

from __future__ import annotations

from src.guardian.engine import empty_retrieval_message
from src.models.chat import RetrievedProduct


def synthesize_template(query: str, products: list[RetrievedProduct]) -> str:
    from src.llm.response_variety import pick_variant, style_seed

    if not products:
        return empty_retrieval_message()
    key = style_seed(query, "catalog", str(len(products)))
    names = [p.product_name for p in products[:4]]
    if len(names) == 1:
        mention = names[0]
    elif len(names) == 2:
        mention = f"{names[0]} and {names[1]}"
    else:
        mention = f"{names[0]}, {names[1]}, and {len(names) - 2} more"

    intros = (
        f"I pulled a few matches for your question — see the cards below (e.g. {mention}).",
        f"Here are some options from this shop — details are in the product cards ({mention}).",
        f"These fit what you asked; check the cards for prices and SKUs (including {mention}).",
    )
    outros = (
        "Want me to filter by dog or cat, brand, or budget?",
        "Tell me if you'd like fewer grain-free options or a specific pet type.",
        "Happy to narrow further — puppy vs adult, dry vs wet, etc.",
    )
    return f"{pick_variant(key, intros)} {pick_variant(key + 'out', outros)}"
