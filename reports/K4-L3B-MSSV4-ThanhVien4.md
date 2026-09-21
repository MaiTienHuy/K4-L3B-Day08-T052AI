# Individual contribution report

## Thông tin

- **Họ và tên:** [Điền họ tên thành viên 4]
- **Mã học viên:** [Điền MSSV]
- **Nhóm:** K4-Day08, nhóm 4 thành viên
- **Repository:** K4-Day08-MaiTienHuy-2A202602914 / branch: main

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit | Trạng thái |
|---|---|---|---|
| Generation có citation | Hoàn thiện `reorder_for_llm()`, `format_context()`, `call_llm()` (Gemini/OpenAI/Anthropic), `generate_with_citation()` với safe refusal khi thiếu evidence | `src/task10_generation.py` | Done |
| Streamlit UI | Hoàn thiện `app.py`: nhận query + top_k, gọi `generate_with_citation()`, hiển thị answer + sources + score + retrieval_method; lưu lịch sử session | `app.py` | Done |
| Golden dataset | Tạo 15 golden cases từ corpus (mốc thời gian, điều kiện xét tuyển, chính sách ưu tiên, hướng dẫn thanh toán) | `group_project/evaluation/golden_dataset.json` | Done |
| A/B Evaluation | Chạy Config A (dense-only) vs Config B (hybrid+RRF) trên 15 cases; tính Context Recall và Precision; phân tích 3 worst performers | `group_project/evaluation/RESULT.md` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** `reorder_for_llm()` dùng chiến lược xen kẽ (even indices → đầu, odd indices → cuối đảo ngược) thay vì giữ nguyên thứ tự  
   **Lý do/evidence:** Lost-in-the-middle problem — LLM có xu hướng bỏ qua thông tin ở giữa context dài; đặt chunk quan trọng ở đầu và cuối tăng khả năng được trích dẫn  
   **Trade-off:** Thứ tự RRF score không còn được giữ nguyên trong context; nhưng tất cả ID vẫn được giữ đủ

2. **Quyết định:** `retrieval_source` trong `GenerationResult` map theo `retrieval_method` của chunk đầu tiên, fallback về "hybrid" cho các method không có trong spec  
   **Lý do/evidence:** UI cần hiển thị đúng nguồn truy xuất để người dùng biết câu trả lời đến từ dense/hybrid/pageindex; đồng bộ với contract  
   **Trade-off:** Nếu chunks trộn lẫn nhiều method, chỉ lấy method của chunk đầu tiên có thể không phản ánh đầy đủ

---

## Kiểm thử và kết quả

- **Test đã chạy:** `pytest tests/test_contracts.py -q` → PASS; `streamlit run app.py` → chạy được; thử "Học phí đại học 2026 là bao nhiêu?" (ngoài domain) → trả safe refusal, không crash
- **Kết quả evaluation:** Config B (hybrid+RRF) vượt Config A trên Context Recall (+7.7%: 0.8739→0.9505); Precision giữ nguyên 0.92
- **Lỗi đã xử lý:** Ban đầu `retrieval_source` có thể là "dense" hoặc "bm25" (không đúng spec) → thêm normalization để map về "hybrid" khi method không nằm trong {"hybrid", "pageindex", "none"}

---

## Điều còn hạn chế

- **Hạn chế:** Faithfulness và Answer Relevance được ước tính bằng keyword overlap, không dùng LLM evaluator độc lập; kết quả có thể không chính xác với câu trả lời dài hoặc paraphrase
- **Nếu có thêm thời gian:** Tích hợp RAGAS hoặc dùng GPT-4o-mini làm evaluator để tính Faithfulness/Relevance chính xác hơn theo từng case

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 2026-09-21
- **Tên thành viên:** [Điền tên]
