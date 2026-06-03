#!/usr/bin/env python3
"""Run lint + unit + integration + e2e before merge."""

from __future__ import annotations

import subprocess
import sys


def run(cmd: list[str]) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd)


def main() -> int:
    steps: list[tuple[str, list[str]]] = [
        ("ruff check", [sys.executable, "-m", "ruff", "check", "cli", "src", "tests"]),
        ("ruff format", [sys.executable, "-m", "ruff", "format", "--check", "cli", "src", "tests"]),
        ("unit", [sys.executable, "-m", "pytest", "tests/unit", "-q", "-m", "unit"]),
        ("integration", [sys.executable, "-m", "pytest", "tests/integration", "-q", "-m", "integration"]),
        ("e2e", [sys.executable, "-m", "pytest", "tests/e2e", "-q", "-m", "e2e"]),
    ]
    for name, cmd in steps:
        if run(cmd) != 0:
            print(f"FAILED: {name}", file=sys.stderr)
            return 1
    print("All quality gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
