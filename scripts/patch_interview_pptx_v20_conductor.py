#!/usr/bin/env python3
"""Update slides 6–9 (v2.1 conductor) and append release-progress closing slide."""

from __future__ import annotations

import shutil
from pathlib import Path

from patch_interview_pptx_rag_slides import (  # type: ignore[import-not-found]
    PANEL_BG,
    draw_pro_chrome,
    renumber_footer,
)
from patch_interview_pptx_rag_slides import _bullets as _rag_bullets  # type: ignore[import-not-found]
from patch_interview_pptx_rag_slides import _rgb as _rgb_panel  # type: ignore[import-not-found]
from patch_interview_pptx_v14_live_loop import (  # type: ignore[import-not-found]
    DECK,
    _fill,
    _find_slide,
    _fix_left_column,
    _right_column_bullets,
)
from pptx import Presentation
from pptx.util import Inches

SLIDE6_RIGHT_V20 = [
    ("Grounding & answer", True),
    ("• retrieved_products[] from same site_id hits only.", False),
    ("• Off-topic → empty list + polite decline (FR4).", False),
    ("• Synthesis: per-agent OpenCode LLM — never invent SKUs.", False),
    ("v2.1 — conductor playbook (internal)", True),
    ("• conductor_playbook.md — species, templates, forbidden phrases.", False),
    ("• Fast lane probe: social vs catalog — no rigid catalog ack on hola.", False),
    ("• Auto-learn: conductor appends repeats to playbook (shopper never sees).", False),
    ("• Catalog lane: instant contextual ack + parallel RAG (shopper language).", False),
]

SLIDE7_LEFT_V20 = [
    ("Invisible conductor (releases v2.0+)", True),
    ("• Internal MD playbook — conductor maintains silently.", False),
    ("• Social turn → one natural bubble (social-agent only).", False),
    ("• Catalog turn → protocol ack from query (species, price, lang).", False),
    ("• Anti-repeat + dedupe final answer vs live chunks.", False),
    ("Stream + agentic core", True),
    ("• Intent before Chroma · catalog lexicon from ingest.", False),
    ("• ZOOPLUS_STREAM_MODE=conductor (timed = v1.4 fallback).", False),
]

SLIDE8_LEFT_V20 = [
    ("OpenCode specialists", True),
    ("• zooplus-conductor → playbook + stream orchestration (invisible).", False),
    ("• social-agent → shopper voice; greetings ≠ catalog templates.", False),
    ("• intent / topic-guard → scope filter.", False),
    ("• rag + logic + synthesis → grounded catalog answer.", False),
    ("Per-agent LLMs + language", True),
    ("• Reply language: agent mirrors shopper (query · headers · shop).", False),
    ("• No fixed locale list — OpenCode agents handle any language.", False),
]

SLIDE9_LEFT_V20 = [
    ("FR4 guardrails + live demo", True),
    ("• Pet catalog only · default-deny off-topic.", False),
    ("Demo — v2.1 smart loop", True),
    ("• A: hola que tal → ONE social reply (no catalog chunk).", False),
    ("• B: hamsters/tortugas/perros 50€ → scoped ack + progress + products.", False),
    ("• C: any-language greeting — agent replies in kind.", False),
    ("• http://127.0.0.1:8090/ui/ — shop Spain (15).", False),
]

PROGRESS_LEFT = [
    ("Foundation — v0.1.0 → v1.0", True),
    ("v0.1.0 — Coding Task PoC: FR1–5, hybrid RAG, FR4 guardrails.", False),
    ("v0.1.3 — Conductor-first routing; /chat/stream; per-agent OpenCode.", False),
    ("v1.0 — Stable tag: catalog lexicon at ingest, cache, multilingual.", False),
]

PROGRESS_RIGHT = [
    ("Shopper experience — v1.4 → v2.1 (now)", True),
    ("v1.4 — Live loop: timed chunks, parallel catalog, typing pace.", False),
    ("v2.0 — Invisible conductor; brief-driven ticks; anti-repeat scope.", False),
    ("v2.1 — Playbook MD; social vs catalog probe; agent-multilingual.", False),
]


def _find_progress_slide(prs: Presentation) -> int | None:
    for i, slide in enumerate(prs.slides):
        for sh in slide.shapes:
            if sh.has_text_frame and (sh.text or "").strip().startswith("Release progress"):
                return i
    return None


def _append_blank_slide(prs: Presentation):
    layout = prs.slide_layouts[6]
    return prs.slides.add_slide(layout)


def _set_progress_footer(slide) -> None:
    footer = "zooplus Assistant — releases v2.1 · progress since v0.1.0"
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        text = (sh.text or "").strip()
        if "zooplus Assistant" in text and sh.top and sh.top > Inches(6.8):
            sh.text_frame.paragraphs[0].text = footer


def build_release_progress_slide(slide, *, page: int) -> None:
    draw_pro_chrome(
        slide,
        title="Release progress — v0.1.0 → v2.1",
        subtitle="Same five FRs · stronger agentic orchestration and live shopper UX",
        badge="Progress · releases",
        page=page,
    )
    panel = slide.shapes.add_shape(1, Inches(0.64), Inches(1.38), Inches(12.0), Inches(5.45))
    _rgb_panel(panel, PANEL_BG)
    _rag_bullets(
        slide,
        Inches(0.82),
        Inches(1.55),
        Inches(5.85),
        Inches(5.1),
        PROGRESS_LEFT,
        size=15,
    )
    _rag_bullets(
        slide,
        Inches(6.7),
        Inches(1.55),
        Inches(5.75),
        Inches(5.1),
        PROGRESS_RIGHT,
        size=15,
    )
    _set_progress_footer(slide)


def ensure_release_progress_slide(prs: Presentation) -> None:
    idx = _find_progress_slide(prs)
    if idx is None:
        slide = _append_blank_slide(prs)
        build_release_progress_slide(slide, page=len(prs.slides))
    else:
        slide = prs.slides[idx]
        for sh in list(slide.shapes):
            el = sh._element
            el.getparent().remove(el)
        build_release_progress_slide(slide, page=idx + 1)
    renumber_footer(prs)


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
                "v2.1 conductor playbook · smart social/catalog ack · parallel RAG"
            )

    i8 = _find_slide(prs, "Agents")
    _fix_left_column(prs.slides[i8], SLIDE8_LEFT_V20, size=13)

    i9 = _find_slide(prs, "Guardrails", "FR4 guardrails")
    _fix_left_column(prs.slides[i9], SLIDE9_LEFT_V20, size=14)

    ensure_release_progress_slide(prs)

    tmp = DECK.with_name(f"{DECK.stem}_v20{DECK.suffix}")
    prs.save(str(tmp))
    try:
        shutil.copy2(tmp, DECK)
        tmp.unlink(missing_ok=True)
        print(f"Updated v2.1 conductor + release progress slide in {DECK} ({len(prs.slides)} slides)")
    except PermissionError:
        print(f"PPT is open — saved to {tmp}")


if __name__ == "__main__":
    main()
