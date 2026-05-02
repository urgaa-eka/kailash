from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.department import Department
from ..models.user import User
from ..core.mongodb import get_db
from ..api.deps import get_current_active_user

router = APIRouter(prefix="/departments", tags=["departments"])

@router.get("/", response_model=List[Department])
async def get_all_departments(current_user: User = Depends(get_current_active_user)):
    """Get all departments"""
    db = get_db()
    # Optimized query with projection and limit for production performance
    departments = await db.departments.find({}, {"_id": 0}).limit(100).to_list(length=None)
    
    result = []
    for dept in departments:
        # Handle sub_agents - could be int or list
        sub_agents = dept.get("sub_agents", [])
        if isinstance(sub_agents, int):
            dept["sub_agents"] = [{"name": f"Agent {i+1}", "role": "Specialist", "status": "active", "workload": 0, "tasks": 0} for i in range(sub_agents)]
        elif not isinstance(sub_agents, list):
            dept["sub_agents"] = []
        result.append(Department(**dept))
    
    return result

@router.get("/{department_id}", response_model=Department)
async def get_department(department_id: str, current_user: User = Depends(get_current_active_user)):
    """Get a specific department by ID"""
    db = get_db()
    
    # Try exact ID match first
    dept_dict = await db.departments.find_one({"id": {"$regex": f"^{department_id}$", "$options": "i"}}, {"_id": 0})
    
    if not dept_dict:
        # Try name match (handles frontend IDs like 'ganesha' -> 'GANESHA')
        dept_dict = await db.departments.find_one({"name": {"$regex": f"^{department_id}$", "$options": "i"}}, {"_id": 0})
    
    if not dept_dict:
        # Try partial name match
        dept_dict = await db.departments.find_one({"name": {"$regex": department_id, "$options": "i"}}, {"_id": 0})
    
    if not dept_dict:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Handle sub_agents - could be int or list
    sub_agents = dept_dict.get("sub_agents", [])
    if isinstance(sub_agents, int):
        dept_dict["sub_agents"] = [{"name": f"Agent {i+1}", "role": "Specialist", "status": "active", "workload": 0, "tasks": 0} for i in range(sub_agents)]
    elif not isinstance(sub_agents, list):
        dept_dict["sub_agents"] = []
    
    return Department(**dept_dict)

@router.get("/{department_id}/health")
async def get_department_health(department_id: str, current_user: User = Depends(get_current_active_user)):
    """Get department health metrics"""
    db = get_db()
    
    # Use flexible matching like other endpoints
    dept_dict = await db.departments.find_one({"id": {"$regex": f"^{department_id}$", "$options": "i"}})
    
    if not dept_dict:
        dept_dict = await db.departments.find_one({"name": {"$regex": f"^{department_id}$", "$options": "i"}})
    
    if not dept_dict:
        dept_dict = await db.departments.find_one({"name": {"$regex": department_id, "$options": "i"}})
    
    if not dept_dict:
        raise HTTPException(status_code=404, detail="Department not found")
    
    dept = Department(**dept_dict)
    
    return {
        "department_id": dept.id,
        "name": dept.name,
        "status": dept.status,
        "workload": dept.workload,
        "active_tasks": dept.active_tasks,
        "completed_today": dept.completed_today,
        "health_score":  - dept.workload,  # Simple health calculation
        "sub_agents_count": len(dept.sub_agents)
    }

@router.get("/{department_id}/sub-agents")
async def get_department_sub_agents(department_id: str, current_user: User = Depends(get_current_active_user)):
    """Get sub-agents for a department"""
    db = get_db()
    
    # Use flexible matching like other endpoints
    dept_dict = await db.departments.find_one({"id": {"$regex": f"^{department_id}$", "$options": "i"}})
    
    if not dept_dict:
        dept_dict = await db.departments.find_one({"name": {"$regex": f"^{department_id}$", "$options": "i"}})
    
    if not dept_dict:
        dept_dict = await db.departments.find_one({"name": {"$regex": department_id, "$options": "i"}})
    
    if not dept_dict:
        raise HTTPException(status_code=404, detail="Department not found")
    
    dept = Department(**dept_dict)
    return {
        "department_id": dept.id,
        "department_name": dept.name,
        "sub_agents": dept.sub_agents
    }

