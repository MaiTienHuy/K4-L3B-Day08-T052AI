"""
Task 7 — Reciprocal Rank Fusion.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score với BM25
score. Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.

Lưu ý: RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.

-> Dùng Jina hoặc self host hoặc bất cứ công cụ nào bạn quen
"""


import copy


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult."""
    if top_k <= 0 or not ranked_lists:
        return []

    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        if not ranked_list:
            continue
        for rank, item in enumerate(ranked_list, 1):
            item_id = str(item["id"])
            rrf_contrib = 1.0 / (k + rank)
            scores[item_id] = scores.get(item_id, 0.0) + rrf_contrib
            if item_id not in items:
                # Deepcopy để không làm thay đổi các item ban đầu
                items[item_id] = copy.deepcopy(item)

    ranked_ids = sorted(scores.keys(), key=lambda i: scores[i], reverse=True)
    results = []
    for item_id in ranked_ids[:top_k]:
        res = copy.deepcopy(items[item_id])
        res["score"] = scores[item_id]
        res["retrieval_method"] = "hybrid"
        results.append(res)

    return results


if __name__ == "__main__":
    list1 = [{"id": "doc1", "content": "A", "score": 0.9, "metadata": {"source": "s", "title": "t", "doc_type": "legal", "url": None, "chunk_index": 0}, "retrieval_method": "dense"}]
    list2 = [{"id": "doc1", "content": "A", "score": 4.5, "metadata": {"source": "s", "title": "t", "doc_type": "legal", "url": None, "chunk_index": 0}, "retrieval_method": "bm25"}]
    print(rerank_rrf([list1, list2], top_k=2))

