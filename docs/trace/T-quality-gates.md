# Step T-quality — Pre-merge quality gates

| Field | Value |
|-------|-------|
| **Step** | T-quality |
| **Branch** | `feature/quality-gates` → `dev` |
| **Status** | DONE |

---

## Objective

Enforce **unit**, **integration**, and **e2e** tests plus **Ruff** lint/format before any feature merge. Prepare **SonarCloud** for CI.

---

## Deliverables

| Item | Path |
|------|------|
| Test pyramid | `tests/unit/`, `tests/integration/`, `tests/e2e/` |
| Runner | `scripts/run_quality_gates.py` |
| CI | `.github/workflows/quality.yml` |
| Sonar config | `sonar-project.properties` |
| Guide | `docs/QUALITY.md` |
| Git policy | `docs/GIT_WORKFLOW.md` |

---

## Results (local)

| Gate | Result |
|------|--------|
| Ruff check | PASS |
| Ruff format | PASS |
| Unit (6) | PASS |
| Integration (7) | PASS |
| E2E (2) | PASS |

**Total: 15 tests**

---

## SonarCloud

- Scan runs in GitHub Actions when `SONAR_TOKEN` secret is configured.
- Local: generate `coverage.xml` via `pytest --cov` (see `QUALITY.md`).

---

## Next step

Merge → `dev`, then continue **T3** on `feature/T3-opencode-mcp-agents`.
