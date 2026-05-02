"""Department Intelligence with Gap Detection and Alerting System."""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime, timezone
import json
from pathlib import Path

from ..api.deps import get_current_user
from ..core.mongodb import MongoD

router = APIRouter(prefix="/api/departments", tags=["Department Intelligence"])

KNOWLEDGE_BASE_PATH = Path("/app/backend/knowledge")


class DepartmentGap(BaseModel):
    gap_id: str
    department: str
    severity: str  # critical, high, medium, low
    category: str  # compliance, data, api, policy
    title: str
    description: str
    detected_at: str
    resolved: bool = False
    alerted_to_ganesha: bool = False
    alerted_to_parvati: bool = False


class DepartmentTask(BaseModel):
    task_id: str
    department: str
    title: str
    description: str
    assigned_to: str  # sub-agent name
    status: str  # pending, in_progress, completed
    priority: str  # high, medium, low
    created_at: str
    due_date: Optional[str] = None


class SubAgent(BaseModel):
    agent_id: str
    name: str
    department: str
    role: str
    status: str  # active, idle, offline
    current_task: Optional[str] = None


class DepartmentSummary(BaseModel):
    department: str
    scope: str
    description: str
    automation_rate: float
    api_sources: List[Dict]
    latest_intelligence: Optional[str] = None
    gaps: List[DepartmentGap] = []
    tasks: List[DepartmentTask] = []
    sub_agents: List[SubAgent] = []
    daily_tasks: List[str] = []
    last_updated: str


