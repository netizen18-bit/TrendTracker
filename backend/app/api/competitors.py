from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl

from app.database.session import get_db, AsyncSessionLocal
from app.database.models import Competitor, MonitoringSource, Article, MonitoringLog, utcnow
from app.analyzers.website_analyzer import WebsiteAnalyzer
from app.monitors.concurrency_pool import MonitoringEngine

router = APIRouter(prefix="/competitors", tags=["Competitor Management"])

class CreateCompetitorRequest(BaseModel):
    name: str
    website_url: str
    blog_url: Optional[str] = None
    feed_url: Optional[str] = None
    sitemap_url: Optional[str] = None
    check_interval_sec: Optional[int] = 60
    auto_investigate: Optional[bool] = True

class UpdateCompetitorRequest(BaseModel):
    name: Optional[str] = None
    website_url: Optional[str] = None
    blog_url: Optional[str] = None
    feed_url: Optional[str] = None
    sitemap_url: Optional[str] = None
    monitoring_enabled: Optional[bool] = None
    check_interval_sec: Optional[int] = None

@router.get("/")
async def list_competitors(db: AsyncSession = Depends(get_db)):
    """List all competitors with their current monitoring health, source count, and article counts."""
    stmt = select(Competitor).order_by(desc(Competitor.created_at))
    res = await db.execute(stmt)
    competitors = res.scalars().all()

    output = []
    for c in competitors:
        # Count articles
        art_cnt_res = await db.execute(select(func.count(Article.id)).where(Article.competitor_id == c.id))
        articles_count = art_cnt_res.scalar() or 0

        # Latest article
        latest_art_res = await db.execute(
            select(Article).where(Article.competitor_id == c.id).order_by(desc(Article.detected_at)).limit(1)
        )
        latest_art = latest_art_res.scalar_one_or_none()

        output.append({
            "id": c.id,
            "name": c.name,
            "website_url": c.website_url,
            "blog_url": c.blog_url,
            "feed_url": c.feed_url,
            "sitemap_url": c.sitemap_url,
            "monitoring_enabled": c.monitoring_enabled,
            "status": c.status,
            "check_interval_sec": c.check_interval_sec,
            "last_checked": c.last_checked.isoformat() if c.last_checked else None,
            "last_successful_detection": c.last_successful_detection.isoformat() if c.last_successful_detection else None,
            "articles_count": articles_count,
            "latest_article": {
                "title": latest_art.title,
                "detected_at": latest_art.detected_at.isoformat(),
                "delay_formatted": latest_art.detection_delay_formatted,
                "method": latest_art.detection_method
            } if latest_art else None,
            "sources": [
                {
                    "id": s.id,
                    "source_type": s.source_type,
                    "source_url": s.source_url,
                    "is_active": s.is_active,
                    "priority": s.priority,
                    "last_status": s.last_status,
                    "last_checked": s.last_checked.isoformat() if s.last_checked else None
                } for s in c.sources
            ],
            "auto_discovered_config": c.auto_discovered_config,
            "created_at": c.created_at.isoformat()
        })

    return output

@router.post("/")
async def create_competitor(payload: CreateCompetitorRequest, db: AsyncSession = Depends(get_db)):
    """
    Creates a new competitor. If auto_investigate=True, the system automatically
    probes the website to discover RSS, Sitemap, and Blog configurations.
    """
    website_url = payload.website_url.strip()
    if not website_url.startswith("http://") and not website_url.startswith("https://"):
        website_url = "https://" + website_url

    investigation_result = None
    sources_to_add = []

    if payload.auto_investigate:
        # Execute automated intelligent discovery
        investigation_result = await WebsiteAnalyzer.analyze(website_url)
        discovered_sources = investigation_result.get("recommended_sources", [])
        
        feed_url = investigation_result.get("feed_details", {}).get("feed_url") or payload.feed_url
        sitemap_url = investigation_result.get("sitemap_details", {}).get("sitemap_url") or payload.sitemap_url
        blog_url = investigation_result.get("blog_details", {}).get("blog_url") or payload.blog_url

        sources_to_add = discovered_sources
    else:
        feed_url = payload.feed_url
        sitemap_url = payload.sitemap_url
        blog_url = payload.blog_url

        if feed_url:
            sources_to_add.append({"source_type": "RSS", "source_url": feed_url, "priority": 1, "is_active": True})
        if sitemap_url:
            sources_to_add.append({"source_type": "SITEMAP", "source_url": sitemap_url, "priority": 2, "is_active": True})
        if blog_url:
            sources_to_add.append({"source_type": "DIRECT_PAGE", "source_url": blog_url, "priority": 3, "is_active": True})

    competitor = Competitor(
        name=payload.name,
        website_url=website_url,
        blog_url=blog_url,
        feed_url=feed_url,
        sitemap_url=sitemap_url,
        monitoring_enabled=True,
        status="active",
        check_interval_sec=payload.check_interval_sec or 60,
        auto_discovered_config=investigation_result
    )
    db.add(competitor)
    await db.flush()

    for s in sources_to_add:
        ms = MonitoringSource(
            competitor_id=competitor.id,
            source_type=s["source_type"],
            source_url=s["source_url"],
            priority=s.get("priority", 1),
            is_active=s.get("is_active", True)
        )
        db.add(ms)

    await db.commit()
    await db.refresh(competitor)

    # Trigger an immediate initial baseline check in background
    return {
        "status": "created",
        "competitor_id": competitor.id,
        "name": competitor.name,
        "investigation_result": investigation_result
    }

