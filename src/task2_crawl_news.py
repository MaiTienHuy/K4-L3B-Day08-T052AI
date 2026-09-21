"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
import json
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://xaydungchinhsach.chinhphu.vn/toan-van-cong-van-2304-bgddt-gddh-huong-dan-tuyen-sinh-dai-hoc-cao-dang-2026-119260505052505936.htm?utm",
    "https://xaydungchinhsach.chinhphu.vn/tuyen-sinh-dai-hoc-cao-dang-2026-nhung-luu-y-voi-thi-sinh-119260505060425039.htm",
    "https://xaydungchinhsach.chinhphu.vn/tuyen-sinh-2026-cac-moc-thoi-gian-quan-trong-thi-sinh-can-nho-119260206155449664.htm",
    "https://xaydungchinhsach.chinhphu.vn/chinh-sach-uu-tien-trong-tuyen-sinh-dai-hoc-119260227153842885.htm",
    "https://xaydungchinhsach.chinhphu.vn/huong-dan-thanh-toan-truc-tuyen-le-phi-xet-tuyen-dai-hoc-2026-119260716115111114.htm",
]


async def crawl_article(url: str) -> dict:
    """Thu thập bài viết từ URL và trả về dict metadata + markdown content."""
    from datetime import datetime
    import requests
    from bs4 import BeautifulSoup
    import markdownify

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Lấy tiêu đề bài viết
    h1 = soup.find("h1") or soup.find("title")
    title = h1.get_text(strip=True) if h1 else "Không có tiêu đề"

    # Lấy phần nội dung chính
    content_el = (
        soup.find("div", class_="detail-content")
        or soup.find("div", class_="detail-main")
        or soup.find("div", class_="main")
        or soup.find("article")
        or soup.find("body")
    )

    if content_el:
        # Xóa các thẻ script, style, comment, iframe không cần thiết
        for tag in content_el(["script", "style", "noscript", "iframe"]):
            tag.decompose()
        content_markdown = markdownify.markdownify(str(content_el), heading_style="ATX").strip()
    else:
        content_markdown = soup.get_text(separator="\n", strip=True)

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": content_markdown,
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
