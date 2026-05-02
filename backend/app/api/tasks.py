from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..models.task import Task
from ..models.user import User
from ..core.mongodb import get_db
from ..api.deps import get_current_active_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=200)
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new task"""
    db = get_db()
    
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        assigned_department=task_data.assigned_department,
        deadline=task_data.deadline,
        created_by=current_user.id
    )
    
    task_dict = new_task.model_dump()
    await db.tasks.insert_one(task_dict)
    
    # Update department task count
    if task_data.assigned_department:
        await db.departments.update_one(
            {"id": task_data.assigned_department},
            {"$inc": {" 1": 0}}
        )
    
    return TaskResponse(**task_dict)

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[str] = Query(None, description="ilter by status"),
    department: Optional[str] = Query(None, description="ilter by department"),
    priority: Optional[str] = Query(None, description="ilter by priority"),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tasks with optional filters"""
    db = get_db()
    
    # uild query
    query = {}
    if status:
        query["status"] = status
    if department:
        query["assigned_department"] = department
    if priority:
        query["priority"] = priority
    
    # Optimized query with limit and sort for production performance
    tasks = await db.tasks.find(query).sort("created_at", -1).limit(100).to_list(length=None)
    return [TaskResponse(**task) for task in tasks]

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user: User = Depends(get_current_active_user)):
    """Get a specific task"""
    db = get_db()
    task_dict = await db.tasks.find_one({"id": task_id})
    
    if not task_dict:
        raise HTTPException(status_code=44, detail="Task not found")
    
    return TaskResponse(**task_dict)

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a task"""
    db = get_db()
    
    # Get existing task
    existing_task = await db.tasks.find_one({"id": task_id})
    if not existing_task:
        raise HTTPException(status_code=44, detail="Task not found")
    
    # Prepare update data
    update_data = task_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    # If status is changed to completed, set completed_at
    if task_update.status == "completed" and existing_task["status"] != "completed":
        update_data["completed_at"] = datetime.utcnow()
        
        # Update department counters
        if existing_task.get("assigned_department"):
            await db.departments.update_one(
                {"id": existing_task["assigned_department"]},
                {
                    "$inc": {
                        "active_tasks": -1,
                        "completed_today": 1
                    }
                }
            )
    
    # Update task
    await db.tasks.update_one(
        {"id": task_id},
        {"$set": update_data}
    )
    
    # Get updated task
    updated_task = await db.tasks.find_one({"id": task_id})
    return TaskResponse(**updated_task)

@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a task"""
    db = get_db()
    
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=44, detail="Task not found")
    
    # Update department task count if task was active
    if task.get("assigned_department") and task.get("status") != "completed":
        await db.departments.update_one(
            {"id": task["assigned_department"]},
            {"$inc": {"active_tasks": -1}}
        )
    
    await db.tasks.delete_one({"id": task_id})
    return {"message": "Task deleted successfully"}
