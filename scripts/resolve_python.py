"""Resolve Python 3.11 executable (align local dev with CI/Docker)."""

from __future__ import annotations

import shutil
import subprocess
import sys


def preferred_python() -> str:
    """Return path to Python 3.11.x, or current executable with warning."""
    if sys.version_info[:2] == (3, 11):
        return sys.executable

    for candidate in ("python3.11", "python311"):
        found = shutil.which(candidate)
        if found:
            return found

    try:
        out = subprocess.run(
            ["py", "-3.11", "-c", "import sys; print(sys.executable)"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        path = out.stdout.strip()
        if path:
            return path
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass

    major, minor = sys.version_info[:2]
    if (major, minor) != (3, 11):
        print(
            f"WARNING: using Python {major}.{minor} locally; CI/Docker target is 3.11. "
            "Install 3.11 (py install 3.11) or use Docker.",
            file=sys.stderr,
        )
    return sys.executable
