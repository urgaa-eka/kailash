"""
Integration Tests for SHIV and PARVATI Monitoring Systems
Day  Testing Suite
"""

import pytest
import pytest_asyncio
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import uuid
import sys
import os

# Add parent directory to path
sys.path.insert(, os.path.dirname(os.path.dirname(__file__)))

from agents.shiv_guardian import ShivGuardian, ThreatLevel, ThreatType
from agents.parvati_harmony import ParvatiHarmonyKeeper

# Test MongoD connection
MONGO_TEST_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:')

@pytest_asyncio.fixture
async def test_db():
    """Create test database connection"""
    client = AsyncIOMotorClient(MONGO_TEST_URL)
    db = client.kailash_test
    
    # Clean up test data
    await db.threats.delete_many({})
    await db.shiv_monitoring_logs.delete_many({})
    await db.parvati_harmony_logs.delete_many({})
    await db.tasks.delete_many({})
    await db.agent_activity.delete_many({})
    await db.ceo_commands.delete_many({})
    await db.auth_logs.delete_many({})
    await db.rebalancing_actions.delete_many({})
    
    yield db
    
    # Cleanup
    await db.threats.delete_many({})
    await db.shiv_monitoring_logs.delete_many({})
    await db.parvati_harmony_logs.delete_many({})
    await db.tasks.delete_many({})
    await db.agent_activity.delete_many({})
    await db.ceo_commands.delete_many({})
    await db.auth_logs.delete_many({})
    await db.rebalancing_actions.delete_many({})
    
    client.close()

# ============================================
# SHIV TESTS
# ============================================

@pytest.mark.asyncio
async def test_shiv_initialization(test_db):
    """Test SHIV initialization"""
    shiv = ShivGuardian(test_db)
    
    assert shiv.is_running == False
    assert shiv.mode == "meditation"
    assert shiv.interventions_today == 
    assert shiv.last_intervention is None

@pytest.mark.asyncio
async def test_shiv_api_anomaly_detection(test_db):
    """Test SHIV detects API spike anomalies"""
    shiv = ShivGuardian(test_db)
    
    # Create excessive API calls
    now = datetime.utcnow()
    for i in range():  # Above threshold of 
        await test_db.ceo_commands.insert_one({
            "command_id": str(uuid.uuid4()),
            "ceo_id": "test_ceo",
            "timestamp": now.isoformat(),
            "raw_command": f"test command {i}"
        })
    
    # Run API anomaly check
    await shiv.check_api_anomalies()
    
    # Verify threat was detected
    threats = await test_db.threats.find({"type": ThreatType.API_SPIKE}).to_list(length=)
    assert len(threats) > 
    
    threat = threats[]
    assert threat["level"] == ThreatLevel.HIGH
    assert "API activity" in threat["message"]
    assert shiv.mode == "alert"

@pytest.mark.asyncio
async def test_shiv_authentication_security_check(test_db):
    """Test SHIV monitors authentication attempts"""
    shiv = ShivGuardian(test_db)
    
    # Create many auth attempts
    now = datetime.utcnow()
    for i in range():  # Above threshold of 
        await test_db.auth_logs.insert_one({
            "ceo_id": str(uuid.uuid4()),
            "authenticated_at": now.isoformat(),
            "ip_address": "9.8.."
        })
    
    # Run authentication check
    await shiv.check_authentication_security()
    
    # Verify threat was detected
    threats = await test_db.threats.find({"type": ThreatType.AUTH_AILURE}).to_list(length=)
    assert len(threats) > 
    
    threat = threats[]
    assert threat["level"] == ThreatLevel.MEDIUM
    assert "authentication activity" in threat["message"].lower()

