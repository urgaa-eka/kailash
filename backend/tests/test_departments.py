"""
Integration Tests for KAILASH Departments
Day - Testing Suite - VISHWAKARMA, LAKSHMI, SURYA
"""

import pytest
import pytest_asyncio
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid
import sys
import os

# Add parent directory to path
sys.path.insert(, os.path.dirname(os.path.dirname(__file__)))

from agents.dept_vishwakarma import VishwakarmaDepartment, MayaAgent, TvashtaAgent, RibhusAgent
from agents.dept_lakshmi import LakshmiDepartment, KuberaAgent, DhanvantariAgent, AlakshmiAgent
from agents.dept_surya import SuryaDepartment, AgniAgent, VayuAgent, ArunAgent

# Test MongoD connection
MONGO_TEST_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:')

@pytest_asyncio.fixture
async def test_db():
    """Create test database connection"""
    client = AsyncIOMotorClient(MONGO_TEST_URL)
    db = client.kailash_test_departments
    
    # Clean up test data
    await db.tasks.delete_many({})
    await db.agent_activity.delete_many({})
    await db.inter_agent_messages.delete_many({})
    
    yield db
    
    # Cleanup
    await db.tasks.delete_many({})
    await db.agent_activity.delete_many({})
    await db.inter_agent_messages.delete_many({})
    
    client.close()

# ============================================
# VISHWAKARMA DEPARTMENT TESTS
# ============================================

@pytest.mark.asyncio
async def test_vishwakarma_initialization(test_db):
    """Test VISHWAKARMA department initialization"""
    dept = VishwakarmaDepartment(test_db)
    
    assert dept.name == "VISHWAKARMA"
    assert dept.head_agent.name == "VISHWAKARMA"
    assert len(dept.sub_agents) == 3
    assert any(agent.name == "MAYA" for agent in dept.sub_agents)
    assert any(agent.name == "TVASHTA" for agent in dept.sub_agents)
    assert any(agent.name == "RIHUS" for agent in dept.sub_agents)

@pytest.mark.asyncio
async def test_maya_frontend_task(test_db):
    """Test MAYA executes frontend tasks"""
    maya = MayaAgent(test_db)
    
    task = {
        "command": "Improve dashboard loading speed",
        "focus": "frontend_ux"
    }
    
    result = await maya.execute_task(task)
    
    assert result["success"] == True
    assert result["agent"] == "MAYA"
    assert result["task_type"] == "frontend"
    assert "actions_taken" in result

@pytest.mark.asyncio
async def test_tvashta_backend_task(test_db):
    """Test TVASHTA executes backend tasks"""
    tvashta = TvashtaAgent(test_db)
    
    task = {
        "command": "Optimize MongoD queries for reports",
        "focus": "backend_api"
    }
    
    result = await tvashta.execute_task(task)
    
    assert result["success"] == True
    assert result["agent"] == "TVASHTA"
    assert result["task_type"] == "backend"

@pytest.mark.asyncio
async def test_ribhus_devops_task(test_db):
    """Test RIHUS executes DevOps tasks"""
    ribhus = RibhusAgent(test_db)
    
    task = {
        "command": "Set up backup automation",
        "focus": "infrastructure"
    }
    
    result = await ribhus.execute_task(task)
    
    assert result["success"] == True
    assert result["agent"] == "RIHUS"
    assert result["task_type"] == "devops"

@pytest.mark.asyncio
async def test_vishwakarma_task_delegation(test_db):
    """Test VISHWAKARMA delegates tasks correctly"""
    dept = VishwakarmaDepartment(test_db)
    
    task = {
        "command": "Improve dashboard performance",
        "priority": "P"
    }
    
    plan = await dept.analyze_and_delegate(task)
    
    assert "assignments" in plan
    assert len(plan["assignments"]) >= 
    # Should involve MAYA and TVASHTA for dashboard performance
    agents = [a["agent"] for a in plan["assignments"]]
    assert "MAYA" in agents or "TVASHTA" in agents

@pytest.mark.asyncio
async def test_vishwakarma_end_to_end(test_db):
    """Test complete VISHWAKARMA workflow"""
    dept = VishwakarmaDepartment(test_db)
    
    task = {
        "command": "Tech team, check system performance",
        "priority": "P"
    }
    
    task_id = await dept.receive_task(task)
    
    assert task_id is not None
    
    # Wait for processing
    await asyncio.sleep()
    
    # Check task in database
    task_doc = await test_db.tasks.find_one({"task_id": task_id})
    assert task_doc is not None
    assert task_doc["department"] == "VISHWAKARMA"

