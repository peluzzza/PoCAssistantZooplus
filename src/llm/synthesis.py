"""Catalog answers via internal OpenCode synthesis (no template path)."""

from __future__ import annotations

import logging
import os

from src.agents.agent_cascade import run_agent_cascade
from src.agents.instructions_skill import instructions_skill_context
from src.config import Settings, apply_settings
from src.models.chat import RetrievedProduct

logger = logging.getLogger(__name__)


def synthesize_answer(
    query: str,
    site_id: int,
    products: list[RetrievedProduct],
    *,
    settings: Settings | None = None,
    handoff_context: str | None = None,
) -> str:
    cfg = settings or apply_settings()
    if (cfg.synthesis_mode or "").lower() == "template":
        from src.llm.template import synthesize_template

        return synthesize_template(query, products)

    from src.llm.opencode import _build_prompt, synthesize_opencode, synthesize_opencode_with_agents

    extra = "\n".join(
        p
        for p in (
            instructions_skill_context(site_id=site_id),
            handoff_context or "",
            "Write as zooplus Assistant. No numbered product list (UI shows cards).",
        )
        if p
    )

    answer: str | None = None
    if os.environ.get("ZOOPLUS_AGENT_CASCADE", "1").lower() not in ("0", "false", "no"):
        answer, _agent = synthesize_opencode_with_agents(
            query, site_id, products, settings=cfg, extra_context=extra
        )
    if not answer:
        answer = synthesize_opencode(query, site_id, products, settings=cfg, extra_context=extra)

    if answer:
        return answer

    prompt = _build_prompt(query, site_id, products, extra_context=extra)

    def _ok(raw: str) -> str | None:
        t = raw.strip()
        return t if len(t) > 20 else None

    fb = run_agent_cascade("conductor", prompt, settings=cfg, parse=_ok)
    if fb.value:
        return str(fb.value).strip()

    if products:
        n = ", ".join(p.product_name for p in products[:2])
        return f"I found {n} — see the cards. Please retry for a fuller answer."
    return "I could not find matches. Try dog or cat and a product type (food, treats)."
