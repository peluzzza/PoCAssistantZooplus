# Step T3 — OpenCode agents + MCP on server

| Field | Value |
|-------|-------|
| **Step** | T3 |
| **Phase** | P3 |
| **Status** | **DONE** |
| **Brief sections** | Agentic design (PoC extension) |

---

## Objective

Add `.opencode/agents/*.md`, `opencode.json`, and `src/mcp_server/` tools callable per [OpenCode MCP docs](https://opencode.ai/docs/mcp-servers/).

## Evidence

- Added `src/mcp_server/server.py` with `topic_check` and `catalog_search` tool handlers.
- Added `src/api/routes/mcp.py` for `/mcp/tools` endpoints.
- Completed `.opencode/agents/` catalog and enabled MCP in `.opencode/opencode.json`.

---

## Next step

→ **T4** — Dual-lane + ACP
