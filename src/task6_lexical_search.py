"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""


import re
from typing import Any
from rank_bm25 import BM25Okapi

from .task4_chunking_indexing import chunk_documents, load_documents

CORPUS: list[dict] = []
_BM25_CACHE: tuple[int, BM25Okapi | None] = (0, None)


def _tokenize(text: str) -> list[str]:
    """Tách từ đơn giản cho tiếng Việt và tiếng Anh."""
    return re.findall(r"\w+", text.lower())


def build_bm25_index(corpus: list[dict]) -> BM25Okapi:
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    if not corpus:
        return BM25Okapi([[""]])
    tokenized = [_tokenize(item["content"]) for item in corpus]
    bm25 = BM25Okapi(tokenized)
    # Đảm bảo IDF không bị 0/âm khi corpus nhỏ để từ khoá khớp vẫn nhận score dương
    for word, idf_val in bm25.idf.items():
        if idf_val <= 0:
            bm25.idf[word] = 0.1
    return bm25


def _get_corpus() -> list[dict]:
    """Khởi tạo hoặc trả về CORPUS chunks."""
    global CORPUS
    if not CORPUS:
        docs = load_documents()
        CORPUS = chunk_documents(docs)
    return CORPUS


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    if top_k <= 0 or not query.strip():
        return []

    corpus = _get_corpus()
    if not corpus:
        return []

    tokens = _tokenize(query)
    if not tokens:
        tokens = query.lower().split()

    bm25 = build_bm25_index(corpus)
    scores = bm25.get_scores(tokens)

    # Sắp xếp các index theo điểm giảm dần
    import numpy as np
    ranked_indices = np.argsort(scores)[::-1]

    results = []
    seen_ids = set()
    for idx in ranked_indices:
        item = corpus[int(idx)]
        item_id = str(item["id"])
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)

        meta = dict(item["metadata"])
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

        results.append({
            "id": item_id,
            "content": str(item["content"]),
            "score": float(scores[int(idx)]),
            "metadata": chunk_meta,
            "retrieval_method": "bm25",
        })

        if len(results) >= top_k:
            break

    return results


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for res in lexical_search("hướng dẫn tuyển sinh 2026", top_k=3):
        print(f"[{res['score']:.4f}] {res['metadata']['title']} ({res['id']}): {res['content'][:80]}...")

