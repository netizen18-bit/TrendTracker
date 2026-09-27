import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from pydantic import BaseModel

from app.database.session import get_db
from app.database.models import DemoArticle, utcnow

router = APIRouter(prefix="/demo", tags=["Controlled Demo Blog"])

class PublishArticleRequest(BaseModel):
    title: str
    content: str
    author: Optional[str] = "Antigravity Research Lab"
    category: Optional[str] = "Artificial Intelligence"
    featured_image: Optional[str] = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80"
    minutes_ago: Optional[int] = 0  # To simulate an article published X minutes ago!
    custom_publish_time: Optional[datetime.datetime] = None

@router.post("/reset")
async def reset_demo_blog(db: AsyncSession = Depends(get_db)):
    """Resets the demo blog with initial seed articles."""
    await db.execute(DemoArticle.__table__.delete())
    
    now = utcnow()
    seeds = [
        DemoArticle(
            title="The Future of Autonomous AI Agents in Enterprise Systems",
            slug="future-autonomous-ai-agents-2026",
            content="Autonomous agents are redefining modern distributed workflows. By combining proactive monitoring, tool calling, and high-frequency real-time event loops, engineering teams achieve unprecedented agility.\n\nKey architectural pillars include fault isolation, sub-second latency detection, and asynchronous message bus delivery.",
            author="Dr. Maya Vance",
            category="AI Systems",
            featured_image="https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1200&q=80",
            published_at=now - datetime.timedelta(hours=2),
            is_published=True
        ),
        DemoArticle(
            title="Next-Gen High Throughput Distributed Scraping & Monitoring Architectures",
            slug="next-gen-distributed-monitoring-architectures",
            content="When scaling content monitoring beyond hundreds of concurrent targets, traditional sequential polling paradigms collapse. Asynchronous worker pools and circuit breaker patterns isolate flaky endpoints and preserve deterministic sub-minute detection SLAs.",
            author="Devon Chen",
            category="Cloud Infrastructure",
            featured_image="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
            published_at=now - datetime.timedelta(hours=1),
            is_published=True
        )
    ]
    db.add_all(seeds)
    await db.commit()
    return {"status": "ok", "message": "Demo blog reset with 2 seed articles."}

@router.post("/publish")
async def publish_demo_article(payload: PublishArticleRequest, db: AsyncSession = Depends(get_db)):
    """
    Publish a new test article on the controlled demo site with an explicit publication timestamp.
    Used during examination to demonstrate exact Detection Delay calculation!
    """
    slug_base = payload.title.lower().replace(" ", "-").replace(":", "").replace("?", "")
    timestamp_suffix = int(datetime.datetime.now().timestamp())
    slug = f"{slug_base[:40]}-{timestamp_suffix}"

    pub_time = payload.custom_publish_time
    if not pub_time:
        pub_time = utcnow() - datetime.timedelta(minutes=payload.minutes_ago)

    article = DemoArticle(
        title=payload.title,
        slug=slug,
        content=payload.content,
        author=payload.author,
        category=payload.category,
        featured_image=payload.featured_image,
        published_at=pub_time,
        is_published=True
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)

    return {
        "status": "published",
        "article_id": article.id,
        "title": article.title,
        "slug": article.slug,
        "url": f"/demo/blog/{article.slug}",
        "published_at": article.published_at.isoformat(),
        "minutes_ago": payload.minutes_ago
    }

