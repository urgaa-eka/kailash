"""CRUD API for Gaps and Tasks Management."""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from uuid import uuid4

from ..api.deps import get_current_user
from ..core.mongodb import MongoD

router = APIRouter(prefix="/api/management", tags=["Gaps & Tasks Management"])


# ============= GAP MODELS =============
class GapCreate(BaseModel):
    department: str
    title: str
    description: str
    severity: str = Field(..., pattern="^(critical|high|medium|low)$")
    category: str = Field(..., pattern="^(compliance|data|api|policy|security|performance)$")


class GapUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    resolved: Optional[bool] = None


class GapResponse(BaseModel):
    gap_id: str
    department: str
    title: str
    description: str
    severity: str
    category: str
    detected_at: str
    resolved: bool
    alerted_to_ganesha: bool
    alerted_to_parvati: bool


# ============= TASK MODELS =============
class TaskCreate(BaseModel):
    department: str
    title: str
    description: str
    assigned_to: str
    priority: str = Field(..., pattern="^(high|medium|low)$")
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None


class TaskResponse(BaseModel):
    task_id: str
    department: str
    title: str
    description: str
    assigned_to: str
    status: str
    priority: str
    created_at: str
    due_date: Optional[str] = None


# ============= GAP ENDPOINTS =============
@router.get("/gaps", response_model=List[GapResponse])
async def list_gaps(
    department: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """List all gaps with optional filters."""
    db = MongoD.get_database()
    
    query = {}
    if department:
        query["department"] = department.lower()
    if severity:
        query["severity"] = severity
    if resolved is not None:
        query["resolved"] = resolved
    
    gaps = await db.department_gaps.find(query, {"_id": 0}).sort("detected_at", -1).to_list(100)
    return gaps


@router.post("/gaps", response_model=GapResponse)
async def create_gap(
    gap: GapCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new gap."""
    db = MongoD.get_database()
    
    gap_doc = {
        "gap_id": f"gap_{uuid4().hex[:8]}",
        "department": gap.department.lower(),
        "title": gap.title,
        "description": gap.description,
        "severity": gap.severity,
        "category": gap.category,
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "resolved": False,
        "alerted_to_ganesha": False,
        "alerted_to_parvati": False
    }
    
    await db.department_gaps.insert_one(gap_doc)
    
    # Auto-alert GANESHA for high/critical gaps
    if gap.severity in ["critical", "high"]:
        await db.department_gaps.update_one(
            {"gap_id": gap_doc["gap_id"]},
            {"$set": {"alerted_to_ganesha": True}}
        )
        gap_doc["alerted_to_ganesha"] = True
        
        # Escalate critical to PARVATI
        if gap.severity == "critical":
            await db.department_gaps.update_one(
                {"gap_id": gap_doc["gap_id"]},
                {"$set": {"alerted_to_parvati": True}}
            )
            gap_doc["alerted_to_parvati"] = True
    
    return gap_doc


@router.get("/gaps/{gap_id}", response_model=GapResponse)
async def get_gap(
    gap_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific gap by ID."""
    db = MongoD.get_database()
    gap = await db.department_gaps.find_one({"gap_id": gap_id}, {"_id": 0})
    
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")
    
    return gap


@router.put("/gaps/{gap_id}", response_model=GapResponse)
async def update_gap(
    gap_id: str,
    gap_update: GapUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a gap."""
    db = MongoD.get_database()
    
    update_data = {k: v for k, v in gap_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    result = await db.department_gaps.update_one(
        {"gap_id": gap_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Gap not found")
    
    gap = await db.department_gaps.find_one({"gap_id": gap_id}, {"_id": 0})
    return gap


@router.delete("/gaps/{gap_id}")
async def delete_gap(
    gap_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a gap."""
    db = MongoD.get_database()
    
    result = await db.department_gaps.delete_one({"gap_id": gap_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Gap not found")
    
    return {"status": "success", "message": f"Gap {gap_id} deleted"}


# ============= TASK ENDPOINTS =============
@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """List all tasks with optional filters."""
    db = MongoD.get_database()
    
    query = {}
    if department:
        query["department"] = department.lower()
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    
    tasks = await db.department_tasks.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return tasks


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new task."""
    db = MongoD.get_database()
    
    task_doc = {
        "task_id": f"task_{uuid4().hex[:8]}",
        "department": task.department.lower(),
        "title": task.title,
        "description": task.description,
        "assigned_to": task.assigned_to,
        "status": "pending",
        "priority": task.priority,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "due_date": task.due_date
    }
    
    await db.department_tasks.insert_one(task_doc)
    return task_doc


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific task by ID."""
    db = MongoD.get_database()
    task = await db.department_tasks.find_one({"task_id": task_id}, {"_id": 0})
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a task."""
    db = MongoD.get_database()
    
    update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    result = await db.department_tasks.update_one(
        {"task_id": task_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = await db.department_tasks.find_one({"task_id": task_id}, {"_id": 0})
    return task


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a task."""
    db = MongoD.get_database()
    
    result = await db.department_tasks.delete_one({"task_id": task_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"status": "success", "message": f"Task {task_id} deleted"}


# ============= STATS ENDPOINT =============
@router.get("/stats")
async def get_management_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get overall statistics for gaps and tasks."""
    db = MongoD.get_database()
    
    # Gap stats
    total_gaps = await db.department_gaps.count_documents({})
    open_gaps = await db.department_gaps.count_documents({"resolved": False})
    critical_gaps = await db.department_gaps.count_documents({"severity": "critical", "resolved": False})
    
    # Task stats
    total_tasks = await db.department_tasks.count_documents({})
    pending_tasks = await db.department_tasks.count_documents({"status": "pending"})
    in_progress_tasks = await db.department_tasks.count_documents({"status": "in_progress"})
    completed_tasks = await db.department_tasks.count_documents({"status": "completed"})
    
    return {
        "gaps": {
            "total": total_gaps,
            "open": open_gaps,
            "critical": critical_gaps,
            "resolved": total_gaps - open_gaps
        },
        "tasks": {
            "total": total_tasks,
            "pending": pending_tasks,
            "in_progress": in_progress_tasks,
            "completed": completed_tasks
        }
    }