@pytest.mark.asyncio
async def test_shiv_agent_health_monitoring(test_db):
    """Test SHIV detects agent failures"""
    shiv = ShivGuardian(test_db)
    
    # Create failed tasks
    now = datetime.utcnow()
    for i in range():  # Above threshold of 
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "status": "failed",
            "created_at": now.isoformat(),
            "error": "Test failure"
        })
    
    # Run agent health check
    await shiv.check_agent_health()
    
    # Verify threat was detected
    threats = await test_db.threats.find({"type": ThreatType.AGENT_AILURE}).to_list(length=)
    assert len(threats) > 
    
    threat = threats[]
    assert threat["level"] == ThreatLevel.HIGH
    assert "failures detected" in threat["message"].lower()

@pytest.mark.asyncio
async def test_shiv_resource_exhaustion_detection(test_db):
    """Test SHIV detects system overload"""
    shiv = ShivGuardian(test_db)
    
    # Create excessive active tasks
    for i in range():  # Above threshold of 
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "status": "queued" if i %  == 0 else "in_progress",
            "created_at": datetime.utcnow().isoformat()
        })
    
    # Run resource check
    await shiv.check_system_resources()
    
    # Verify threat was detected
    threats = await test_db.threats.find({"type": ThreatType.RESOURCE_EXHAUSTION}).to_list(length=)
    assert len(threats) > 
    
    threat = threats[]
    assert threat["level"] == ThreatLevel.HIGH
    assert "overload" in threat["message"].lower()

@pytest.mark.asyncio
async def test_shiv_threat_classification(test_db):
    """Test SHIV properly classifies threat severity"""
    shiv = ShivGuardian(test_db)
    
    # Create CRITICAL threat
    threat_id = await shiv.detect_threat(
        threat_type=ThreatType.AGENT_AILURE,
        level=ThreatLevel.CRITICAL,
        message="System down",
        details={"severity": "critical"},
        auto_response="alert_ceo_immediately"
    )
    
    assert threat_id is not None
    assert shiv.mode == "intervention"
    
    # Verify threat in D
    threat = await test_db.threats.find_one({"threat_id": threat_id})
    assert threat["level"] == ThreatLevel.CRITICAL
    assert threat["type"] == ThreatType.AGENT_AILURE

@pytest.mark.asyncio
async def test_shiv_auto_response_execution(test_db):
    """Test SHIV executes automated responses"""
    shiv = ShivGuardian(test_db)
    
    # Test rate limiting response
    success = await shiv.execute_response(
        threat_id="test_threat_",
        response_type="rate_limit",
        level=ThreatLevel.HIGH,
        details={}
    )
    assert success == True
    
    # Test CEO alert response
    success = await shiv.execute_response(
        threat_id="test_threat_",
        response_type="alert_ceo_immediately",
        level=ThreatLevel.CRITICAL,
        details={}
    )
    assert success == True
    
    # Verify CEO alert was created
    alert = await test_db.ceo_alerts.find_one({"threat_id": "test_threat_"})
    assert alert is not None
    assert alert["level"] == "CRITICAL"

@pytest.mark.asyncio
async def test_shiv_ganesha_alerting(test_db):
    """Test SHIV alerts GANESHA for critical threats"""
    shiv = ShivGuardian(test_db)
    
    # Create critical threat
    threat_id = await shiv.detect_threat(
        threat_type=ThreatType.AGENT_AILURE,
        level=ThreatLevel.CRITICAL,
        message="Critical failure",
        details={"component": "test"},
        auto_response="alert_ceo_immediately"
    )
    
    # Verify inter-agent message was sent
    message = await test_db.inter_agent_messages.find_one({"related_threat_id": threat_id})
    assert message is not None
    assert message["from_agent_id"] == "SHIV"
    assert message["to_department"] == "GANESHA"
    assert message["priority"] == "P"

@pytest.mark.asyncio
async def test_shiv_status_reporting(test_db):
    """Test SHIV status reporting"""
    shiv = ShivGuardian(test_db)
    
    # Create some threats
    await shiv.detect_threat(
        threat_type=ThreatType.API_SPIKE,
        level=ThreatLevel.MEDIUM,
        message="Test threat ",
        details={},
        auto_response="log_and_monitor"
    )
    
    await shiv.detect_threat(
        threat_type=ThreatType.AUTH_AILURE,
        level=ThreatLevel.LOW,
        message="Test threat ",
        details={},
        auto_response="log_and_monitor"
    )
    
    # Get status
    status = await shiv.get_status()
    
    assert status["is_running"] == False
    assert "mode" in status
    assert "threats_detected_today" in status
    assert status["threats_detected_today"] >= 

