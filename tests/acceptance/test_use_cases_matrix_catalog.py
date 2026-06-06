"""Acceptance — 100+ use-case matrix validated against instructions catalog (Coding Task)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.acceptance

ROOT = Path(__file__).resolve().parents[2]
INSTRUCTIONS_CATALOG = ROOT / "docs" / "instructions" / "product_catalog_dataset.json"
MATRIX = Path(__file__).resolve().parents[1] / "fixtures" / "use_cases_matrix.json"
CODING_TASK = ROOT / "docs" / "instructions" / "Coding Task.docx"


def _load_matrix() -> list[dict]:
    return json.loads(MATRIX.read_text(encoding="utf-8"))


def _catalog_rows() -> list[dict]:
    return json.loads(INSTRUCTIONS_CATALOG.read_text(encoding="utf-8"))


def _catalog_index() -> dict[tuple[int, int], dict]:
    index: dict[tuple[int, int], dict] = {}
    for row in _catalog_rows():
        index[(int(row["site_id"]), int(row["article_id"]))] = row
    return index


def test_coding_task_artifacts_present() -> None:
    assert CODING_TASK.is_file()
    assert INSTRUCTIONS_CATALOG.is_file()


def test_matrix_at_least_100_cases() -> None:
    cases = _load_matrix()
    assert len(cases) >= 100, (
        f"matrix has {len(cases)} cases; need >= 100 per Coding Task validation"
    )


def test_matrix_covers_coding_task_requirements() -> None:
    cases = _load_matrix()
    reqs = {c["requirement"] for c in cases}
    for token in ("B2", "B3", "B4", "B5", "B6"):
        assert any(token in r for r in reqs), f"missing requirement coverage for {token}"


def test_matrix_catalog_refs_exist_in_instructions_dataset() -> None:
    cases = _load_matrix()
    rows = _catalog_rows()
    index = _catalog_index()
    assert len(rows) == 300
    assert len(index) >= 280, "expected near-unique (site_id, article_id) keys in catalog"
    missing: list[str] = []
    for case in cases:
        sid = int(case["site_id"])
        ref = case.get("catalog_ref") or {}
        aid = case.get("target_article_id") or ref.get("article_id")
        if aid is None:
            continue
        if (sid, int(aid)) not in index:
            missing.append(f"{case['id']} article_id={aid} site={sid}")
    msg = "catalog refs not in product_catalog_dataset.json:\n" + "\n".join(missing[:15])
    assert not missing, msg


@pytest.mark.parametrize(
    "case",
    _load_matrix(),
    ids=lambda c: c["id"],
)
def test_matrix_catalog_backed_product_cases_have_grounding_target(
    case: dict,
) -> None:
    """Every catalog_backed / target_article_id case points at a real instructions row."""
    exp = case["expect"]
    if exp.get("decline") or not exp.get("products_grounded"):
        return
    aid = case.get("target_article_id")
    ref = case.get("catalog_ref")
    if aid is None and not ref:
        return
    index = _catalog_index()
    sid = int(case["site_id"])
    article_id = int(aid or ref["article_id"])
    row = index[(sid, article_id)]
    if ref:
        assert int(ref["site_id"]) == sid
        if ref.get("brands"):
            assert ref["brands"] == row.get("brands")
