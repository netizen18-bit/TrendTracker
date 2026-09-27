from typing import List, Dict, Any, Tuple
from app.utils.http_client import fetch_url
from app.analyzers.blog_detector import BlogDetector

class PageMonitor:
    """
    Method 3: Direct Blog Page Monitor
    Periodically checks competitor blog/article index page and discovers newly listed articles.
    """
    @staticmethod
    async def check(blog_url: str) -> Tuple[List[Dict[str, Any]], float, int, str]:
        """
        Returns (items, response_time_ms, status_code, error_msg)
        Each item has: { 'url', 'title', 'detection_method' }
        """
        content, resp, latency_ms, error = await fetch_url(blog_url)
        if error or not content:
            status_code = resp.status_code if resp else 0
            return [], latency_ms, status_code, error or "Empty blog page response"

        article_urls, meta_signals = BlogDetector.extract_article_links(blog_url, content)
        items = []

        for url in article_urls:
            slug = url.rstrip("/").split("/")[-1]
            title = slug.replace("-", " ").replace("_", " ").title() if slug else url
            items.append({
                "url": url,
                "title": title,
                "published_at": None,  # Will be extracted directly from article HTML on discovery
                "detection_method": "DIRECT_PAGE"
            })

        status_code = resp.status_code if resp else 200
        return items, latency_ms, status_code, None
