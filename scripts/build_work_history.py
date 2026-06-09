#!/usr/bin/env python3
"""Generate PROJECT_WORK_HISTORY.md from full git log (all branches, chronological)."""

from __future__ import annotations

import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "PROJECT_WORK_HISTORY.md"

# Chapter boundaries: first commit hash that starts each era (chronological)
CHAPTERS = [
    (
        "Prologue — The brief",
        "zooplus Coding Task: five FRs, hybrid RAG, guardrails, production-ready repo, 15-minute interview.",
    ),
    (
        "Chapter 1 — Foundation (3 Jun, afternoon)",
        "a6f9d26",
        "P0 bootstrap, EDA (T1), Chroma ingest (T2), quality gates, pipeline T3–T6, tag v1.0.0.",
    ),
    (
        "Chapter 2 — Stream and evaluation (3 Jun, evening)",
        "c51836b",
        "Golden queries, /chat/stream NDJSON, topic guard G1, hybrid BM25+vector v1.2.",
    ),
    (
        "Chapter 3 — Production and demos (3–4 Jun)",
        "3d5603b",
        "Docker, runbook, demo pack v2.2, acceptance suite, OpenCode UI.",
    ),
    (
        "Chapter 4 — Agentic social and security (4 Jun)",
        "151a43c",
        "Chat UI, guardrails 500 fix, agentic cascade, matrix 173/173, releases baseline v0.1.0.",
    ),
    (
        "Chapter 5 — Releases branch and wizard (4–5 Jun)",
        "bcaff4c",
        "Slim releases, PPT base, setup wizard, QUICKSTART, prod cleanup.",
    ),
    (
        "Chapter 6 — Latency and conductor (6 Jun)",
        "cb40821",
        "Conductor-first, per-agent LLMs, status stream, cache, git workflow chain.",
    ),
    (
        "Chapter 7 — Live loop v1.4 (7 Jun)",
        "1d4411d",
        "Social chunks every 5s, merge to releases, smoke F1/F3.",
    ),
    (
        "Chapter 8 — Invisible conductor v2.0–v2.1 (7 Jun)",
        "e041fc8",
        "MD orchestrator, playbook, fast intent v2.1.3, agent-driven multilingual.",
    ),
    (
        "Chapter 9 — Species, dynamic picks, phrase index (8 Jun)",
        "835f3a0",
        "v2.1.4–v2.1.6: species inference, product_batch, social help routing, PPT.",
    ),
    (
        "Chapter 10 — Interview polish (8–9 Jun)",
        "1b03e4b",
        "FR code panels, English deck, greeting fix, CUSTOMER_VOICE, docs sync; QA/script on main only.",
    ),
    (
        "Epilogue",
        "At main HEAD: v2.1.6 code aligned with releases; work history on both branches; QA and speaker script on main only.",
    ),
]


