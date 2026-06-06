# Operations runbook (v2.0 production profile)

**First install?** Start with [`QUICKSTART.md`](QUICKSTART.md) and `.\scripts\setup_wizard.ps1`.

**Service:** zooplus Assistant API  
**Dev port:** 8090 (`run_dev.ps1`) · **Docker:** 8080

---

## 1. Local Docker deploy

```bash
docker compose build
docker compose up -d
python scripts/deploy_smoke.py http://127.0.0.1:8080
```

Expected: `Deploy smoke PASSED` (health, ready, chat, metrics).

---

## 2. Bare-metal / venv

```bash
pip install -e ".[rag,dev]"
python -m cli ingest
uvicorn src.api.app:app --host 0.0.0.0 --port 8080
python scripts/deploy_smoke.py
```

---

## 3. Endpoints

| Path | Purpose |
|------|---------|
| `GET /health` | Liveness |
| `GET /ready` | Readiness (Chroma index present) |
| `GET /metrics` | JSON request/chat metrics |
| `POST /chat` | Main API |
| `POST /chat/stream` | NDJSON stream |
| `GET /mcp/tools` | MCP tool list |

---

## 4. Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ZOOPLUS_CHROMA_PATH` | `artifacts/index/chroma` | Vector index directory |
| `ZOOPLUS_RETRIEVAL_MODE` | `hybrid` | `hybrid` or `vector` |
| `ZOOPLUS_VECTOR_BACKEND` | `chroma_local` | `chroma_local` (PoC); `managed` reserved |
| `ZOOPLUS_LOG_LEVEL` | `INFO` | Python log level |
| `ZOOPLUS_METRICS` | `1` | Set `0` to disable middleware metrics |

---

## 5. Managed vector DB (future)

Set `ZOOPLUS_VECTOR_BACKEND=managed` only after wiring a hosted client in `src/rag/store/`.  
PoC ships **Chroma persistent local**; swap path documented in [`02-rag-architecture.md`](02-rag-architecture.md).

---

## 6. Rollback

```bash
docker compose down
git checkout main && git pull
docker compose up -d --build
python scripts/deploy_smoke.py
```

---

## 7. Quality before release

```bash
python scripts/run_quality_gates.py
```
