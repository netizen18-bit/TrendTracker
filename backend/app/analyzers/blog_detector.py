import re
import json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any, Set
from app.utils.http_client import fetch_url

COMMON_BLOG_PATHS = [
    "/blog",
    "/news",
    "/articles",
    "/posts",
    "/insights",
    "/press-releases",
    "/stories",
    "/feed",
    "/journal"
]

ARTICLE_URL_PATTERNS = [
    re.compile(r'/blog/[a-zA-Z0-9_-]+'),
    re.compile(r'/news/[a-zA-Z0-9_-]+'),
    re.compile(r'/articles/[a-zA-Z0-9_-]+'),
    re.compile(r'/posts/[a-zA-Z0-9_-]+'),
    re.compile(r'/\d{4}/\d{2}/[a-zA-Z0-9_-]+'),
    re.compile(r'/\d{4}/\d{2}/\d{2}/[a-zA-Z0-9_-]+'),
]

class BlogDetector:
    @staticmethod
    async def detect(base_url: str, html_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Investigates the website to identify the blog index page, article patterns, and metadata structures.
        """
        results = {
            "found": False,
            "blog_url": None,
            "article_urls_sample": [],
            "article_count": 0,
            "has_json_ld": False,
            "has_opengraph": False,
            "has_time_tags": False,
            "article_pattern_hint": None,
        }

        # 1. Search homepage links for blog/news nav items
        candidate_blog_urls: List[str] = []
        if html_content:
            soup = BeautifulSoup(html_content, "lxml")
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").strip()
                text = a.get_text().strip().lower()
                full_url = urljoin(base_url, href)
                if any(k in text for k in ["blog", "news", "articles", "stories", "insights", "resources"]):
                    if full_url not in candidate_blog_urls and urlparse(full_url).netloc == urlparse(base_url).netloc:
                        candidate_blog_urls.append(full_url)

        # 2. Add common paths
        for path in COMMON_BLOG_PATHS:
            full = urljoin(base_url, path)
            if full not in candidate_blog_urls:
                candidate_blog_urls.append(full)

        # 3. Test base_url itself in case the user supplied the blog page directly
        if base_url not in candidate_blog_urls:
            candidate_blog_urls.insert(0, base_url)

        # 4. Check candidates
        for blog_url in candidate_blog_urls:
            content, resp, _, err = await fetch_url(blog_url, timeout=6.0)
            if not content:
                continue

            extracted_articles, meta_signals = BlogDetector.extract_article_links(blog_url, content)
            if len(extracted_articles) >= 2 or (blog_url != base_url and len(extracted_articles) >= 1):
                results["found"] = True
                results["blog_url"] = blog_url
                results["article_urls_sample"] = extracted_articles[:10]
                results["article_count"] = len(extracted_articles)
                results["has_json_ld"] = meta_signals["has_json_ld"]
                results["has_opengraph"] = meta_signals["has_opengraph"]
                results["has_time_tags"] = meta_signals["has_time_tags"]
                results["article_pattern_hint"] = meta_signals.get("pattern")
                return results

        return results

    @staticmethod
    def extract_article_links(page_url: str, html: str) -> (List[str], Dict[str, Any]):
        soup = BeautifulSoup(html, "lxml")
        base_domain = urlparse(page_url).netloc
        
        # Check metadata signals on the page
        has_json_ld = bool(soup.find("script", type="application/ld+json"))
        has_og = bool(soup.find("meta", property=re.compile(r"^og:")))
        has_time = bool(soup.find("time"))

        discovered_links: Set[str] = set()

        # Strategy A: Check semantic <article> tags first
        articles = soup.find_all(["article", "div"], class_=re.compile(r"(post|article|card|entry|story)", re.I))
        for container in articles:
            for a in container.find_all("a", href=True):
                href = a.get("href")
                full = urljoin(page_url, href)
                parsed = urlparse(full)
                if parsed.netloc == base_domain and len(parsed.path) > 3 and parsed.path != urlparse(page_url).path:
                    # Ignore tag/category/author links
                    if not any(x in parsed.path.lower() for x in ["/tag/", "/category/", "/author/", "/page/", "/feed"]):
                        discovered_links.add(full.split("#")[0].split("?")[0])

        # Strategy B: Search matching URL patterns across all <a> tags
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            full = urljoin(page_url, href)
            parsed = urlparse(full)
            if parsed.netloc == base_domain:
                clean_url = full.split("#")[0].split("?")[0]
                for pattern in ARTICLE_URL_PATTERNS:
                    if pattern.search(clean_url):
                        discovered_links.add(clean_url)
                        break

        # Filter out homepage or the blog page itself
        clean_page_url = page_url.split("#")[0].split("?")[0]
        discovered_links.discard(clean_page_url)
        discovered_links.discard(urljoin(page_url, "/"))

        return list(discovered_links), {
            "has_json_ld": has_json_ld,
            "has_opengraph": has_og,
            "has_time_tags": has_time,
            "pattern": "custom_heuristics" if discovered_links else None
        }
