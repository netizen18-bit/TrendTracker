from bs4 import BeautifulSoup
from typing import List, Dict, Any, Tuple
from app.utils.http_client import fetch_url
from app.monitors.timing_engine import normalize_datetime

class SitemapMonitor:
    """
    Method 2: XML Sitemap Monitor
    Periodically queries competitor XML sitemaps / sitemap indexes and tracks URLs + lastmod.
    """
    @staticmethod
    async def check(sitemap_url: str) -> Tuple[List[Dict[str, Any]], float, int, str]:
        """
        Returns (items, response_time_ms, status_code, error_msg)
        Each item has: { 'url', 'title', 'published_at', 'detection_method' }
        """
        content, resp, latency_ms, error = await fetch_url(sitemap_url)
        if error or not content:
            status_code = resp.status_code if resp else 0
            return [], latency_ms, status_code, error or "Empty sitemap response"

        soup = BeautifulSoup(content, "xml")
        items = []

        # Check if sitemapindex
        sitemap_tags = soup.find_all("sitemap")
        if sitemap_tags:
            # Handle sitemap index by inspecting sub-sitemaps (prioritizing post/blog sitemaps)
            post_sub_urls = []
            for sm in sitemap_tags:
                loc = sm.find("loc")
                if loc and loc.text:
                    u = loc.text.strip()
                    if any(k in u.lower() for k in ["post", "blog", "article", "news"]):
                        post_sub_urls.append(u)

            target_sub = post_sub_urls[0] if post_sub_urls else (sitemap_tags[0].find("loc").text.strip() if sitemap_tags[0].find("loc") else None)
            if target_sub:
                sub_content, sub_resp, sub_lat, sub_err = await fetch_url(target_sub)
                if sub_content:
                    soup = BeautifulSoup(sub_content, "xml")
                    latency_ms += sub_lat

        # Parse standard <url> tags
        for url_node in soup.find_all("url"):
            loc = url_node.find("loc")
            if not loc or not loc.text:
                continue

            url = loc.text.strip()
            lastmod_tag = url_node.find("lastmod")
            published_at = normalize_datetime(lastmod_tag.text.strip()) if lastmod_tag and lastmod_tag.text else None

            # Attempt a readable fallback title from URL slug
            slug = url.rstrip("/").split("/")[-1]
            title = slug.replace("-", " ").replace("_", " ").title() if slug else url

            items.append({
                "url": url,
                "title": title,
                "published_at": published_at,
                "detection_method": "SITEMAP"
            })

        status_code = resp.status_code if resp else 200
        return items, latency_ms, status_code, None
