# Individual contribution report

## Thông tin

- **Họ và tên:** Hoàng Ngọc Đức
- **Mã học viên:** 2A202602380
- **Nhóm:** K4-Day08, nhóm 4 thành viên
- **Repository:** K4-Day08-MaiTienHuy-2A202602914 / branch: main

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit | Trạng thái |
|---|---|---|---|
| RRF Reranking | Hoàn thiện `rerank_rrf()`: tính `1/(k+rank)` cho từng ranked list, deepcopy item tránh mutation, gộp theo ID, set `retrieval_method="hybrid"` | `src/task7_reranking.py` | Done |
| PageIndex Fallback | Hoàn thiện `pageindex_search()` với timeout và error handling; tránh crash khi provider lỗi | `src/task8_pageindex_vectorless.py` | Done |
| Retrieval Pipeline | Hoàn thiện `retrieve()`: gọi dense + BM25 → RRF một lần → đọc best cosine score → fallback pageindex khi dưới threshold; giữ hybrid khi fallback lỗi | `src/task9_retrieval_pipeline.py` | Done |
| Threshold calibration | Kiểm thử SCORE_THRESHOLD=0.30 trên query đúng domain (score 0.6–0.9) và ngoài domain (score 0.10–0.25) | `src/task9_retrieval_pipeline.py` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Đặt SCORE_THRESHOLD=0.30 dựa trên thực nghiệm với 2 loại query  
   **Lý do/evidence:** Query đúng domain ("thời gian đăng ký nguyện vọng") cho dense score 0.65–0.90; query ngoài domain ("thời tiết hôm nay") cho score 0.10–0.22 → threshold 0.30 tạo ranh giới rõ ràng  
   **Trade-off:** Threshold cố định có thể sai với corpus khác; nên hiệu chỉnh lại nếu thay corpus

2. **Quyết định:** RRF chỉ chạy một lần trong Task 9, không gọi lại trong các module khác  
   **Lý do/evidence:** Contract quy định rõ RRF score và dense score là hai thang đo khác nhau; fallback decision dùng cosine score gốc (trước RRF), không dùng RRF score  
   **Trade-off:** Phải truyền dense list riêng ra ngoài `rerank_rrf()` để đọc best_dense_score; code dài hơn nhưng đúng theo spec

---

## Kiểm thử và kết quả

- **Test đã chạy:** `pytest tests/test_contracts.py -q` → PASS; thử query "thời tiết hôm nay" → trả safe refusal (không crash); thử "xác nhận nhập học 2026" → trả hybrid results có citation
- **Kết quả:** Chunk xuất hiện cả dense và BM25 nhận RRF score cao hơn; pipeline không bị crash khi pageindex_search raise Exception
- **Lỗi đã xử lý:** Lỗi ban đầu RRF mutate item đầu vào → sửa bằng `copy.deepcopy()` trước khi ghi score và retrieval_method mới

---

## Điều còn hạn chế

- **Hạn chế:** SCORE_THRESHOLD=0.30 là hằng số cứng; không tự động điều chỉnh theo phân phối score của corpus
- **Nếu có thêm thời gian:** Tính dynamic threshold dựa trên mean - std của dense scores trong một batch query đại diện

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 2026-09-21
- **Tên thành viên:** Hoàng Ngọc Đức
