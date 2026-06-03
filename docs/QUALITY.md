# Quality gates (pre-merge)

Run **before** merging any `feature/*` branch into `dev`, and before `dev` → `main`.

---

## Local commands

```bash
pip install -e ".[rag,dev]" pytest-cov

# Lint
ruff check cli src tests
ruff format --check cli src tests

# Tests (pyramid)
pytest tests/unit -q -m unit
pytest tests/integration -q -m integration
pytest tests/e2e -q -m e2e

# All + coverage (Sonar input)
mkdir -p reports
pytest tests/ -q --cov=cli --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml
```

One-shot script:

```bash
python scripts/run_quality_gates.py
```

---

## Test pyramid

| Layer | Path | Scope |
|-------|------|--------|
| **Unit** | `tests/unit/` | normalize, models — no Chroma |
| **Integration** | `tests/integration/` | API, RAG + isolated Chroma (`ZOOPLUS_CHROMA_PATH`) |
| **E2E** | `tests/e2e/` | CLI `eda` + ingest→search smoke |

---

## SonarCloud

- Config: `sonar-project.properties`
- CI: `.github/workflows/quality.yml` (scan when `SONAR_TOKEN` is set in repo secrets)
- Create project: [SonarCloud](https://sonarcloud.io) → import `peluzzza/PoCAssistantZooplus`

---

## Merge policy

| Target | Requirement |
|--------|-------------|
| `feature/*` → `dev` | All gates green locally or in GitHub Actions |
| `dev` → `main` | Same + brief alignment checklist in `docs/00-brief-alignment.md` |

Trace: `docs/trace/T-quality-gates.md`
