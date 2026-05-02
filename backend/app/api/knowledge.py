"""Knowledge retrieval API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta
import os

from ..api.deps import get_current_user

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

KNOWLEDGE_BASE_PATH = Path("/app/backend/knowledge")


class KnowledgeQuery(BaseModel):
    department: str
    include_pre_data: bool = True
    include_post_data: bool = True
    days_back: int = 7


class KnowledgeResponse(BaseModel):
    department: str
    scope: str
    pre_data: Optional[Dict] = None
    post_data: Optional[List[Dict]] = None
    last_updated: str


@router.get("/departments")
async def get_departments(current_user: dict = Depends(get_current_user)):
    """Get list of all departments."""
    return {
        "internal": [
            "lakshmi", "vishwakarma", "agni", "indra", "vayu", "yama", "kubera",
            "ashwini", "brihaspati", "chandra", "kartikeya", "marut", "narada",
            "rudra", "tvashta"
        ],
        "external": ["surya", "brahma", "saraswati", "varuna", "pragya"]
    }


@router.post("/query")
async def query_knowledge(query: KnowledgeQuery, current_user: dict = Depends(get_current_user)):
    """Query knowledge for a specific department."""
    
    # Determine scope
    internal_depts = ["lakshmi", "vishwakarma", "agni", "indra", "vayu", "yama", "kubera",
                      "ashwini", "brihaspati", "chandra", "kartikeya", "marut", "narada",
                      "rudra", "tvashta"]
    external_depts = ["surya", "brahma", "saraswati", "varuna", "pragya"]
    
    if query.department in internal_depts:
        scope = "internal"
    elif query.department in external_depts:
        scope = "external"
    else:
        raise HTTPException(status_code=404, detail="Department not found")
    
    result = {
        "department": query.department,
        "scope": scope,
        "pre_data": None,
        "post_data": [],
        "last_updated": datetime.now().isoformat()
    }
    
    # Load pre-data
    if query.include_pre_data:
        pre_data_dir = KNOWLEDGE_BASE_PATH / "pre-data" / scope / query.department
        if pre_data_dir.exists():
            pre_data = {}
            for file in pre_data_dir.glob("*.md"):
                with open(file, "r") as f:
                    pre_data[file.stem] = f.read()
            for file in pre_data_dir.glob("*.json"):
                with open(file, "r") as f:
                    pre_data[file.stem] = json.load(f)
            result["pre_data"] = pre_data
    
    # Load post-data (recent intelligence)
    if query.include_post_data:
        post_data_dir = KNOWLEDGE_BASE_PATH / "post-data" / "department-specific" / scope / query.department
        if post_data_dir.exists():
            post_data = []
            # Get last N days of intelligence
            for i in range(query.days_back):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                file_path = post_data_dir / f"{date}.json"
                if file_path.exists():
                    with open(file_path, "r") as f:
                        post_data.append(json.load(f))
            result["post_data"] = post_data
    
    return result


@router.get("/daily-digest/{date}")
async def get_daily_digest(date: str, current_user: dict = Depends(get_current_user)):
    """Get daily intelligence digest for a specific date."""
    digest_dir = KNOWLEDGE_BASE_PATH / "post-data" / "daily-digest" / date
    
    if not digest_dir.exists():
        raise HTTPException(status_code=404, detail="No digest found for this date")
    
    # Load summary
    summary_file = digest_dir / "summary.json"
    if summary_file.exists():
        with open(summary_file, "r") as f:
            summary = json.load(f)
    else:
        summary = None
    
    # Load all department intelligence
    departments = {}
    for file in digest_dir.glob("*.json"):
        if file.name != "summary.json":
            with open(file, "r") as f:
                departments[file.stem] = json.load(f)
    
    return {
        "date": date,
        "summary": summary,
        "departments": departments
    }


@router.post("/trigger-learning")
async def trigger_learning(current_user: dict = Depends(get_current_user)):
    """Manually trigger daily learning pipeline (admin only)."""
    from ..tasks.daily_learning import async_daily_learning_pipeline
    import asyncio
    
    # Check if user has admin role
    # current_user can be either dict or User object
    is_admin = current_user.get("is_admin") if isinstance(current_user, dict) else getattr(current_user, "is_admin", False)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Run the pipeline directly in background (for now without Celery)
    # In production, this should use Celery with proper broker
    try:
        # Start the pipeline as a background task
        asyncio.create_task(async_daily_learning_pipeline())
        
        return {
            "status": "started",
            "message": "Daily learning pipeline started in background",
            "note": "This is running directly. In production, use Celery Beat for scheduled tasks."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start pipeline: {str(e)}")
