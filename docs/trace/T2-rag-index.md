# Step T2 — RAG index (ingest)

| Field | Value |
|-------|-------|
| **Step** | T2 |
| **Phase** | P2 |
| **Status** | DONE |
| **Branch** | `feature/T2-rag-index` → `dev` |
| **Brief sections** | RAG — knowledge from dataset only |

---

## Objective

Build a reproducible vector index from `data/raw/` with HTML normalization, per-variant chunks, and **site_id-scoped** retrieval.

---

## Work log

| Step | Action | Module / command |
|------|--------|------------------|
| 2.1 | HTML → plain text | `src/rag/normalize.py` |
| 2.2 | Variant → document + metadata | `src/rag/chunking.py` |
| 2.3 | Chroma persistent store | `src/rag/store/chroma_store.py` |
| 2.4 | Ingest orchestration | `src/rag/pipeline.py` |
| 2.5 | Retrieval helper | `src/rag/retrieve.py` |
| 2.6 | CLI wired | `python -m cli ingest` |
| 2.7 | Skills registered | `src/skills/registry.py` (04–06) |
| 2.8 | Tests | `tests/test_rag_index.py` |
| 2.9 | Architecture doc | `docs/02-rag-architecture.md` |

---

## Decisions

| Decision | Rationale |
|----------|-------------|
| Chroma default embeddings | No API key for PoC CI/local smoke |
| Recreate collection on ingest | Idempotent rebuild during development |
| Filter `site_id` in Chroma `where` | Brief multi-shop requirement |

---

## Quality evidence

```bash
python -m cli ingest   # ingested=300
pytest tests/test_rag_index.py -q
```

- **G2:** `test_no_cross_site_leak` — PASS  
- **B4:** retrieval only from indexed catalog — PASS  

---

## Next step

→ **T3** — `feature/T3-opencode-mcp-agents` (OpenCode agents + MCP tools on server)