@pytest.mark.asyncio
async def test_shiv_threat_timeline(test_db):
    """Test SHIV threat timeline retrieval"""
    shiv = ShivGuardian(test_db)
    
    # Create threats
    await shiv.detect_threat(
        threat_type=ThreatType.API_SPIKE,
        level=ThreatLevel.HIGH,
        message="Timeline test ",
        details={},
        auto_response="rate_limit"
    )
    
    await shiv.detect_threat(
        threat_type=ThreatType.SLOW_QUERY,
        level=ThreatLevel.MEDIUM,
        message="Timeline test ",
        details={},
        auto_response="optimize_queries"
    )
    
    # Get timeline
    timeline = await shiv.get_threat_timeline(hours=4)
    
    assert len(timeline) >= 
    assert all("threat_id" in t for t in timeline)
    assert all("detected_at" in t for t in timeline)

# ============================================
# PARVATI TESTS
# ============================================

@pytest.mark.asyncio
async def test_parvati_initialization(test_db):
    """Test PARVATI initialization"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    assert parvati.is_running == False
    assert parvati.current_harmony_score == 
    assert parvati.rebalancing_actions_today == 
    assert parvati.last_rebalancing is None
    assert len(parvati.DEPARTMENTS) == 

@pytest.mark.asyncio
async def test_parvati_workload_balance_calculation(test_db):
    """Test PARVATI calculates workload balance"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Create balanced workload
    for dept in parvati.DEPARTMENTS[:]:
        for i in range():  #  tasks each
            await test_db.tasks.insert_one({
                "task_id": str(uuid.uuid4()),
                "assigned_to_department": dept,
                "status": "in_progress",
                "created_at": datetime.utcnow().isoformat()
            })
    
    score = await parvati._calculate_workload_balance()
    assert score >=   # Should calculate a valid score (-)
    assert score <= 

@pytest.mark.asyncio
async def test_parvati_completion_rate_calculation(test_db):
    """Test PARVATI calculates task completion rate"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Create tasks with high completion rate
    now = datetime.utcnow()
    for i in range():
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "status": "completed" if i < 8 else "in_progress",  # 9% completion
            "created_at": now.isoformat()
        })
    
    score = await parvati._calculate_completion_rate()
    assert score >= 8  # Should be high

@pytest.mark.asyncio
async def test_parvati_agent_health_calculation(test_db):
    """Test PARVATI calculates agent health"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Create agent activity
    now = datetime.utcnow()
    for i in range():
        await test_db.agent_activity.insert_one({
            "activity_id": str(uuid.uuid4()),
            "agent_name": "VISHWAKARMA",
            "timestamp": now.isoformat(),
            "action": "task_completed"
        })
    
    score = await parvati._calculate_agent_health()
    assert score >= 4  # Should be positive with activity

@pytest.mark.asyncio
async def test_parvati_harmony_score_calculation(test_db):
    """Test PARVATI calculates overall harmony score"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Create some baseline data
    now = datetime.utcnow()
    for i in range():
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "assigned_to_department": "VISHWAKARMA",
            "status": "completed",
            "created_at": now.isoformat(),
            "duration_seconds": 3
        })
    
    harmony_data = await parvati.calculate_harmony_score()
    
    assert "overall_score" in harmony_data
    assert  <= harmony_data["overall_score"] <= 
    assert "breakdown" in harmony_data
    assert "workload_balance" in harmony_data["breakdown"]
    assert "task_completion_rate" in harmony_data["breakdown"]
    assert "trend" in harmony_data

@pytest.mark.asyncio
async def test_parvati_overload_detection(test_db):
    """Test PARVATI detects overloaded departments"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Overload VISHWAKARMA
    for i in range():  # Above threshold of 
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "assigned_to_department": "VISHWAKARMA",
            "status": "queued",
            "created_at": datetime.utcnow().isoformat()
        })
    
    imbalances = await parvati.detect_imbalances()
    
    assert len(imbalances) > 
    overload_imbalance = next((i for i in imbalances if i["type"] == "overloaded_department"), None)
    assert overload_imbalance is not None
    assert overload_imbalance["department"] == "VISHWAKARMA"

