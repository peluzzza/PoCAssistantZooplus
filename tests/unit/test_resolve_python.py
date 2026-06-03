"""Unit tests — Python 3.11 resolver."""

import sys

import pytest
from scripts.resolve_python import preferred_python

pytestmark = pytest.mark.unit


def test_preferred_python_returns_executable() -> None:
    path = preferred_python()
    assert path
    assert "python" in path.lower() or path.endswith(".exe")


def test_version_policy_documented() -> None:
    assert sys.version_info >= (3, 11)
