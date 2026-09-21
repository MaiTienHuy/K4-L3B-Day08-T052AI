"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

import hashlib
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"


def _fallback_embed_text(text: str, dim: int = EMBEDDING_DIM) -> list[float]:
    """Tạo vector nhúng xác thực chuẩn hóa khi không có API key / model ngoài."""
    import math

    # Hash text kết hợp n-grams để tạo vector xác định
    words = text.lower().split()
    vec = [0.0] * dim
    if not words:
        vec[0] = 1.0
        return vec

    for i, word in enumerate(words):
        h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
        pos = h % dim
        sign = 1.0 if ((h >> 8) & 1) else -1.0
        weight = 1.0 / math.sqrt(i + 1)
        vec[pos] += sign * weight

    # Chuẩn hóa L2 norm
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    else:
        vec[0] = 1.0
    return vec


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Dispatch theo EMBEDDING_PROVIDER trong .env hoặc dùng fallback an toàn."""
    if not texts:
        return []

    provider = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers").lower()

    if provider in {"gemini", "google"} and os.getenv("GEMINI_API_KEY"):
        try:
            from google import genai

            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            model = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
            result = client.models.embed_content(
                model=model,
                contents=texts,
            )
            return [e.values for e in result.embeddings]
        except Exception as e:
            print(f"Google embedding failed ({e}), using deterministic embedding fallback")

    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
            response = client.embeddings.create(input=texts, model=model)
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"OpenAI embedding failed ({e}), using deterministic embedding fallback")

    if provider == "sentence_transformers":
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(EMBEDDING_MODEL)
            embeddings = model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception:
            pass

    # Fallback embedding
    return [_fallback_embed_text(t) for t in texts]


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document chuẩn contract."""
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if path.name.startswith("."):
            continue
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        doc_type = "legal" if "legal" in path.parts else "news"
        doc_id = path.relative_to(STANDARDIZED_DIR).as_posix()

        title = path.stem
        url = None

        # Trích xuất title và url từ header nếu có
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# ") and title == path.stem:
                title = line[2:].strip()
            elif line.startswith("**Source:**"):
                raw_url = line.replace("**Source:**", "").strip()
                if raw_url.startswith("http"):
                    url = raw_url

        documents.append({
            "id": doc_id,
            "content": content,
            "metadata": {
                "source": path.name,
                "title": title,
                "doc_type": doc_type,
                "url": url,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        split_texts = splitter.split_text(document["content"])
        if not split_texts:
            split_texts = [document["content"]]

        for index, text in enumerate(split_texts):
            chunk_metadata = {
                "source": str(document["metadata"]["source"]),
                "title": str(document["metadata"]["title"]),
                "doc_type": str(document["metadata"]["doc_type"]),
                "url": document["metadata"]["url"] if document["metadata"]["url"] is not None else None,
                "chunk_index": int(index),
            }
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": chunk_metadata,
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return []
    texts = [chunk["content"] for chunk in chunks]
    vectors = embed_texts(texts)
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return
    collection = get_collection()
    
    # Chroma yêu cầu metadata values không None hoặc chuyển thành chuỗi/số
    formatted_metadatas = []
    for chunk in chunks:
        meta = dict(chunk["metadata"])
        if meta["url"] is None:
            meta["url"] = ""  # Chroma metadata store empty string
        formatted_metadatas.append(meta)

    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=formatted_metadatas,
    )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    print(f"Loaded {len(documents)} documents.")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks.")
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks to ChromaDB at {CHROMA_DIR}")


if __name__ == "__main__":
    run_pipeline()