# ============================================
# LAKSHMI DEPARTMENT TESTS
# ============================================

@pytest.mark.asyncio
async def test_lakshmi_initialization(test_db):
    """Test LAKSHMI department initialization"""
    dept = LakshmiDepartment(test_db)
    
    assert dept.name == "LAKSHMI"
    assert dept.head_agent.name == "LAKSHMI"
    assert len(dept.sub_agents) == 3
    assert any(agent.name == "KUERA" for agent in dept.sub_agents)
    assert any(agent.name == "DHANVANTARI" for agent in dept.sub_agents)
    assert any(agent.name == "ALAKSHMI" for agent in dept.sub_agents)

@pytest.mark.asyncio
async def test_kubera_budget_task(test_db):
    """Test KUERA executes budget tasks"""
    kubera = KuberaAgent(test_db)
    
    task = {
        "command": "Review Q4 budget allocation",
        "focus": "budget_analysis"
    }
    
    result = await kubera.execute_task(task)
    
    assert result["success"] == True
    assert result["agent"] == "KUERA"
    assert result["task_type"] == "budget"
    assert "financial_data" in result

@pytest.mark.asyncio
async def test_dhanvantari_revenue_task(test_db):
    """Test DHANVANTARI executes revenue tasks"""
    dhanvantari = DhanvantariAgent(test_db)
    
    task = {
        "command": "Generate monthly revenue report",
        "focus": "revenue_analysis"
    }
    
    result = await dhanvantari.execute_task(task)
    
    assert result["success"] == True
    assert result["agent"] == "DHANVANTARI"
    assert result["task_type"] == "revenue"
    assert "revenue_data" in result

@pytest.mark.asyncio
async def test_alakshmi_cost_control_task(test_db):
    """Test ALAKSHMI executes cost optimization tasks"""
    alakshmi = AlakshmiAgent(test_db)
    
    task = {
        "command": "Identify cost reduction opportunities",
        "focus": "cost_optimization"
    }
    
    result = await alakshmi.execute_task(task)
    
    assert result["success"] == True
    assert result["agent"] == "ALAKSHMI"
    assert result["task_type"] == "cost_control"
    assert "savings_data" in result

@pytest.mark.asyncio
async def test_lakshmi_task_delegation(test_db):
    """Test LAKSHMI delegates tasks correctly"""
    dept = LakshmiDepartment(test_db)
    
    task = {
        "command": "Review our monthly burn rate",
        "priority": "P"
    }
    
    plan = await dept.analyze_and_delegate(task)
    
    assert "assignments" in plan
    assert len(plan["assignments"]) >= 
    # urn rate should involve KUERA and ALAKSHMI
    agents = [a["agent"] for a in plan["assignments"]]
    assert "KUERA" in agents or "ALAKSHMI" in agents

@pytest.mark.asyncio
async def test_lakshmi_end_to_end(test_db):
    """Test complete LAKSHMI workflow"""
    dept = LakshmiDepartment(test_db)
    
    task = {
        "command": "inance team, provide financial overview",
        "priority": "P"
    }
    
    task_id = await dept.receive_task(task)
    
    assert task_id is not None
    
    # Wait for processing
    await asyncio.sleep()
    
    # Check task in database
    task_doc = await test_db.tasks.find_one({"task_id": task_id})
    assert task_doc is not None
    assert task_doc["department"] == "LAKSHMI"

# ============================================
# SURYA DEPARTMENT TESTS
# ============================================

@pytest.mark.asyncio
async def test_surya_initialization(test_db):
    """Test SURYA department initialization"""
    dept = SuryaDepartment(test_db)
    
    assert dept.name == "SURYA"
    assert dept.head_agent.name == "SURYA"
    assert len(dept.sub_agents) == 3
    assert any(agent.name == "AGNI" for agent in dept.sub_agents)
    assert any(agent.name == "VAYU" for agent in dept.sub_agents)
    assert any(agent.name == "ARUN" for agent in dept.sub_agents)

