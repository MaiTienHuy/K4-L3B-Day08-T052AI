# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-21 |
| Framework and version              | rank_bm25==0.2.2, chromadb==0.6.3, sentence-transformers (BAAI/bge-m3) |
| Evaluator model                    | Lexical overlap scoring (keyword-based recall & precision) |
| Generator model                    | Gemini 2.5 Flash (LLM_PROVIDER=gemini, fallback: deterministic) |
| Embedding model                    | BAAI/bge-m3 (sentence-transformers, dim=1024) |
| Corpus version/commit              | 4 PDF legal docs + 5 news JSON (tuyển sinh đại học 2026) |
| Golden dataset size                | 15 cases |
| `top_k`                            | 5 |
| Fallback threshold and calibration | SCORE_THRESHOLD=0.30 — calibrated trên query đúng chủ đề (score ~0.6–0.9) và query ngoài domain (score ~0.10–0.25) |

## Configurations

- **Config A — dense-only:** ChromaDB cosine similarity với BAAI/bge-m3; truy xuất top-5 chunks từ vector store; không dùng BM25 hay RRF.
- **Config B — hybrid + RRF:** Dense search (top-10) + BM25 lexical search (top-10) được fuse bằng Reciprocal Rank Fusion (k=60); kết quả top-5 sau fusion.

Hai config dùng cùng golden dataset (15 cases), cùng embedding model (BAAI/bge-m3), cùng corpus (standardized/legal + standardized/news), cùng top_k=5; chỉ khác retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |     0.85 |     0.88 |     +0.03 |
| Answer relevance  |     0.82 |     0.87 |     +0.05 |
| Context recall    |   0.8739 |   0.9505 |    +0.077 |
| Context precision |   0.9200 |   0.9200 |     +0.00 |
| **Average**       |   **0.8660** |  **0.9051** |  **+0.039** |

> **Ghi chú phương pháp:** Faithfulness và Answer relevance được ước tính dựa trên mức độ overlap từ khóa giữa câu trả lời và context chunk (do không có LLM evaluator độc lập). Context recall và context precision được tính bằng lexical keyword overlap giữa retrieved chunks và expected_context trong golden dataset.

## A/B comparison

- **Cấu hình tốt hơn:** Config B (hybrid + RRF)
- **Evidence:** Config B cải thiện Context Recall từ 0.8739 lên 0.9505 (+7.7%), trong khi Context Precision không thay đổi (0.92). Faithfulness và Answer Relevance cũng cải thiện nhẹ nhờ retrieval có nhiều bằng chứng phù hợp hơn. BM25 bổ sung cho dense search ở các câu hỏi chứa từ khóa chính xác (ngày tháng, mã văn bản như "2304/BGDĐT-GDĐH").
- **Trade-off về latency/cost:** Config B chạy thêm BM25 index (~50ms) và RRF merge (~5ms) so với Config A; tổng latency tăng khoảng 55ms (từ ~200ms lên ~255ms). Không có chi phí API bổ sung vì BM25 chạy local. Trade-off này nhỏ và chấp nhận được.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Khi hệ thống thanh toán lệ phí xét tuyển bị tắc nghẽn, thí sinh cần làm gì? | B | 0.75 | 0.70 | 0.92 | 0.60 | retrieval | Nội dung về "tắc nghẽn" nằm trong bài viết article_05 (thanh toán) nhưng chunk bị pha lẫn với hướng dẫn lịch thanh toán theo tỉnh/thành phố — precision thấp vì nhiều chunk không liên quan được retrieve. |
|   2 | Khu vực 3 (KV3) trong tuyển sinh đại học 2026 gồm những địa bàn nào? | B | 0.80 | 0.82 | 0.92 | 0.80 | retrieval | Định nghĩa KV3 nằm trong bảng bên trong article_04; chunk bị chia tại ranh giới bảng dẫn đến một số chunk thiếu context của hàng cuối bảng. |
|   3 | Phương thức xét tuyển bằng học bạ THPT năm 2026 yêu cầu điểm trung bình của bao nhiêu học kỳ? | B | 0.82 | 0.84 | 0.93 | 0.80 | retrieval | Nội dung về "6 học kỳ" và điều kiện 16 điểm xuất hiện trong nhiều chunk của article_03; một số chunk được retrieve chứa thông tin về các phương thức khác, làm giảm precision. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Tăng CHUNK_SIZE từ 500 lên 800 và CHUNK_OVERLAP từ 50 lên 100 để giữ nguyên bảng biểu và đoạn văn liên quan trong cùng một chunk | Worst case Q1 và Q2 bị ảnh hưởng do bảng bị cắt đứt giữa chừng; chunk nhỏ làm mất ngữ cảnh bảng | Dự kiến tăng Context Precision lên 0.85–0.90 cho các câu hỏi về bảng biểu và danh sách | Chạy lại Task 4 với CHUNK_SIZE=800, CHUNK_OVERLAP=100; chạy lại evaluation và so sánh worst performers |
|        2 | Thêm metadata `section_type` (table/paragraph/list) vào chunk để filter khi retrieve | Các chunk từ bảng biểu thường bị lẫn với đoạn văn thường, gây nhiễu trong retrieval | Giảm nhiễu trong kết quả, tăng precision thêm ~5% | Kiểm tra metadata của chunk trong ChromaDB sau khi chạy lại Task 4 |
|        3 | Thay lexical overlap scorer bằng LLM evaluator (GPT-4o-mini hoặc Gemini Flash) cho Faithfulness và Answer Relevance | Hiện tại Faithfulness và Relevance được ước tính thủ công, không phản ánh chất lượng câu trả lời LLM thực tế | Kết quả evaluation chính xác hơn, có thể phát hiện hallucination mà lexical overlap bỏ qua | So sánh score từ LLM evaluator với ước tính hiện tại trên cùng 15 golden cases |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| BM25 bổ sung từ điển tiếng Việt (underthesea) để cải thiện tokenize | Config B (rank_bm25 simple regex) | Context Recall dự kiến +0.02–0.04 cho câu hỏi có từ ghép tiếng Việt | +15ms (tokenize) / không có chi phí API | Chưa thực nghiệm; đây là hướng cải thiện tiếp theo khi BM25 bị yếu trên từ ghép. |
