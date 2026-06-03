# zooplus Assistant (PoC)

**Canonical project root:** this folder (`PoC chatbot zooplus`).

Async FastAPI chat API with agent-first RAG over the provided pet product catalog.

## Documentation

| Doc | Path |
|-----|------|
| Index | [`docs/README.md`](docs/README.md) |
| Proposal v2 | [`docs/plans/PROPOSAL.md`](docs/plans/PROPOSAL.md) |
| Progress | [`docs/trace/PROGRESS.md`](docs/trace/PROGRESS.md) |
| Brief checklist | [`docs/00-brief-alignment.md`](docs/00-brief-alignment.md) |

## Layout

```
├── cli/              # Operator commands (eda, ingest, evaluate)
├── src/              # Application logic (api, agents, rag, lanes, mcp, acp)
├── .opencode/        # OpenCode agent definitions
├── data/raw/         # Immutable catalog copy (do not edit)
├── docs/             # Spec + trace journal
├── artifacts/        # Generated EDA / vector index (gitignored)
└── tests/
```

## Quick start (when T5 complete)

```bash
# from this directory
pip install -e .
python -m cli eda
python -m cli ingest
uvicorn src.api.app:app --reload --port 8080
```

## Status

See [`docs/trace/PROGRESS.md`](docs/trace/PROGRESS.md) — currently **P0/T0** (scaffold).
