"""Synthesis router — template (default) or OpenCode free-tier models."""

from __future__ import annotations

import logging
import re

from src.config import Settings, apply_settings
from src.llm.opencode import synthesize_opencode
from src.llm.template import synthesize_template
from src.models.chat import RetrievedProduct

logger = logging.getLogger(__name__)

_GREETING = re.compile(
    r"^(hi|hello|hey|hola|buenas|good\s+(morning|afternoon|evening))[!?.]*$",
    re.I,
)


def _is_greeting(query: str) -> bool:
    return bool(_GREETING.match(query.strip()))


def synthesize_answer(    query: str,
    site_id: int,
    products: list[RetrievedProduct],
    *,
    settings: Settings | None = None,
) -> str:
    cfg = settings or apply_settings()
    mode = (cfg.synthesis_mode or "template").lower()

    if _is_greeting(query):
        if products:
            return synthesize_template(products)
        return (
            "Hello! I'm the zooplus Assistant. Ask me about pet food, treats, or "
            "accessories for your shop — for example: best dry food for a puppy."
        )

    if mode == "opencode":
        llm_answer = synthesize_opencode(query, site_id, products, settings=cfg)
        if llm_answer:
            return llm_answer
        logger.info("OpenCode synthesis failed; using template fallback")

    return synthesize_template(products)
