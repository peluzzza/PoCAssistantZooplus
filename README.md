# zooplus Assistant (PoC)

**Canonical project root:** this folder (`PoC chatbot zooplus`).  
**GitHub:** [peluzzza/PoCAssistantZooplus](https://github.com/peluzzza/PoCAssistantZooplus.git)

Async FastAPI chat API with agent-first RAG over the provided pet product catalog.

## Git branches

| Branch | Role |
|--------|------|
| `main` | Stable / demo-ready |
| `dev` | Integration (merge `feature/*` here) |
| `feature/*` | Step work (e.g. `feature/T1-eda`) |

See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md).

### Remote sync

Branches on GitHub: `main` (P0 bootstrap), `dev` (P0 + T1 EDA), `feature/T1-eda`.

```bash
git fetch origin
git checkout dev
```

## Documentation

| Doc | Path |
|-----|------|
| Index | [`docs/README.md`](docs/README.md) |
| Proposal v2 | [`docs/plans/PROPOSAL.md`](docs/plans/PROPOSAL.md) |
| Progress | [`docs/trace/PROGRESS.md`](docs/trace/PROGRESS.md) |
| Quality gates | [`docs/QUALITY.md`](docs/QUALITY.md) |
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

## Quick start

```bash
# from this directory
pip install -e ".[rag,dev]"
python -m cli eda
python -m cli ingest
pytest tests/ -q
uvicorn src.api.app:app --reload --port 8080
```

## Status

See [`docs/trace/PROGRESS.md`](docs/trace/PROGRESS.md) — currently **P0/T0** (scaffold).