@router.get("/{department_id}/summary")
async def get_department_summary(department_id: str, current_user: User = Depends(get_current_active_user)):
    """Get department summary with tasks, gaps, and sub-agents"""
    db = get_db()
    
    # Try to find by id (case-insensitive)
    dept_dict = await db.departments.find_one({"id": {"$regex": f"^{department_id}$", "$options": "i"}}, {"_id": 0})
    
    if not dept_dict:
        # Try finding by name (case-insensitive) - handles frontend IDs like 'ganesha' -> 'GANESHA'
        dept_dict = await db.departments.find_one({"name": {"$regex": f"^{department_id}$", "$options": "i"}}, {"_id": 0})
    
    if not dept_dict:
        # Try partial name match for better compatibility
        dept_dict = await db.departments.find_one({"name": {"$regex": department_id, "$options": "i"}}, {"_id": 0})
    
    if not dept_dict:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Handle sub_agents - could be int or list
    sub_agents = dept_dict.get("sub_agents", [])
    if isinstance(sub_agents, int):
        sub_agents = [{"id": f"agent_{i+1}", "name": f"Agent {i+1}", "status": "active", "role": "Specialist Agent", "current_task": None} for i in range(sub_agents)]
    elif isinstance(sub_agents, list):
        # Ensure each agent has required fields
        sub_agents = [
            {
                "id": agent.get("id", f"agent_{i+1}"),
                "name": agent.get("name", f"Agent {i+1}"),
                "status": agent.get("status", "active"),
                "role": agent.get("role", "Specialist Agent"),
                "current_task": agent.get("current_task", None)
            } if isinstance(agent, dict) else {"id": f"agent_{i+1}", "name": str(agent), "status": "active", "role": "Specialist Agent", "current_task": None}
            for i, agent in enumerate(sub_agents)
        ]
    
    # Use the found department name for consistent queries
    dept_name = dept_dict.get("name", department_id)
    
    # Get related tasks using department name
    tasks = await db.tasks.find(
        {"department": {"$regex": dept_name, "$options": "i"}},
        {"_id": 0}
    ).limit(10).to_list(length=None)
    
    # Ensure tasks have required fields
    formatted_tasks = [
        {
            "title": task.get("title", "Untitled Task"),
            "description": task.get("description", ""),
            "status": task.get("status", "pending"),
            "priority": task.get("priority", "medium"),
            "assigned_to": task.get("assigned_to", "Unassigned")
        }
        for task in (tasks or [])
    ]
    
    # Get related gaps using department name
    gaps = await db.gaps.find(
        {"department": {"$regex": dept_name, "$options": "i"}},
        {"_id": 0}
    ).limit(10).to_list(length=None)
    
    # Ensure gaps have required fields
    formatted_gaps = [
        {
            "title": gap.get("title", "Untitled Gap"),
            "description": gap.get("description", ""),
            "severity": gap.get("severity", "medium"),
            "category": gap.get("category", "General"),
            "alerted_to_ganesha": gap.get("alerted_to_ganesha", False),
            "alerted_to_parvati": gap.get("alerted_to_parvati", False)
        }
        for gap in (gaps or [])
    ]
    
    # Build complete response with all fields frontend expects
    return {
        "department": dept_dict.get("name", department_id),
        "description": dept_dict.get("description", ""),
        "scope": dept_dict.get("scope", "operations"),
        "status": dept_dict.get("status", "active"),
        "workload": dept_dict.get("workload", 0),
        "active_tasks": dept_dict.get("active_tasks", 0),
        "completed_today": dept_dict.get("completed_today", 0),
        "automation_rate": dept_dict.get("automation_rate", 0.75),
        "sub_agents": sub_agents,
        "tasks": formatted_tasks,
        "gaps": formatted_gaps,
        "api_sources": dept_dict.get("api_sources", [
            {"name": "Internal API", "description": "Core system integration", "update_frequency": "Real-time"}
        ]),
        "daily_tasks": dept_dict.get("daily_tasks", [
            "Monitor department metrics",
            "Process incoming requests",
            "Generate daily reports"
        ]),
        "last_updated": dept_dict.get("last_updated", None),
        "metrics": {
            "health_score": 100 - dept_dict.get("workload", 0),
            "efficiency": 85 + (dept_dict.get("completed_today", 0) % 10),
            "uptime": 99.2
        }
    }

@router.post("/{name}/invoke")
async def invoke_department(
    name: str, 
    task: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Invoke a department to process a task"""
    from ..departments.registry import get_department
    
    department = get_department(name)
    if not department:
        raise HTTPException(status_code=404, detail=f"Department '{name}' not found")
    
    try:
        result = await department.process_task(task)
        return {
            "department": name,
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Department invocation failed: {str(e)}")
