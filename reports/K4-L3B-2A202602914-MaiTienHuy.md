# Individual contribution report

## Thông tin

- **Họ và tên:** Mai Tiến Huy
- **Mã học viên:** 2A202602914
- **Nhóm:** K4-Day08, nhóm 4 thành viên
- **Repository:** K4-Day08-MaiTienHuy-2A202602914 / branch: main

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit | Trạng thái |
|---|---|---|---|
| Thu thập tài liệu chính sách | Tải 4 PDF tuyển sinh 2026 (quy chế, kế hoạch, hướng dẫn, số lượng) từ nguồn công khai | `src/task1_collect_legal_docs.py`, `data/landing/legal/*.pdf` | Done |
| Crawl bài viết | Viết `crawl_article()` dùng requests + BeautifulSoup + markdownify; điền 5 URL từ xaydungchinhsach.chinhphu.vn | `src/task2_crawl_news.py`, `data/landing/news/*.json` | Done |
| Chuẩn hóa Markdown | Hoàn thiện `convert_legal_docs()` dùng MarkItDown + pypdf fallback; `convert_news_articles()` thêm header metadata | `src/task3_convert_markdown.py`, `data/standardized/` | Done |
| Quản lý repo | Duy trì cấu trúc thư mục, `.gitignore`, kiểm tra acceptance test pass | `.gitignore`, `TEAMMATES.md` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng `requests` + `BeautifulSoup` + `markdownify` thay vì Crawl4AI cho task 2  
   **Lý do/evidence:** Website xaydungchinhsach.chinhphu.vn không chặn crawler đơn giản; requests đủ để lấy nội dung HTML tĩnh, nhẹ hơn và không cần cài browser  
   **Trade-off:** Mất khả năng render JavaScript, nhưng các trang mục tiêu đều là nội dung tĩnh nên không bị ảnh hưởng

2. **Quyết định:** Dùng MarkItDown với pypdf làm fallback khi convert PDF  
   **Lý do/evidence:** MarkItDown giữ cấu trúc heading tốt hơn; pypdf là fallback khi MarkItDown gặp PDF scan  
   **Trade-off:** MarkItDown đôi khi tạo output có nhiều ký tự thừa từ bảng biểu PDF; cần validate thủ công

---

## Kiểm thử và kết quả

- **Test đã chạy:** `pytest tests/test_acceptance.py -v` → 5/5 PASS
- **Kết quả:** 4 PDF landing (879KB–3.4MB), 5 JSON đủ `url/title/date_crawled/content_markdown`, 9 Markdown chuẩn hóa (7KB–87KB)
- **Lỗi đã xử lý:** article_01 trả về 200 nhưng content chủ yếu là ảnh scan → thêm logic lọc `script/style/iframe` trước khi markdownify

---

## Điều còn hạn chế

- **Hạn chế:** Crawler không xử lý được nội dung JavaScript-rendered; một số ảnh trong bài viết bị giữ lại dưới dạng markdown image link gây nhiễu khi chunking
- **Nếu có thêm thời gian:** Thêm bước post-process để lọc bỏ dòng `![]()` ảnh khỏi content_markdown trước khi lưu JSON

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 2026-09-21
- **Tên thành viên:** Mai Tiến Huy
