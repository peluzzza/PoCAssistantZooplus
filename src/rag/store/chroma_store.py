"""ChromaDB persistent store for PoC (local embeddings)."""

from __future__ import annotations

from pathlib import Path

COLLECTION_NAME = "zooplus_variants"


def get_client(persist_dir: Path):
    import chromadb

    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_dir))


def get_or_create_collection(client):
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "zooplus variant catalog PoC"},
    )


def upsert_items(persist_dir: Path, items: list[dict]) -> int:
    client = get_client(persist_dir)
    collection = get_or_create_collection(client)
    ids = [i["id"] for i in items]
    documents = [i["document"] for i in items]
    metadatas = [i["metadata"] for i in items]
    # Idempotent rebuild: delete collection contents by recreating
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = get_or_create_collection(client)
    batch = 50
    for start in range(0, len(ids), batch):
        end = start + batch
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )
    return len(ids)


def query(
    persist_dir: Path,
    query_text: str,
    site_id: int,
    n_results: int = 5,
    pet_type: str | None = None,
) -> list[dict]:
    client = get_client(persist_dir)
    collection = get_or_create_collection(client)
    where: dict = {"site_id": site_id}
    if pet_type:
        where = {"$and": [{"site_id": site_id}, {"pet_type": pet_type}]}
    result = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    hits: list[dict] = []
    if not result["ids"] or not result["ids"][0]:
        return hits
    for i, vid in enumerate(result["ids"][0]):
        hits.append(
            {
                "variant_id": vid,
                "document": (result["documents"] or [[]])[0][i],
                "metadata": (result["metadatas"] or [[]])[0][i],
                "distance": (result["distances"] or [[]])[0][i],
            }
        )
    return hits
