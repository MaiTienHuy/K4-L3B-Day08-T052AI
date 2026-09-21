"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải và kiểm tra ít nhất 3 PDF/DOCX từ nguồn công khai."""
    sources = {
        "01_quy_che_tuyen_sinh_2026.pdf": "https://moet.gov.vn/van-ban/van-ban-quan-ly-nha-nuoc/Pages/chi-tiet-van-ban.aspx?ItemID=8456",
        "02_ke_hoach_tuyen_sinh_2026.pdf": "https://moet.gov.vn/van-ban/van-ban-quan-ly-nha-nuoc/Pages/chi-tiet-van-ban.aspx?ItemID=8457",
        "03_huong_dan_tuyen_sinh_2026.pdf": "https://moet.gov.vn/van-ban/van-ban-quan-ly-nha-nuoc/Pages/chi-tiet-van-ban.aspx?ItemID=8458",
        "04_so_luong_tuyen_sinh_2026.pdf": "https://moet.gov.vn/van-ban/van-ban-quan-ly-nha-nuoc/Pages/chi-tiet-van-ban.aspx?ItemID=8459",
    }
    
    # Kiểm tra các file đã có trong thư mục
    existing_files = [p for p in DATA_DIR.iterdir() if p.suffix.lower() in {".pdf", ".doc", ".docx"} and p.stat().st_size > 1024]
    if len(existing_files) >= 3:
        print(f"Found {len(existing_files)} valid legal documents in {DATA_DIR}:")
        for f in existing_files:
            print(f"  - {f.name} ({f.stat().st_size} bytes)")
        return

    # Nếu chưa có đủ file, tải từ sources
    import requests
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for filename, url in sources.items():
        dest = DATA_DIR / filename
        if not dest.exists() or dest.stat().st_size <= 1024:
            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200 and len(response.content) > 1024:
                    dest.write_bytes(response.content)
                    print(f"Downloaded: {filename} ({len(response.content)} bytes)")
            except Exception as e:
                print(f"Failed to download {filename} from {url}: {e}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
