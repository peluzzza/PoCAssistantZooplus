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

### Push (first time — use account `peluzzza`)

Local commits exist; push failed with `peluzzzaZero`. Fix auth, then:

```bash
git remote set-url origin https://github.com/peluzzza/PoCAssistantZooplus.git
git push -u origin main
git push -u origin dev
git push -u origin feature/T1-eda
```

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
