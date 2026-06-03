"""MCP-compatible tool routes for local agents and OpenCode."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from src.mcp_server.server import tool_catalog_search, tool_topic_check

router = APIRouter(prefix="/mcp")


@router.get("/tools")
async def list_tools() -> dict[str, list[str]]:
    return {"tools": ["topic_check", "catalog_search"]}


@router.post("/tools/topic_check")
async def topic_check_tool(payload: dict) -> dict:
    query = payload.get("query")
    if not isinstance(query, str) or not query.strip():
        raise HTTPException(status_code=422, detail="query must be a non-empty string")
    return await tool_topic_check(query=query)


@router.post("/tools/catalog_search")
async def catalog_search_tool(payload: dict) -> dict:
    query_text = payload.get("query_text")
    site_id = payload.get("site_id")
    if not isinstance(query_text, str) or not query_text.strip():
        raise HTTPException(status_code=422, detail="query_text must be a non-empty string")
    if not isinstance(site_id, int) or site_id < 1:
        raise HTTPException(status_code=422, detail="site_id must be a positive integer")
    n_results = payload.get("n_results")
    pet_type = payload.get("pet_type")
    if n_results is not None and (not isinstance(n_results, int) or n_results < 1):
        raise HTTPException(status_code=422, detail="n_results must be a positive integer")
    if pet_type is not None and not isinstance(pet_type, str):
        raise HTTPException(status_code=422, detail="pet_type must be a string")
    return await tool_catalog_search(
        query_text=query_text,
        site_id=site_id,
        n_results=n_results,
        pet_type=pet_type,
    )