def load_commits() -> list[dict]:
    raw = subprocess.check_output(
        ["git", "log", "--all", "--reverse", "--format=%H|%ai|%an|%D|%s"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    commits = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("|", 4)
        if len(parts) < 5:
            continue
        full, dt, author, refs, subject = parts
        commits.append(
            {
                "full": full,
                "hash": full[:7],
                "datetime": dt.strip(),
                "date": dt[:10],
                "time": dt[11:19] if len(dt) > 19 else "",
                "author": author.strip(),
                "refs": refs.strip(),
                "subject": subject.strip(),
            }
        )
    return commits


def assign_chapters(commits: list[dict]) -> dict[str, list[dict]]:
    starts = {e[1]: e[0] for e in CHAPTERS if len(e) >= 3}
    start_hashes = set(starts.keys())
    chapter_order = [e[0] for e in CHAPTERS if len(e) >= 3]
    by_chapter: dict[str, list[dict]] = defaultdict(list)
    current = chapter_order[0]
    for c in commits:
        if c["hash"] in start_hashes:
            current = starts[c["hash"]]
        by_chapter[current].append(c)
    return by_chapter


def narrative_bullets(chapter: str) -> list[str]:
    narratives: dict[str, list[str]] = {
        "Chapter 1 — Foundation (3 Jun, afternoon)": [
            "**Goal:** deliver the Coding Task from scratch in a single afternoon.",
            "Bootstrap the repo (P0), explore the dataset (T1 EDA), index Chroma with `site_id` (T2).",
            "CI with ruff, unit, integration, e2e; first fix for an invalid GitHub Actions workflow.",
            "Dual-lane pipeline: topic guard, MCP, ACP, async orchestrator — **FR1–FR4** underway.",
            "Merge to `dev` and plan **v1.0.0** release.",
        ],
        "Chapter 4 — Agentic social and security (4 Jun)": [
            "Chat UI + optional OpenCode synthesis; fixes for `.env`, `/ui` routes, 12s timeout.",
            "**INC-001:** guardrails 500 on synthesis timeout — dedicated bugfix.",
            "Default-deny firewall; warm declines; fast social path without RAG on greetings.",
            "Test matrix 173/173; **releases** line born from agentic baseline v0.1.0.",
        ],
        "Chapter 6 — Latency and conductor (6 Jun)": [
            "**Conductor-first:** classify before Chroma — key latency lesson.",
            "OpenCode models per agent; status stream from backend (no fake UI timers).",
            "TTL cache, parallel RAG; language policy: English UI, multilingual agent replies.",
            "Formal git chain: feature → dev → main → releases.",
        ],
        "Chapter 7 — Live loop v1.4 (7 Jun)": [
            "Social chunks every ~5s while catalog runs in parallel — human-feel UX.",
            "Several main→releases merges; PPT work stashed as WIP.",
            "Unstable smoke F1 → product browse hint fix.",
        ],
        "Chapter 8 — Invisible conductor v2.0–v2.1 (7 Jun)": [
            "Invisible OpenCode conductor: `emit_message` / `wait` / `complete` per tick.",
            "`conductor_playbook.md` learns forbidden phrases and species.",
            "v2.1.3: intent-agent first (lower latency); parallel stream.",
        ],
        "Chapter 9 — Species, dynamic picks, phrase index (8 Jun)": [
            "v2.1.4: dynamic species inference (iguanas, capybaras…) without a fixed list.",
            "v2.1.6: 4 picks by default, up to 20 when the shopper asks; `product_batch` in UI.",
            "`social_phrases.yaml` index; social help does not trigger catalog progress.",
            "PPT: v2.1.6 diagrams; overlapping text on slides 5–6 — several layout fixes.",
        ],
        "Chapter 10 — Interview polish (8–9 Jun)": [
            "FR code panels in PPT (slides 3–4, 6, 9–10); demo phrases translated to English.",
            "Greeting bug: answer started with orphan «for this shop.» — partial intro strip.",
            "«Can you help» + product request → catalog, not system FAQ.",
            "**CUSTOMER_VOICE:** professional tone, no technical manual for shoppers.",
            "QA and speaker script **main only**; releases carries PPT + checklist only.",
            "Fast-forward `releases` → `main` to align code; restore QA and PRESENTATION on main.",
            "Work history published on **main** and **releases** as `PROJECT_WORK_HISTORY.md`.",
        ],
    }
    return narratives.get(chapter, [])


def is_incident(c: dict) -> bool:
    s = c["subject"].lower()
    return any(
        k in s
        for k in (
            "fix(",
            "revert",
            "rollback",
            "accidental",
            "overlap",
            "500",
            "stash",
            "wip",
        )
    )


def build_markdown(commits: list[dict]) -> str:
    by_chapter = assign_chapters(commits)
    lines: list[str] = [
        "# Project work history — zooplus Assistant PoC",
        "",
        "**Repository:** [peluzzza/PoCAssistantZooplus](https://github.com/peluzzza/PoCAssistantZooplus)  ",
        f"**Commits recorded (all branches, chronological):** {len(commits)}  ",
        "**Generated by:** `scripts/build_work_history.py` — re-run after new milestones.",
        "",
        "> A work diary: goals, deliveries, bugs, reverts, and branch promotion.",
        "",
        "---",
        "",
    ]

    lines.append(f"## {CHAPTERS[0][0]}")
    lines.append("")
    lines.append(CHAPTERS[0][1])
    lines.append("")
    lines.append("**Main branches:**")
    lines.append("- `feature/*` → milestone experiments (T1, T2, v1.1 stream, v1.4 chunks, v2.0 conductor…)")
    lines.append("- `dev` → integration")
    lines.append("- `main` → full history, internal QA, speaker script")
    lines.append("- `releases` → take-home / interview delivery line (slim)")
    lines.append("")
    lines.append(
        "**Relevant tags:** `v0.1.0`, `v1.0.0`, `v1.1.0`, `v1.2.0`, `v1.4.0`, `v2.0.0`, `v2.1.0` … working tree **v2.1.6**."
    )
    lines.append("")

    for entry in CHAPTERS[1:-1]:
        if len(entry) < 3:
            continue
        title, _start, summary = entry[0], entry[1], entry[2]
        ch_commits = by_chapter.get(title, [])
        lines.append("---")
        lines.append("")
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"*{summary}*")
        lines.append("")
        for bullet in narrative_bullets(title):
            lines.append(f"- {bullet}")
        lines.append("")
        incidents = [c for c in ch_commits if is_incident(c)]
        if incidents:
            lines.append("**Incidents / fixes in this stretch:**")
            lines.append("")
            for c in incidents[:12]:
                lines.append(f"- `{c['hash']}` ({c['date']}) — {c['subject']}")
            if len(incidents) > 12:
                lines.append(f"- … and {len(incidents) - 12} more fixes in the appendix.")
            lines.append("")
        lines.append("<details>")
        lines.append(f"<summary>Chapter commits ({len(ch_commits)})</summary>")
        lines.append("")
        lines.append("| Date | Hash | Message | Branches/tags |")
        lines.append("|------|------|---------|---------------|")
        for c in ch_commits:
            refs = (c["refs"] or "").replace("|", "/")[:80]
            subj = c["subject"].replace("|", "/")[:100]
            lines.append(f"| {c['date']} {c['time']} | `{c['hash']}` | {subj} | {refs} |")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    ep = CHAPTERS[-1]
    lines.append("---")
    lines.append("")
    lines.append(f"## {ep[0]}")
    lines.append("")
    lines.append(ep[1])
    lines.append("")
    head = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT, text=True).strip()
    lines.append(f"**HEAD when generated:** `{branch}` @ `{head}`")
    lines.append("")
    lines.append("**On `releases`:** pro PPT (14 slides), checklist, README, API on :8090, work history.")
    lines.append("")
    lines.append(
        "**Main only:** `QA_FOR_POC.md`, `PRESENTATION_15MIN.md`. "
        "**Both branches:** `docs/PROJECT_WORK_HISTORY.md`."
    )
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Appendix A — Full chronology (commit by commit)")
    lines.append("")
    lines.append("| # | Date | Hash | Author | Message |")
    lines.append("|---|------|------|--------|---------|")
    for n, c in enumerate(commits, 1):
        subj = c["subject"].replace("|", "/")
        lines.append(f"| {n} | {c['date']} | `{c['hash']}` | {c['author']} | {subj} |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Appendix B — Errors, reverts, and lessons")
    lines.append("")
    lessons = [
        ("Invalid CI workflow", "5502a55", "First quality-gates workflow failed GitHub Actions validation."),
        ("G1 benchmark imports", "5c4e2c4", "Benchmark moved under `src.guardian` for unit test imports."),
        ("Guardrails 500", "e19c7fb", "Synthesis timeout triggered 500 — INC-001."),
        ("OpenCode blocked UI", "fix(chat)", "12s synthesis cap and fast social path."),
        ("Intent spam help", "fix(intent)", "Topic fallback when OpenCode intent fails."),
        ("PPT overlaps", "5fa20a3", "v1.4+v2.x columns stacked on slides 5–6 — `_rebuild_two_columns`."),
        ("Broken greeting", "b96a997", "Intro strip left orphan «for this shop.» at the start."),
        ("Help vs shopping", "1a7943e", "«can you help» inside a product query routed to FAQ, not RAG."),
        ("Accidental EDA on releases", "c23249c", "Revert of `docs/01-eda-report.md` included by mistake in a docs commit."),
        ("Stash WIP PPT", "b9de817", "In-progress deck work saved in stash during v1.4."),
        ("Forced multilingual revert", "bf9bd50", "Reverted forced English in prompts; English UI, multilingual agent."),
    ]
    for title, ref, desc in lessons:
        lines.append(f"- **{title}** (`{ref}`): {desc}")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    commits = load_commits()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_markdown(commits), encoding="utf-8")
    print(f"Wrote {len(commits)} commits -> {OUT}")


if __name__ == "__main__":
    main()
