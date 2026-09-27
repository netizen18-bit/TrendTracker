import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.session import init_db, AsyncSessionLocal
from app.database.models import Competitor, MonitoringSource, DemoArticle, Article, utcnow
from app.monitors.scheduler import start_scheduler, stop_scheduler
from app.api.competitors import router as competitors_router
from app.api.articles import router as articles_router
from app.api.dashboard import router as dashboard_router
from app.api.analysis import router as analysis_router
from app.api.benchmark import router as benchmark_router
from app.api.demo_publisher import router as demo_router
from app.api.websocket import ws_manager
import datetime
from sqlalchemy import select, func

async def seed_initial_data():
    """Seeds the database with default controlled testbeds and live sample sources if empty."""
    async with AsyncSessionLocal() as db:
        cnt = (await db.execute(select(func.count(Competitor.id)))).scalar()
        if cnt == 0:
            print("[SEED] Seeding initial competitor sources...")
            
            # 1. Controlled Demo Blog (Local high-speed test target)
            demo_comp = Competitor(
                name="Demo Tech Corporation",
                website_url="http://127.0.0.1:8000/demo/blog",
                blog_url="http://127.0.0.1:8000/demo/blog",
                feed_url="http://127.0.0.1:8000/demo/rss.xml",
                sitemap_url="http://127.0.0.1:8000/demo/sitemap.xml",
                monitoring_enabled=True,
                status="active",
                check_interval_sec=30,
                auto_discovered_config={
                    "selected_strategy": "RSS + Sitemap + Direct Page",
                    "strategies_available": {"rss": True, "sitemap": True, "direct_page": True}
                }
            )
            db.add(demo_comp)
            await db.flush()

            db.add_all([
                MonitoringSource(competitor_id=demo_comp.id, source_type="RSS", source_url="http://127.0.0.1:8000/demo/rss.xml", priority=1),
                MonitoringSource(competitor_id=demo_comp.id, source_type="SITEMAP", source_url="http://127.0.0.1:8000/demo/sitemap.xml", priority=2),
                MonitoringSource(competitor_id=demo_comp.id, source_type="DIRECT_PAGE", source_url="http://127.0.0.1:8000/demo/blog", priority=3),
            ])

            # 2. Live Industry Competitors (from project description)
            techcrunch = Competitor(
                name="TechCrunch",
                website_url="https://techcrunch.com",
                blog_url="https://techcrunch.com",
                feed_url="https://techcrunch.com/feed/",
                monitoring_enabled=True,
                status="active",
                check_interval_sec=60,
                auto_discovered_config={"selected_strategy": "RSS"}
            )
            db.add(techcrunch)
            await db.flush()
            db.add(MonitoringSource(competitor_id=techcrunch.id, source_type="RSS", source_url="https://techcrunch.com/feed/", priority=1))

            aws = Competitor(
                name="AWS Architecture Blog",
                website_url="https://aws.amazon.com/blogs/architecture",
                blog_url="https://aws.amazon.com/blogs/architecture",
                feed_url="https://aws.amazon.com/blogs/architecture/feed/",
                monitoring_enabled=True,
                status="active",
                check_interval_sec=60,
                auto_discovered_config={"selected_strategy": "RSS"}
            )
            db.add(aws)
            await db.flush()
            db.add(MonitoringSource(competitor_id=aws.id, source_type="RSS", source_url="https://aws.amazon.com/blogs/architecture/feed/", priority=1))

            # Seed demo blog articles
            now = utcnow()
            db.add_all([
                DemoArticle(
                    title="The Future of Autonomous AI Agents in Enterprise Systems",
                    slug="future-autonomous-ai-agents-2026",
                    content="Autonomous agents are redefining modern distributed workflows. By combining proactive monitoring, tool calling, and high-frequency real-time event loops, engineering teams achieve unprecedented agility.\n\nKey architectural pillars include fault isolation, sub-second latency detection, and asynchronous message bus delivery.",
                    author="Dr. Maya Vance",
                    category="AI Systems",
                    featured_image="https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1200&q=80",
                    published_at=now - datetime.timedelta(minutes=14),
                    is_published=True
                ),
                DemoArticle(
                    title="Next-Gen High Throughput Distributed Scraping & Monitoring Architectures",
                    slug="next-gen-distributed-monitoring-architectures",
                    content="When scaling content monitoring beyond hundreds of concurrent targets, traditional sequential polling paradigms collapse. Asynchronous worker pools and circuit breaker patterns isolate flaky endpoints and preserve deterministic sub-minute detection SLAs.",
                    author="Devon Chen",
                    category="Cloud Infrastructure",
                    featured_image="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
                    published_at=now - datetime.timedelta(minutes=8),
                    is_published=True
                )
            ])

            await db.commit()
            print("[SEED] Database seeded successfully.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await seed_initial_data()
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Real-Time Competitor Content Monitoring & Intelligence Platform",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST Routers
app.include_router(competitors_router, prefix=settings.API_V1_STR)
app.include_router(articles_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(analysis_router, prefix=settings.API_V1_STR)
app.include_router(benchmark_router, prefix=settings.API_V1_STR)
app.include_router(demo_router)  # Mounted directly at /demo

@app.websocket("/ws/live")
async def websocket_live_feed(websocket: WebSocket):
    """Real-time event stream for detection alerts and monitoring cycle status."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

@app.get("/")
async def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "demo_blog": "/demo/blog",
        "demo_rss": "/demo/rss.xml",
        "demo_sitemap": "/demo/sitemap.xml"
    }