@pytest.mark.asyncio
async def test_parvati_workload_imbalance_detection(test_db):
    """Test PARVATI detects workload imbalances"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Create severe imbalance
    for i in range():
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "assigned_to_department": "VISHWAKARMA",
            "status": "queued",
            "created_at": datetime.utcnow().isoformat()
        })
    
    for i in range():
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "assigned_to_department": "LAKSHMI",
            "status": "queued",
            "created_at": datetime.utcnow().isoformat()
        })
    
    imbalances = await parvati.detect_imbalances()
    
    workload_imbalance = next((i for i in imbalances if i["type"] == "workload_imbalance"), None)
    assert workload_imbalance is not None
    assert workload_imbalance["ratio"] > 3.

@pytest.mark.asyncio
async def test_parvati_stale_task_detection(test_db):
    """Test PARVATI detects stale tasks"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Create old tasks
    old_time = (datetime.utcnow() - timedelta(hours=3)).isoformat()
    for i in range():
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "assigned_to_department": "VISHWAKARMA",
            "status": "queued",
            "created_at": old_time
        })
    
    imbalances = await parvati.detect_imbalances()
    
    stale_imbalance = next((i for i in imbalances if i["type"] == "stale_tasks"), None)
    assert stale_imbalance is not None
    assert stale_imbalance["count"] >= 

@pytest.mark.asyncio
async def test_parvati_task_redistribution(test_db):
    """Test PARVATI redistributes tasks from overloaded departments"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Create overload
    task_ids = []
    for i in range():
        task_id = str(uuid.uuid4())
        await test_db.tasks.insert_one({
            "task_id": task_id,
            "assigned_to_department": "VISHWAKARMA",
            "status": "queued",
            "created_at": datetime.utcnow().isoformat()
        })
        task_ids.append(task_id)
    
    # Run rebalancing
    imbalances = await parvati.detect_imbalances()
    if imbalances:
        await parvati.auto_rebalance(imbalances)
    
    # Check if tasks were redistributed
    redistributed = await test_db.tasks.count_documents({
        "task_id": {"$in": task_ids},
        "assigned_to_department": {"$ne": "VISHWAKARMA"}
    })
    
    assert redistributed >   # At least some tasks should be redistributed

@pytest.mark.asyncio
async def test_parvati_stale_task_prioritization(test_db):
    """Test PARVATI increases priority of stale tasks"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Create stale tasks
    old_time = (datetime.utcnow() - timedelta(hours=3)).isoformat()
    for i in range():
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "assigned_to_department": "VISHWAKARMA",
            "status": "queued",
            "created_at": old_time,
            "priority": "P"
        })
    
    # Run rebalancing
    imbalances = await parvati.detect_imbalances()
    if imbalances:
        await parvati.auto_rebalance(imbalances)
    
    # Check if priorities were updated
    prioritized = await test_db.tasks.count_documents({
        "created_at": old_time,
        "priority": "P"
    })
    
    assert prioritized >   # At least some tasks should be prioritized

