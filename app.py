import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation

load_dotenv()

st.set_page_config(
    page_title="Hỏi đáp Tuyển sinh 2026 — RAG Assistant",
    page_icon="🎓",
    layout="wide",
)

# Khởi tạo state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar cấu hình
with st.sidebar:
    st.title("🎓 RAG Assistant")
    st.markdown("---")
    st.markdown(
        "**Chủ đề:** Tuyển sinh Đại học & Cao đẳng 2026\n\n"
        "**Corpus bao gồm:**\n"
        "- Quy chế tuyển sinh & Kế hoạch tuyển sinh 2026\n"
        "- Hướng dẫn xét tuyển (CV 2304/BGDĐT-GDĐH)\n"
        "- Các mốc thời gian quan trọng & Hướng dẫn thanh toán lệ phí"
    )
    st.markdown("---")
    top_k = st.slider("Số lượng tài liệu truy xuất (Top-K Chunks)", min_value=1, max_value=10, value=5, step=1)
    
    if st.button("🗑️ Xóa lịch sử hội thoại"):
        st.session_state.messages = []
        st.rerun()

st.title("🎓 Trợ lý Tra cứu Tuyển sinh Đại học 2026")
st.caption("Tra cứu quy chế, mốc thời gian đăng ký xét tuyển, chính sách ưu tiên và hướng dẫn nộp hồ sơ.")

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            retrieval_src = msg.get("retrieval_source", "hybrid")
            st.caption(f"🔍 **Phương thức truy xuất:** `{retrieval_src}` | **Số trích dẫn:** {len(msg['sources'])}")
            with st.expander("📚 Xem danh sách tài liệu trích dẫn"):
                for idx, src in enumerate(msg["sources"], 1):
                    meta = src.get("metadata", {})
                    score_str = f"{src.get('score', 0):.4f}" if isinstance(src.get('score'), (int, float)) else str(src.get('score'))
                    url_part = f" | [Nguồn trực tuyến]({meta['url']})" if meta.get("url") else ""
                    st.markdown(f"**{idx}. [{src.get('retrieval_method', 'source').upper()}] {meta.get('title', 'Tài liệu')}** (Điểm: `{score_str}`){url_part}")
                    st.caption(f"Tài liệu gốc: `{meta.get('source', '')}` (Chunk #{meta.get('chunk_index', 0)})")
                    st.code(src.get("content", ""), language="markdown")

# Khung nhập câu hỏi
query = st.chat_input("Nhập câu hỏi của bạn (ví dụ: Khi nào bắt đầu đăng ký nguyện vọng xét tuyển đại học 2026?)...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm tài liệu và tổng hợp câu trả lời..."):
            result = generate_with_citation(query, top_k=top_k)
            answer = result["answer"]
            sources = result.get("sources", [])
            retrieval_source = result.get("retrieval_source", "none")

            st.markdown(answer)

            if sources:
                st.caption(f"🔍 **Phương thức truy xuất:** `{retrieval_source}` | **Số trích dẫn:** {len(sources)}")
                with st.expander("📚 Xem danh sách tài liệu trích dẫn"):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        score_str = f"{src.get('score', 0):.4f}" if isinstance(src.get('score'), (int, float)) else str(src.get('score'))
                        url_part = f" | [Nguồn trực tuyến]({meta['url']})" if meta.get("url") else ""
                        st.markdown(f"**{idx}. [{src.get('retrieval_method', 'source').upper()}] {meta.get('title', 'Tài liệu')}** (Điểm: `{score_str}`){url_part}")
                        st.caption(f"Tài liệu gốc: `{meta.get('source', '')}` (Chunk #{meta.get('chunk_index', 0)})")
                        st.code(src.get("content", ""), language="markdown")

    # Lưu lại câu trả lời và sources vào session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
