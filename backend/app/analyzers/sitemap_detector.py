import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any, Tuple
from app.utils.http_client import fetch_url

COMMON_SITEMAP_PATHS = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/post-sitemap.xml",
    "/blog-sitemap.xml",
    "/sitemap-posts.xml",
    "/sitemap/sitemap.xml",
    "/wp-sitemap.xml",
    "/sitemap-news.xml"
]

class SitemapDetector:
    @staticmethod
    async def detect(base_url: str) -> Dict[str, Any]:
        """
        Investigates robots.txt and standard endpoints to detect XML sitemaps and sitemap indexes.
        """
        results = {
            "found": False,
            "sitemap_url": None,
            "is_index": False,
            "sub_sitemaps": [],
            "sample_urls": [],
            "url_count": 0,
            "has_lastmod": False,
            "discovery_method": None,
        }

        discovered_candidates: List[Tuple[str, str]] = []

        # 1. Investigate robots.txt
        robots_url = urljoin(base_url, "/robots.txt")
        robots_content, _, _, _ = await fetch_url(robots_url, timeout=5.0)
        if robots_content:
            for line in robots_content.splitlines():
                if line.lower().startswith("sitemap:"):
                    sitemap_path = line.split(":", 1)[1].strip()
                    if sitemap_path:
                        discovered_candidates.append((sitemap_path, "robots.txt"))

        # 2. Add standard paths
        for path in COMMON_SITEMAP_PATHS:
            full_path = urljoin(base_url, path)
            if full_path not in [c[0] for c in discovered_candidates]:
                discovered_candidates.append((full_path, "common_probe"))

        # 3. Test candidates
        for sm_url, method in discovered_candidates:
            content, resp, _, err = await fetch_url(sm_url, timeout=6.0)
            if not content:
                continue

            # Check if valid XML sitemap
            if "<urlset" in content or "<sitemapindex" in content:
                soup = BeautifulSoup(content, "xml")
                
                # Check for sitemap index
                sitemap_tags = soup.find_all("sitemap")
                if sitemap_tags or "<sitemapindex" in content:
                    results["found"] = True
                    results["sitemap_url"] = sm_url
                    results["is_index"] = True
                    results["discovery_method"] = method
                    
                    sub_urls = []
                    for sm in sitemap_tags:
                        loc = sm.find("loc")
                        if loc and loc.text:
                            sub_urls.append(loc.text.strip())
                    
                    results["sub_sitemaps"] = sub_urls

                    # Try to inspect the most promising sub-sitemap (e.g. post/blog/article)
                    post_sitemaps = [u for u in sub_urls if any(k in u.lower() for k in ["post", "blog", "article", "news"])]
                    target_sub = post_sitemaps[0] if post_sitemaps else (sub_urls[0] if sub_urls else None)
                    
                    if target_sub:
                        sub_content, _, _, _ = await fetch_url(target_sub, timeout=6.0)
                        if sub_content:
                            sub_soup = BeautifulSoup(sub_content, "xml")
                            urls = [loc.text.strip() for loc in sub_soup.find_all("loc") if loc.text]
                            results["sample_urls"] = urls[:10]
                            results["url_count"] = len(urls)
                            results["has_lastmod"] = bool(sub_soup.find("lastmod"))
                    return results

                # Regular urlset
                url_tags = soup.find_all("url")
                if url_tags or "<urlset" in content:
                    urls = [loc.text.strip() for loc in soup.find_all("loc") if loc.text]
                    results["found"] = True
                    results["sitemap_url"] = sm_url
                    results["is_index"] = False
                    results["url_count"] = len(urls)
                    results["sample_urls"] = urls[:10]
                    results["has_lastmod"] = bool(soup.find("lastmod"))
                    results["discovery_method"] = method
                    return results

        return results
