import feedparser
from typing import List, Dict, Any, Tuple
from app.utils.http_client import fetch_url
from app.monitors.timing_engine import normalize_datetime

class RssMonitor:
    """
    Method 1: RSS/Atom Feed Monitor
    Periodically queries competitor RSS/Atom feeds and returns article entries with dates.
    """
    @staticmethod
    async def check(feed_url: str) -> Tuple[List[Dict[str, Any]], float, int, str]:
        """
        Returns (items, response_time_ms, status_code, error_msg)
        Each item has: { 'url', 'title', 'published_at', 'author', 'summary' }
        """
        content, resp, latency_ms, error = await fetch_url(feed_url)
        if error or not content:
            status_code = resp.status_code if resp else 0
            return [], latency_ms, status_code, error or "Empty feed response"

        parsed = feedparser.parse(content)
        items = []

        for entry in parsed.entries:
            link = entry.get("link")
            if not link:
                continue

            title = entry.get("title", "Untitled")
            
            # Extract date from parsed entry
            pub_date_raw = (
                entry.get("published") or
                entry.get("updated") or
                entry.get("created") or
                entry.get("pubDate")
            )
            
            published_at = normalize_datetime(pub_date_raw)
            if not published_at and hasattr(entry, "published_parsed") and entry.published_parsed:
                import datetime
                import time
                try:
                    published_at = datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=datetime.timezone.utc)
                except Exception:
                    pass

            author = entry.get("author") or "Editorial Staff"
            summary = entry.get("summary") or ""

            items.append({
                "url": link.strip(),
                "title": title.strip(),
                "published_at": published_at,
                "author": author,
                "summary": summary[:500],
                "detection_method": "RSS"
            })

        status_code = resp.status_code if resp else 200
        return items, latency_ms, status_code, None
