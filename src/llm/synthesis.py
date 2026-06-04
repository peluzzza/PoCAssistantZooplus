"""Synthesis router — template (default) or local OpenCode (your auth)."""

from __future__ import annotations

import logging
import os

from src.config import Settings, apply_settings
from src.llm.opencode import synthesize_opencode
from src.llm.template import synthesize_template
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
    mode = (cfg.synthesis_mode or "template").lower()

    if mode == "opencode":
        from src.llm.opencode import synthesize_opencode, synthesize_opencode_with_agents

        use_cascade = os.environ.get("ZOOPLUS_AGENT_CASCADE", "1").lower() not in (
            "0",
            "false",
            "no",
        )
        llm_answer = None
        if use_cascade:
            llm_answer, agent = synthesize_opencode_with_agents(
                query,
                site_id,
                products,
                settings=cfg,
                extra_context=handoff_context or "",
            )
            if llm_answer and agent:
                logger.info("synthesis via opencode agent=%s", agent)
        if not llm_answer:
            llm_answer = synthesize_opencode(
                query,
                site_id,
                products,
                settings=cfg,
                extra_context=handoff_context or "",
            )
        if llm_answer:
            return llm_answer
        logger.info("OpenCode synthesis cascade failed; using template fallback")

    return synthesize_template(query, products)
