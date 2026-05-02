"""APScheduler-based task scheduler for KAILASH AI.

This provides a simpler alternative to Celery Beat that doesn't require Redis.
It runs within the FastAPI application process.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timezone
import logging
import asyncio
import os

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: AsyncIOScheduler = None


def get_scheduler() -> AsyncIOScheduler:
    """Get the global scheduler instance."""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler(timezone="UTC")
    return scheduler


async def run_daily_learning():
    """Run the daily learning pipeline."""
    from ..tasks.daily_learning import async_daily_learning_pipeline
    
    logger.info("🚀 Starting scheduled daily learning pipeline...")
    try:
        result = await async_daily_learning_pipeline()
        logger.info(f"✅ Daily learning completed: {result.get('successful', 0)}/{result.get('total_departments', 0)} departments")
        return result
    except Exception as e:
        logger.error(f"❌ Daily learning failed: {e}")
        return {"status": "error", "error": str(e)}


async def run_live_data_refresh():
    """Refresh live API data for all departments."""
    from .live_api_connector import get_connector
    from ..core.mongodb import MongoD
    
    logger.info("🔄 Starting scheduled live data refresh...")
    try:
        connector = get_connector()
        db = MongoD.get_database()
        
        departments = [
            "lakshmi", "vishwakarma", "indra", "surya", "agni", 
            "tvashta", "kartikeya", "kubera", "yama"
        ]
        
        success_count = 0
        for dept in departments:
            try:
                data = await connector.fetch_department_live_data(dept)
                await db.live_data_cache.update_one(
                    {"department": dept},
                    {
                        "$set": {
                            "department": dept,
                            "data": data,
                            "last_updated": datetime.now(timezone.utc).isoformat()
                        }
                    },
                    upsert=True
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Error refreshing {dept}: {e}")
        
        logger.info(f"✅ Live data refresh completed: {success_count}/{len(departments)} departments")
        return {"status": "success", "refreshed": success_count}
    except Exception as e:
        logger.error(f"❌ Live data refresh failed: {e}")
        return {"status": "error", "error": str(e)}


def init_scheduler():
    """Initialize and start the scheduler with scheduled tasks."""
    global scheduler
    scheduler = get_scheduler()
    
    # Skip if already running
    if scheduler.running:
        logger.info("Scheduler already running")
        return scheduler
    
    # Daily learning pipeline - runs at 6:00 AM UTC
    scheduler.add_job(
        run_daily_learning,
        CronTrigger(hour=6, minute=0),
        id="daily_learning",
        name="Daily Intelligence Gathering",
        replace_existing=True
    )
    
    # Live data refresh - runs every 4 hours
    scheduler.add_job(
        run_live_data_refresh,
        IntervalTrigger(hours=4),
        id="live_data_refresh",
        name="Live API Data Refresh",
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("✅ APScheduler started with scheduled tasks")
    logger.info("   - Daily learning: 06:00 UTC")
    logger.info("   - Live data refresh: Every 4 hours")
    
    return scheduler


def shutdown_scheduler():
    """Shutdown the scheduler."""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown complete")


def get_scheduled_jobs():
    """Get list of all scheduled jobs."""
    s = get_scheduler()
    jobs = []
    for job in s.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    return jobs
