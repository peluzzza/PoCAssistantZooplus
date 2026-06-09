#!/usr/bin/env python3
"""Generate HISTORIA_DEL_PROYECTO.md from full git log (all branches, chronological)."""

from __future__ import annotations

import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "HISTORIA_DEL_PROYECTO.md"

# Chapter boundaries: first commit hash that starts each era (chronological)
CHAPTERS = [
    ("Prólogo — El encargo", "Coding Task zooplus: cinco FRs, RAG híbrido, guardrails, repo production-ready, entrevista 15 min."),
    ("Capítulo 1 — Fundación (3 jun, tarde)", "a6f9d26", "P0 bootstrap, EDA (T1), ingest Chroma (T2), quality gates, pipeline T3–T6, tag v1.0.0."),
    ("Capítulo 2 — Stream y evaluación (3 jun, noche)", "c51836b", "Golden queries, /chat/stream NDJSON, topic guard G1, híbrido BM25+vector v1.2."),
    ("Capítulo 3 — Producción y demos (3–4 jun)", "3d5603b", "Docker, runbook, demo pack v2.2, acceptance suite, OpenCode UI."),
    ("Capítulo 4 — Agentic social y seguridad (4 jun)", "151a43c", "Chat UI, guardrails 500 fix, cascade agentic, matrix 173/173, baseline releases v0.1.0."),
    ("Capítulo 5 — Rama releases y wizard (4–5 jun)", "bcaff4c", "Slim releases, PPT base, setup wizard, QUICKSTART, prod cleanup."),
    ("Capítulo 6 — Latencia y conductor (6 jun)", "cb40821", "Conductor-first, per-agent LLMs, status stream, caché, git workflow chain."),
    ("Capítulo 7 — Live loop v1.4 (7 jun)", "1d4411d", "Chunks sociales cada 5s, merge a releases, smoke F1/F3."),
    ("Capítulo 8 — Conductor invisible v2.0–v2.1 (7 jun)", "e041fc8", "Orquestador MD, playbook, intent rápido v2.1.3, multilingual agent-driven."),
    ("Capítulo 9 — Especies, picks dinámicos, phrase index (8 jun)", "835f3a0", "v2.1.4–v2.1.6: species inference, product_batch, social help routing, PPT."),
    ("Capítulo 10 — Pulido entrevista (8–9 jun)", "1b03e4b", "Paneles código FR, inglés en deck, saludo, CUSTOMER_VOICE, docs sync, QA/script solo en main."),
    ("Epílogo", "Estado al HEAD de main: código v2.1.6 alineado con releases; QA, speaker script e historia solo en main."),
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
        "Capítulo 1 — Fundación (3 jun, tarde)": [
            "**Objetivo:** cumplir el Coding Task desde cero en una sola tarde.",
            "Se levanta el repo (P0), se explora el dataset (T1 EDA), se indexa Chroma con `site_id` (T2).",
            "CI con ruff, unit, integration, e2e; primer fix de workflow inválido en GitHub Actions.",
            "Pipeline dual-lane: topic guard, MCP, ACP, orquestador async — **FR1–FR4** en marcha.",
            "Merge a `dev` y plan de release **v1.0.0**.",
        ],
        "Capítulo 4 — Agentic social y seguridad (4 jun)": [
            "Chat UI + síntesis OpenCode opcional; fixes de `.env`, rutas `/ui`, timeout 12s.",
            "**INC-001:** 500 en guardrails por timeout de síntesis — bugfix dedicado.",
            "Firewall default-deny; declines cálidos; social rápido sin RAG en saludos.",
            "Matrix de tests 173/173; nace la línea **releases** desde baseline agentic v0.1.0.",
        ],
        "Capítulo 6 — Latencia y conductor (6 jun)": [
            "**Conductor-first:** clasificar antes de Chroma — lección clave de latencia.",
            "Modelos OpenCode por agente; stream de estado desde backend (no timers falsos en UI).",
            "Caché TTL, RAG en paralelo; política de idioma: UI en inglés, agente multilingüe.",
            "Cadena git formalizada: feature → dev → main → releases.",
        ],
        "Capítulo 7 — Live loop v1.4 (7 jun)": [
            "Chunks sociales cada ~5s mientras el catálogo corre en paralelo — UX «humana».",
            "Varios merges main→releases; stash WIP en PPT.",
            "Smoke F1 inestable → fix de product browse hint.",
        ],
        "Capítulo 8 — Conductor invisible v2.0–v2.1 (7 jun)": [
            "Conductor OpenCode invisible: `emit_message` / `wait` / `complete` por tick.",
            "`conductor_playbook.md` aprende frases prohibidas y especies.",
            "v2.1.3: intent-agent primero (menos latencia); stream en paralelo.",
        ],
        "Capítulo 9 — Especies, picks dinámicos, phrase index (8 jun)": [
            "v2.1.4: inferencia dinámica de especies (iguanas, capibaras…) sin lista fija.",
            "v2.1.6: 4 picks por defecto, hasta 20 si el shopper pide; `product_batch` en UI.",
            "Índice `social_phrases.yaml`; help social no dispara progreso de catálogo.",
            "PPT: diagramas v2.1.6; slides 5–6 con texto solapado — varios fixes de layout.",
        ],
        "Capítulo 10 — Pulido entrevista (8–9 jun)": [
            "Paneles de código FR en PPT (slides 3–4, 6, 9–10); demos traducidas al inglés.",
            "Bug saludo: respuesta empezaba por «for this shop.» — strip parcial del intro.",
            "«Can you help» + petición de producto → catálogo, no FAQ del sistema.",
            "**CUSTOMER_VOICE:** tono profesional, sin manual técnico al cliente.",
            "QA y speaker script **solo en main**; releases lleva PPT + checklist únicamente.",
            "Fast-forward `releases` → `main` para alinear código; se restauran QA y PRESENTATION en main.",
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
        "# Historia del proyecto — zooplus Assistant PoC",
        "",
        "**Repositorio:** [peluzzza/PoCAssistantZooplus](https://github.com/peluzzza/PoCAssistantZooplus)  ",
        f"**Commits registrados (todas las ramas, orden cronológico):** {len(commits)}  ",
        "**Generado:** script `scripts/build_work_history.py` — actualizar tras hitos nuevos.",
        "",
        "> Un libro de trabajo: objetivos, entregas, errores, reverts y promoción de ramas.",
        "",
        "---",
        "",
    ]

    lines.append(f"## {CHAPTERS[0][0]}")
    lines.append("")
    lines.append(CHAPTERS[0][1])
    lines.append("")
    lines.append("**Ramas principales:**")
    lines.append("- `feature/*` → experimentación por hito (T1, T2, v1.1 stream, v1.4 chunks, v2.0 conductor…)")
    lines.append("- `dev` → integración")
    lines.append("- `main` → historial completo, QA interno, speaker script, **esta historia**")
    lines.append("- `releases` → línea de entrega take-home / entrevista (slim)")
    lines.append("")
    lines.append("**Tags relevantes:** `v0.1.0`, `v1.0.0`, `v1.1.0`, `v1.2.0`, `v1.4.0`, `v2.0.0`, `v2.1.0` … working tree **v2.1.6**.")
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
            lines.append("**Incidentes / fixes en este tramo:**")
            lines.append("")
            for c in incidents[:12]:
                lines.append(f"- `{c['hash']}` ({c['date']}) — {c['subject']}")
            if len(incidents) > 12:
                lines.append(f"- … y {len(incidents) - 12} fixes más en el apéndice.")
            lines.append("")
        lines.append("<details>")
        lines.append(f"<summary>Commits del capítulo ({len(ch_commits)})</summary>")
        lines.append("")
        lines.append("| Fecha | Hash | Mensaje | Ramas/tags |")
        lines.append("|-------|------|---------|-------------|")
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
    lines.append(f"**HEAD actual al generar:** `{branch}` @ `{head}`")
    lines.append("")
    lines.append("**Entregables en `releases`:** PPT pro (14 slides), checklist, README, API en :8090.")
    lines.append("")
    lines.append("**Solo en `main`:** `QA_FOR_POC.md`, `PRESENTATION_15MIN.md`, `docs/HISTORIA_DEL_PROYECTO.md`.")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Apéndice A — Cronología completa (commit a commit)")
    lines.append("")
    lines.append("| # | Fecha | Hash | Autor | Mensaje |")
    lines.append("|---|-------|------|-------|---------|")
    for n, c in enumerate(commits, 1):
        subj = c["subject"].replace("|", "/")
        lines.append(f"| {n} | {c['date']} | `{c['hash']}` | {c['author']} | {subj} |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Apéndice B — Errores, reverts y lecciones")
    lines.append("")
    lessons = [
        ("CI workflow inválido", "5502a55", "Primer workflow de quality gates no pasaba validación de GitHub Actions."),
        ("G1 benchmark imports", "5c4e2c4", "Benchmark movido a `src.guardian` para imports en unit tests."),
        ("Guardrails 500", "e19c7fb", "Timeout de síntesis disparaba 500 — INC-001."),
        ("OpenCode bloquea UI", "fix(chat)", "Cap de síntesis 12s y path social rápido."),
        ("Intent spam help", "fix(intent)", "Fallback por tema cuando falla OpenCode intent."),
        ("PPT solapamientos", "5fa20a3", "Columnas v1.4+v2.x apiladas en slides 5–6 — `_rebuild_two_columns`."),
        ("Saludo roto", "b96a997", "Strip de intro dejaba «for this shop.» al inicio."),
        ("Help vs shopping", "1a7943e", "«can you help» en query de producto iba a FAQ, no a RAG."),
        ("EDA accidental en releases", "c23249c", "Revert de `docs/01-eda-report.md` incluido por error en commit de docs."),
        ("Stash WIP PPT", "b9de817", "Trabajo en curso en deck guardado en stash durante v1.4."),
        ("Revert multilingual forzado", "bf9bd50", "Se revierte inglés forzado en prompts; UI EN, agente multilingüe."),
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
