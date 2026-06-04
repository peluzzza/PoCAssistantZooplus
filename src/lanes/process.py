"""Process lane for retrieval and grounded answer synthesis."""

from __future__ import annotations

import asyncio
import logging

from src.acp.envelopes import ChatProcessEnvelope, ProcessLaneReceipt
from src.guardian.engine import load_constraints, max_recommendations
from src.llm.synthesis import synthesize_answer
from src.models.chat import RetrievedProduct
from src.rag.hybrid import retrieval_mode
from src.rag.rerank import recommendation_reason, vector_similarity
from src.rag.retrieve import search_catalog

logger = logging.getLogger(__name__)


def _hit_relevance_score(hit: dict) -> float | None:
    if hit.get("hybrid_score") is not None:
        return round(float(hit["hybrid_score"]), 4)
    return round(vector_similarity(hit.get("distance")), 4)


def _to_retrieved_product(hit: dict) -> RetrievedProduct:
    metadata = hit.get("metadata", {})
    return RetrievedProduct(
        article_id=int(metadata["article_id"]),
        product_id=int(metadata["product_id"]),
        variant_id=str(metadata["variant_id"]),
        product_name=str(metadata["product_name"]),
        variant_name=None,
        price=float(metadata["price"]),
        currency="EUR",
        pet_type=str(metadata["pet_type"]),
        brands=str(metadata["brands"]),
        relevance_score=_hit_relevance_score(hit),
        recommendation_reason=recommendation_reason(metadata, hybrid=retrieval_mode() == "hybrid"),
    )


async def run_process_lane(envelope: ChatProcessEnvelope) -> ProcessLaneReceipt:
    hits = await asyncio.to_thread(
        search_catalog,
        envelope.query,
        envelope.site_id,
        n_results=max_recommendations(),
    )
    products = [_to_retrieved_product(hit) for hit in hits][: max_recommendations()]

    constraints = load_constraints()
    process_cfg = constraints.get("process_lane", {})
    synth_timeout = float(process_cfg.get("synthesis_timeout_seconds", 12))

    try:
        answer = await asyncio.wait_for(
            asyncio.to_thread(
                synthesize_answer,
                envelope.query,
                envelope.site_id,
                products,
                handoff_context=envelope.intent_handoff,
            ),
            timeout=synth_timeout,
        )
    except TimeoutError:
        from src.llm.template import synthesize_template

        answer = synthesize_template(envelope.query, products)
    except Exception as exc:
        from src.llm.template import synthesize_template

        logger.warning("synthesis failed, template fallback: %s", exc)
        answer = synthesize_template(envelope.query, products)

    return ProcessLaneReceipt(
        dispatch_id=envelope.dispatch_id,
        dispatch_ok=True,
        status="ok",
        answer=answer,
        retrieved_products=products,
    )
