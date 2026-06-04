#!/usr/bin/env python3
"""Run 50+ use-case matrix and write trace report."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "use_cases_matrix.json"
REPORT = ROOT / "docs" / "trace" / "sessions" / "use-case-matrix-latest.json"
MARKDOWN = ROOT / "docs" / "instructions" / "USE_CASES.md"


def _generate_markdown(cases: list[dict]) -> str:
    lines = [
        "# Use case matrix (Coding Task + instructions catalog)",
        "",
        f"**Generated:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"**Total cases:** {len(cases)}  ",
        "**Source of truth:** `docs/instructions/Coding Task.docx`, "
        "`docs/instructions/product_catalog_dataset.json`",
        "",
        "| ID | Req | Branch | Site | Query (excerpt) | Expected |",
        "|----|-----|--------|------|-----------------|----------|",
    ]
    for c in cases:
        exp = c["expect"]
        outcome = "DECLINE" if exp.get("decline") else f"≥{exp.get('min_products', 0)} products"
        q = c["query"].replace("|", "\\|")
        if len(q) > 55:
            q = q[:52] + "..."
        lines.append(
            f"| {c['id']} | {c['requirement']} | {c['branch']} | {c['site_id']} | {q} | {outcome} |"
        )
    lines.extend(
        [
            "",
            "## Requirement mapping (Coding Task)",
            "",
            "| Req | Description | Covered by branches |",
            "|-----|-------------|---------------------|",
            "| B1 | Async FastAPI | `contract` + pytest async |",
            "| B2 | POST /chat contract | all matrix + API tests |",
            "| B3 | answer + retrieved_products | all matrix |",
            "| B4 | RAG catalog-only | `product_search`, grounding asserts |",
            "| B5 | site_id scoping | per-site cases + isolation |",
            "| B6 | pet-only guardrails | `guardrail_decline` |",
            "| B7–B9 | README, structure, evaluation | acceptance + repo tests |",
            "",
            "## Run automated matrix",
            "",
            "```bash",
            "python -m cli ingest",
            "set ZOOPLUS_SYNTHESIS_MODE=template",
            "python scripts/run_use_case_matrix.py",
            "pytest tests/social -q -m social",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_use_case_matrix.py")],
        check=True,
        cwd=str(ROOT),
    )
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))
    MARKDOWN.write_text(_generate_markdown(cases), encoding="utf-8")

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/social/test_use_cases_matrix.py",
        "-q",
        "-m",
        "social",
        "--tb=no",
        "-q",
    ]
    print("+", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)

    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "cases": len(cases),
        "pytest_exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-2000:] if proc.stdout else "",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Report: {REPORT}")
    print(f"Matrix doc: {MARKDOWN}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
