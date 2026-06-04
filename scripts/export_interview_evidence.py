#!/usr/bin/env python3
"""Write a timestamped evidence snapshot for interview defense (English)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "interview"
OUT_FILE = OUT_DIR / "EVIDENCE_SNAPSHOT.md"

CATALOG_ORDER = ROOT / "docs" / "instructions" / "order" / "product_catalog_dataset.json"
CATALOG_INSTRUCTIONS = ROOT / "docs" / "instructions" / "product_catalog_dataset.json"
MATRIX_TRACE = ROOT / "docs" / "trace" / "sessions" / "use-case-matrix-latest.json"
MATRIX_FIXTURE = ROOT / "tests" / "fixtures" / "use_cases_matrix.json"


def _catalog_path() -> Path:
    if CATALOG_INSTRUCTIONS.is_file():
        return CATALOG_INSTRUCTIONS
    return CATALOG_ORDER


def _catalog_stats() -> dict:
    rows = json.loads(_catalog_path().read_text(encoding="utf-8"))
    from collections import Counter

    return {
        "records": len(rows),
        "sites": dict(Counter(int(r["site_id"]) for r in rows)),
        "pets": dict(Counter(str(r["pet_type"]) for r in rows)),
        "locales": dict(Counter(str(r["locale"]) for r in rows)),
    }


def _matrix_info() -> dict:
    info: dict = {"fixture_cases": 0, "last_run": None}
    if MATRIX_FIXTURE.is_file():
        cases = json.loads(MATRIX_FIXTURE.read_text(encoding="utf-8"))
        info["fixture_cases"] = len(cases)
    if MATRIX_TRACE.is_file():
        info["last_run"] = json.loads(MATRIX_TRACE.read_text(encoding="utf-8"))
    return info


def _pytest_count() -> str:
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        tail = (proc.stdout or proc.stderr or "").strip().splitlines()
        return tail[-1] if tail else "unknown"
    except Exception as exc:  # noqa: BLE001
        return f"collect failed: {exc}"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stats = _catalog_stats()
    matrix = _matrix_info()
    collected = _pytest_count()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Evidence snapshot (auto-generated)",
        "",
        f"**Generated:** {ts}",
        f"**Repo:** `{ROOT.name}`",
        "",
        "## Catalog (`instructions/order` or instructions copy)",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Records | {stats['records']} |",
        f"| Sites | {stats['sites']} |",
        f"| Pet types | {stats['pets']} |",
        f"| Locales | {stats['locales']} |",
        "",
        "## Test suite",
        "",
        f"- Pytest collect: `{collected}`",
        "",
        "## Use-case matrix",
        "",
        f"- Fixture cases: **{matrix['fixture_cases']}**",
        "",
    ]
    last = matrix.get("last_run")
    if last:
        lines.extend(
            [
                f"- Last E2E run: **{last.get('timestamp', 'n/a')}**",
                f"- Cases in run: **{last.get('cases', 'n/a')}**",
                f"- Pytest exit code: **{last.get('pytest_exit_code', 'n/a')}**",
                "",
            ]
        )
    else:
        lines.append("- Last E2E run: *no `use-case-matrix-latest.json` yet*")
        lines.append("")

    lines.extend(
        [
            "## Regenerate",
            "",
            "```bash",
            "python scripts/build_use_case_matrix.py",
            "python scripts/run_use_case_matrix.py",
            "python scripts/export_interview_evidence.py",
            "```",
            "",
            "See also: [`docs/INTERVIEW_DEFENSE.md`](../INTERVIEW_DEFENSE.md)",
            "",
        ]
    )

    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
