#!/usr/bin/env python3
"""Update slides 6–9 — v2.0 invisible conductor orchestrator."""

from __future__ import annotations

import shutil
from pathlib import Path

from patch_interview_pptx_v14_live_loop import (  # type: ignore[import-not-found]
    DECK,
    SLIDE6_RIGHT,
    SLIDE7_LEFT,
    SLIDE8_LEFT,
    SLIDE9_LEFT,
    _fill,
    _find_slide,
    _fix_left_column,
    _right_column_bullets,
)
from pptx import Presentation

SLIDE6_RIGHT_V20 = [
    ("Grounding & answer", True),
    ("• retrieved_products[] from same site_id hits only.", False),
    ("• Off-topic → empty list + polite decline (FR4).", False),
    ("• Synthesis: per-agent OpenCode LLM — never invent SKUs.", False),
    ("v2.0 — invisible conductor", True),
    ("• Strong LLM admin decides each stream tick (JSON actions).", False),
    ("• social-agent voices briefs; shopper never sees conductor.", False),
    ("• Anti-repeat: scope disclaimer once, then progress only.", False),
    ("• Parallel catalog + paced typing/chunks (v1.4 UX kept).", False),
]

SLIDE7_LEFT_V20 = [
    ("Invisible conductor (v2.0 official)", True),
    ("• minimax-m2.7 orchestrator — emit_message | wait | complete.", False),
    ("• Delegates: social · topic-guard · RAG · logic · synthesis.", False),
    ("• Each tick: new brief only — no repeated tortuga/gato disclaimers.", False),
    ("• ZOOPLUS_STREAM_MODE=conductor (timed = v1.4 fallback).", False),
    ("Agentic core (unchanged)", True),
    ("• Conductor-first intent before Chroma.", False),
    ("• Catalog lexicon from ingest; optional Redis + session turns.", False),
]

SLIDE8_LEFT_V20 = [
    ("OpenCode specialists", True),
    ("• zooplus-conductor → invisible stream orchestrator (v2.0).", False),
    ("• social-agent → shopper voice from conductor briefs.", False),
    ("• intent / topic-guard → scope filter.", False),
    ("• rag + logic + synthesis → grounded catalog answer.", False),
    ("Per-agent LLMs (OpenCode Go)", True),
    ("• Conductor + logic: minimax-m2.7.", False),
    ("• Social + intent: fast flash models.", False),
    ("• UI badge shows real model from response meta.", False),
]

SLIDE9_LEFT_V20 = [
    ("FR4 guardrails + live demo", True),
    ("• Pet catalog only · default-deny off-topic.", False),
    ("Demo — v2.0 live loop", True),
    ("• A: hola → fast social.", False),
    ("• B: gatos/tortugas 20–50€ → 2–3 different bubbles, no repeat.", False),
    ("• C: weather → decline.", False),
    ("• http://127.0.0.1:8090/ui/ — shop Spain (15).", False),
]


def main() -> None:
    if not DECK.is_file():
        raise SystemExit(f"Missing deck: {DECK}")
    prs = Presentation(str(DECK))

    i6 = _find_slide(prs, "RAG strategy")
    right6 = _right_column_bullets(prs.slides[i6])
    if right6 is not None:
        _fill(right6, SLIDE6_RIGHT_V20, size=14)

    i7 = _find_slide(prs, "Agentic architecture", "Agentic routing", "Live loop")
    _fix_left_column(prs.slides[i7], SLIDE7_LEFT_V20, size=14)
    for sh in prs.slides[i7].shapes:
        if sh.has_text_frame and "How each request" in (sh.text or ""):
            sh.text_frame.paragraphs[0].text = (
                "v2.0 invisible conductor · paced live loop · parallel catalog"
            )

    i8 = _find_slide(prs, "Agents")
    _fix_left_column(prs.slides[i8], SLIDE8_LEFT_V20, size=13)

    i9 = _find_slide(prs, "Guardrails", "FR4 guardrails")
    _fix_left_column(prs.slides[i9], SLIDE9_LEFT_V20, size=14)

    tmp = DECK.with_name(f"{DECK.stem}_v20{DECK.suffix}")
    prs.save(str(tmp))
    try:
        shutil.copy2(tmp, DECK)
        tmp.unlink(missing_ok=True)
        print(f"Updated v2.0 conductor content in {DECK}")
    except PermissionError:
        print(f"PPT is open — saved to {tmp}")


if __name__ == "__main__":
    main()
