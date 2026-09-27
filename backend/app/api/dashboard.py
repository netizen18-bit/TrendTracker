import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database.session import get_db
from app.database.models import Competitor, Article, MonitoringLog, utcnow
from app.monitors.timing_engine import compute_sla_metrics

router = APIRouter(prefix="/dashboard", tags=["Executive Dashboard Analytics"])

@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Computes comprehensive executive statistics, SLA performance, and time series charts."""
    now = utcnow()
    today_start = datetime.datetime(now.year, now.month, now.day, tzinfo=datetime.timezone.utc)

    # 1. Competitor counts
    total_comp = (await db.execute(select(func.count(Competitor.id)))).scalar() or 0
    active_comp = (await db.execute(select(func.count(Competitor.id)).where(Competitor.status == "active", Competitor.monitoring_enabled == True))).scalar() or 0
    error_comp = (await db.execute(select(func.count(Competitor.id)).where(Competitor.status == "error"))).scalar() or 0
    paused_comp = (await db.execute(select(func.count(Competitor.id)).where(Competitor.monitoring_enabled == False))).scalar() or 0

    # 2. Article counts
    total_articles = (await db.execute(select(func.count(Article.id)))).scalar() or 0
    today_articles = (await db.execute(select(func.count(Article.id)).where(Article.detected_at >= today_start))).scalar() or 0

    # 3. Detection Delays & SLA Performance
    delay_stmt = select(Article.detection_delay_seconds).where(Article.detection_delay_seconds.isnot(None))
    delays_res = await db.execute(delay_stmt)
    delays = [d for d in delays_res.scalars().all() if d is not None]

    sla_metrics = compute_sla_metrics(delays, target_seconds=300)

    # 4. Method Breakdown
    methods_res = await db.execute(
        select(Article.detection_method, func.count(Article.id)).group_by(Article.detection_method)
    )
    method_counts = {m: c for m, c in methods_res.all()}

    # 5. Recent 8 Detected Articles
    recent_art_stmt = select(Article, Competitor.name.label("competitor_name")).join(
        Competitor, Article.competitor_id == Competitor.id
    ).order_by(desc(Article.detected_at)).limit(8)
    recent_art_res = await db.execute(recent_art_stmt)
    recent_articles = []
    for art, comp_name in recent_art_res.all():
        recent_articles.append({
            "id": art.id,
            "competitor_name": comp_name,
            "title": art.title,
            "url": art.url,
            "published_at": art.published_at.isoformat() if art.published_at else None,
            "detected_at": art.detected_at.isoformat() if art.detected_at else None,
            "detection_delay_seconds": art.detection_delay_seconds,
            "detection_delay_formatted": art.detection_delay_formatted,
            "is_within_sla": (art.detection_delay_seconds is not None and art.detection_delay_seconds <= 300),
            "detection_method": art.detection_method,
            "featured_image": art.featured_image
        })

    # 6. Recent 10 Monitoring Logs
    recent_logs_stmt = select(MonitoringLog, Competitor.name.label("competitor_name")).join(
        Competitor, MonitoringLog.competitor_id == Competitor.id
    ).order_by(desc(MonitoringLog.checked_at)).limit(10)
    recent_logs_res = await db.execute(recent_logs_stmt)
    recent_logs = []
    for log, comp_name in recent_logs_res.all():
        recent_logs.append({
            "id": log.id,
            "competitor_name": comp_name,
            "checked_at": log.checked_at.isoformat(),
            "status": log.status,
            "response_time_ms": log.response_time_ms,
            "articles_found": log.articles_found,
            "new_articles_detected": log.new_articles_detected,
            "strategy_used": log.strategy_used,
            "error_message": log.error_message
        })

    # 7. Latency Trend Chart Data (last 15 detected items)
    trend_stmt = select(Article.title, Article.detection_delay_seconds, Article.detected_at, Article.detection_method).where(
        Article.detection_delay_seconds.isnot(None)
    ).order_by(desc(Article.detected_at)).limit(15)
    trend_res = await db.execute(trend_stmt)
    trend_data = [
        {
            "label": f"#{i+1} {row.title[:15]}...",
            "delay_sec": round(row.detection_delay_seconds, 1),
            "delay_min": round(row.detection_delay_seconds / 60, 2),
            "method": row.detection_method,
            "detected_at": row.detected_at.strftime("%H:%M:%S")
        } for i, row in enumerate(reversed(trend_res.all()))
    ]

    return {
        "competitors": {
            "total": total_comp,
            "active": active_comp,
            "error": error_comp,
            "paused": paused_comp
        },
        "articles": {
            "total": total_articles,
            "today": today_articles
        },
        "performance": sla_metrics,
        "method_distribution": {
            "RSS": method_counts.get("RSS", 0),
            "SITEMAP": method_counts.get("SITEMAP", 0),
            "DIRECT_PAGE": method_counts.get("DIRECT_PAGE", 0),
        },
        "recent_articles": recent_articles,
        "recent_logs": recent_logs,
        "delay_trends": trend_data
    }
