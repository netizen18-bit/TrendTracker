import feedparser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any
from app.utils.http_client import fetch_url

COMMON_FEED_PATHS = [
    "/feed",
    "/rss",
    "/rss.xml",
    "/feed.xml",
    "/atom.xml",
    "/index.xml",
    "/blog/feed",
    "/blog/rss.xml",
    "/posts/rss.xml",
    "/feed/atom",
    "/feeds/posts/default"
]

class RssDetector:
    @staticmethod
    async def detect(base_url: str, html_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Investigates a website to locate RSS/Atom feeds.
        Returns detailed results including feed URL, feed title, item count, and discovery method.
        """
        results = {
            "found": False,
            "feed_url": None,
            "title": None,
            "format": None,
            "items_count": 0,
            "discovery_method": None,
            "discovered_feeds": []
        }

        discovered_urls = []

        # 1. Search HTML <link> tags
        if html_content:
            soup = BeautifulSoup(html_content, "lxml")
            feed_links = soup.find_all("link", type=["application/rss+xml", "application/atom+xml", "text/xml"])
            for link in feed_links:
                href = link.get("href")
                if href:
                    full_url = urljoin(base_url, href)
                    if full_url not in discovered_urls:
                        discovered_urls.append((full_url, "html_link_tag"))

        # 2. Probe common standard feed paths
        for path in COMMON_FEED_PATHS:
            test_url = urljoin(base_url, path)
            if test_url not in [u[0] for u in discovered_urls]:
                discovered_urls.append((test_url, "common_path_probe"))

        # 3. Test discovered URLs
        for feed_url, method in discovered_urls:
            content, resp, latency, err = await fetch_url(feed_url, timeout=5.0)
            if content and ("<rss" in content.lower() or "<feed" in content.lower() or "xml" in str(getattr(resp, 'headers', {}).get('content-type', '')).lower()):
                parsed = feedparser.parse(content)
                if parsed.entries or (parsed.version and parsed.version != ''):
                    results["discovered_feeds"].append({
                        "url": feed_url,
                        "title": parsed.feed.get("title", "Untitled Feed"),
                        "format": parsed.version or "RSS/Atom",
                        "entries_count": len(parsed.entries),
                        "discovery_method": method
                    })

        if results["discovered_feeds"]:
            # Pick best feed (prioritize by most entries and html_link_tag)
            best = sorted(
                results["discovered_feeds"], 
                key=lambda x: (x["entries_count"] > 0, x["discovery_method"] == "html_link_tag", x["entries_count"]), 
                reverse=True
            )[0]
            results["found"] = True
            results["feed_url"] = best["url"]
            results["title"] = best["title"]
            results["format"] = best["format"]
            results["items_count"] = best["entries_count"]
            results["discovery_method"] = best["discovery_method"]

        return results
