# Phase P2 Complete: RAG index

**Status:** COMPLETE  
**Date:** 2026-06-03  
**Branch:** `feature/T2-rag-index` → `dev`  

---

## Summary

Chroma index built from `data/raw/` with HTML normalization, site-scoped retrieval, and pytest coverage. Dataset duplicate SKU rows handled with `:dupN` id suffix.

---

## Evidence

- `python -m cli ingest` → 300 ids
- `pytest tests/test_rag_index.py` → site isolation PASS

---

## Next phase

→ **P3 / T3** — OpenCode agents + MCP (`feature/T3-opencode-mcp-agents`)
