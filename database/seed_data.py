#!/usr/bin/env python3
"""
Data seeding script for Kailash
Seeds the database with:
1. Initial user (Vivek with Kailash Code <REDACTED_kailash_code>)
2. All 20 departments from frontend data
3. Sample activities
"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend/ to path so `app.*` imports resolve (this script now lives
# under database/, a sibling of backend/, not backend/scripts/ anymore)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.core.mongodb import MongoD
from app.core.security import get_password_hash
from app.models.user import User
from app.models.department import Department, SubAgent
from app.models.activity import Activity

# Department data sourced from frontend/src/data/departmentsData.js
# (regenerated 2026-07-31: the prior copy of this literal in this file had
# every 'B', 'F', '0' and '1' character stripped by a broken redaction pass
# upstream -- restored from the frontend source of truth instead of guessed)
DEPARTMENTS_DATA = [
    {
        "id": "ganesha", "name": "GANESHA", "chief": "Lord Ganesha",
        "role": "Executive Assistant & Obstacle Remover", "tier": "Executive",
        "color": "#FFD700", "status": "active", "workload": 78,
        "active_tasks": 15, "completed_today": 7,
        "description": "Coordinates all departments, removes obstacles, processes CEO commands",
        "responsibilities": ["Natural language command processing", "Task routing and assignment", "Department coordination", "Obstacle identification and removal"],
        "ai_tools": ["Claude API", "Command Parser", "Task Router"],
        "k_location": "/oversight/ganesha/",
        "sub_agents": [
            {"name": "Command Parser", "role": "Natural language understanding", "status": "active", "workload": 82, "tasks": 5},
            {"name": "Task Router", "role": "Intelligent task distribution", "status": "active", "workload": 75, "tasks": 6},
            {"name": "Priority Manager", "role": "Task prioritization", "status": "active", "workload": 68, "tasks": 4},
            {"name": "Obstacle Detector", "role": "Identifies and removes blockers", "status": "active", "workload": 71, "tasks": 3}
        ]
    },
    {
        "id": "vishwakarma", "name": "VISHWAKARMA", "chief": "Lord Vishwakarma",
        "role": "Chief Technology Officer", "tier": "Executive",
        "color": "#4F46E5", "status": "active", "workload": 85,
        "active_tasks": 18, "completed_today": 9,
        "description": "Divine architect managing all technical infrastructure",
        "responsibilities": ["System architecture design", "Infrastructure management", "DevOps and automation", "Security implementation"],
        "ai_tools": ["GitHub Copilot", "Infrastructure Monitor", "Deploy Manager"],
        "k_location": "/oversight/vishwakarma/",
        "sub_agents": [
            {"name": "Infrastructure Manager", "role": "Server and cloud management", "status": "active", "workload": 88, "tasks": 7},
            {"name": "DevOps Specialist", "role": "CI/CD and automation", "status": "active", "workload": 82, "tasks": 6},
            {"name": "Security Engineer", "role": "Security protocols", "status": "active", "workload": 79, "tasks": 5}
        ]
    },
    {
        "id": "surya", "name": "SURYA", "chief": "Lord Surya",
        "role": "URJAA Head (Energy Solutions)", "tier": "Product",
        "color": "#F59E0B", "status": "active", "workload": 72,
        "active_tasks": 14, "completed_today": 8,
        "description": "Powers URJAA energy solutions and solar operations",
        "responsibilities": ["Solar energy analytics", "Energy trading platform", "Customer success", "Product development"],
        "ai_tools": ["Energy Predictor", "Trading Algorithm", "Customer Insights"],
        "k_location": "/oversight/surya/",
        "sub_agents": [
            {"name": "Solar Analytics", "role": "Energy data analysis", "status": "active", "workload": 76, "tasks": 5},
            {"name": "Trading Engine", "role": "Energy market optimization", "status": "active", "workload": 70, "tasks": 6},
            {"name": "Customer Success", "role": "Client relationship management", "status": "active", "workload": 68, "tasks": 3}
        ]
    },
    {
        "id": "tvashta", "name": "TVASHTA", "chief": "Lord Tvashta",
        "role": "Go4Garage Operations", "tier": "Product",
        "color": "#8B5CF6", "status": "active", "workload": 80,
        "active_tasks": 16, "completed_today": 10,
        "description": "Manages Go4Garage service platform and operations",
        "responsibilities": ["Service booking management", "Garage partner operations", "Quality assurance", "Customer experience"],
        "ai_tools": ["Booking Optimizer", "Partner Matcher", "Quality Checker"],
        "k_location": "/oversight/tvashta/",
        "sub_agents": [
            {"name": "Booking Manager", "role": "Service appointment scheduling", "status": "active", "workload": 83, "tasks": 6},
            {"name": "Partner Coordinator", "role": "Garage network management", "status": "active", "workload": 78, "tasks": 5},
            {"name": "Quality Inspector", "role": "Service quality monitoring", "status": "active", "workload": 81, "tasks": 5}
        ]
    },
    {
        "id": "kartikeya", "name": "KARTIKEYA", "chief": "Lord Kartikeya",
        "role": "IGNITION Mobile App", "tier": "Product",
        "color": "#EC4899", "status": "active", "workload": 74,
        "active_tasks": 12, "completed_today": 6,
        "description": "Leads IGNITION mobile platform development and user experience",
        "responsibilities": ["Mobile app development", "User experience design", "Feature rollout", "App performance"],
        "ai_tools": ["UX Analyzer", "Performance Monitor", "Feature Recommender"],
        "k_location": "/oversight/kartikeya/",
        "sub_agents": [
            {"name": "App Developer", "role": "Mobile development", "status": "active", "workload": 77, "tasks": 5},
            {"name": "UX Designer", "role": "User interface design", "status": "active", "workload": 72, "tasks": 4},
            {"name": "Performance Engineer", "role": "App optimization", "status": "active", "workload": 73, "tasks": 3}
        ]
    },
    {
        "id": "kamadeva", "name": "KAMADEVA", "chief": "Lord Kamadeva",
        "role": "Chief Marketing Officer", "tier": "Executive",
        "color": "#EF4444", "status": "active", "workload": 76,
        "active_tasks": 13, "completed_today": 8,
        "description": "Drives marketing strategy and brand presence",
        "responsibilities": ["Brand strategy", "Digital marketing", "Content creation", "Campaign management"],
        "ai_tools": ["Content Generator", "Campaign Analyzer", "Trend Predictor"],
        "k_location": "/oversight/kamadeva/",
        "sub_agents": [
            {"name": "Brand Manager", "role": "Brand identity and positioning", "status": "active", "workload": 79, "tasks": 5},
            {"name": "Digital Marketer", "role": "Online campaign execution", "status": "active", "workload": 75, "tasks": 4},
            {"name": "Content Creator", "role": "Marketing content production", "status": "active", "workload": 74, "tasks": 4}
        ]
    },
    {
        "id": "kubera", "name": "KUBERA", "chief": "Lord Kubera",
        "role": "Chief Sales Officer", "tier": "Executive",
        "color": "#10B981", "status": "active", "workload": 82,
        "active_tasks": 17, "completed_today": 11,
        "description": "Leads sales operations and revenue generation",
        "responsibilities": ["Sales strategy", "Revenue targets", "Client acquisition", "Sales team management"],
        "ai_tools": ["Lead Scorer", "Pipeline Manager", "Revenue Forecaster"],
        "k_location": "/oversight/kubera/",
        "sub_agents": [
            {"name": "Lead Generator", "role": "Prospect identification", "status": "active", "workload": 85, "tasks": 6},
            {"name": "Account Manager", "role": "Client relationship", "status": "active", "workload": 80, "tasks": 6},
            {"name": "Revenue Analyst", "role": "Sales performance tracking", "status": "active", "workload": 81, "tasks": 5}
        ]
    },
    {
        "id": "lakshmi", "name": "LAKSHMI", "chief": "Goddess Lakshmi",
        "role": "Chief Financial Officer", "tier": "Executive",
        "color": "#F59E0B", "status": "active", "workload": 79,
        "active_tasks": 14, "completed_today": 9,
        "description": "Manages financial operations and planning",
        "responsibilities": ["Financial planning", "Budget management", "Financial reporting", "Cash flow management"],
        "ai_tools": ["Financial Modeler", "Budget Optimizer", "Risk Analyzer"],
        "k_location": "/oversight/lakshmi/",
        "sub_agents": [
            {"name": "Budget Controller", "role": "Budget oversight", "status": "active", "workload": 82, "tasks": 5},
            {"name": "Financial Analyst", "role": "Financial reporting", "status": "active", "workload": 78, "tasks": 5},
            {"name": "Cash Manager", "role": "Cash flow optimization", "status": "active", "workload": 77, "tasks": 4}
        ]
    },
    {
        "id": "brihaspati", "name": "BRIHASPATI", "chief": "Lord Brihaspati",
        "role": "Investor Relations", "tier": "Executive",
        "color": "#3B82F6", "status": "active", "workload": 68,
        "active_tasks": 9, "completed_today": 5,
        "description": "Manages investor communications and relations",
        "responsibilities": ["Investor communications", "Fundraising", "Board relations", "Financial presentations"],
        "ai_tools": ["Pitch Generator", "Investor Tracker", "Valuation Modeler"],
        "k_location": "/oversight/brihaspati/",
        "sub_agents": [
            {"name": "Investor Manager", "role": "Investor engagement", "status": "active", "workload": 71, "tasks": 4},
            {"name": "Presentation Designer", "role": "Deck creation", "status": "active", "workload": 66, "tasks": 3},
            {"name": "Fundraising Lead", "role": "Capital raising", "status": "active", "workload": 67, "tasks": 2}
        ]
    },
    {
        "id": "mitra", "name": "MITRA", "chief": "Lord Mitra",
        "role": "Partnerships & Alliances", "tier": "Operations",
        "color": "#8B5CF6", "status": "active", "workload": 70,
        "active_tasks": 11, "completed_today": 6,
        "description": "Develops strategic partnerships and collaborations",
        "responsibilities": ["Partnership development", "Alliance management", "Collaboration frameworks", "Partnership ROI"],
        "ai_tools": ["Partner Matcher", "Deal Analyzer", "ROI Calculator"],
        "k_location": "/oversight/mitra/",
        "sub_agents": [
            {"name": "Partnership Manager", "role": "Partner relationship", "status": "active", "workload": 73, "tasks": 4},
            {"name": "Deal Negotiator", "role": "Contract negotiation", "status": "active", "workload": 69, "tasks": 4},
            {"name": "Integration Lead", "role": "Partnership integration", "status": "active", "workload": 68, "tasks": 3}
        ]
    },
    {
        "id": "dharma", "name": "DHARMA", "chief": "Lord Dharma",
        "role": "Government Relations", "tier": "Operations",
        "color": "#059669", "status": "active", "workload": 65,
        "active_tasks": 8, "completed_today": 4,
        "description": "Manages government affairs and regulatory compliance",
        "responsibilities": ["Government liaisons", "Policy advocacy", "Regulatory compliance", "Public affairs"],
        "ai_tools": ["Policy Tracker", "Compliance Monitor", "Regulation Analyzer"],
        "k_location": "/oversight/dharma/",
        "sub_agents": [
            {"name": "Policy Analyst", "role": "Policy research", "status": "active", "workload": 68, "tasks": 3},
            {"name": "Compliance Officer", "role": "Regulatory adherence", "status": "active", "workload": 64, "tasks": 3},
            {"name": "Liaison Coordinator", "role": "Government relations", "status": "active", "workload": 63, "tasks": 2}
        ]
    },
    {
        "id": "shukra", "name": "SHUKRA", "chief": "Lord Shukra",
        "role": "Chief Strategy Officer", "tier": "Executive",
        "color": "#6366F1", "status": "active", "workload": 73,
        "active_tasks": 12, "completed_today": 7,
        "description": "Defines corporate strategy and long-term planning",
        "responsibilities": ["Strategic planning", "Market analysis", "Competitive intelligence", "Business modeling"],
        "ai_tools": ["Strategy Simulator", "Market Analyzer", "Scenario Planner"],
        "k_location": "/oversight/shukra/",
        "sub_agents": [
            {"name": "Strategy Analyst", "role": "Strategic research", "status": "active", "workload": 76, "tasks": 4},
            {"name": "Market Researcher", "role": "Market intelligence", "status": "active", "workload": 72, "tasks": 4},
            {"name": "Business Modeler", "role": "Business case development", "status": "active", "workload": 71, "tasks": 4}
        ]
    },
    {
        "id": "chandra", "name": "CHANDRA", "chief": "Lord Chandra",
        "role": "Data & Analytics", "tier": "Operations",
        "color": "#06B6D4", "status": "active", "workload": 84,
        "active_tasks": 16, "completed_today": 10,
        "description": "Manages data infrastructure and analytics",
        "responsibilities": ["Data warehousing", "Analytics platform", "Business intelligence", "Data governance"],
        "ai_tools": ["Data Pipeline", "BI Dashboard", "Predictive Models"],
        "k_location": "/oversight/chandra/",
        "sub_agents": [
            {"name": "Data Engineer", "role": "Data infrastructure", "status": "active", "workload": 87, "tasks": 6},
            {"name": "Analytics Lead", "role": "Data analysis", "status": "active", "workload": 83, "tasks": 5},
            {"name": "BI Developer", "role": "Dashboard development", "status": "active", "workload": 82, "tasks": 5}
        ]
    },
    {
        "id": "brahma", "name": "BRAHMA", "chief": "Lord Brahma",
        "role": "Research & Development", "tier": "Operations",
        "color": "#F59E0B", "status": "active", "workload": 77,
        "active_tasks": 13, "completed_today": 8,
        "description": "Leads innovation and product research",
        "responsibilities": ["Technology research", "Product innovation", "Prototype development", "IP management"],
        "ai_tools": ["Research Assistant", "Patent Analyzer", "Innovation Tracker"],
        "k_location": "/oversight/brahma/",
        "sub_agents": [
            {"name": "Research Scientist", "role": "Technology research", "status": "active", "workload": 80, "tasks": 5},
            {"name": "Innovation Lead", "role": "New product concepts", "status": "active", "workload": 76, "tasks": 4},
            {"name": "Prototype Engineer", "role": "Prototype building", "status": "active", "workload": 75, "tasks": 4}
        ]
    },
    {
        "id": "indra", "name": "INDRA", "chief": "Lord Indra",
        "role": "Chief Operating Officer", "tier": "Executive",
        "color": "#EF4444", "status": "active", "workload": 86,
        "active_tasks": 19, "completed_today": 12,
        "description": "Oversees daily operations and execution",
        "responsibilities": ["Operations management", "Process optimization", "Resource allocation", "Performance monitoring"],
        "ai_tools": ["Operations Dashboard", "Process Optimizer", "Resource Planner"],
        "k_location": "/oversight/indra/",
        "sub_agents": [
            {"name": "Operations Manager", "role": "Daily operations", "status": "active", "workload": 89, "tasks": 7},
            {"name": "Process Engineer", "role": "Process improvement", "status": "active", "workload": 85, "tasks": 6},
            {"name": "Resource Coordinator", "role": "Resource management", "status": "active", "workload": 84, "tasks": 6}
        ]
    },
    {
        "id": "chitragupta", "name": "CHITRAGUPTA", "chief": "Lord Chitragupta",
        "role": "Quality Assurance", "tier": "Operations",
        "color": "#10B981", "status": "active", "workload": 71,
        "active_tasks": 10, "completed_today": 6,
        "description": "Ensures quality standards and testing",
        "responsibilities": ["Quality control", "Testing protocols", "Standards compliance", "Defect tracking"],
        "ai_tools": ["Test Automator", "Defect Tracker", "Quality Scorer"],
        "k_location": "/oversight/chitragupta/",
        "sub_agents": [
            {"name": "Test Engineer", "role": "Automated testing", "status": "active", "workload": 74, "tasks": 4},
            {"name": "Quality Analyst", "role": "Quality audits", "status": "active", "workload": 70, "tasks": 3},
            {"name": "Compliance Checker", "role": "Standards verification", "status": "active", "workload": 69, "tasks": 3}
        ]
    },
    {
        "id": "prajapati", "name": "PRAJAPATI", "chief": "Lord Prajapati",
        "role": "Product Management", "tier": "Operations",
        "color": "#8B5CF6", "status": "active", "workload": 78,
        "active_tasks": 14, "completed_today": 9,
        "description": "Manages product strategy and roadmap",
        "responsibilities": ["Product strategy", "Roadmap planning", "Feature prioritization", "User feedback"],
        "ai_tools": ["Roadmap Planner", "Feature Scorer", "User Insight"],
        "k_location": "/oversight/prajapati/",
        "sub_agents": [
            {"name": "Product Manager", "role": "Product strategy", "status": "active", "workload": 81, "tasks": 5},
            {"name": "Roadmap Lead", "role": "Roadmap planning", "status": "active", "workload": 77, "tasks": 5},
            {"name": "User Researcher", "role": "User feedback analysis", "status": "active", "workload": 76, "tasks": 4}
        ]
    },
    {
        "id": "yama", "name": "YAMA", "chief": "Lord Yama",
        "role": "Legal & Compliance", "tier": "Operations",
        "color": "#6B7280", "status": "active", "workload": 66,
        "active_tasks": 9, "completed_today": 5,
        "description": "Manages legal affairs and compliance",
        "responsibilities": ["Legal counsel", "Contract management", "Compliance oversight", "Risk mitigation"],
        "ai_tools": ["Contract Analyzer", "Compliance Checker", "Legal Research"],
        "k_location": "/oversight/yama/",
        "sub_agents": [
            {"name": "Legal Counsel", "role": "Legal advice", "status": "active", "workload": 69, "tasks": 3},
            {"name": "Contract Manager", "role": "Contract review", "status": "active", "workload": 65, "tasks": 3},
            {"name": "Compliance Lead", "role": "Regulatory compliance", "status": "active", "workload": 64, "tasks": 3}
        ]
    },
    {
        "id": "vani", "name": "VANI", "chief": "Goddess Vani",
        "role": "Content & Communications", "tier": "Operations",
        "color": "#EC4899", "status": "active", "workload": 75,
        "active_tasks": 12, "completed_today": 7,
        "description": "Creates content and manages communications",
        "responsibilities": ["Content strategy", "Internal communications", "External PR", "Editorial oversight"],
        "ai_tools": ["Content Generator", "PR Manager", "Communication Planner"],
        "k_location": "/oversight/vani/",
        "sub_agents": [
            {"name": "Content Writer", "role": "Content creation", "status": "active", "workload": 78, "tasks": 4},
            {"name": "Communications Lead", "role": "Internal comms", "status": "active", "workload": 74, "tasks": 4},
            {"name": "PR Manager", "role": "Public relations", "status": "active", "workload": 73, "tasks": 4}
        ]
    },
    {
        "id": "vayu", "name": "VAYU", "chief": "Lord Vayu",
        "role": "Sustainability & ESG", "tier": "Operations",
        "color": "#10B981", "status": "active", "workload": 64,
        "active_tasks": 7, "completed_today": 4,
        "description": "Manages sustainability initiatives and ESG",
        "responsibilities": ["Sustainability strategy", "Environmental impact", "Social responsibility", "ESG reporting"],
        "ai_tools": ["Carbon Tracker", "ESG Scorer", "Impact Analyzer"],
        "k_location": "/oversight/vayu/",
        "sub_agents": [
            {"name": "Sustainability Lead", "role": "Green initiatives", "status": "active", "workload": 67, "tasks": 3},
            {"name": "ESG Analyst", "role": "ESG metrics", "status": "active", "workload": 63, "tasks": 2},
            {"name": "Impact Coordinator", "role": "Social impact", "status": "active", "workload": 62, "tasks": 2}
        ]
    },
]

# Initial activities
INITIAL_ACTIVITIES = [
    {"type": "task_assigned", "message": "Task assigned to KAMADEVA", "department": "kamadeva"},
    {"type": "security_scan", "message": "SHIV: Security scan completed - All systems OK", "department": None},
    {"type": "rebalance", "message": "PARVATI rebalanced workload across departments", "department": None},
    {"type": "task_completed", "message": "Task completed by KUBERA", "department": "kubera"}
]

async def seed_database():
    """Main seeding function"""
    try:
        # Connect to MongoDB
        await MongoD.connect_db()
        db = MongoD.get_database()

        print("Starting database seeding...")

        # 1. Seed default user
        print("\nSeeding users...")
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

        # 2. Seed all 20 departments
        print("\nSeeding departments...")
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
        print("\nSeeding activities...")
        activity_count = await db.activities.count_documents({})
        if activity_count == 0:
            for act_data in INITIAL_ACTIVITIES:
                activity = Activity(**act_data)
                await db.activities.insert_one(activity.model_dump())
            print(f"   [OK] Created {len(INITIAL_ACTIVITIES)} initial activities")
        else:
            print(f"   ℹ️  Activities already exist ({activity_count} records)")

        # Summary
        print("\n" + "="*60)
        print("Database seeding completed successfully!")
        print("="*60)
        print("\nSummary:")
        user_count = await db.users.count_documents({})
        dept_count = await db.departments.count_documents({})
        activity_count = await db.activities.count_documents({})
        print(f"   Users: {user_count}")
        print(f"   Departments: {dept_count}")
        print(f"   Activities: {activity_count}")
        print("\nDefault Login Credentials:")
        print("   Kailash Code: <REDACTED_kailash_code>")
        print("   Decode: <REDACTED_PASSWORD>")
        print("\n✨ Backend is ready for use!")

    except Exception as e:
        print(f"\n[FAIL] Error during seeding: {e}")
        raise e
    finally:
        await MongoD.close_db()

if __name__ == "__main__":
    asyncio.run(seed_database())
