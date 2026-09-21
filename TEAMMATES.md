# TEAMMATES — Phân công nhóm

> Repository: `K4-Day08-MaiTienHuy-2A202602914`  
> Chủ đề corpus: **Tuyển sinh Đại học & Cao đẳng 2026**  
> Nhóm: 4 thành viên

---

## Phân công tổng quan

| Thành viên | Vai trò chính | Module phụ trách |
|---|---|---|
| **Thành viên 1** (Mai Tiến Huy) | Lead & Data Engineer | Task 1, Task 2, Task 3 — Thu thập & chuẩn hóa corpus |
| **Thành viên 2** (Lê Việt Hoàng) | Retrieval Engineer | Task 4, Task 5, Task 6 — Chunking, Dense search, BM25 |
| **Thành viên 3** (Hoàng Ngọc Đức) | Pipeline Engineer | Task 7, Task 8, Task 9 — RRF, Fallback, Retrieval pipeline |
| **Thành viên 4** (Trịnh Xuân Huy) | Generation & Evaluation| Task 10, app.py, Golden dataset, RESULT.md |

---

## Chi tiết phân công

### Thành viên 1 — Mai Tiến Huy (Lead)
- **Trách nhiệm chính:** Quản lý repo, thu thập và chuẩn hóa dữ liệu
- **Module:** `src/task1_collect_legal_docs.py`, `src/task2_crawl_news.py`, `src/task3_convert_markdown.py`
- **Output:** 4 PDF tuyển sinh, 5 JSON bài viết, toàn bộ `data/landing/` và `data/standardized/`
- **Deliverables:** `reports/2A202602914-mai-tien-huy.md`

### Thành viên 2 — Lê Việt Hoàng
- **Trách nhiệm chính:** Xây dựng vector store và hai đường tìm kiếm
- **Module:** `src/task4_chunking_indexing.py`, `src/task5_semantic_search.py`, `src/task6_lexical_search.py`
- **Output:** ChromaDB với embeddings BAAI/bge-m3, BM25 index
- **Deliverables:** `reports/K4-L3B-2A202602596-LeVietHoang.md`

### Thành viên 3 - Hoàng Ngọc Đức
- **Trách nhiệm chính:** Hợp nhất kết quả và xây dựng retrieval pipeline
- **Module:** `src/task7_reranking.py`, `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py`
- **Output:** RRF fusion, fallback logic, pipeline end-to-end
- **Deliverables:** `reports/<id>-<name>.md`

### Thành viên 4 — Trịnh Xuân Huy
- **Trách nhiệm chính:** Generation, UI và evaluation
- **Module:** `src/task10_generation.py`, `app.py`, `group_project/evaluation/`
- **Output:** Chatbot Streamlit, golden dataset 15 cases, RESULT.md A/B
- **Deliverables:** `reports\K4-L3B-2A202602995-TrinhXuanHuy.md`

---

## Checklist nhóm trước khi nộp

- [ ] `pytest tests/test_acceptance.py -q` → 5/5 PASS
- [ ] `pytest tests/test_contracts.py -q` → toàn bộ PASS
- [ ] `streamlit run app.py` → chạy được, hiển thị answer + sources
- [ ] Demo query đúng domain có citation
- [ ] Demo query ngoài domain → safe refusal (không crash)
- [ ] `group_project/evaluation/golden_dataset.json` → 15 cases
- [ ] `group_project/evaluation/RESULT.md` → không còn TODO
- [ ] 4 file báo cáo cá nhân trong `reports/`
- [ ] `data/landing/` và `data/standardized/` đã commit
- [ ] `.env` **không** commit (chỉ `.env.example`)
- [ ] `chroma_db/` không commit (thêm vào `.gitignore`)

---

## Lệnh chạy lại từ đầu (cho reviewer)

```bash
# 1. Cài đặt
pip install -e .

# 2. Thu thập dữ liệu
python -m src.task1_collect_legal_docs
python -m src.task2_crawl_news
python -m src.task3_convert_markdown

# 3. Index
python -m src.task4_chunking_indexing

# 4. Kiểm tra search
python -m src.task5_semantic_search
python -m src.task6_lexical_search

# 5. Chạy tests
pytest tests/test_acceptance.py -q
pytest tests/test_contracts.py -q

# 6. Chạy chatbot
streamlit run app.py
```
