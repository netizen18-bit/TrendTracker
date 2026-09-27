import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database.session import AsyncSessionLocal
from app.monitors.concurrency_pool import MonitoringEngine
from app.config import settings

scheduler = AsyncIOScheduler()

async def scheduled_monitoring_job():
    """Background monitoring cycle executed periodically."""
    try:
        await MonitoringEngine.check_all_concurrently(AsyncSessionLocal, max_concurrency=settings.MAX_CONCURRENT_WORKERS)
    except Exception as e:
        print(f"[SCHEDULER ERROR] Monitoring job failed: {e}")

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            scheduled_monitoring_job,
            "interval",
            seconds=settings.DEFAULT_CHECK_INTERVAL_SEC,
            id="global_monitoring_cycle",
            replace_existing=True
        )
        scheduler.start()
        print(f"[SCHEDULER] Continuous monitoring started (Interval: {settings.DEFAULT_CHECK_INTERVAL_SEC}s)")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("[SCHEDULER] Continuous monitoring stopped")