@router.get("/{department_name}/summary")
async def get_department_summary(
    department_name: str,
    current_user: dict = Depends(get_current_user)
) -> DepartmentSummary:
    """Get comprehensive department summary with intelligence, gaps, tasks, and agents."""
    
    # Determine scope
    internal_depts = ["lakshmi", "vishwakarma", "agni", "indra", "vayu", "yama", "kubera",
                      "ashwini", "brihaspati", "chandra", "kartikeya", "marut", "narada",
                      "rudra", "tvashta"]
    external_depts = ["surya", "brahma", "saraswati", "varuna", "pragya"]
    
    if department_name in internal_depts:
        scope = "internal"
    elif department_name in external_depts:
        scope = "external"
    else:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Load API sources
    api_sources_file = KNOWLEDGE_BASE_PATH / "config" / "api_sources.json"
    api_sources = []
    if api_sources_file.exists():
        with open(api_sources_file, "r") as f:
            all_sources = json.load(f)
            dept_sources = all_sources.get(scope, {}).get(department_name, {})
            api_sources = dept_sources.get("api_sources", [])
    
    # Load domain expertise for description
    domain_file = KNOWLEDGE_BASE_PATH / "pre-data" / scope / department_name / "domain_expertise.md"
    description = ""
    if domain_file.exists():
        with open(domain_file, "r") as f:
            content = f.read()
            # Extract first paragraph as description
            lines = content.split("\n")
            for line in lines:
                if line.strip() and not line.startswith("#"):
                    description = line.strip()
                    break
    
    # Load rules for automation rate
    rules_file = KNOWLEDGE_BASE_PATH / "pre-data" / scope / department_name / "rules.json"
    automation_rate = 0.0
    if rules_file.exists():
        with open(rules_file, "r") as f:
            rules = json.load(f)
            automation_rate = rules.get("department_config", {}).get("automation_rate_target", 0.0)
    
    # Load latest intelligence from post-data
    latest_intelligence = None
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    intelligence_file = KNOWLEDGE_BASE_PATH / "post-data" / "daily-digest" / today / f"{department_name}.json"
    if intelligence_file.exists():
        with open(intelligence_file, "r") as f:
            intel_data = json.load(f)
            latest_intelligence = intel_data.get("processed_intelligence", "")
    
    # Load gaps from database
    db = MongoD.get_database()
    gaps_data = await db.department_gaps.find(
        {"department": department_name, "resolved": False},
        {"_id": 0}
    ).to_list(100)
    gaps = [DepartmentGap(**gap) for gap in gaps_data] if gaps_data else []
    
    # Load tasks from database
    tasks_data = await db.department_tasks.find(
        {"department": department_name},
        {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(100)
    tasks = [DepartmentTask(**task) for task in tasks_data] if tasks_data else []
    
    # Load sub-agents from database
    agents_data = await db.sub_agents.find(
        {"department": department_name},
        {"_id": 0}
    ).to_list(100)
    sub_agents = [SubAgent(**agent) for agent in agents_data] if agents_data else []
    
    # Generate daily tasks from SOP
    daily_tasks = []
    sop_file = KNOWLEDGE_BASE_PATH / "pre-data" / scope / department_name / "sop.md"
    if sop_file.exists():
        with open(sop_file, "r") as f:
            sop_content = f.read()
            # Extract daily tasks from SOP (look for Morning/Daily sections)
            if "Morning" in sop_content or "Daily" in sop_content:
                daily_tasks = [
                    "Review overnight alerts and incidents",
                    "Check system health and metrics",
                    "Process pending items and requests",
                    "Update dashboards and reports"
                ]
    
    return DepartmentSummary(
        department=department_name.upper(),
        scope=scope,
        description=description,
        automation_rate=automation_rate,
        api_sources=api_sources,
        latest_intelligence=latest_intelligence,
        gaps=gaps,
        tasks=tasks,
        sub_agents=sub_agents,
        daily_tasks=daily_tasks,
        last_updated=datetime.now(timezone.utc).isoformat()
    )


@router.post("/{department_name}/detect-gaps")
async def detect_department_gaps(
    department_name: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Run gap detection for department and alert GANESHA if gaps found."""
    
    # This will run gap detection logic
    # For now, we'll create a sample gap for demonstration
    db = MongoD.get_database()
    
    # Example gap detection logic
    gap_id = f"gap_{department_name}_{datetime.now().timestamp()}"
    gap = {
        "gap_id": gap_id,
        "department": department_name,
        "severity": "high",
        "category": "api",
        "title": "API Source Update Required",
        "description": f"One or more API sources for {department_name} need authentication update",
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "resolved": False,
        "alerted_to_ganesha": False,
        "alerted_to_parvati": False
    }
    
    # Save gap to database
    await db.department_gaps.insert_one(gap)
    
    # Alert GANESHA in background
    background_tasks.add_task(alert_ganesha, department_name, gap)
    
    return {
        "status": "success",
        "message": f"Gap detection completed for {department_name}",
        "gaps_detected": 1
    }


async def alert_ganesha(department: str, gap: dict):
    """Alert GANESHA about detected gap."""
    db = MongoD.get_database()
    
    # Create alert for GANESHA
    alert = {
        "type": "gap_detected",
        "department": department,
        "gap_id": gap["gap_id"],
        "severity": gap["severity"],
        "title": gap["title"],
        "description": gap["description"],
        "alerted_at": datetime.now(timezone.utc).isoformat(),
        "escalated_to_parvati": False
    }
    
    await db.ganesha_alerts.insert_one(alert)
    
    # Update gap to mark as alerted
    await db.department_gaps.update_one(
        {"gap_id": gap["gap_id"]},
        {"$set": {"alerted_to_ganesha": True}}
    )
    
    # If severity is critical or high, escalate to PARVATI
    if gap["severity"] in ["critical", "high"]:
        await alert_parvati(department, gap, alert)


async def alert_parvati(department: str, gap: dict, ganesha_alert: dict):
    """Escalate alert to PARVATI for high-priority gaps."""
    db = MongoD.get_database()
    
    # Create alert for PARVATI
    parvati_alert = {
        "type": "gap_escalation",
        "department": department,
        "gap_id": gap["gap_id"],
        "severity": gap["severity"],
        "title": f"[ESCALATED] {gap['title']}",
        "description": gap["description"],
        "escalated_from": "ganesha",
        "alerted_at": datetime.now(timezone.utc).isoformat(),
        "requires_user_attention": True
    }
    
    await db.parvati_alerts.insert_one(parvati_alert)
    
    # Update gap and GANESHA alert
    await db.department_gaps.update_one(
        {"gap_id": gap["gap_id"]},
        {"$set": {"alerted_to_parvati": True}}
    )
    
    await db.ganesha_alerts.update_one(
        {"type": "gap_detected", "gap_id": gap["gap_id"]},
        {"$set": {"escalated_to_parvati": True}}
    )