@router.get("/{competitor_id}")
async def get_competitor(competitor_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Competitor).where(Competitor.id == competitor_id)
    res = await db.execute(stmt)
    competitor = res.scalar_one_or_none()

    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    # Fetch recent logs
    logs_stmt = select(MonitoringLog).where(MonitoringLog.competitor_id == competitor_id).order_by(desc(MonitoringLog.checked_at)).limit(20)
    logs_res = await db.execute(logs_stmt)
    logs = logs_res.scalars().all()

    return {
        "competitor": {
            "id": competitor.id,
            "name": competitor.name,
            "website_url": competitor.website_url,
            "blog_url": competitor.blog_url,
            "feed_url": competitor.feed_url,
            "sitemap_url": competitor.sitemap_url,
            "monitoring_enabled": competitor.monitoring_enabled,
            "status": competitor.status,
            "check_interval_sec": competitor.check_interval_sec,
            "last_checked": competitor.last_checked.isoformat() if competitor.last_checked else None,
            "last_successful_detection": competitor.last_successful_detection.isoformat() if competitor.last_successful_detection else None,
            "auto_discovered_config": competitor.auto_discovered_config,
            "sources": [
                {
                    "id": s.id,
                    "source_type": s.source_type,
                    "source_url": s.source_url,
                    "is_active": s.is_active,
                    "priority": s.priority,
                    "last_status": s.last_status,
                    "last_error": s.last_error,
                    "last_checked": s.last_checked.isoformat() if s.last_checked else None
                } for s in competitor.sources
            ]
        },
        "recent_logs": [
            {
                "id": l.id,
                "checked_at": l.checked_at.isoformat(),
                "status": l.status,
                "response_time_ms": l.response_time_ms,
                "articles_found": l.articles_found,
                "new_articles_detected": l.new_articles_detected,
                "strategy_used": l.strategy_used,
                "error_message": l.error_message
            } for l in logs
        ]
    }

@router.post("/{competitor_id}/toggle")
async def toggle_competitor(competitor_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Competitor).where(Competitor.id == competitor_id)
    res = await db.execute(stmt)
    competitor = res.scalar_one_or_none()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    competitor.monitoring_enabled = not competitor.monitoring_enabled
    await db.commit()
    return {"status": "ok", "monitoring_enabled": competitor.monitoring_enabled}

@router.post("/{competitor_id}/check")
async def trigger_competitor_check(competitor_id: int, db: AsyncSession = Depends(get_db)):
    """On-demand immediate monitoring check for a competitor."""
    result = await MonitoringEngine.check_competitor(competitor_id, db)
    return result

@router.post("/check-all")
async def trigger_check_all():
    """On-demand parallel monitoring check across all active competitors."""
    result = await MonitoringEngine.check_all_concurrently(AsyncSessionLocal)
    return result

@router.delete("/{competitor_id}")
async def delete_competitor(competitor_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Competitor).where(Competitor.id == competitor_id)
    res = await db.execute(stmt)
    competitor = res.scalar_one_or_none()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    await db.delete(competitor)
    await db.commit()
    return {"status": "deleted", "competitor_id": competitor_id}
