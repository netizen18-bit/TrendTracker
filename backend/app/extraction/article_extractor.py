import re
import json
import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from app.utils.http_client import fetch_url
from app.monitors.timing_engine import normalize_datetime

class ArticleExtractor:
    """
    Deep article extractor that extracts full body, metadata, publication dates,
    authors, images, tags, and canonical URLs from discovered articles.
    """
    @staticmethod
    async def extract(url: str, preloaded_html: Optional[str] = None) -> Dict[str, Any]:
        html = preloaded_html
        if not html:
            html, _, _, _ = await fetch_url(url, timeout=8.0)

        if not html:
            return {
                "title": url.split("/")[-1].replace("-", " ").title() or "Untitled",
                "url": url,
                "canonical_url": url,
                "author": "Unknown",
                "published_at": None,
                "content": "",
                "featured_image": None,
                "meta_description": "",
                "categories": [],
                "tags": [],
                "inline_images": [],
                "relevant_links": [],
                "raw_metadata": {}
            }

        soup = BeautifulSoup(html, "lxml")
        base_domain = urlparse(url).netloc

        # 1. Canonical URL
        canonical_tag = soup.find("link", rel="canonical")
        canonical_url = canonical_tag.get("href") if canonical_tag else url
        canonical_url = urljoin(url, canonical_url).split("#")[0]

        # 2. OpenGraph & Twitter & Meta tags dictionary
        meta_dict = {}
        for m in soup.find_all("meta"):
            name = m.get("name") or m.get("property") or m.get("itemprop")
            content = m.get("content")
            if name and content:
                meta_dict[name.lower()] = content.strip()

        # 3. JSON-LD structured data extraction
        json_ld_data = {}
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "{}")
                if isinstance(data, list) and data:
                    data = data[0]
                if isinstance(data, dict):
                    # Look for Article / BlogPosting / NewsArticle
                    schema_type = data.get("@type", "")
                    if any(t in str(schema_type) for t in ["Article", "BlogPosting", "NewsArticle", "TechArticle", "WebPage"]):
                        json_ld_data = data
                        break
                    elif "@graph" in data:
                        for item in data["@graph"]:
                            if any(t in str(item.get("@type", "")) for t in ["Article", "BlogPosting", "NewsArticle"]):
                                json_ld_data = item
                                break
            except Exception:
                continue

        # 4. Title Extraction
        title = (
            meta_dict.get("og:title") or
            meta_dict.get("twitter:title") or
            json_ld_data.get("headline") or
            (soup.find("h1").get_text().strip() if soup.find("h1") else None) or
            (soup.title.string.strip() if soup.title else None) or
            "Untitled Article"
        )
        title = re.sub(r"\s+", " ", title).strip()

        # 5. Publication Date Extraction
        pub_date_raw = (
            json_ld_data.get("datePublished") or
            json_ld_data.get("dateCreated") or
            meta_dict.get("article:published_time") or
            meta_dict.get("og:article:published_time") or
            meta_dict.get("publication_date") or
            meta_dict.get("date") or
            meta_dict.get("pubdate") or
            meta_dict.get("dc.date.issued") or
            meta_dict.get("parsely-pub-date")
        )

        # Fallback to <time> tag
        if not pub_date_raw:
            time_tag = soup.find("time")
            if time_tag:
                pub_date_raw = time_tag.get("datetime") or time_tag.get_text()

        published_at = normalize_datetime(pub_date_raw)

        # 6. Author Extraction
        author = meta_dict.get("author") or meta_dict.get("article:author")
        if not author and json_ld_data.get("author"):
            author_obj = json_ld_data["author"]
            if isinstance(author_obj, dict):
                author = author_obj.get("name")
            elif isinstance(author_obj, list) and author_obj:
                author = author_obj[0].get("name") if isinstance(author_obj[0], dict) else str(author_obj[0])
            elif isinstance(author_obj, str):
                author = author_obj

        if not author:
            author_elem = soup.find(class_=re.compile(r"(author|byline|writer)", re.I))
            if author_elem:
                author = author_elem.get_text().strip()
                author = re.sub(r"^[bB]y\s+", "", author)

        author = author or "Editorial Team"

        # 7. Featured Image
        featured_image = (
            meta_dict.get("og:image") or
            meta_dict.get("twitter:image") or
            meta_dict.get("image")
        )
        if not featured_image and json_ld_data.get("image"):
            img_val = json_ld_data["image"]
            if isinstance(img_val, str):
                featured_image = img_val
            elif isinstance(img_val, dict):
                featured_image = img_val.get("url")
            elif isinstance(img_val, list) and img_val:
                featured_image = img_val[0] if isinstance(img_val[0], str) else img_val[0].get("url")

        if featured_image:
            featured_image = urljoin(url, featured_image)

        # 8. Meta Description
        meta_description = (
            meta_dict.get("description") or
            meta_dict.get("og:description") or
            meta_dict.get("twitter:description") or
            json_ld_data.get("description") or
            ""
        )

        # 9. Categories and Tags
        categories = []
        tags = []
        if meta_dict.get("article:section"):
            categories.append(meta_dict["article:section"])
        if json_ld_data.get("articleSection"):
            sec = json_ld_data["articleSection"]
            if isinstance(sec, list):
                categories.extend(sec)
            elif isinstance(sec, str):
                categories.append(sec)

        for key, val in meta_dict.items():
            if "tag" in key or key == "keywords":
                for item in val.split(","):
                    if item.strip() and item.strip() not in tags:
                        tags.append(item.strip())

        # 10. Clean Body Text & Inline Images & Relevant Links
        # Remove navigation, headers, footers, scripts, styles
        for trash in soup(["script", "style", "nav", "footer", "header", "noscript", "aside", "form"]):
            trash.decompose()

        article_container = (
            soup.find("article") or
            soup.find(class_=re.compile(r"(post-content|article-content|entry-content|main-content)", re.I)) or
            soup.find("main") or
            soup.body
        )

        content = ""
        inline_images = []
        relevant_links = []

        if article_container:
            # Inline images
            for img in article_container.find_all("img"):
                src = img.get("src") or img.get("data-src")
                if src:
                    full_img = urljoin(url, src)
                    if full_img != featured_image and full_img not in inline_images:
                        inline_images.append(full_img)

            # Relevant links
            for a in article_container.find_all("a", href=True):
                href = a.get("href")
                full_link = urljoin(url, href)
                if full_link != url and full_link not in relevant_links:
                    relevant_links.append(full_link)

            # Clean paragraphs
            paragraphs = [p.get_text().strip() for p in article_container.find_all(["p", "h2", "h3", "h4", "li"]) if p.get_text().strip()]
            content = "\n\n".join(paragraphs)

        return {
            "title": title,
            "url": url,
            "canonical_url": canonical_url,
            "author": author[:250],
            "published_at": published_at,
            "content": content,
            "featured_image": featured_image,
            "meta_description": meta_description[:1000],
            "categories": categories[:5],
            "tags": tags[:10],
            "inline_images": inline_images[:10],
            "relevant_links": relevant_links[:15],
            "raw_metadata": {k: v for k, v in meta_dict.items() if len(v) < 300}
        }
