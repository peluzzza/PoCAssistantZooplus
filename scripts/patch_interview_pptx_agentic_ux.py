#!/usr/bin/env python3
"""Update slides 6–9 in the pro interview deck — agentic UX since v0.1.2 PPT."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "docs" / "deliverables" / "v0.1" / "zooplus-assistant-interview-15min-pro.pptx"

INK = RGBColor(0x33, 0x41, 0x55)
TITLE_INK = RGBColor(0x0A, 0x25, 0x40)


def _find_slide(prs: Presentation, title_prefix: str) -> int:
    for i, slide in enumerate(prs.slides):
        for sh in slide.shapes:
            if sh.has_text_frame and sh.text.strip().startswith(title_prefix):
                return i
    raise SystemExit(f"Slide not found: {title_prefix!r}")


def _content_boxes(slide) -> list:
    boxes = []
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        if sh.top and 1_200_000 < sh.top < 6_000_000 and sh.height and sh.height > 2_000_000:
            boxes.append(sh)
    boxes.sort(key=lambda s: s.left or 0)
    return boxes


def _set_paragraphs(text_frame, lines: list[tuple[str, bool]], *, size: int = 16) -> None:
    text_frame.clear()
    for i, (line, bold) in enumerate(lines):
        p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
        p.text = line
        p.font.name = "Arial"
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = TITLE_INK if bold else INK
        p.space_after = Pt(5)
        if line.startswith("•"):
            p.level = 1


def _fill_box(shape, lines: list[tuple[str, bool]], *, size: int = 16) -> None:
    _set_paragraphs(shape.text_frame, lines, size=size)


SLIDE6_RIGHT = [
    ("Grounding & answer", True),
    ("• retrieved_products[] from same site_id hits only.", False),
    ("• Off-topic → empty list + polite decline (FR4).", False),
    ("• Synthesis: per-agent OpenCode LLM — never invent SKUs.", False),
    ("• Stream: /chat/stream → status* → products → done", False),
    ("• UI: one transient status bubble (agent shopper_status).", False),
    ("Production path", True),
    ("• routing_lexicon.json at ingest; optional Redis mirror.", False),
    ("• Managed vector DB + scheduled re-ingest (roadmap P1).", False),
]

SLIDE7_LEFT = [
    ("Agentic routing (v0.1.3)", True),
    ("• Shopper: ONE assistant · POST /chat contract unchanged.", False),
    ("• Conductor-first: classify TOPIC before catalog search.", False),
    ("• Social/greeting → social agent only (no Chroma).", False),
    ("• Catalog lane → prefetch search → process → synthesis.", False),
    ("• Any language: agent + catalog lexicon in prompt.", False),
]

SLIDE7_RIGHT = [
    ("Latency & pre-index", True),
    ("• TTL cache: intent · chat · retrieval (600s).", False),
    ("• Optional Redis: shared cache + lexicon (scale-out).", False),
    ("• Lexicon: brands/tokens from indexed JSON at ingest.", False),
    ("• No hardcoded perro/gato — catalog-derived signals only.", False),
    ("• Fast social path: hola que tal ≈ seconds, not 30s+.", False),
]

SLIDE8_LEFT = [
    ("OpenCode specialists (.opencode/agents/*.md)", True),
    ("• zooplus-conductor → lane + shopper_status (JSON).", False),
    ("• zooplus-social-agent → multilingual social/decline.", False),
    ("• zooplus-intent-agent → fallback cascade.", False),
    ("• rag-worker + logic-worker → hybrid retrieve, cap 4.", False),
    ("• zooplus-synthesis → grounded prose from hits only.", False),
]

SLIDE8_RIGHT = [
    ("Per-agent LLMs (official OpenCode config)", True),
    ("• Conductor / social: mimo-v2.5-free (fast).", False),
    ("• Intent / RAG: deepseek-v4-flash.", False),
    ("• Logic: qwen3.6-plus · Topic-guard: minimax-m2.5.", False),
    ("• Synthesis: deepseek-v4-flash-free.", False),
    ("• UI badge shows real model from response meta.", False),
]

SLIDE9_LEFT = [
    ("FR4 guardrails + live demo", True),
    ("• Pet catalog only · default-deny off-topic.", False),
    ("• constraints.yaml + agentic intent + social decline.", False),
    ("• Demo A: hola que tal → fast social (no RAG).", False),
    ("• Demo B: cat food 40–60 € → stream status → products.", False),
    ("• Demo C: off-topic weather → polite decline.", False),
    ("• http://127.0.0.1:8090/ui/ · shops 1 / 3 / 15", False),
]


def main() -> None:
    if not DECK.is_file():
        raise SystemExit(f"Missing deck: {DECK}")
    prs = Presentation(str(DECK))

    i6 = _find_slide(prs, "RAG strategy")
    boxes6 = _content_boxes(prs.slides[i6])
    if len(boxes6) >= 2:
        _fill_box(boxes6[1], SLIDE6_RIGHT, size=15)

    i7 = _find_slide(prs, "Agentic architecture")
    boxes7 = _content_boxes(prs.slides[i7])
    if boxes7:
        _fill_box(boxes7[0], SLIDE7_LEFT)
    if len(boxes7) >= 2:
        _fill_box(boxes7[1], SLIDE7_RIGHT)

    i8 = _find_slide(prs, "Agents")
    boxes8 = _content_boxes(prs.slides[i8])
    if boxes8:
        _fill_box(boxes8[0], SLIDE8_LEFT, size=15)
    if len(boxes8) >= 2:
        _fill_box(boxes8[1], SLIDE8_RIGHT, size=15)

    i9 = _find_slide(prs, "Guardrails")
    boxes9 = _content_boxes(prs.slides[i9])
    if boxes9:
        _fill_box(boxes9[0], SLIDE9_LEFT, size=15)

    # Subtitle slide 7
    for sh in prs.slides[i7].shapes:
        if sh.has_text_frame and sh.text.strip().startswith("How each request"):
            sh.text_frame.paragraphs[0].text = (
                "Conductor-first · catalog lexicon · stream status — fast multilingual UX"
            )

    prs.save(str(DECK))
    print(f"Updated agentic UX slides in {DECK}")


if __name__ == "__main__":
    main()
