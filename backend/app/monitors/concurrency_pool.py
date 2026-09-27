import asyncio
import datetime
import time
from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Competitor, MonitoringSource, Article, MonitoringLog, utcnow
from app.monitors.rss_monitor import RssMonitor
from app.monitors.sitemap_monitor import SitemapMonitor
from app.monitors.page_monitor import PageMonitor
from app.extraction.article_extractor import ArticleExtractor
from app.monitors.timing_engine import calculate_detection_delay, normalize_datetime
from app.api.websocket import ws_manager
from app.config import settings

class MonitoringEngine:
    @staticmethod
    async def check_competitor(competitor_id: int, db: AsyncSession) -> Dict[str, Any]:
        """
        Executes a monitoring pass for a single competitor across its configured strategies.
        Guarantees fault isolation and records complete logs and timing data.
        """
        # Fetch competitor and sources
        stmt = select(Competitor).where(Competitor.id == competitor_id)
        result = await db.execute(stmt)
        competitor = result.scalar_one_or_none()

        if not competitor or not competitor.monitoring_enabled:
            return {"status": "skipped", "competitor_id": competitor_id}

        # Fetch active sources ordered by priority
        src_stmt = select(MonitoringSource).where(
            and_(MonitoringSource.competitor_id == competitor_id, MonitoringSource.is_active == True)
        ).order_by(MonitoringSource.priority.asc())
        sources_res = await db.execute(src_stmt)
        sources = list(sources_res.scalars().all())

        if not sources:
            return {"status": "no_active_sources", "competitor_id": competitor_id}

        check_time = utcnow()
        total_discovered = 0
        newly_detected_articles = []
        overall_status = "success"
        last_error = None
        total_resp_time = 0.0

        for source in sources:
            source_items: List[Dict[str, Any]] = []
            source_lat = 0.0
            source_status_code = 200
            source_err = None

            try:
                if source.source_type == "RSS":
                    source_items, source_lat, source_status_code, source_err = await RssMonitor.check(source.source_url)
                elif source.source_type == "SITEMAP":
                    source_items, source_lat, source_status_code, source_err = await SitemapMonitor.check(source.source_url)
                elif source.source_type == "DIRECT_PAGE":
                    source_items, source_lat, source_status_code, source_err = await PageMonitor.check(source.source_url)

                total_resp_time += source_lat
                source.last_checked = check_time

                if source_err:
                    source.last_status = "ERROR"
                    source.last_error = source_err
                    overall_status = "warning" if newly_detected_articles else "error"
                    last_error = source_err
                else:
                    source.last_status = "OK"
                    source.last_error = None

                # Process discovered items for this source
                new_from_source = 0
                for item in source_items:
                    total_discovered += 1
                    item_url = item["url"]

                    # Duplicate prevention check (canonical check)
                    dup_stmt = select(Article).where(
                        (Article.url == item_url) | (Article.canonical_url == item_url)
                    )
                    dup_res = await db.execute(dup_stmt)
                    existing_article = dup_res.scalar_one_or_none()

                    if existing_article:
                        # Already known article, skip to avoid duplicates
                        continue

                    # NEW ARTICLE FOUND! Extract full metadata & content
                    detection_time = utcnow()
                    extracted = await ArticleExtractor.extract(item_url)

                    # Re-verify canonical URL in case of redirects
                    canon_url = extracted.get("canonical_url") or item_url
                    canon_dup_stmt = select(Article).where(Article.canonical_url == canon_url)
                    canon_dup_res = await db.execute(canon_dup_stmt)
                    if canon_dup_res.scalar_one_or_none():
                        continue

                    # Determine publication timestamp (priority: source timestamp -> extracted timestamp)
                    pub_date = item.get("published_at") or extracted.get("published_at") or detection_time

                    # Calculate precise Detection Delay
                    delay_sec, delay_fmt = calculate_detection_delay(pub_date, detection_time)

                    # Create new Article record
                    new_article = Article(
                        competitor_id=competitor.id,
                        title=extracted.get("title") or item.get("title") or "Untitled",
                        url=item_url,
                        canonical_url=canon_url,
                        author=extracted.get("author") or item.get("author"),
                        published_at=pub_date,
                        detected_at=detection_time,
                        detection_delay_seconds=delay_sec,
                        detection_delay_formatted=delay_fmt,
                        detection_method=source.source_type,
                        content=extracted.get("content"),
                        featured_image=extracted.get("featured_image"),
                        meta_description=extracted.get("meta_description"),
                        categories=extracted.get("categories", []),
                        tags=extracted.get("tags", []),
                        inline_images=extracted.get("inline_images", []),
                        relevant_links=extracted.get("relevant_links", []),
                        raw_metadata=extracted.get("raw_metadata", {}),
                        status="detected"
                    )

                    db.add(new_article)
                    await db.flush()  # populate ID
                    new_from_source += 1

                    article_dict = {
                        "id": new_article.id,
                        "competitor_name": competitor.name,
                        "competitor_id": competitor.id,
                        "title": new_article.title,
                        "url": new_article.url,
                        "published_at": new_article.published_at.isoformat() if new_article.published_at else None,
                        "detected_at": new_article.detected_at.isoformat() if new_article.detected_at else None,
                        "detection_delay_seconds": new_article.detection_delay_seconds,
                        "detection_delay_formatted": new_article.detection_delay_formatted,
                        "detection_method": new_article.detection_method,
                        "featured_image": new_article.featured_image,
                    }
                    newly_detected_articles.append(article_dict)

                    # Broadcast real-time event
                    await ws_manager.broadcast({
                        "event": "NEW_ARTICLE_DETECTED",
                        "data": article_dict
                    })

                # Log check result for this specific source
                log_entry = MonitoringLog(
                    competitor_id=competitor.id,
                    source_id=source.id,
                    checked_at=check_time,
                    status="success" if not source_err else "error",
                    response_time_ms=round(source_lat, 2),
                    articles_found=len(source_items),
                    new_articles_detected=new_from_source,
                    strategy_used=source.source_type,
                    error_message=source_err
                )
                db.add(log_entry)

            except Exception as e:
                overall_status = "error"
                last_error = str(e)
                source.last_status = "ERROR"
                source.last_error = str(e)
                log_entry = MonitoringLog(
                    competitor_id=competitor.id,
                    source_id=source.id,
                    checked_at=check_time,
                    status="error",
                    response_time_ms=round(source_lat, 2),
                    articles_found=0,
                    new_articles_detected=0,
                    strategy_used=source.source_type,
                    error_message=str(e)
                )
                db.add(log_entry)

        # Update Competitor summary status
        competitor.last_checked = check_time
        if newly_detected_articles:
            competitor.last_successful_detection = check_time
        competitor.status = "active" if overall_status in ["success", "warning"] else "error"

        await db.commit()

        return {
            "competitor_id": competitor.id,
            "competitor_name": competitor.name,
            "checked_at": check_time.isoformat(),
            "status": overall_status,
            "total_discovered": total_discovered,
            "newly_detected": len(newly_detected_articles),
            "response_time_ms": round(total_resp_time, 2),
            "articles": newly_detected_articles,
            "error": last_error
        }

    @staticmethod
    async def check_all_concurrently(session_maker, max_concurrency: int = settings.MAX_CONCURRENT_WORKERS) -> Dict[str, Any]:
        """
        Asynchronously checks all enabled competitors in parallel using a worker pool (semaphore).
        Demonstrates non-blocking isolation for scale (100-website architecture).
        """
        start_time = time.perf_counter()
        
        async with session_maker() as session:
            stmt = select(Competitor.id).where(Competitor.monitoring_enabled == True)
            res = await session.execute(stmt)
            competitor_ids = list(res.scalars().all())

        if not competitor_ids:
            return {
                "total_checked": 0,
                "duration_ms": 0,
                "newly_detected": 0,
                "results": []
            }

        semaphore = asyncio.Semaphore(max_concurrency)

        async def worker(c_id: int):
            async with semaphore:
                # Each worker gets its own isolated DB session
                async with session_maker() as worker_session:
                    try:
                        return await MonitoringEngine.check_competitor(c_id, worker_session)
                    except Exception as ex:
                        return {
                            "competitor_id": c_id,
                            "status": "fatal_error",
                            "error": str(ex),
                            "newly_detected": 0
                        }

        tasks = [worker(c_id) for c_id in competitor_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Clean exceptions if any
        cleaned_results = []
        total_new = 0
        for r in results:
            if isinstance(r, Exception):
                cleaned_results.append({"status": "exception", "error": str(r)})
            elif isinstance(r, dict):
                cleaned_results.append(r)
                total_new += r.get("newly_detected", 0)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Broadcast cycle complete
        await ws_manager.broadcast({
            "event": "MONITORING_CYCLE_COMPLETED",
            "data": {
                "total_checked": len(competitor_ids),
                "duration_ms": round(elapsed_ms, 2),
                "new_articles_count": total_new
            }
        })

        return {
            "total_checked": len(competitor_ids),
            "duration_ms": round(elapsed_ms, 2),
            "newly_detected": total_new,
            "results": cleaned_results
        }
