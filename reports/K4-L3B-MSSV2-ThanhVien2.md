# Individual contribution report

## Thông tin

- **Họ và tên:** [Điền họ tên thành viên 2]
- **Mã học viên:** [Điền MSSV]
- **Nhóm:** K4-Day08, nhóm 4 thành viên
- **Repository:** K4-Day08-MaiTienHuy-2A202602914 / branch: main

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit | Trạng thái |
|---|---|---|---|
| Chunking & Embedding | Hoàn thiện `load_documents()`, `chunk_documents()`, `embed_texts()`, `embed_chunks()`, `get_collection()`, `index_to_vectorstore()` | `src/task4_chunking_indexing.py`, `chroma_db/` | Done |
| Dense semantic search | Hoàn thiện `semantic_search()` dùng chung `embed_texts()` từ Task 4; convert cosine distance → similarity; sort giảm dần | `src/task5_semantic_search.py` | Done |
| BM25 lexical search | Hoàn thiện `build_bm25_index()` và `lexical_search()` trên cùng corpus chunk; tokenize tiếng Việt/Anh bằng regex `\w+` | `src/task6_lexical_search.py` | Done |
| Contract test | Chạy `tests/test_contracts.py` để xác nhận schema SearchResult và chunk đúng contract | `tests/test_contracts.py` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng BAAI/bge-m3 (sentence-transformers, dim=1024) làm embedding model mặc định, với fallback deterministic hash-based khi không có model  
   **Lý do/evidence:** bge-m3 hỗ trợ đa ngôn ngữ (tiếng Việt + Anh) tốt hơn các model monolingual; dim=1024 cân bằng giữa chất lượng và tốc độ  
   **Trade-off:** Download model ~570MB lần đầu; chậm hơn `text-embedding-3-small` của OpenAI nhưng không tốn API cost

2. **Quyết định:** CHUNK_SIZE=500, CHUNK_OVERLAP=50 với `RecursiveCharacterTextSplitter`  
   **Lý do/evidence:** Giá trị starter phù hợp với độ dài văn bản pháp quy tiếng Việt (~500 ký tự ≈ 2–3 câu); overlap 50 giữ ranh giới câu  
   **Trade-off:** Bảng biểu trong PDF đôi khi bị cắt ngang hàng; cải thiện bằng cách tăng CHUNK_SIZE lên 800 nếu cần

---

## Kiểm thử và kết quả

- **Test đã chạy:** `pytest tests/test_contracts.py -v` → contract tests PASS; `python -m src.task5_semantic_search` trả kết quả đúng schema
- **Kết quả:** ChromaDB index thành công toàn bộ chunks với ID ổn định (`path::chunk-{index}`); upsert không nhân bản khi chạy lại
- **Lỗi đã xử lý:** ChromaDB không chấp nhận `metadata.url = None` → chuyển thành chuỗi rỗng `""` khi upsert, restore về `None` khi query

---

## Điều còn hạn chế

- **Hạn chế:** BM25 dùng tokenize đơn giản bằng `\w+`; từ ghép tiếng Việt như "xét tuyển" bị tách thành 2 token riêng, làm giảm accuracy cho query có từ ghép
- **Nếu có thêm thời gian:** Tích hợp `underthesea` hoặc `pyvi` để word-segment tiếng Việt trước khi build BM25 index

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 2026-09-21
- **Tên thành viên:** [Điền tên]
