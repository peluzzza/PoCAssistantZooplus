# Acceptance criteria (source of truth)

**Authoritative inputs (must match for any test run):**

| Artifact | Path |
|----------|------|
| Brief | `docs/instructions/Coding Task.docx` |
| Catalog | `docs/instructions/product_catalog_dataset.json` |
| Runtime copy | `data/raw/product_catalog_dataset.json` (byte-identical to instructions) |

**Automated suite:** `tests/acceptance/test_coding_task_brief.py`  
**Fixture queries:** `tests/fixtures/acceptance_queries.json`

## Functional requirements (Coding Task)

| ID | Requirement | Test coverage |
|----|-------------|---------------|
| B1 | Async FastAPI backend | `test_app_is_async_fastapi` |
| B2 | `POST /chat` `{ site_id, query }` | `test_chat_request_contract_*` |
| B3 | `{ answer, retrieved_products }` | `test_response_schema_*` |
| B4 | RAG — knowledge only from dataset | `test_retrieved_products_grounded_in_instructions_catalog` |
| B5 | `site_id` shop scoping | `test_site_scoping_*` |
| B6 | Pet-products guardrails; off-topic declined | `test_off_topic_*` |
| B7 | Production-oriented structure | `test_repo_layout_brief` (static) |
| B8 | README + runnable setup | `test_readme_and_cli_entrypoints` (static) |
| B9 | Evaluation / trade-offs documented | `test_evaluation_docs_present` (static) |

## Policy (constraints.yaml / guardian)

| ID | Policy | Test |
|----|--------|------|
| P1 | Max 4 recommendations | `test_max_four_retrieved_products` |
| P2 | Decline has answer, empty products | golden + acceptance off-topic cases |
| P3 | Catalog ingest 300 variants | `test_instructions_catalog_record_count` |

## Query scenarios (PoC plan — ≥10 cases)

Covered by `acceptance_queries.json` (product lookup, ingredients, feeding, price/stock, popularity, multi-site).

## Local run

```bash
pip install -e ".[rag,dev]"
python -m cli ingest
python scripts/run_quality_gates.py
python -m pytest tests/acceptance -q -m acceptance
```

With live API:

```bash
uvicorn src.api.app:app --host 127.0.0.1 --port 8080
python scripts/demo_all.py
```
