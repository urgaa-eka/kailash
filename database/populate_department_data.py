"""Populate sample department data (gaps, tasks, sub-agents) for demonstration."""
import asyncio
import sys
sys.path.insert(0, '/app/backend')

from app.core.mongodb import MongoD
from datetime import datetime, timezone, timedelta
import motor.motor_asyncio

async def populate_sample_data():
    """Populate sample gaps, tasks, and sub-agents."""
    
    # Initialize MongoDB
    await MongoD.connect_db()
    
    # Get database
    db = MongoD.get_database()
    
    # Sample gaps for LAKSHMI
    gaps = [
        {
            "gap_id": "gap_lakshmi_1",
            "department": "lakshmi",
            "severity": "high",
            "category": "api",
            "title": "GST API Authentication Expired",
            "description": "GST API credentials need renewal for compliance updates",
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "resolved": False,
            "alerted_to_ganesha": True,
            "alerted_to_parvati": True
        },
        {
            "gap_id": "gap_vishwakarma_1",
            "department": "vishwakarma",
            "severity": "medium",
            "category": "compliance",
            "title": "Dependency Security Vulnerability",
            "description": "3 npm packages have known security vulnerabilities",
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "resolved": False,
            "alerted_to_ganesha": True,
            "alerted_to_parvati": False
        },
        {
            "gap_id": "gap_surya_1",
            "department": "surya",
            "severity": "critical",
            "category": "data",
            "title": "DISCOM API Connection Issues",
            "description": "Real-time tariff data sync failing for 2 hours",
            "detected_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "resolved": False,
            "alerted_to_ganesha": True,
            "alerted_to_parvati": True
        }
    ]
    
    # Sample tasks
    tasks = [
        {
            "task_id": "task_lakshmi_1",
            "department": "lakshmi",
            "title": "Implement Dynamic Pricing Model",
            "description": "Build ML model for real-time subscription pricing optimization",
            "assigned_to": "Finance-AI-Agent-01",
            "status": "in_progress",
            "priority": "high",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
            "due_date": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
        },
        {
            "task_id": "task_lakshmi_2",
            "department": "lakshmi",
            "title": "Automate Invoice Generation",
            "description": "Create automated monthly invoice system with PDF generation",
            "assigned_to": "Finance-AI-Agent-02",
            "status": "pending",
            "priority": "medium",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "due_date": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
        },
        {
            "task_id": "task_vishwakarma_1",
            "department": "vishwakarma",
            "title": "Migrate to Kubernetes v1.30",
            "description": "Upgrade cluster and test all services",
            "assigned_to": "DevOps-AI-Agent-01",
            "status": "completed",
            "priority": "high",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
            "due_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        },
        {
            "task_id": "task_surya_1",
            "department": "surya",
            "title": "Optimize Charger Health Prediction",
            "description": "Improve predictive maintenance accuracy to 80%",
            "assigned_to": "SURYA-Analytics-Agent",
            "status": "in_progress",
            "priority": "high",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
            "due_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        }
    ]
    
    # Sample sub-agents
    sub_agents = [
        {
            "agent_id": "agent_lakshmi_01",
            "name": "Finance-AI-Agent-01",
            "department": "lakshmi",
            "role": "Revenue Optimization Specialist",
            "status": "active",
            "current_task": "Implement Dynamic Pricing Model"
        },
        {
            "agent_id": "agent_lakshmi_02",
            "name": "Finance-AI-Agent-02",
            "department": "lakshmi",
            "role": "Billing Automation Specialist",
            "status": "idle",
            "current_task": None
        },
        {
            "agent_id": "agent_lakshmi_03",
            "name": "Fraud-Detection-Agent",
            "department": "lakshmi",
            "role": "Security & Fraud Prevention",
            "status": "active",
            "current_task": "Monitor real-time transactions"
        },
        {
            "agent_id": "agent_vishwakarma_01",
            "name": "DevOps-AI-Agent-01",
            "department": "vishwakarma",
            "role": "Infrastructure Management",
            "status": "active",
            "current_task": "System health monitoring"
        },
        {
            "agent_id": "agent_vishwakarma_02",
            "name": "Code-Review-Agent",
            "department": "vishwakarma",
            "role": "Code Quality Assurance",
            "status": "active",
            "current_task": "Review pending PRs"
        },
        {
            "agent_id": "agent_surya_01",
            "name": "SURYA-Analytics-Agent",
            "department": "surya",
            "role": "Predictive Maintenance",
            "status": "active",
            "current_task": "Optimize Charger Health Prediction"
        },
        {
            "agent_id": "agent_surya_02",
            "name": "SURYA-Grid-Agent",
            "department": "surya",
            "role": "Energy Load Balancing",
            "status": "active",
            "current_task": "Dynamic load distribution"
        }
    ]
    
    # Insert data
    print("Inserting gaps...")
    await db.department_gaps.delete_many({})  # Clear existing
    await db.department_gaps.insert_many(gaps)
    print(f"✓ Inserted {len(gaps)} gaps")
    
    print("Inserting tasks...")
    await db.department_tasks.delete_many({})  # Clear existing
    await db.department_tasks.insert_many(tasks)
    print(f"✓ Inserted {len(tasks)} tasks")
    
    print("Inserting sub-agents...")
    await db.sub_agents.delete_many({})  # Clear existing
    await db.sub_agents.insert_many(sub_agents)
    print(f"✓ Inserted {len(sub_agents)} sub-agents")
    
    print("\n✅ Sample data populated successfully!")
    print("\nSummary:")
    print(f"  - Gaps: {len(gaps)}")
    print(f"  - Tasks: {len(tasks)}")
    print(f"  - Sub-Agents: {len(sub_agents)}")

if __name__ == "__main__":
    asyncio.run(populate_sample_data())
