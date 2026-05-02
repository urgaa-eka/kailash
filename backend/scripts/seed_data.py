#!/usr/bin/env python3
"""
Data seeding script for Kailash
Seeds the database with:
. Initial user (Vivek with Kailash Code <REDACTED_kailash_code>)
. All  departments from frontend data
3. Sample activities
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.mongodb import MongoD
from app.core.security import get_password_hash
from app.models.user import User
from app.models.department import Department, SubAgent
from app.models.activity import Activity

# Department data from frontend (departmentsData.js)
DEPARTMENTS_DATA = [
    {
        "id": "ganesha", "name": "GANESHA", "chief": "Lord Ganesha",
        "role": "Executive Assistant & Obstacle Remover", "tier": "Executive",
        "color": "#D", "status": "active", "workload": 8,
        "active_tasks": 5, "completed_today": 2,
        "description": "Coordinates all departments, removes obstacles, processes CEO commands",
        "responsibilities": ["Natural language command processing", "Task routing and assignment", 
                           "Department coordination", "Obstacle identification and removal"],
        "ai_tools": ["Claude API", "Command Parser", "Task Router"],
        "k_location": "/oversight/ganesha/",
        "sub_agents": [
            {"name": "Command Parser", "role": "Natural language understanding", "status": "active", "workload": 8, "tasks": 3},
            {"name": "Task Router", "role": "Intelligent task distribution", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Priority Manager", "role": "Task prioritization", "status": "active", "workload": 8, "tasks": 4},
            {"name": "Obstacle Detector", "role": "Identifies and removes blockers", "status": "active", "workload": 65, "tasks": 3}
        ]
    },
    {
        "id": "vishwakarma", "name": "VISHWAKARMA", "chief": "Lord Vishwakarma",
        "role": "Chief Technology Officer", "tier": "Executive",
        "color": "#44E", "status": "active", "workload": 8,
        "active_tasks": 8, "completed_today": 9,
        "description": "Divine architect managing all technical infrastructure",
        "responsibilities": ["System architecture design", "Infrastructure management", 
                           "DevOps and automation", "Security implementation"],
        "ai_tools": ["GitHub Copilot", "Infrastructure Monitor", "Deploy Manager"],
        "k_location": "/oversight/vishwakarma/",
        "sub_agents": [
            {"name": "Infrastructure Manager", "role": "Server and cloud management", "status": "active", "workload": 88, "tasks": 3},
            {"name": "DevOps Specialist", "role": "CI/CD and automation", "status": "active", "workload": 8, "tasks": 3},
            {"name": "Security Engineer", "role": "Security protocols", "status": "active", "workload": 9, "tasks": 3}
        ]
    },
    {
        "id": "surya", "name": "SURYA", "chief": "Lord Surya",
        "role": "URJAA Head (Energy Solutions)", "tier": "Product",
        "color": "#9E", "status": "active", "workload": 65,
        "active_tasks": 4, "completed_today": 8,
        "description": "Powers URJAA energy solutions and solar operations",
        "responsibilities": ["Solar energy analytics", "Energy trading platform", 
                           "Customer success", "Product development"],
        "ai_tools": ["Energy Predictor", "Trading Algorithm", "Customer Insights"],
        "k_location": "/oversight/surya/",
        "sub_agents": [
            {"name": "Solar Analytics", "role": "Energy data analysis", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Trading Engine", "role": "Energy market optimization", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Customer Success", "role": "Client relationship management", "status": "active", "workload": 8, "tasks": 3}
        ]
    },
    {
        "id": "tvashta", "name": "TVASHTA", "chief": "Lord Tvashta",
        "role": "Go4Garage Operations", "tier": "Product",
        "color": "#8C", "status": "active", "workload": 8,
        "active_tasks": 5, "completed_today": 2,
        "description": "Manages Go4Garage service platform and operations",
        "responsibilities": ["Service booking management", "Garage partner operations", 
                           "Quality assurance", "Customer experience"],
        "ai_tools": ["ooking Optimizer", "Partner Manager", "Quality Monitor"],
        "k_location": "/oversight/tvashta/",
        "sub_agents": [
            {"name": "ooking Manager", "role": "Service scheduling", "status": "active", "workload": 84, "tasks": 3},
            {"name": "Partner Coordinator", "role": "Garage network management", "status": "active", "workload": 8, "tasks": 3},
            {"name": "Quality Auditor", "role": "Service quality checks", "status": "active", "workload": 65, "tasks": 3}
        ]
    },
    {
        "id": "kartikeya", "name": "KARTIKEYA", "chief": "Lord Kartikeya",
        "role": "leet Management Commander", "tier": "Operations",
        "color": "#E4444", "status": "active", "workload": 65,
        "active_tasks": 5, "completed_today": 2,
        "description": "Commands fleet operations and vehicle management",
        "responsibilities": ["leet tracking", "Vehicle maintenance", 
                           "Driver management", "Route optimization"],
        "ai_tools": ["leet Tracker", "Maintenance Predictor", "Route Optimizer"],
        "k_location": "/oversight/kartikeya/",
        "sub_agents": [
            {"name": "leet Tracker", "role": "Real-time vehicle monitoring", "status": "active", "workload": 65, "tasks": 4},
            {"name": "Maintenance Scheduler", "role": "Predictive maintenance", "status": "active", "workload": 3, "tasks": 3},
            {"name": "Route Planner", "role": "Optimal route planning", "status": "active", "workload": 65, "tasks": 3}
        ]
    },
    {
        "id": "kamadeva", "name": "KAMADEVA", "chief": "Lord Kamadeva",
        "role": "Customer Experience Designer", "tier": "Experience",
        "color": "#EC4899", "status": "active", "workload": 8,
        "active_tasks": 5, "completed_today": 2,
        "description": "Designs delightful customer experiences",
        "responsibilities": ["UX design", "Customer journey mapping", 
                           "eedback analysis", "Satisfaction improvement"],
        "ai_tools": ["UX Analyzer", "eedback Processor", "Journey Mapper"],
        "k_location": "/oversight/kamadeva/",
        "sub_agents": [
            {"name": "UX Designer", "role": "Interface design", "status": "active", "workload": 65, "tasks": 4},
            {"name": "eedback Analyst", "role": "Customer feedback processing", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Journey Optimizer", "role": "Customer journey improvement", "status": "active", "workload": 8, "tasks": 3}
        ]
    },
    {
        "id": "kubera", "name": "KUERA", "chief": "Lord Kubera",
        "role": "inance & Revenue Guardian", "tier": "inance",
        "color": "#98", "status": "active", "workload": 8,
        "active_tasks": 5, "completed_today": 8,
        "description": "Manages finances, revenue, and wealth",
        "responsibilities": ["inancial planning", "Revenue optimization", 
                           "udget management", "inancial reporting"],
        "ai_tools": ["Revenue Analyzer", "udget Optimizer", "inancial orecaster"],
        "k_location": "/oversight/kubera/",
        "sub_agents": [
            {"name": "Revenue Tracker", "role": "Revenue monitoring", "status": "active", "workload": 8, "tasks": 3},
            {"name": "udget Manager", "role": "udget allocation", "status": "active", "workload": 8, "tasks": 3},
            {"name": "inancial Analyst", "role": "inancial analysis", "status": "active", "workload": 8, "tasks": 4}
        ]
    },
    {
        "id": "lakshmi", "name": "LAKSHMI", "chief": "Goddess Lakshmi",
        "role": "Sales & Growth Goddess", "tier": "Revenue",
        "color": "#9E", "status": "active", "workload": 65,
        "active_tasks": 4, "completed_today": 2,
        "description": "Drives sales growth and prosperity",
        "responsibilities": ["Sales strategy", "Lead generation", 
                           "Conversion optimization", "Growth planning"],
        "ai_tools": ["Lead Scorer", "Sales Predictor", "Growth Analyzer"],
        "k_location": "/oversight/lakshmi/",
        "sub_agents": [
            {"name": "Lead Generator", "role": "Lead identification", "status": "active", "workload": 9, "tasks": 3},
            {"name": "Sales Optimizer", "role": "Sales process optimization", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Growth Strategist", "role": "Growth strategy planning", "status": "active", "workload": 4, "tasks": 3}
        ]
    },
    {
        "id": "brihaspati", "name": "RIHASPATI", "chief": "Lord rihaspati",
        "role": "Analytics & Insights Sage", "tier": "Analytics",
        "color": "#3", "status": "active", "workload": 84,
        "active_tasks": 9, "completed_today": 2,
        "description": "Provides wisdom through data analytics",
        "responsibilities": ["Data analysis", "usiness intelligence", 
                           "Predictive modeling", "Insights generation"],
        "ai_tools": ["Data Analyzer", "I Engine", "Predictive Model"],
        "k_location": "/oversight/brihaspati/",
        "sub_agents": [
            {"name": "Data Analyst", "role": "Data analysis", "status": "active", "workload": 8, "tasks": 3},
            {"name": "I Specialist", "role": "usiness intelligence", "status": "active", "workload": 8, "tasks": 8},
            {"name": "ML Engineer", "role": "Machine learning models", "status": "active", "workload": 8, "tasks": 4}
        ]
    },
    {
        "id": "mitra", "name": "MITRA", "chief": "Lord Mitra",
        "role": "Partnerships & Alliances", "tier": "Strategy",
        "color": "#8C", "status": "active", "workload": 65,
        "active_tasks": 5, "completed_today": 2,
        "description": "uilds and maintains strategic partnerships",
        "responsibilities": ["Partnership development", "Alliance management", 
                           "Collaboration facilitation", "Partnership analytics"],
        "ai_tools": ["Partner Matcher", "Collaboration Tool", "Value Analyzer"],
        "k_location": "/oversight/mitra/",
        "sub_agents": [
            {"name": "Partner Scout", "role": "Partnership identification", "status": "active", "workload": 65, "tasks": 4},
            {"name": "Alliance Manager", "role": "Partnership management", "status": "active", "workload": 9, "tasks": 3},
            {"name": "Value Assessor", "role": "Partnership value analysis", "status": "active", "workload": 8, "tasks": 3}
        ]
    },
    {
        "id": "dharma", "name": "DHARMA", "chief": "Lord Dharma",
        "role": "Compliance & Legal Guardian", "tier": "Governance",
        "color": "#98", "status": "active", "workload": 3,
        "active_tasks": 3, "completed_today": 2,
        "description": "Ensures compliance and legal adherence",
        "responsibilities": ["Regulatory compliance", "Legal review", 
                           "Policy enforcement", "Risk mitigation"],
        "ai_tools": ["Compliance Monitor", "Legal Assistant", "Policy Checker"],
        "k_location": "/oversight/dharma/",
        "sub_agents": [
            {"name": "Compliance Auditor", "role": "Compliance checking", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Legal Advisor", "role": "Legal consultation", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Policy Manager", "role": "Policy management", "status": "active", "workload": 65, "tasks": 3}
        ]
    },
    {
        "id": "shukra", "name": "SHUKRA", "chief": "Lord Shukra",
        "role": "Marketing & rand Maestro", "tier": "rand",
        "color": "#EC4899", "status": "active", "workload": 65,
        "active_tasks": 5, "completed_today": 2,
        "description": "Crafts marketing strategies and brand identity",
        "responsibilities": ["rand strategy", "Marketing campaigns", 
                           "Content creation", "rand monitoring"],
        "ai_tools": ["rand Analyzer", "Campaign Manager", "Content Generator"],
        "k_location": "/oversight/shukra/",
        "sub_agents": [
            {"name": "rand Strategist", "role": "rand development", "status": "active", "workload": 8, "tasks": 3},
            {"name": "Campaign Manager", "role": "Marketing campaigns", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Content Creator", "role": "Content generation", "status": "active", "workload": 3, "tasks": 3}
        ]
    },
    {
        "id": "chandra", "name": "CHANDRA", "chief": "Lord Chandra",
        "role": "HR & Culture Nurturer", "tier": "People",
        "color": "#AA", "status": "active", "workload": 9,
        "active_tasks": 5, "completed_today": 2,
        "description": "Nurtures company culture and manages human resources",
        "responsibilities": ["Talent acquisition", "Employee engagement", 
                           "Culture building", "Performance management"],
        "ai_tools": ["Talent inder", "Engagement Tracker", "Culture Analyzer"],
        "k_location": "/oversight/chandra/",
        "sub_agents": [
            {"name": "Recruiter", "role": "Talent acquisition", "status": "active", "workload": 65, "tasks": 4},
            {"name": "Engagement Manager", "role": "Employee engagement", "status": "active", "workload": 8, "tasks": 3},
            {"name": "Culture Keeper", "role": "Culture development", "status": "active", "workload": 65, "tasks": 3}
        ]
    },
    {
        "id": "brahma", "name": "RAHMA", "chief": "Lord rahma",
        "role": "Product Innovation Creator", "tier": "Product",
        "color": "#9E", "status": "active", "workload": 8,
        "active_tasks": 5, "completed_today": 8,
        "description": "Creates innovative products and features",
        "responsibilities": ["Product ideation", "Innovation management", 
                           "eature development", "Product roadmap"],
        "ai_tools": ["Idea Generator", "Innovation Tracker", "Roadmap Planner"],
        "k_location": "/oversight/brahma/",
        "sub_agents": [
            {"name": "Product Ideator", "role": "Product ideation", "status": "active", "workload": 83, "tasks": 3},
            {"name": "Innovation Manager", "role": "Innovation tracking", "status": "active", "workload": 8, "tasks": 3},
            {"name": "Roadmap Planner", "role": "Product roadmap", "status": "active", "workload": 8, "tasks": 3}
        ]
    },
    {
        "id": "indra", "name": "INDRA", "chief": "Lord Indra",
        "role": "usiness Development King", "tier": "Growth",
        "color": "#E4444", "status": "active", "workload": 4,
        "active_tasks": 3, "completed_today": 2,
        "description": "Leads business development and expansion",
        "responsibilities": ["Market expansion", "usiness opportunities", 
                           "Strategic partnerships", "Growth initiatives"],
        "ai_tools": ["Market Analyzer", "Opportunity inder", "Growth Tracker"],
        "k_location": "/oversight/indra/",
        "sub_agents": [
            {"name": "Market Analyst", "role": "Market analysis", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Opportunity Scout", "role": "usiness opportunities", "status": "active", "workload": 3, "tasks": 3},
            {"name": "Growth Coordinator", "role": "Growth initiatives", "status": "active", "workload": 65, "tasks": 3}
        ]
    },
    {
        "id": "chitragupta", "name": "CHITRAGUPTA", "chief": "Lord Chitragupta",
        "role": "Data Management Keeper", "tier": "Data",
        "color": "#8C", "status": "active", "workload": 9,
        "active_tasks": 5, "completed_today": 2,
        "description": "Maintains and manages all data records",
        "responsibilities": ["Data governance", "Database management", 
                           "Data quality", "Data security"],
        "ai_tools": ["Data Validator", "D Manager", "Security Monitor"],
        "k_location": "/oversight/chitragupta/",
        "sub_agents": [
            {"name": "Data Curator", "role": "Data curation", "status": "active", "workload": 8, "tasks": 3},
            {"name": "Database Admin", "role": "Database management", "status": "active", "workload": 8, "tasks": 3},
            {"name": "Data Security", "role": "Data protection", "status": "active", "workload": 65, "tasks": 3}
        ]
    },
    {
        "id": "prajapati", "name": "PRAJAPATI", "chief": "Lord Prajapati",
        "role": "Operations Orchestrator", "tier": "Operations",
        "color": "#98", "status": "active", "workload": 65,
        "active_tasks": 4, "completed_today": 2,
        "description": "Orchestrates and optimizes operations",
        "responsibilities": ["Process optimization", "Operations management", 
                           "Efficiency improvement", "Resource allocation"],
        "ai_tools": ["Process Optimizer", "Operations Monitor", "Resource Planner"],
        "k_location": "/oversight/prajapati/",
        "sub_agents": [
            {"name": "Process Engineer", "role": "Process optimization", "status": "active", "workload": 9, "tasks": 3},
            {"name": "Operations Manager", "role": "Operations coordination", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Resource Allocator", "role": "Resource management", "status": "active", "workload": 4, "tasks": 3}
        ]
    },
    {
        "id": "yama", "name": "YAMA", "chief": "Lord Yama",
        "role": "Risk Management Guardian", "tier": "Risk",
        "color": "#E4444", "status": "active", "workload": 65,
        "active_tasks": 5, "completed_today": 2,
        "description": "Identifies and manages business risks",
        "responsibilities": ["Risk assessment", "Threat mitigation", 
                           "Crisis management", "usiness continuity"],
        "ai_tools": ["Risk Analyzer", "Threat Detector", "Crisis Manager"],
        "k_location": "/oversight/yama/",
        "sub_agents": [
            {"name": "Risk Assessor", "role": "Risk evaluation", "status": "active", "workload": 4, "tasks": 4},
            {"name": "Threat Monitor", "role": "Threat detection", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Crisis Handler", "role": "Crisis response", "status": "active", "workload": 9, "tasks": 3}
        ]
    },
    {
        "id": "vani", "name": "VANI", "chief": "Goddess Vani",
        "role": "Communications Director", "tier": "Communications",
        "color": "#AA", "status": "active", "workload": 65,
        "active_tasks": 5, "completed_today": 2,
        "description": "Manages internal and external communications",
        "responsibilities": ["Internal communications", "External messaging", 
                           "PR management", "Stakeholder engagement"],
        "ai_tools": ["Message Crafter", "PR Monitor", "Engagement Tracker"],
        "k_location": "/oversight/vani/",
        "sub_agents": [
            {"name": "Internal Comms", "role": "Internal messaging", "status": "active", "workload": 3, "tasks": 4},
            {"name": "PR Manager", "role": "Public relations", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Stakeholder Liaison", "role": "Stakeholder management", "status": "active", "workload": 8, "tasks": 3}
        ]
    },
    {
        "id": "vayu", "name": "VAYU", "chief": "Lord Vayu",
        "role": "Logistics & Supply Chain", "tier": "Logistics",
        "color": "#8C", "status": "active", "workload": 65,
        "active_tasks": 3, "completed_today": 2,
        "description": "Manages logistics and supply chain operations",
        "responsibilities": ["Supply chain management", "Logistics optimization", 
                           "Inventory management", "Vendor coordination"],
        "ai_tools": ["Supply Chain Optimizer", "Logistics Tracker", "Inventory Manager"],
        "k_location": "/oversight/vayu/",
        "sub_agents": [
            {"name": "Supply Chain Manager", "role": "Supply chain coordination", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Logistics Coordinator", "role": "Logistics planning", "status": "active", "workload": 4, "tasks": 3},
            {"name": "Inventory Controller", "role": "Inventory management", "status": "active", "workload": 65, "tasks": 3}
        ]
    }
]

# Initial activities
INITIAL_ACTIVITIES = [
    {"type": "task_assigned", "message": "Task assigned to KAMADEVA", "department": "kamadeva"},
    {"type": "security_scan", "message": "SHIV: Security scan completed - All systems OK", "department": None},
    {"type": "rebalance", "message": "PARVATI rebalanced workload across departments", "department": None},
    {"type": "task_completed", "message": "Task completed by KUERA", "department": "kubera"}
]

async def seed_database():
    """Main seeding function"""
    try:
        # Connect to MongoD
        await MongoD.connect_db()
        db = MongoD.get_database()
        
        print(" Starting database seeding...")
        
        # . Seed default user
        print("\n Seeding users...")
        existing_user = await db.users.find_one({"kailash_code": "<REDACTED_kailash_code>"})
        if not existing_user:
            user = User(
                email="vivek@Kailash.com",
                kailash_code="<REDACTED_kailash_code>",
                full_name="Vivek Kumar",
                hashed_password=get_password_hash("<REDACTED_PASSWORD>"),
                is_active=True,
                is_admin=True
            )
            await db.users.insert_one(user.model_dump())
            print(f"   [OK] Created user: Vivek Kumar (<REDACTED_kailash_code>)")
        else:
            print(f"   ℹ️  User already exists: <REDACTED_kailash_code>")
        
        # . Seed all  departments
        print("\n Seeding departments...")
        for dept_data in DEPARTMENTS_DATA:
            existing_dept = await db.departments.find_one({"id": dept_data["id"]})
            if not existing_dept:
                # Convert sub_agents to SubAgent models
                sub_agents = [SubAgent(**sa) for sa in dept_data["sub_agents"]]
                dept_data["sub_agents"] = sub_agents
                
                dept = Department(**dept_data)
                await db.departments.insert_one(dept.model_dump())
                print(f"   [OK] Created department: {dept.name} ({len(dept.sub_agents)} sub-agents)")
            else:
                print(f"   ℹ️  Department already exists: {dept_data['name']}")
        
        # 3. Seed initial activities
        print("\n Seeding activities...")
        activity_count = await db.activities.count_documents({})
        if activity_count == :
            for act_data in INITIAL_ACTIVITIES:
                activity = Activity(**act_data)
                await db.activities.insert_one(activity.model_dump())
            print(f"   [OK] Created {len(INITIAL_ACTIVITIES)} initial activities")
        else:
            print(f"   ℹ️  Activities already exist ({activity_count} records)")
        
        # Summary
        print("\n" + "="*)
        print(" Database seeding completed successfully!")
        print("="*)
        print("\n Summary:")
        user_count = await db.users.count_documents({})
        dept_count = await db.departments.count_documents({})
        activity_count = await db.activities.count_documents({})
        print(f"   Users: {user_count}")
        print(f"   Departments: {dept_count}")
        print(f"   Activities: {activity_count}")
        print("\n Default Login Credentials:")
        print("   Kailash Code: <REDACTED_kailash_code>")
        print("   Decode: <REDACTED_PASSWORD>")
        print("\n✨ ackend is ready for use!")
        
    except Exception as e:
        print(f"\n[AIL] Error during seeding: {e}")
        raise e
    finally:
        await MongoD.close_db()

if __name__ == "__main__":
    asyncio.run(seed_database())
