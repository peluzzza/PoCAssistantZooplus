#!/usr/bin/env python3
"""Insert three dedicated "LangGraph approach" slides before the closing
Release-progress slide. This deck (releases, v2.1.6 baseline) carries no
LangGraph code — the slides document the approach in technical detail and
point to the standalone showcase branch (feature/lg-catalog-probe-intent)
where it's actually implemented. Idempotent — re-running updates content
instead of duplicating slides.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from patch_interview_pptx_rag_slides import (  # type: ignore[import-not-found]
    PANEL_BG,
    _bullets,
    draw_pro_chrome,
    insert_slide_at,
    renumber_footer,
)
from patch_interview_pptx_rag_slides import _rgb as _rgb_panel  # type: ignore[import-not-found]
from pptx import Presentation
from pptx.util import Inches

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "docs" / "deliverables" / "v0.1" / "zooplus-assistant-interview-15min-pro.pptx"

# (title_prefix used to find/replace, subtitle, badge, left_bullets, right_bullets)
SLIDE1_TITLE = "LangGraph 1/3 — explicit graph vs Python branches"
SLIDE1_LEFT = [
    ("The problem this explores", True),
    ("• Legacy: one async function (_handle_chat_inner) with nested", False),
    ("  if/elif per lane — retry/fallback chains hidden inside helpers.", False),
    ("• Hard to unit-test one decision in isolation — e.g. \"what happens", False),
    ("  on an intent timeout?\" — without exercising the whole function.", False),
    ("Same agentic core, explicit shape", True),
    ("• feature/lg-catalog-probe-intent — StateGraph: nodes are", False),
    ("  functions, edges are typed routing functions, independently", False),
    ("  testable in isolation (pure dict in, string out).", False),
    ("• Every node calls THIS repo's own functions verbatim — zero", False),
    ("  re-implemented logic, nothing invented.", False),
]
SLIDE1_RIGHT = [
    ("Graph topology (7 nodes, all async)", True),
    ("START → cache_check", False),
    ("  ├─ cache hit  → END (cached answer, ~0.02s)", False),
    ("  └─ cache miss → classify_intent", False),
    ("classify_intent → [route_by_lane]", False),
    ("  ├─ social (decline_off_topic | conversational) ──┐", False),
    ("  └─ prefetch → process_lane ─────────────────────┤", False),
    ("                                    cache_store → END", False),
    ("4 routing functions; graph.ainvoke(), not graph.invoke().", False),
]

SLIDE2_TITLE = "LangGraph 2/3 — every node, what it calls"
SLIDE2_LEFT = [
    ("Social path", True),
    ("• classify_intent → orchestrator._classify_intent_bounded() —", False),
    ("  same 22s timeout, same _fallback_intent_decision() fallback.", False),
    ("• social_node → social_agent.social_reply() — unchanged behaviour,", False),
    ("  only made async.", False),
    ("Cache path (new)", True),
    ("• cache_check_node / cache_store_node → the SAME chat_cache", False),
    ("  singleton + key format (site_id:query.lower()) the legacy", False),
    ("  orchestrator already uses — not a separate cache.", False),
]
SLIDE2_RIGHT = [
    ("Catalog path", True),
    ("• prefetch_node → resolve_recommendation_count + price_band +", False),
    ("  retrieval_pool_size + search_catalog — orchestrator step 3.", False),
    ("• process_lane_node → dispatch_process(envelope, run_process_lane,", False),
    ("  timeout=<constraints.yaml>) — the real nested 40s outer /", False),
    ("  18s inner synthesis timeout, replacing two nodes that had", False),
    ("  re-derived retrieval + synthesis + template fallback inline.", False),
    ("Result", True),
    ("• rag_node + synthesis_node deleted — process_lane_node replaces", False),
    ("  both with one verbatim call into the existing ACP dispatch.", False),
]

SLIDE3_TITLE = "LangGraph 3/3 — audit findings & verified results"
SLIDE3_LEFT = [
    ("3 real gaps found in the first migration", True),
    ("1. preferred_model (UI's per-request model override) was stored", False),
    ("   in graph state but no node ever read it — silently inert.", False),
    ("   Fixed: ContextVar set for the whole graph run, mirroring", False),
    ("   handle_chat()'s own wrapper.", False),
    ("2. No chat-level cache existed on the LangGraph path at all.", False),
    ("3. Catalog path bypassed dispatch_process — one 18s timeout, no", False),
    ("   outer-timeout cancellation message was ever reachable.", False),
]
SLIDE3_RIGHT = [
    ("Verified live against the running server", True),
    ("• preferred_model: requested opencode/deepseek-v4-flash-free →", False),
    ("  that exact value now echoed in meta.llm_model (previously", False),
    ("  always silently ignored).", False),
    ("• Cache: identical repeat query — 19.2s (cold) → 0.02s (hit),", False),
    ("  same answer.", False),
    ("Test coverage", True),
    ("• 179/180 unit (+19 new tests for the 3 gaps), 206/206", False),
    ("  acceptance, 33/33 integration — ZOOPLUS_ORCHESTRATOR=langchain.", False),
    ("• Branch: feature/lg-catalog-probe-intent — standalone, not", False),
    ("  merged into dev/main/releases.", False),
]

SLIDES = [
    (SLIDE1_TITLE, "Same agentic core, new explicit state graph", SLIDE1_LEFT, SLIDE1_RIGHT),
    (SLIDE2_TITLE, "Every node is a verbatim call into this repo's own functions", SLIDE2_LEFT, SLIDE2_RIGHT),
    (SLIDE3_TITLE, "What a faithful audit found, and how it was verified", SLIDE3_LEFT, SLIDE3_RIGHT),
]

def build_langgraph_slide(slide, *, title: str, subtitle: str, left, right, page: int) -> None:
    draw_pro_chrome(slide, title=title, subtitle=subtitle, badge="Architecture · LG", page=page)
    panel = slide.shapes.add_shape(1, Inches(0.64), Inches(1.38), Inches(12.0), Inches(5.45))
    _rgb_panel(panel, PANEL_BG)
    _bullets(slide, Inches(0.82), Inches(1.55), Inches(5.85), Inches(5.1), left, size=13)
    _bullets(slide, Inches(6.7), Inches(1.55), Inches(5.75), Inches(5.1), right, size=13)


def _find_slide_by_title(prs: Presentation, title_prefix: str) -> int | None:
    for i, slide in enumerate(prs.slides):
        for sh in slide.shapes:
            if sh.has_text_frame and (sh.text or "").strip().startswith(title_prefix):
                return i
    return None


_OLD_SINGLE_SLIDE_TITLES = ("LangGraph orchestrator", "LangGraph approach")
_PROGRESS_TITLE = "Release progress"


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


def _ensure_slide(
    prs: Presentation, title: str, subtitle: str, left, right, *, before_title: str, reuse_index: int | None = None
) -> None:
    existing = reuse_index if reuse_index is not None else _find_slide_by_title(prs, title)
    if existing is not None:
        slide = prs.slides[existing]
        for sh in list(slide.shapes):
            el = sh._element
            el.getparent().remove(el)
        build_langgraph_slide(slide, title=title, subtitle=subtitle, left=left, right=right, page=existing + 1)
        return
    insert_at = _find_slide_by_title(prs, before_title)
    if insert_at is None:
        insert_at = len(prs.slides)
    slide = insert_slide_at(prs, insert_at)
    build_langgraph_slide(slide, title=title, subtitle=subtitle, left=left, right=right, page=insert_at + 1)


def main() -> None:
    if not DECK.is_file():
        raise SystemExit(f"Missing deck: {DECK}")
    prs = Presentation(str(DECK))

    # If an older one-slide version exists, repurpose it in place as SLIDE1
    # instead of deleting + re-adding (avoids a python-pptx part-name
    # collision when add_slide() runs multiple times after a manual
    # _sldIdLst removal in the same session — see _repurpose_old_single_slide).
    reuse_index = _repurpose_old_single_slide(prs)
    if reuse_index is not None:
        _ensure_slide(prs, SLIDE1_TITLE, SLIDES[0][1], SLIDE1_LEFT, SLIDE1_RIGHT, before_title="", reuse_index=reuse_index)
        _ensure_slide(prs, SLIDE2_TITLE, SLIDES[1][1], SLIDE2_LEFT, SLIDE2_RIGHT, before_title=_PROGRESS_TITLE)
        _ensure_slide(prs, SLIDE3_TITLE, SLIDES[2][1], SLIDE3_LEFT, SLIDE3_RIGHT, before_title=_PROGRESS_TITLE)
    else:
        # Insert/update in order, each anchored just before "Release progress"
        # (or before the next LG slide, once it exists) so the three stay together.
        _ensure_slide(prs, SLIDE3_TITLE, SLIDES[2][1], SLIDE3_LEFT, SLIDE3_RIGHT, before_title=_PROGRESS_TITLE)
        _ensure_slide(prs, SLIDE2_TITLE, SLIDES[1][1], SLIDE2_LEFT, SLIDE2_RIGHT, before_title=SLIDE3_TITLE)
        _ensure_slide(prs, SLIDE1_TITLE, SLIDES[0][1], SLIDE1_LEFT, SLIDE1_RIGHT, before_title=SLIDE2_TITLE)

    renumber_footer(prs)

    tmp = DECK.with_name(f"{DECK.stem}_lg{DECK.suffix}")
    prs.save(str(tmp))
    try:
        shutil.copy2(tmp, DECK)
        tmp.unlink(missing_ok=True)
        print(f"Updated {DECK} — now {len(prs.slides)} slides (3 LangGraph slides)")
    except PermissionError:
        print(f"PPT is open — saved to {tmp}")
        print("Close PowerPoint, then copy the patched file over the deck.")


if __name__ == "__main__":
    main()
