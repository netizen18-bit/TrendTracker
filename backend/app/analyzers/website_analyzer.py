import asyncio
import time
from urllib.parse import urlparse
from typing import Dict, Any, List
from app.utils.http_client import fetch_url
from app.analyzers.rss_detector import RssDetector
from app.analyzers.sitemap_detector import SitemapDetector
from app.analyzers.blog_detector import BlogDetector

class WebsiteAnalyzer:
    """
    Autonomous intelligence pipeline that investigates any website URL
    and determines available monitoring strategies and metadata support.
    """
    @staticmethod
    async def analyze(target_url: str) -> Dict[str, Any]:
        start_time = time.perf_counter()
        
        # Normalize URL
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "https://" + target_url

        parsed_url = urlparse(target_url)
        base_origin = f"{parsed_url.scheme}://{parsed_url.netloc}"

        investigation_log = [
            f"Initiating autonomous investigation for: {target_url}",
            f"Normalized base origin: {base_origin}"
        ]

        # 1. Fetch Root Page
        root_html, root_resp, root_latency, root_err = await fetch_url(target_url, timeout=7.0)
        if root_err:
            investigation_log.append(f"Root URL probe encountered issue: {root_err}")
        else:
            investigation_log.append(f"Root page retrieved successfully ({round(root_latency, 1)}ms)")

        # 2. Run Parallel Probing for RSS, Sitemap, and Blog
        investigation_log.append("Executing parallel probes for RSS feeds, XML sitemaps, and direct blog pages...")
        rss_task = RssDetector.detect(base_origin, root_html)
        sitemap_task = SitemapDetector.detect(base_origin)
        blog_task = BlogDetector.detect(target_url, root_html)

        rss_res, sitemap_res, blog_res = await asyncio.gather(rss_task, sitemap_task, blog_task)

        # Log findings
        if rss_res["found"]:
            investigation_log.append(f"RSS/Atom Feed discovered: {rss_res['feed_url']} (Format: {rss_res['format']}, Items: {rss_res['items_count']}) via {rss_res['discovery_method']}")
        else:
            investigation_log.append("No public RSS/Atom feed detected on standard endpoints or link tags.")

        if sitemap_res["found"]:
            type_str = "Sitemap Index" if sitemap_res["is_index"] else "Standard Sitemap"
            investigation_log.append(f"XML Sitemap discovered: {sitemap_res['sitemap_url']} ({type_str}, ~{sitemap_res['url_count']} URLs) via {sitemap_res['discovery_method']}")
        else:
            investigation_log.append("No standard XML sitemap or robots.txt sitemap directive found.")

        if blog_res["found"]:
            investigation_log.append(f"Blog Section identified: {blog_res['blog_url']} (Extracted ~{blog_res['article_count']} sample article links)")
        else:
            investigation_log.append("Blog section not explicitly isolated; fallback to homepage link pattern tracking.")

        # Strategy selection intelligence
        strategies: List[str] = []
        sources_to_create: List[Dict[str, Any]] = []

        if rss_res["found"]:
            strategies.append("RSS")
            sources_to_create.append({
                "source_type": "RSS",
                "source_url": rss_res["feed_url"],
                "priority": 1,
                "is_active": True
            })

        if sitemap_res["found"]:
            strategies.append("SITEMAP")
            # If sitemap is an index and has post-sitemap, prioritize sub-sitemap if available
            target_sitemap_url = sitemap_res["sitemap_url"]
            if sitemap_res.get("sub_sitemaps"):
                post_sms = [s for s in sitemap_res["sub_sitemaps"] if any(k in s.lower() for k in ["post", "blog", "article"])]
                if post_sms:
                    target_sitemap_url = post_sms[0]

            sources_to_create.append({
                "source_type": "SITEMAP",
                "source_url": target_sitemap_url,
                "priority": 2 if rss_res["found"] else 1,
                "is_active": True
            })

        if blog_res["found"]:
            strategies.append("DIRECT_PAGE")
            sources_to_create.append({
                "source_type": "DIRECT_PAGE",
                "source_url": blog_res["blog_url"],
                "priority": 3 if (rss_res["found"] and sitemap_res["found"]) else (2 if rss_res["found"] or sitemap_res["found"] else 1),
                "is_active": True
            })

        # Fallback if nothing specific was found
        if not sources_to_create:
            strategies.append("DIRECT_PAGE")
            sources_to_create.append({
                "source_type": "DIRECT_PAGE",
                "source_url": target_url,
                "priority": 1,
                "is_active": True
            })
            investigation_log.append("Fallback to direct page link monitoring on root URL.")

        primary_strategy = " + ".join(strategies)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        investigation_log.append(f"Investigation complete in {round(elapsed_ms, 1)}ms. Selected Strategy: {primary_strategy}")

        return {
            "target_url": target_url,
            "base_origin": base_origin,
            "analysis_duration_ms": round(elapsed_ms, 2),
            "investigation_log": investigation_log,
            "strategies_available": {
                "rss": rss_res["found"],
                "sitemap": sitemap_res["found"],
                "direct_page": blog_res["found"],
            },
            "selected_strategy": primary_strategy,
            "feed_details": rss_res,
            "sitemap_details": sitemap_res,
            "blog_details": blog_res,
            "recommended_sources": sources_to_create,
            "publication_metadata_support": {
                "json_ld": blog_res.get("has_json_ld", False),
                "opengraph": blog_res.get("has_opengraph", False),
                "time_tags": blog_res.get("has_time_tags", False),
                "sitemap_lastmod": sitemap_res.get("has_lastmod", False),
            }
        }
