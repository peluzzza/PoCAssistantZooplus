#!/usr/bin/env python3
"""Insert three dedicated "LangGraph approach" slides before the closing
Release-progress slide. This deck (releases, v2.1.6 baseline) carries no
LangGraph code — the slides document the approach with an actual flowchart
diagram, a node-by-node table, and a bar chart of the verified cache-hit
speedup, pointing to the standalone showcase branch
(feature/lg-catalog-probe-intent) where it's implemented. Idempotent —
re-running replaces slide content in place rather than duplicating slides.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from patch_interview_pptx_rag_slides import (  # type: ignore[import-not-found]
    INK,
    PALE,
    PANEL_BG,
    TITLE_INK,
    WHITE,
    _bullets,
    _text,
    draw_pro_chrome,
    insert_slide_at,
    renumber_footer,
)
from patch_interview_pptx_rag_slides import _rgb as _rgb_panel  # type: ignore[import-not-found]
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "docs" / "deliverables" / "v0.1" / "zooplus-assistant-interview-15min-pro.pptx"

_OLD_SINGLE_SLIDE_TITLES = ("LangGraph orchestrator", "LangGraph approach")
_PROGRESS_TITLE = "Release progress"
_BADGE = "Architecture · LG"

SLIDE1_TITLE = "LangGraph 1/3 — explicit graph vs Python branches"
SLIDE2_TITLE = "LangGraph 2/3 — every node, what it calls"
SLIDE3_TITLE = "LangGraph 3/3 — audit findings & verified results"

# Node fill colors by role — same legend reused across slides 1 and 2.
COLOR_TERMINAL = RGBColor(0x33, 0x41, 0x55)
COLOR_CACHE = RGBColor(0x60, 0xA5, 0xFA)
COLOR_INTENT = RGBColor(0xF5, 0x9E, 0x0B)
COLOR_SOCIAL = RGBColor(0x34, 0xD3, 0x99)
COLOR_CATALOG = RGBColor(0xA7, 0x8B, 0xFA)
COLOR_ARROW = RGBColor(0x55, 0x66, 0x80)
COLOR_LABEL = RGBColor(0x6B, 0x72, 0x80)

# ---------------------------------------------------------------------------
# Generic shape helpers
# ---------------------------------------------------------------------------


def _box(slide, text, x, y, w, h, *, fill, font_color=WHITE, size=11):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = fill
    shape.shadow.inherit = False
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Pt(3)
    tf.margin_right = Pt(3)
    tf.margin_top = Pt(1)
    tf.margin_bottom = Pt(1)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = True
    p.font.name = "Arial"
    p.font.color.rgb = font_color
    return shape


def _arrow(slide, x1, y1, x2, y2, *, label=None):
    conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    conn.line.color.rgb = COLOR_ARROW
    conn.line.width = Pt(1.5)
    ln = conn.line._get_or_add_ln()
    tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
    ln.append(tail)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        box = slide.shapes.add_textbox(Inches(mid_x - 0.55), Inches(mid_y - 0.13), Inches(1.1), Inches(0.26))
        tf = box.text_frame
        tf.word_wrap = False
        tf.margin_left = 0
        tf.margin_right = 0
        tf.margin_top = 0
        tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = label
        p.font.size = Pt(9)
        p.font.italic = True
        p.font.bold = True
        p.font.color.rgb = COLOR_LABEL


def _legend_dot(slide, x, y, *, fill, text):
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(0.16), Inches(0.16))
    dot.fill.solid()
    dot.fill.fore_color.rgb = fill
    dot.line.fill.background()
    dot.shadow.inherit = False
    _text(slide, Inches(x + 0.22), Inches(y - 0.04), Inches(1.6), Inches(0.24), text, size=10, color=INK)


# ---------------------------------------------------------------------------
# Slide 1 — flowchart diagram
# ---------------------------------------------------------------------------

SLIDE1_LEFT = [
    ("The problem this explores", True),
    ("• Legacy: one async function with nested if/elif per lane —", False),
    ("  retry/fallback chains hidden inside helper functions.", False),
    ("• Hard to unit-test one decision in isolation (e.g. \"what happens", False),
    ("  on an intent timeout?\") without exercising the whole function.", False),
    ("Same agentic core, explicit shape", True),
    ("• Every node calls THIS repo's own functions verbatim — zero", False),
    ("  re-implemented logic, nothing invented.", False),
    ("• 4 typed routing functions, independently unit-tested.", False),
    ("• All 7 nodes async — graph.ainvoke(), not graph.invoke().", False),
]


def _draw_slide1_diagram(slide) -> None:
    _box(slide, "START", 8.55, 1.55, 1.3, 0.32, fill=COLOR_TERMINAL, size=10)
    _box(slide, "cache_check", 7.25, 2.15, 2.7, 0.42, fill=COLOR_CACHE)
    _box(slide, "END\n(cached answer)", 10.75, 2.10, 1.55, 0.50, fill=COLOR_TERMINAL, size=9)
    _box(slide, "classify_intent", 7.25, 2.95, 2.7, 0.42, fill=COLOR_INTENT)
    _box(slide, "social", 5.85, 3.75, 1.9, 0.42, fill=COLOR_SOCIAL)
    _box(slide, "prefetch", 8.95, 3.75, 1.9, 0.42, fill=COLOR_CATALOG)
    _box(slide, "process_lane", 8.95, 4.45, 2.2, 0.42, fill=COLOR_CATALOG)
    _box(slide, "cache_store", 7.25, 5.25, 2.7, 0.42, fill=COLOR_CACHE)
    _box(slide, "END", 8.35, 6.00, 1.3, 0.30, fill=COLOR_TERMINAL, size=10)

    _arrow(slide, 9.20, 1.87, 8.60, 2.15)
    _arrow(slide, 9.95, 2.36, 10.75, 2.35, label="hit")
    _arrow(slide, 8.60, 2.57, 8.60, 2.95, label="miss")
    _arrow(slide, 8.00, 3.37, 6.80, 3.75, label="social")
    _arrow(slide, 9.30, 3.37, 9.90, 3.75, label="catalog")
    _arrow(slide, 9.90, 4.17, 10.05, 4.45)
    _arrow(slide, 6.80, 4.17, 7.90, 5.25)
    _arrow(slide, 10.05, 4.87, 9.60, 5.25)
    _arrow(slide, 8.60, 5.67, 8.95, 6.00)

    _legend_dot(slide, 5.85, 6.35, fill=COLOR_CACHE, text="cache")
    _legend_dot(slide, 7.15, 6.35, fill=COLOR_INTENT, text="intent")
    _legend_dot(slide, 8.40, 6.35, fill=COLOR_SOCIAL, text="social")
    _legend_dot(slide, 9.60, 6.35, fill=COLOR_CATALOG, text="catalog")


def build_slide1(slide, *, page: int) -> None:
    draw_pro_chrome(
        slide,
        title=SLIDE1_TITLE,
        subtitle="Same agentic core, new explicit state graph",
        badge=_BADGE,
        page=page,
    )
    panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.64), Inches(1.38), Inches(12.0), Inches(5.45))
    _rgb_panel(panel, PANEL_BG)
    _bullets(slide, Inches(0.82), Inches(1.55), Inches(4.55), Inches(5.1), SLIDE1_LEFT, size=12)
    _draw_slide1_diagram(slide)


# ---------------------------------------------------------------------------
# Slide 2 — node-by-node table
# ---------------------------------------------------------------------------

TABLE_ROWS = [
    ("Node", "Calls (verbatim)", "Purpose", True),
    ("cache_check", "chat_cache.get(key)", "Same singleton + key format as the legacy orchestrator", False),
    (
        "classify_intent",
        "orchestrator._classify_intent_bounded()",
        "Same 22s timeout, same _fallback_intent_decision() on timeout",
        False,
    ),
    (
        "prefetch",
        "resolve_recommendation_count + price_band + search_catalog",
        "Catalog hits fetched once — orchestrator.py step 3",
        False,
    ),
    ("social", "social_agent.social_reply()", "Unchanged behaviour, only made async", False),
    (
        "process_lane",
        "dispatch_process(run_process_lane, timeout=<constraints.yaml>)",
        "Real nested 40s outer / 18s inner timeout — replaces rag_node + synthesis_node",
        False,
    ),
    ("cache_store", "chat_cache.set(key, response)", "Same singleton as the legacy orchestrator", False),
]


def _set_cell(cell, text, *, bold=False, size=12, color=INK, fill=None, align=PP_ALIGN.LEFT) -> None:
    if fill is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left = Pt(8)
    cell.margin_right = Pt(8)
    cell.margin_top = Pt(4)
    cell.margin_bottom = Pt(4)
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.name = "Arial"
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color


def _draw_slide2_table(slide) -> None:
    rows, cols = len(TABLE_ROWS), 3
    gframe = slide.shapes.add_table(rows, cols, Inches(0.82), Inches(2.05), Inches(11.6), Inches(4.55))
    table = gframe.table
    table.columns[0].width = Inches(2.0)
    table.columns[1].width = Inches(4.6)
    table.columns[2].width = Inches(5.0)

    header_fill = TITLE_INK
    for r, (col0, col1, col2, is_header) in enumerate(TABLE_ROWS):
        if is_header:
            row_fill = header_fill
        elif r % 2 == 0:
            row_fill = PANEL_BG
        else:
            row_fill = WHITE
        text_color = WHITE if is_header else INK
        size = 13 if is_header else 12
        _set_cell(table.cell(r, 0), col0, bold=True, size=size, color=text_color, fill=row_fill)
        _set_cell(table.cell(r, 1), col1, bold=is_header, size=size - 1, color=text_color, fill=row_fill)
        _set_cell(table.cell(r, 2), col2, bold=is_header, size=size - 1, color=text_color, fill=row_fill)
        table.rows[r].height = Inches(0.42) if is_header else Inches(0.68)


def build_slide2(slide, *, page: int) -> None:
    draw_pro_chrome(
        slide,
        title=SLIDE2_TITLE,
        subtitle="Every node is a verbatim call into this repo's own functions",
        badge=_BADGE,
        page=page,
    )
    panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.64), Inches(1.38), Inches(12.0), Inches(5.45))
    _rgb_panel(panel, PANEL_BG)
    _text(
        slide,
        Inches(0.82),
        Inches(1.5),
        Inches(11.6),
        Inches(0.45),
        "rag_node + synthesis_node deleted — process_lane replaces both with one call into the existing ACP dispatch.",
        size=13,
        color=INK,
    )
    _draw_slide2_table(slide)


# ---------------------------------------------------------------------------
# Slide 3 — audit findings (callout cards) + verified-results bar chart
# ---------------------------------------------------------------------------

GAPS = [
    ("1", "preferred_model silently ignored", "UI's model override stored in state but no node read it. Fixed via ContextVar set for the whole graph run."),
    ("2", "No chat-level cache existed", "cache_check_node / cache_store_node now share the legacy orchestrator's own chat_cache singleton."),
    ("3", "Catalog path bypassed dispatch_process", "Single 18s timeout, no outer-timeout cancellation. process_lane_node now calls the real ACP dispatch."),
]

STATS = [
    ("179/180", "unit tests"),
    ("206/206", "acceptance tests"),
    ("33/33", "integration tests"),
]


def _draw_gap_cards(slide) -> None:
    x, w = 0.82, 5.55
    card_h = 1.35
    for i, (num, title, desc) in enumerate(GAPS):
        y = 1.95 + i * (card_h + 0.12)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(card_h))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = COLOR_INTENT
        card.line.width = Pt(1.25)
        card.shadow.inherit = False
        badge = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.12), Inches(y + 0.12), Inches(0.42), Inches(0.42))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_INTENT
        badge.line.fill.background()
        badge.shadow.inherit = False
        btf = badge.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.text = num
        bp.alignment = PP_ALIGN.CENTER
        bp.font.bold = True
        bp.font.size = Pt(16)
        bp.font.color.rgb = WHITE
        _text(slide, Inches(x + 0.68), Inches(y + 0.08), Inches(w - 0.8), Inches(0.3), title, size=13, bold=True, color=TITLE_INK)
        _text(slide, Inches(x + 0.68), Inches(y + 0.40), Inches(w - 0.8), Inches(0.9), desc, size=11, color=INK)


def _draw_speedup_chart(slide) -> None:
    chart_data = CategoryChartData()
    chart_data.categories = ["Cache miss\n(cold, real OpenCode call)", "Cache hit\n(repeat query)"]
    chart_data.add_series("Response time (seconds)", (19.2, 0.02))

    gframe = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(6.85), Inches(1.95), Inches(5.55), Inches(3.55), chart_data
    )
    chart = gframe.chart
    chart.has_legend = False
    chart.has_title = True
    chart.chart_title.text_frame.text = "Verified live: cache-hit speedup"
    chart.chart_title.text_frame.paragraphs[0].font.size = Pt(13)
    chart.chart_title.text_frame.paragraphs[0].font.bold = True

    plot = chart.plots[0]
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = '0.00"s"'
    dl.number_format_is_linked = False
    dl.font.size = Pt(12)
    dl.font.bold = True
    dl.font.color.rgb = TITLE_INK

    series = plot.series[0]
    series.format.fill.solid()
    series.format.fill.fore_color.rgb = COLOR_CACHE

    category_axis = chart.category_axis
    category_axis.tick_labels.font.size = Pt(10)
    value_axis = chart.value_axis
    value_axis.has_title = True
    value_axis.axis_title.text_frame.text = "Seconds"
    value_axis.axis_title.text_frame.paragraphs[0].font.size = Pt(10)

    _text(
        slide,
        Inches(6.85),
        Inches(5.62),
        Inches(5.55),
        Inches(0.4),
        "~960x faster — same answer, identical bytes.",
        size=14,
        bold=True,
        color=COLOR_CACHE,
        align=PP_ALIGN.CENTER,
    )


def _draw_stat_strip(slide) -> None:
    x0, w, gap = 6.85, 1.75, 0.15
    y = 6.15
    for i, (value, label) in enumerate(STATS):
        x = x0 + i * (w + gap)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.62))
        card.fill.solid()
        card.fill.fore_color.rgb = TITLE_INK
        card.line.fill.background()
        card.shadow.inherit = False
        tf = card.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_top = Pt(1)
        tf.margin_bottom = Pt(1)
        p0 = tf.paragraphs[0]
        p0.text = value
        p0.alignment = PP_ALIGN.CENTER
        p0.font.bold = True
        p0.font.size = Pt(15)
        p0.font.color.rgb = WHITE
        p1 = tf.add_paragraph()
        p1.text = label
        p1.alignment = PP_ALIGN.CENTER
        p1.font.size = Pt(9)
        p1.font.color.rgb = PALE


def build_slide3(slide, *, page: int) -> None:
    draw_pro_chrome(
        slide,
        title=SLIDE3_TITLE,
        subtitle="What a faithful audit found, and how it was verified",
        badge=_BADGE,
        page=page,
    )
    panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.64), Inches(1.38), Inches(12.0), Inches(5.45))
    _rgb_panel(panel, PANEL_BG)
    _draw_gap_cards(slide)
    _draw_speedup_chart(slide)
    _draw_stat_strip(slide)
    _text(
        slide,
        Inches(0.82),
        Inches(6.65),
        Inches(5.55),
        Inches(0.3),
        "Branch: feature/lg-catalog-probe-intent — standalone, not merged into dev/main/releases.",
        size=10,
        color=COLOR_LABEL,
    )


# ---------------------------------------------------------------------------
# Slide management — find/reuse/insert
# ---------------------------------------------------------------------------

BUILDERS = {SLIDE1_TITLE: build_slide1, SLIDE2_TITLE: build_slide2, SLIDE3_TITLE: build_slide3}


def _find_slide_by_title(prs: Presentation, title_prefix: str) -> int | None:
    for i, slide in enumerate(prs.slides):
        for sh in slide.shapes:
            if sh.has_text_frame and (sh.text or "").strip().startswith(title_prefix):
                return i
    return None


def _clear_slide(slide) -> None:
    for sh in list(slide.shapes):
        el = sh._element
        el.getparent().remove(el)


def _repurpose_old_single_slide(prs: Presentation) -> int | None:
    """Find the older one-slide version of this content, if present, and
    return its index so the caller can overwrite it in place as SLIDE1 —
    avoids any slide deletion (python-pptx's add_slide() can mis-allocate a
    colliding part name across multiple add_slide() calls in one run after a
    manual _sldIdLst removal, even with drop_rel; rewriting in place sidesteps
    that entirely)."""
    for title in _OLD_SINGLE_SLIDE_TITLES:
        idx = _find_slide_by_title(prs, title)
        if idx is not None:
            return idx
    return None


def _ensure_slide(prs: Presentation, title: str, *, before_title: str, reuse_index: int | None = None) -> None:
    builder = BUILDERS[title]
    existing = reuse_index if reuse_index is not None else _find_slide_by_title(prs, title)
    if existing is not None:
        slide = prs.slides[existing]
        _clear_slide(slide)
        builder(slide, page=existing + 1)
        return
    insert_at = _find_slide_by_title(prs, before_title)
    if insert_at is None:
        insert_at = len(prs.slides)
    slide = insert_slide_at(prs, insert_at)
    builder(slide, page=insert_at + 1)


def main() -> None:
    if not DECK.is_file():
        raise SystemExit(f"Missing deck: {DECK}")
    prs = Presentation(str(DECK))

    reuse_index = _repurpose_old_single_slide(prs)
    if reuse_index is not None:
        _ensure_slide(prs, SLIDE1_TITLE, before_title="", reuse_index=reuse_index)
        _ensure_slide(prs, SLIDE2_TITLE, before_title=_PROGRESS_TITLE)
        _ensure_slide(prs, SLIDE3_TITLE, before_title=_PROGRESS_TITLE)
    else:
        _ensure_slide(prs, SLIDE3_TITLE, before_title=_PROGRESS_TITLE)
        _ensure_slide(prs, SLIDE2_TITLE, before_title=SLIDE3_TITLE)
        _ensure_slide(prs, SLIDE1_TITLE, before_title=SLIDE2_TITLE)

    renumber_footer(prs)

    tmp = DECK.with_name(f"{DECK.stem}_lg{DECK.suffix}")
    prs.save(str(tmp))
    try:
        shutil.copy2(tmp, DECK)
        tmp.unlink(missing_ok=True)
        print(f"Updated {DECK} — now {len(prs.slides)} slides (3 LangGraph slides: diagram, table, chart)")
    except PermissionError:
        print(f"PPT is open — saved to {tmp}")
        print("Close PowerPoint, then copy the patched file over the deck.")


if __name__ == "__main__":
    main()