@pytest.mark.asyncio
async def test_agni_station_task(test_db):
    """Test AGNI executes station management tasks"""
    agni = AgniAgent(test_db)
    
    task = {
        "command": "Check all charging station statuses",
        "focus": "station_management"
    }
    
    result = await agni.execute_task(task)
    
    assert result["success"] == True
    assert result["agent"] == "AGNI"
    assert result["task_type"] == "station_monitoring"
    assert "station_data" in result

@pytest.mark.asyncio
async def test_vayu_energy_task(test_db):
    """Test VAYU executes energy management tasks"""
    vayu = VayuAgent(test_db)
    
    task = {
        "command": "Optimize energy distribution",
        "focus": "energy_management"
    }
    
    result = await vayu.execute_task(task)
    
    assert result["success"] == True
    assert result["agent"] == "VAYU"
    assert result["task_type"] == "energy_management"
    assert "energy_data" in result

@pytest.mark.asyncio
async def test_arun_monitoring_task(test_db):
    """Test ARUN executes monitoring tasks"""
    arun = ArunAgent(test_db)
    
    task = {
        "command": "Monitor all stations in real-time",
        "focus": "monitoring"
    }
    
    result = await arun.execute_task(task)
    
    assert result["success"] == True
    assert result["agent"] == "ARUN"
    assert result["task_type"] == "monitoring"
    assert "monitoring_data" in result

@pytest.mark.asyncio
async def test_surya_task_delegation(test_db):
    """Test SURYA delegates tasks correctly"""
    dept = SuryaDepartment(test_db)
    
    task = {
        "command": "Status of all charging stations",
        "priority": "P"
    }
    
    plan = await dept.analyze_and_delegate(task)
    
    assert "assignments" in plan
    assert len(plan["assignments"]) >= 
    # Station status should involve AGNI and ARUN
    agents = [a["agent"] for a in plan["assignments"]]
    assert "AGNI" in agents or "ARUN" in agents

@pytest.mark.asyncio
async def test_surya_end_to_end(test_db):
    """Test complete SURYA workflow"""
    dept = SuryaDepartment(test_db)
    
    task = {
        "command": "URJAA team, provide operations status",
        "priority": "P"
    }
    
    task_id = await dept.receive_task(task)
    
    assert task_id is not None
    
    # Wait for processing
    await asyncio.sleep()
    
    # Check task in database
    task_doc = await test_db.tasks.find_one({"task_id": task_id})
    assert task_doc is not None
    assert task_doc["department"] == "SURYA"

# ============================================
# INTEGRATION TESTS
# ============================================

@pytest.mark.asyncio
async def test_all_departments_initialized(test_db):
    """Test all 3 departments can be initialized simultaneously"""
    vishwakarma = VishwakarmaDepartment(test_db)
    lakshmi = LakshmiDepartment(test_db)
    surya = SuryaDepartment(test_db)
    
    assert vishwakarma.name == "VISHWAKARMA"
    assert lakshmi.name == "LAKSHMI"
    assert surya.name == "SURYA"
    
    # Total: 3 departments,  agents
    total_agents = len(vishwakarma.sub_agents) + len(lakshmi.sub_agents) + len(surya.sub_agents)
    assert total_agents == 9  # 3 sub-agents per department

@pytest.mark.asyncio
async def test_parallel_department_execution(test_db):
    """Test multiple departments can process tasks in parallel"""
    vishwakarma = VishwakarmaDepartment(test_db)
    lakshmi = LakshmiDepartment(test_db)
    surya = SuryaDepartment(test_db)
    
    # Send tasks to all departments simultaneously
    tasks = await asyncio.gather(
        vishwakarma.receive_task({"command": "Check system performance", "priority": "P"}),
        lakshmi.receive_task({"command": "Review budget", "priority": "P"}),
        surya.receive_task({"command": "Check stations", "priority": "P"})
    )
    
    assert len(tasks) == 3
    assert all(task_id is not None for task_id in tasks)

@pytest.mark.asyncio
async def test_department_status_reporting(test_db):
    """Test all departments can report their status"""
    vishwakarma = VishwakarmaDepartment(test_db)
    lakshmi = LakshmiDepartment(test_db)
    surya = SuryaDepartment(test_db)
    
    statuses = await asyncio.gather(
        vishwakarma.get_status(),
        lakshmi.get_status(),
        surya.get_status()
    )
    
    assert len(statuses) == 3
    for status in statuses:
        assert "name" in status
        assert "head_agent" in status
        assert "sub_agents" in status
        assert "active_tasks" in status
        assert status["status"] == "active"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