@router.get("/blog", response_class=HTMLResponse)
async def demo_blog_index(request: Request, db: AsyncSession = Depends(get_db)):
    """HTML Blog Index Page for Direct Page Monitoring Method 3"""
    stmt = select(DemoArticle).where(DemoArticle.is_published == True).order_by(desc(DemoArticle.published_at))
    res = await db.execute(stmt)
    articles = res.scalars().all()

    base_url = str(request.base_url).rstrip("/")
    
    article_cards = ""
    for a in articles:
        article_cards += f"""
        <article class="post-card" style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; margin-bottom: 24px; background: #ffffff; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="font-size: 12px; font-weight: 700; color: #4f46e5; text-transform: uppercase; margin-bottom: 8px;">{a.category}</div>
            <h2 style="margin: 0 0 12px 0; font-size: 22px;">
                <a href="{base_url}/demo/blog/{a.slug}" style="color: #0f172a; text-decoration: none; font-weight: 700;">{a.title}</a>
            </h2>
            <p style="color: #475569; font-size: 14px; line-height: 1.6; margin-bottom: 16px;">{a.content[:160]}...</p>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #64748b; border-top: 1px solid #f1f5f9; padding-top: 12px;">
                <span>By <strong>{a.author}</strong></span>
                <time datetime="{a.published_at.isoformat()}">{a.published_at.strftime('%B %d, %Y at %I:%M:%S %p UTC')}</time>
            </div>
        </article>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Demo Tech Corporation Blog — Controlled Examination Testbed</title>
    <meta name="description" content="Official controlled publication blog for real-time detection delay testing.">
    <link rel="alternate" type="application/rss+xml" title="Demo Blog RSS Feed" href="{base_url}/demo/rss.xml" />
    <meta property="og:title" content="Demo Tech Corporation Blog">
    <meta property="og:type" content="website">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px;">
    <div style="max-width: 800px; margin: 0 auto;">
        <header style="margin-bottom: 40px; text-align: center;">
            <div style="display: inline-block; padding: 4px 12px; background: #e0e7ff; color: #4338ca; border-radius: 9999px; font-size: 12px; font-weight: 600; margin-bottom: 12px;">
                TARGET TESTBED SITE
            </div>
            <h1 style="color: #0f172a; font-size: 36px; margin: 0 0 10px 0;">Demo Tech Corporation Blog</h1>
            <p style="color: #64748b; font-size: 16px; margin: 0;">Official simulated publication source for testing ContentPulse real-time detection delay.</p>
            <div style="margin-top: 16px; display: flex; gap: 12px; justify-content: center;">
                <a href="{base_url}/demo/rss.xml" style="padding: 6px 14px; background: #ea580c; color: white; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600;">RSS Feed (/demo/rss.xml)</a>
                <a href="{base_url}/demo/sitemap.xml" style="padding: 6px 14px; background: #0284c7; color: white; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600;">XML Sitemap (/demo/sitemap.xml)</a>
            </div>
        </header>
        
        <main>
            {article_cards if article_cards else '<p style="text-align: center; color: #94a3b8;">No articles published yet.</p>'}
        </main>
    </div>
</body>
</html>
"""
    return HTMLResponse(content=html)

