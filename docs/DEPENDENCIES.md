# Dependencies and Python version policy

**Canonical runtime:** Python **3.11.x** (same as Dockerfile and GitHub Actions).

| Surface | Python | Notes |
|---------|--------|-------|
| GitHub Actions `quality.yml` | 3.11 | Source of truth for CI |
| `Dockerfile` | `python:3.11-slim-bookworm` | Production image |
| Local dev | **3.11 recommended** | `.python-version` → `3.11.9` |
| Local 3.13 | Allowed with warning | `requires-python <3.13`; gates may differ from CI |

## Why not 3.13 locally?

PoC is validated on **3.11** in CI/Docker. Running `py -3` on Windows often resolves to 3.13, which can hide compatibility issues with Chroma/embeddings stacks. Use:

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -e ".[rag,dev]"
python scripts/run_quality_gates.py
```

Or Docker: `docker compose up --build`.

## Pinned ranges (`pyproject.toml`)

Dependencies use **compatible upper bounds** tested on 3.11:

- FastAPI / Uvicorn / Pydantic — API stack
- ChromaDB 0.5.x — vector index (no 3.13-only APIs assumed)
- pytest / ruff — dev tooling

Refresh lockfile after bumps:

```bash
pip install -e ".[rag,dev]"
pip freeze > requirements-lock.txt
```

(`requirements-lock.txt` is informational; `pyproject.toml` remains authoritative.)
