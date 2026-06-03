"""Golden query evaluation against POST /chat contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from src.api.app import app
from src.rag.pipeline import index_dir, run_ingest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "golden_queries.json"


def _ensure_index() -> None:
    path = index_dir()
    if not path.exists() or not any(path.iterdir()):
        print("Building index (first run)...", file=sys.stderr)
        run_ingest()


def run_evaluate() -> int:
    if not FIXTURE.exists():
        print(f"Missing fixture: {FIXTURE}", file=sys.stderr)
        return 1
    _ensure_index()
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))
    client = TestClient(app)
    failed = 0
    for case in cases:
        case_id = case["id"]
        response = client.post(
            "/chat",
            json={"site_id": case["site_id"], "query": case["query"]},
        )
        status = response.status_code
        if status != case.get("expect_status", 200):
            print(f"FAIL {case_id}: status {status}", file=sys.stderr)
            failed += 1
            continue
        payload = response.json()
        products = payload.get("retrieved_products", [])
        answer = payload.get("answer", "")
        if case.get("expect_decline"):
            if products:
                print(f"FAIL {case_id}: expected no products on decline", file=sys.stderr)
                failed += 1
            elif not answer.strip():
                print(f"FAIL {case_id}: expected decline answer text", file=sys.stderr)
                failed += 1
        min_products = case.get("min_products", 0)
        if len(products) < min_products:
            print(
                f"FAIL {case_id}: expected >= {min_products} products, got {len(products)}",
                file=sys.stderr,
            )
            failed += 1
        max_products = case.get("max_products")
        if max_products is not None and len(products) > max_products:
            print(f"FAIL {case_id}: expected <= {max_products} products", file=sys.stderr)
            failed += 1
    if failed:
        print(f"Golden evaluation: {len(cases) - failed}/{len(cases)} passed", file=sys.stderr)
        return 1
    print(f"Golden evaluation: {len(cases)}/{len(cases)} passed")
    return 0
