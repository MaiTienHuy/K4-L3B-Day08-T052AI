"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if top_k <= 0 or not query.strip():
        return []

    query_vectors = embed_texts([query])
    if not query_vectors:
        return []
    query_vector = query_vectors[0]

    collection = get_collection()
    response = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    results = []
    if response and response.get("ids") and response["ids"][0]:
        ids = response["ids"][0]
        docs = response["documents"][0] if response.get("documents") else [""] * len(ids)
        metas = response["metadatas"][0] if response.get("metadatas") else [{}] * len(ids)
        dists = response["distances"][0] if response.get("distances") else [0.0] * len(ids)

        for item_id, content, metadata, distance in zip(ids, docs, metas, dists):
            meta = dict(metadata) if metadata else {}
            # Đảm bảo url là None nếu chuỗi rỗng
            url_val = meta.get("url")
            if url_val == "" or url_val is None:
                url_val = None

            chunk_meta = {
                "source": str(meta.get("source", "unknown")),
                "title": str(meta.get("title", "unknown")),
                "doc_type": str(meta.get("doc_type", "unknown")),
                "url": url_val,
                "chunk_index": int(meta.get("chunk_index", 0)),
            }

            similarity = max(0.0, 1.0 - float(distance))
            results.append({
                "id": str(item_id),
                "content": str(content),
                "score": similarity,
                "metadata": chunk_meta,
                "retrieval_method": "dense",
            })

    # Sort giảm dần theo score và giới hạn top_k
    sorted_results = sorted(results, key=lambda item: item["score"], reverse=True)
    return sorted_results[:top_k]


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for res in semantic_search("quy chế tuyển sinh đại học 2026", top_k=3):
        print(f"[{res['score']:.4f}] {res['metadata']['title']} ({res['id']}): {res['content'][:80]}...")
