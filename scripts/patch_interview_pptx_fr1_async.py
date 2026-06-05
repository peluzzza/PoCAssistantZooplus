#!/usr/bin/env python3
"""Add async FastAPI evidence to FR1 slide (slide 3) in the pro deck."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "docs" / "deliverables" / "v0.1" / "zooplus-assistant-interview-15min-pro.pptx"

INK = RGBColor(0x33, 0x41, 0x55)
TITLE_INK = RGBColor(0x0A, 0x25, 0x40)
CODE_BG = RGBColor(0x1E, 0x29, 0x3B)
CODE_FG = RGBColor(0xE2, 0xE8, 0xF0)
ACCENT = RGBColor(0x25, 0x63, 0xEB)
GREEN = RGBColor(0x16, 0xA3, 0x4A)

LEFT_BULLETS = [
    ("FR1 = Functional Requirement 1 (Coding Task §1)", True),
    ("Async Python FastAPI · POST /chat { site_id, query }", True),
    ("", False),
    ("Async evidence (B1)", True),
    ("• Endpoint: async def chat() → await handle_chat()", False),
    ("  src/api/routes/chat.py", False),
    ("• Pipeline: handle_chat / process lane are async coroutines", False),
    ("• Blocking I/O (Chroma, intent) → asyncio.to_thread", False),
    ("• Runtime: uvicorn ASGI (Dockerfile CMD)", False),
    ("• Test: test_app_is_async_fastapi — inspect.iscoroutinefunction(chat)", False),
    ("", False),
    ("Live: Swagger /docs — Try it out + mandatory brief query", True),
]

CODE_SNIPPET = """@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    return await handle_chat(body)

# tests/acceptance/test_coding_task_brief.py
assert inspect.iscoroutinefunction(chat)  # B1 ✅"""

MARKER = "async def chat()"


def _set_bullets(text_frame, lines: list[tuple[str, bool]], *, size: int = 16) -> None:
    text_frame.clear()
    for i, (line, bold) in enumerate(lines):
        p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
        p.text = line
        p.font.name = "Arial"
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = TITLE_INK if bold else INK
        p.space_after = Pt(4)


def _find_slide(prs: Presentation, title_prefix: str) -> int:
    for i, slide in enumerate(prs.slides):
        for sh in slide.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip().startswith(title_prefix):
                return i
    raise SystemExit(f"Slide not found: {title_prefix!r}")


def patch_fr1_slide(prs: Presentation) -> bool:
    idx = _find_slide(prs, "API endpoint")
    slide = prs.slides[idx]

    for sh in slide.shapes:
        if sh.name == "TextBox 12" and sh.has_text_frame:
            if MARKER in sh.text_frame.text:
                return False
            _set_bullets(sh.text_frame, LEFT_BULLETS, size=15)
        if sh.name == "TextBox 9" and sh.has_text_frame:
            sh.text_frame.paragraphs[0].text = (
                "FR1 — Async FastAPI (Coding Task §1) · evidence in code + test B1"
            )

    # Code evidence panel (right column, below Swagger screenshot area)
    existing = [s.name for s in slide.shapes]
    if "TextBox AsyncEvidence" not in existing:
        panel = slide.shapes.add_shape(
            1, Inches(6.65), Inches(5.35), Inches(5.55), Inches(1.55)
        )
        panel.name = "Panel AsyncEvidence"
        panel.fill.solid()
        panel.fill.fore_color.rgb = CODE_BG
        panel.line.fill.background()

        box = slide.shapes.add_textbox(Inches(6.78), Inches(5.45), Inches(5.3), Inches(1.35))
        box.name = "TextBox AsyncEvidence"
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        p = tf.paragraphs[0]
        p.text = "Async evidence (source)"
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ACCENT
        p2 = tf.add_paragraph()
        p2.text = CODE_SNIPPET
        p2.font.name = "Consolas"
        p2.font.size = Pt(10)
        p2.font.color.rgb = CODE_FG

        badge = slide.shapes.add_textbox(Inches(6.78), Inches(5.12), Inches(2.2), Inches(0.28))
        badge.name = "TextBox B1Badge"
        bp = badge.text_frame.paragraphs[0]
        bp.text = "B1 test_app_is_async_fastapi ✅"
        bp.font.name = "Arial"
        bp.font.size = Pt(11)
        bp.font.bold = True
        bp.font.color.rgb = GREEN

    return True


def main() -> None:
    if not DECK.is_file():
        raise SystemExit(f"Missing deck: {DECK}")
    prs = Presentation(str(DECK))
    if patch_fr1_slide(prs):
        prs.save(str(DECK))
        print(f"Patched FR1 async evidence in {DECK}")
    else:
        print("FR1 slide already contains async evidence — skipped.")


if __name__ == "__main__":
    main()
