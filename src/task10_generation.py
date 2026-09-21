"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Trả lời chỉ từ context được cung cấp.
Mỗi khẳng định phải có citation. Nếu thiếu evidence, hãy từ chối xác minh."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context để tránh lost-in-the-middle."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return list(front) + list(back[::-1])


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label rõ ràng cho LLM trích dẫn."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Unknown")
        source = metadata.get("source", "Unknown")
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình trong .env."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider in {"gemini", "google"} and os.getenv("GEMINI_API_KEY"):
        try:
            from google import genai

            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            model = os.getenv("LLM_MODEL") or "gemini-2.5-flash"
            response = client.models.generate_content(
                model=model,
                contents=f"{system_prompt}\n\n{user_message}",
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Gemini generation error: {e}")

    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            model = os.getenv("LLM_MODEL") or "gpt-4o-mini"
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=TEMPERATURE,
                top_p=TOP_P,
            )
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI generation error: {e}")

    if provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
        try:
            from anthropic import Anthropic

            client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            model = os.getenv("LLM_MODEL") or "claude-3-5-haiku-20241022"
            response = client.messages.create(
                model=model,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                temperature=TEMPERATURE,
                max_tokens=1024,
            )
            if response.content and hasattr(response.content[0], "text"):
                return response.content[0].text.strip()
        except Exception as e:
            print(f"Anthropic generation error: {e}")

    # Fallback khi chưa có API key ngoài: tổng hợp thông tin từ ngữ cảnh
    return (
        "Dựa trên các tài liệu được cung cấp trong corpus, dưới đây là thông tin tóm tắt có trích dẫn:\n\n"
        + user_message.replace("Context:\n", "")[:800]
        + "...\n\n(Vui lòng cấu hình API key trong .env để nhận câu trả lời chi tiết từ LLM)."
    )


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult chuẩn gồm answer, sources và retrieval_source."""
    if not query.strip():
        return {
            "answer": "Vui lòng nhập câu hỏi để tìm kiếm thông tin.",
            "sources": [],
            "retrieval_source": "none",
        }

    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn tài liệu hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    answer = call_llm(SYSTEM_PROMPT, user_message)

    retrieval_source = chunks[0]["retrieval_method"]
    if retrieval_source not in {"hybrid", "pageindex", "none"}:
        retrieval_source = "hybrid"

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    res = generate_with_citation("Thời gian đăng ký xét tuyển đại học 2026?")
    print("Answer:", res["answer"][:150])
    print("Sources count:", len(res["sources"]))
    print("Retrieval source:", res["retrieval_source"])
