"""API endpoints for scheduler management and manual task triggers."""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
from datetime import datetime, timezone

from ..api.deps import get_current_user
from ..services.scheduler import (
    get_scheduler, get_scheduled_jobs, 
    run_daily_learning, run_live_data_refresh
)
from ..core.mongodb import MongoD

router = APIRouter(prefix="/api/scheduler", tags=["Scheduler & Automation"])


@router.get("/status")
async def get_scheduler_status(current_user: dict = Depends(get_current_user)):
    """Get scheduler status and scheduled jobs."""
    scheduler = get_scheduler()
    
    return {
        "running": scheduler.running if scheduler else False,
        "jobs": get_scheduled_jobs(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/trigger/daily-learning")
async def trigger_daily_learning(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger the daily learning pipeline."""
    
    async def run_task():
        result = await run_daily_learning()
        # Store result in database
        db = MongoD.get_database()
        await db.scheduler_runs.insert_one({
            "task": "daily_learning",
            "triggered_by": current_user.get("email", "manual"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": result
        })
    
    background_tasks.add_task(run_task)
    
    return {
        "status": "started",
        "message": "Daily learning pipeline started in background",
        "triggered_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/trigger/live-data-refresh")
async def trigger_live_data_refresh(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger live data refresh for all departments."""
    
    async def run_task():
        result = await run_live_data_refresh()
        # Store result in database
        db = MongoD.get_database()
        await db.scheduler_runs.insert_one({
            "task": "live_data_refresh",
            "triggered_by": current_user.get("email", "manual"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": result
        })
    
    background_tasks.add_task(run_task)
    
    return {
        "status": "started",
        "message": "Live data refresh started in background",
        "triggered_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/history")
async def get_scheduler_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get history of scheduler task runs."""
    db = MongoD.get_database()
    
    runs = await db.scheduler_runs.find(
        {},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    return {"runs": runs, "count": len(runs)}


@router.get("/next-runs")
async def get_next_scheduled_runs(current_user: dict = Depends(get_current_user)):
    """Get next scheduled run times for all jobs."""
    jobs = get_scheduled_jobs()
    
    return {
        "jobs": jobs,
        "server_time": datetime.now(timezone.utc).isoformat()
    }