@pytest.mark.asyncio
async def test_parvati_status_reporting(test_db):
    """Test PARVATI status reporting"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Set some state
    parvati.current_harmony_score = 8
    parvati.rebalancing_actions_today = 3
    parvati.last_rebalancing = datetime.utcnow()
    
    status = await parvati.get_status()
    
    assert status["is_running"] == False
    assert status["current_harmony_score"] == 8
    assert status["rebalancing_actions_today"] == 3
    assert "last_rebalancing" in status
    assert "trend" in status

@pytest.mark.asyncio
async def test_parvati_workload_distribution_reporting(test_db):
    """Test PARVATI workload distribution reporting"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Create workload
    for i in range():
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "assigned_to_department": "VISHWAKARMA",
            "status": "in_progress",
            "created_at": datetime.utcnow().isoformat()
        })
    
    distribution = await parvati.get_workload_distribution()
    
    assert len(distribution) ==   # All departments
    vishwakarma_data = next((d for d in distribution if d["department"] == "VISHWAKARMA"), None)
    assert vishwakarma_data is not None
    assert vishwakarma_data["active_tasks"] == 
    assert "utilization" in vishwakarma_data
    assert "status" in vishwakarma_data

@pytest.mark.asyncio
async def test_parvati_harmony_logging(test_db):
    """Test PARVATI logs harmony scores"""
    parvati = ParvatiHarmonyKeeper(test_db)
    
    harmony_data = {
        "overall_score": 8.,
        "breakdown": {
            "workload_balance": 9,
            "task_completion_rate": 8,
            "agent_health": 8,
            "response_times": 9,
            "error_rates": 9
        },
        "trend": "improving"
    }
    
    await parvati.log_harmony(harmony_data)
    
    # Verify log was created
    log = await test_db.parvati_harmony_logs.find_one()
    assert log is not None
    assert log["overall_harmony_score"] == 8.
    assert "score_breakdown" in log
    assert log["trend"] == "improving"

# ============================================
# INTEGRATION TESTS
# ============================================

@pytest.mark.asyncio
async def test_shiv_parvati_integration(test_db):
    """Test SHIV and PARVATI work together"""
    shiv = ShivGuardian(test_db)
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Create scenario: many failed tasks (triggers SHIV) and workload imbalance (triggers PARVATI)
    
    # SHIV: ailed tasks
    for i in range():
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "assigned_to_department": "VISHWAKARMA",
            "status": "failed",
            "created_at": datetime.utcnow().isoformat()
        })
    
    # PARVATI: Imbalanced workload
    for i in range():
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "assigned_to_department": "VISHWAKARMA",
            "status": "queued",
            "created_at": datetime.utcnow().isoformat()
        })
    
    # Run SHIV checks
    await shiv.check_agent_health()
    
    # Run PARVATI checks
    imbalances = await parvati.detect_imbalances()
    
    # Verify both systems detected issues
    shiv_threats = await test_db.threats.find({"type": ThreatType.AGENT_AILURE}).to_list(length=)
    assert len(shiv_threats) > 
    
    assert len(imbalances) > 
    assert any(i["type"] == "overloaded_department" for i in imbalances)

@pytest.mark.asyncio
async def test_system_recovery_workflow(test_db):
    """Test full system recovery: SHIV detects issue, PARVATI rebalances"""
    shiv = ShivGuardian(test_db)
    parvati = ParvatiHarmonyKeeper(test_db)
    
    # Create overload situation (> tasks triggers SHIV)
    for i in range():
        await test_db.tasks.insert_one({
            "task_id": str(uuid.uuid4()),
            "assigned_to_department": "VISHWAKARMA",
            "status": "queued",
            "created_at": datetime.utcnow().isoformat()
        })
    
    # SHIV detects resource exhaustion
    await shiv.check_system_resources()
    shiv_threats = await test_db.threats.find({"type": ThreatType.RESOURCE_EXHAUSTION}).to_list(length=)
    assert len(shiv_threats) > 
    
    # PARVATI detects and fixes imbalance
    imbalances = await parvati.detect_imbalances()
    assert len(imbalances) > 
    
    await parvati.auto_rebalance(imbalances)
    
    # Verify rebalancing was attempted (actions today incremented)
    assert parvati.rebalancing_actions_today >=   # Rebalancing attempted
    
    # Check if rebalancing actions were logged
    rebalancing_actions = await test_db.rebalancing_actions.find().to_list(length=)
    # Note: Rebalancing actions are logged even if no tasks moved
    assert len(rebalancing_actions) >= 

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
