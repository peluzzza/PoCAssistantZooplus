#!/usr/bin/env python3
"""Run lint + unit + integration + e2e before merge (Python 3.11 aligned)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.resolve_python import preferred_python  # noqa: E402


def run(cmd: list[str]) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd)


def main() -> int:
    py = preferred_python()
    steps: list[tuple[str, list[str]]] = [
        ("ruff check", [py, "-m", "ruff", "check", "cli", "src", "tests"]),
        ("ruff format", [py, "-m", "ruff", "format", "--check", "cli", "src", "tests"]),
        ("unit", [py, "-m", "pytest", "tests/unit", "-q", "-m", "unit"]),
        ("integration", [py, "-m", "pytest", "tests/integration", "-q", "-m", "integration"]),
        (
            "acceptance",
            [py, "-m", "pytest", "tests/acceptance", "-q", "-m", "acceptance"],
        ),
        (
            "security",
            [py, "-m", "pytest", "tests/security", "-q", "-m", "security"],
        ),
        ("social", [py, "-m", "pytest", "tests/social", "-q", "-m", "social"]),
        ("agentic", [py, "-m", "pytest", "tests/agentic", "-q", "-m", "agentic"]),
        ("e2e", [py, "-m", "pytest", "tests/e2e", "-q", "-m", "e2e"]),
    ]
    for name, cmd in steps:
        if run(cmd) != 0:
            print(f"FAILED: {name}", file=sys.stderr)
            return 1
    print("All quality gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
