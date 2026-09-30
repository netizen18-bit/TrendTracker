from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_
from typing import Optional, List

from app.database.session import get_db
from app.database.models import Article, Competitor

router = APIRouter(prefix="/articles", tags=["Articles & Detection Intelligence"])

@router.get("")
async def list_articles(
    competitor_id: Optional[int] = Query(None),
    detection_method: Optional[str] = Query(None),
    sla_filter: Optional[str] = Query(None),  # "within_5min", "over_5min"
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve detected competitor articles with precise detection timing and SLA tags."""
    stmt = select(Article, Competitor.name.label("competitor_name")).join(
        Competitor, Article.competitor_id == Competitor.id
    ).order_by(desc(Article.detected_at))

    if competitor_id:
        stmt = stmt.where(Article.competitor_id == competitor_id)

    if detection_method:
        stmt = stmt.where(Article.detection_method == detection_method.upper())

    if sla_filter == "within_5min":
        stmt = stmt.where(Article.detection_delay_seconds <= 300)
    elif sla_filter == "over_5min":
        stmt = stmt.where(Article.detection_delay_seconds > 300)

    if search:
        term = f"%{search}%"
        stmt = stmt.where(or_(Article.title.ilike(term), Article.content.ilike(term), Article.author.ilike(term)))

    stmt = stmt.limit(limit).offset(offset)
    res = await db.execute(stmt)
    records = res.all()

    articles_list = []
    for art, comp_name in records:
        articles_list.append({
            "id": art.id,
            "competitor_id": art.competitor_id,
            "competitor_name": comp_name,
            "title": art.title,
            "url": art.url,
            "canonical_url": art.canonical_url,
            "author": art.author,
            "published_at": art.published_at.isoformat() if art.published_at else None,
            "detected_at": art.detected_at.isoformat() if art.detected_at else None,
            "detection_delay_seconds": art.detection_delay_seconds,
            "detection_delay_formatted": art.detection_delay_formatted,
            "is_within_sla": (art.detection_delay_seconds is not None and art.detection_delay_seconds <= 300),
            "detection_method": art.detection_method,
            "featured_image": art.featured_image,
            "meta_description": art.meta_description,
            "categories": art.categories or [],
            "tags": art.tags or [],
            "status": art.status,
            "created_at": art.created_at.isoformat()
        })

    return {
        "count": len(articles_list),
        "limit": limit,
        "offset": offset,
        "articles": articles_list
    }

@router.get("/{article_id}")
async def get_article_detail(article_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve full extracted article payload including clean body, images, and raw metadata."""
    stmt = select(Article, Competitor.name.label("competitor_name")).join(
        Competitor, Article.competitor_id == Competitor.id
    ).where(Article.id == article_id)
    res = await db.execute(stmt)
    record = res.one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Article not found")

    art, comp_name = record
    return {
        "id": art.id,
        "competitor_id": art.competitor_id,
        "competitor_name": comp_name,
        "title": art.title,
        "url": art.url,
        "canonical_url": art.canonical_url,
        "author": art.author,
        "published_at": art.published_at.isoformat() if art.published_at else None,
        "detected_at": art.detected_at.isoformat() if art.detected_at else None,
        "detection_delay_seconds": art.detection_delay_seconds,
        "detection_delay_formatted": art.detection_delay_formatted,
        "is_within_sla": (art.detection_delay_seconds is not None and art.detection_delay_seconds <= 300),
        "detection_method": art.detection_method,
        "content": art.content,
        "featured_image": art.featured_image,
        "meta_description": art.meta_description,
        "categories": art.categories or [],
        "tags": art.tags or [],
        "inline_images": art.inline_images or [],
        "relevant_links": art.relevant_links or [],
        "raw_metadata": art.raw_metadata or {},
        "status": art.status
    }

@router.delete("/{article_id}")
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Article).where(Article.id == article_id)
    res = await db.execute(stmt)
    art = res.scalar_one_or_none()
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")

    await db.delete(art)
    await db.commit()
    return {"status": "deleted", "article_id": article_id}
