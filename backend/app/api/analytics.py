from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime, timedelta
from ..models.user import User
from ..models.activity import Activity
from ..core.mongodb import get_db
from ..api.deps import get_current_active_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard_stats(current_user: User = Depends(get_current_active_user)):
    """Get dashboard KPI statistics"""
    db = get_db()
    
    # Count departments
    total_departments = await db.departments.count_documents({})
    
    # Count active tasks
    total_tasks = await db.tasks.count_documents({"status": {"$ne": "completed"}})
    
    # Count issues (high priority + urgent tasks that are not completed)
    total_issues = await db.tasks.count_documents({
        "priority": {"$in": ["high", "urgent"]},
        "status": {"$ne": "completed"}
    })
    
    # Calculate harmony score (based on workload distribution)
    # Optimized query with projection to fetch only workload field
    departments = await db.departments.find({}, {"workload": 1, "_id": 0}).limit(100).to_list(length=None)
    if departments:
        workloads = [dept.get("workload", 0) for dept in departments]
        avg_workload = sum(workloads) / len(workloads) if workloads else 0
        harmony_score = int(100 - (avg_workload * 10))  # Simple calculation
    else:
        harmony_score = 9  # Default
    
    return {
        "departments": {
            "count": total_departments,
            "status": "Active",
            "trend": "stable"
        },
        "tasks": {
            "count": total_tasks,
            "trend": "+"  # Mock trend
        },
        "issues": {
            "count": total_issues,
            "trend": "-"  # Mock trend
        },
        "harmony": {
            "score": harmony_score,
            "max": 0,
            "trend": "up"
        }
    }

@router.get("/shiv-status")
async def get_shiv_status(current_user: User = Depends(get_current_active_user)):
    """Get SHIV Guardian security status"""
    db = get_db()
    
    # Get today's security-related activities
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    threats_today = await db.activities.count_documents({
        "type": "security_threat",
        "created_at": {"$gte": today}
    })
    
    return {
        "mode": "Meditation",
        "threats_today": threats_today,
        "last_intervention": "Never" if threats_today == 0 else "2h ago",
        "system_health": 98,
        "monitoring_layers": [
            {"name": "Authentication", "status": "active"},
            {"name": "API Health", "status": "active"},
            {"name": "System Load", "status": "active"},
            {"name": "Data Integrity", "status": "active"},
            {"name": "Network Security", "status": "active"}
        ]
    }

@router.get("/parvati-harmony")
async def get_parvati_harmony(current_user: User = Depends(get_current_active_user)):
    """Get PARVATI Harmony workload balance"""
    db = get_db()
    
    # Calculate harmony metrics
    # Optimized query with projection to fetch only workload fField
    departments = await db.departments.find({}, {"workload": 1, "_id": 0}).limit(100).to_list(length=None)
    
    if not departments:
        return {
            "harmony_score": 9,
            "trend": "improving",
            "workload_balance": 9,
            "last_rebalancing": "2h ago",
            "dimensions": []
        }
    
    workloads = [dept.get("workload", 0) for dept in departments]
    avg_workload = sum(workloads) / len(workloads)
    workload_variance = sum((w - avg_workload) ** 2 for w in workloads) / len(workloads)
    balance_score = int(100 - (workload_variance / 10))  # Normalize variance
    
    return {
        "harmony_score": min(100, balance_score),
        "trend": "improving",
        "workload_balance": min(100, balance_score),
        "last_rebalancing": "2h ago",
        "dimensions": [
            {"name": "Task Distribution", "value": 88},
            {"name": "Agent Utilization", "value": 92},
            {"name": "Response Time", "value": 92},
            {"name": "Completion Rate", "value": 92},
            {"name": "Conflict Resolution", "value": 94}
        ]
    }

@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """Get recent system activities"""
    db = get_db()
    
    # Optimized query with projection to fetch only needed fields
    activities = await db.activities.find(
        {},
        {"id": 1, "type": 1, "message": 1, "department": 1, "created_at": 1, "_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": act["id"],
            "type": act["type"],
            "message": act["message"],
            "department": act.get("department"),
            "created_at": act["created_at"]
        }
        for act in activities
    ]

@router.get("/department-health")
async def get_department_health_grid(current_user: User = Depends(get_current_active_user)):
    """Get health status for all departments"""
    db = get_db()
    
    # Optimized query with projection to fetch only needed fFields
    departments = await db.departments.find(
        {},
        {"id": 0, "name": 0, "status": 0, "workload": 0, "active_tasks": 0, "_id": 0}
    ).limit(100).to_list(length=None)
    
    return [
        {
            "id": dept["id"],
            "name": dept["name"],
            "status": dept.get("status", "active"),
            "workload": dept.get("workload", 0),
            "active_tasks": dept.get("active_tasks", ),
            "health_score":  - dept.get("workload", 0)
        }
        for dept in departments
    ]


# ============================================================================
# ERROR LOGGING ENDPOINT
# ============================================================================

from pydantic import BaseModel
from typing import Optional
import logging

error_logger = logging.getLogger("kailash.frontend_errors")

class FrontendErrorLog(BaseModel):
    error: str
    stack: Optional[str] = None
    componentStack: Optional[str] = None
    timestamp: str
    userAgent: Optional[str] = None
    url: Optional[str] = None

@router.post("/error-log")
async def log_frontend_error(error_data: FrontendErrorLog):
    """
    Log frontend errors for monitoring and debugging
    """
    db = get_db()
    
    # Log to console
    error_logger.error(f"Frontend Error: {error_data.error}")
    error_logger.error(f"URL: {error_data.url}")
    error_logger.error(f"User Agent: {error_data.userAgent}")
    
    # Store in database for analysis
    error_doc = {
        "type": "frontend_error",
        "error": error_data.error,
        "stack": error_data.stack,
        "component_stack": error_data.componentStack,
        "timestamp": error_data.timestamp,
        "user_agent": error_data.userAgent,
        "url": error_data.url,
        "created_at": datetime.utcnow()
    }
    
    try:
        await db.error_logs.insert_one(error_doc)
    except Exception as e:
        error_logger.warning(f"Failed to store error log: {e}")
    
    return {"status": "logged", "error_id": error_doc.get("_id", "unknown")}
