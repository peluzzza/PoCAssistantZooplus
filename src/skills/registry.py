"""Skill catalog — agents load capabilities by ID (PoC)."""

from __future__ import annotations

SKILLS: dict[str, dict] = {
    "skill_04_html_normalize": {
        "module": "src.rag.normalize",
        "description": "Strip HTML from catalog fields before embedding",
    },
    "skill_05_embed_index": {
        "module": "src.rag.pipeline",
        "description": "Build Chroma index from data/raw (cli ingest)",
    },
    "skill_06_hybrid_retrieve": {
        "module": "src.rag.retrieve",
        "description": "Semantic search with mandatory site_id filter",
    },
}