@router.get("/blog/{slug}", response_class=HTMLResponse)
async def demo_blog_detail(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    """HTML Article Detail Page with full structured metadata (JSON-LD & OpenGraph)"""
    stmt = select(DemoArticle).where(DemoArticle.slug == slug)
    res = await db.execute(stmt)
    article = res.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    base_url = str(request.base_url).rstrip("/")
    canonical_url = f"{base_url}/demo/blog/{article.slug}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{article.title} — Demo Tech Blog</title>
    <meta name="description" content="{article.content[:160]}">
    <meta name="author" content="{article.author}">
    <link rel="canonical" href="{canonical_url}">
    
    <!-- OpenGraph Metadata -->
    <meta property="og:title" content="{article.title}">
    <meta property="og:description" content="{article.content[:160]}">
    <meta property="og:image" content="{article.featured_image}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:type" content="article">
    <meta property="article:published_time" content="{article.published_at.isoformat()}">
    <meta property="article:author" content="{article.author}">
    <meta property="article:section" content="{article.category}">
    <meta property="article:tag" content="AI, Technology, Cloud">

    <!-- JSON-LD Structured Metadata -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      "headline": "{article.title}",
      "image": "{article.featured_image}",
      "author": {{
        "@type": "Person",
        "name": "{article.author}"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "Demo Tech Corporation"
      }},
      "datePublished": "{article.published_at.isoformat()}",
      "articleBody": "{article.content.replace('"', "'")}",
      "articleSection": "{article.category}"
    }}
    </script>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px;">
    <article style="max-width: 740px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);">
        <a href="{base_url}/demo/blog" style="color: #4f46e5; text-decoration: none; font-size: 14px; font-weight: 600;">← Back to Blog Index</a>
        <div style="margin-top: 24px; font-size: 12px; font-weight: 700; color: #4f46e5; text-transform: uppercase;">{article.category}</div>
        <h1 style="color: #0f172a; font-size: 32px; margin: 8px 0 16px 0; line-height: 1.2;">{article.title}</h1>
        
        <div style="display: flex; gap: 16px; font-size: 14px; color: #64748b; margin-bottom: 24px; border-bottom: 1px solid #f1f5f9; padding-bottom: 16px;">
            <span>By <strong>{article.author}</strong></span>
            <span>•</span>
            <time datetime="{article.published_at.isoformat()}">Published: {article.published_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</time>
        </div>

        {f'<img src="{article.featured_image}" alt="{article.title}" style="width: 100%; height: 360px; object-fit: cover; border-radius: 12px; margin-bottom: 24px;" />' if article.featured_image else ''}

        <div class="post-content" style="color: #334155; font-size: 16px; line-height: 1.8;">
            <p>{article.content}</p>
        </div>
    </article>
</body>
</html>
"""
    return HTMLResponse(content=html)

@router.get("/rss.xml")
async def demo_rss_feed(request: Request, db: AsyncSession = Depends(get_db)):
    """Method 1: RSS 2.0 Feed for Controlled Demo Blog"""
    stmt = select(DemoArticle).where(DemoArticle.is_published == True).order_by(desc(DemoArticle.published_at))
    res = await db.execute(stmt)
    articles = res.scalars().all()

    base_url = str(request.base_url).rstrip("/")

    items_xml = ""
    for a in articles:
        rfc822_date = a.published_at.strftime("%a, %d %b %Y %H:%M:%S +0000")
        items_xml += f"""
        <item>
            <title><![CDATA[{a.title}]]></title>
            <link>{base_url}/demo/blog/{a.slug}</link>
            <guid>{base_url}/demo/blog/{a.slug}</guid>
            <pubDate>{rfc822_date}</pubDate>
            <author><![CDATA[{a.author}]]></author>
            <category><![CDATA[{a.category}]]></category>
            <description><![CDATA[{a.content[:200]}...]]></description>
        </item>
        """

    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>Demo Tech Corporation Blog Feed</title>
        <link>{base_url}/demo/blog</link>
        <description>Real-Time Controlled Test Feed for ContentPulse Detection System</description>
        <language>en-us</language>
        <atom:link href="{base_url}/demo/rss.xml" rel="self" type="application/rss+xml" />
        {items_xml}
    </channel>
</rss>"""

    return Response(content=rss_content, media_type="application/rss+xml")

@router.get("/sitemap.xml")
async def demo_sitemap_xml(request: Request, db: AsyncSession = Depends(get_db)):
    """Method 2: XML Sitemap for Controlled Demo Blog"""
    stmt = select(DemoArticle).where(DemoArticle.is_published == True).order_by(desc(DemoArticle.published_at))
    res = await db.execute(stmt)
    articles = res.scalars().all()

    base_url = str(request.base_url).rstrip("/")

    urls_xml = f"""
    <url>
        <loc>{base_url}/demo/blog</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    """

    for a in articles:
        urls_xml += f"""
        <url>
            <loc>{base_url}/demo/blog/{a.slug}</loc>
            <lastmod>{a.published_at.strftime('%Y-%m-%dT%H:%M:%SZ')}</lastmod>
            <changefreq>monthly</changefreq>
            <priority>0.8</priority>
        </url>
        """

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {urls_xml}
</urlset>"""

    return Response(content=sitemap_content, media_type="application/xml")
