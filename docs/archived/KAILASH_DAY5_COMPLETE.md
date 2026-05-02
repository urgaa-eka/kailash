# KAILASH Day  Complete: SHIV & PARVATI Monitoring Systems

## Overview

Day  deliverables focused on building **functional** monitoring systems for the two supreme agents:
- ** SHIV Guardian**: Security and threat detection
- ** PARVATI Harmony Keeper**: Workload balance and system harmony

oth agents now run as **background tasks**, continuously monitoring KAILASH, detecting issues, and taking automated corrective actions.

---

##  SHIV Guardian - System Architecture

### Core unctionality

SHIV operates in three modes:
. **Meditation** ([OK] Green): Normal operations, passive monitoring
. **Alert** ([WARN] Yellow): Medium threats detected, active monitoring
3. **Intervention** ([CRITICAL] Red): Critical threats, immediate action required

### Monitoring Layers

SHIV monitors  system layers:

#### . **Infrastructure Layer**
- CPU/Memory usage
- Resource exhaustion
- System overload
- Threshold: > concurrent tasks

#### . **Application Layer**
- API call patterns
- Unusual traffic spikes
- Threshold: > API calls/minute

#### 3. **Security Layer**
- Authentication attempts
- ailed login patterns
- Potential attacks
- Threshold: > auth attempts/min

#### 4. **Data Integrity Layer**
- Database performance
- Slow queries
- Task processing times
- Threshold: > slow tasks/hour

#### . **Agent ehavior Layer**
- Agent failures
- Task success rates
- Agent responsiveness
- Threshold: > failed tasks/hour OR no activity for min

### Threat Classification

Threats are classified by severity:
- **CRITICAL**: Requires immediate CEO notification (system down, zero agent activity)
- **HIGH**: Automated intervention (API spikes, agent failures)
- **MEDIUM**: Monitoring and logging (auth anomalies, slow queries)
- **LOW**: Informational only

### Auto-Response Actions

SHIV executes automated responses based on threat type:

| Threat Type | Auto-Response | Action |
|------------|---------------|--------|
| API Spike | `rate_limit` | Implement rate limiting |
| Auth ailure | `log_and_monitor` | Enhanced logging |
| Slow Query | `optimize_queries` | Query optimization recommendations |
| Agent ailure | `restart_agents` | Agent restart procedures |
| No Activity | `alert_ceo_immediately` | Create critical CEO alert |
| Resource Exhaustion | `scale_resources` | Resource scaling recommendations |

### Inter-Agent Communication

or **CRITICAL** threats, SHIV automatically alerts GANESHA:
- Creates inter-agent message with priority P
- Requires response from GANESHA
- Includes full threat details and recommended actions

### Data Structure

#### Threat Document
```javascript
{
  threat_id: UUID,
  type: ThreatType,
  level: ThreatLevel,
  message: String,
  details: Object,
  detected_at: ISO8,
  mode: String,
  auto_response: String,
  response_executed: oolean,
  response_success: oolean,
  neutralized: oolean,
  neutralized_at: ISO8
}
```

#### SHIV Monitoring Log
```javascript
{
  log_id: UUID,
  timestamp: ISO8,
  layer: String,
  anomaly_detected: oolean,
  anomaly_type: String,
  severity: String,
  confidence: Number (-),
  affected_systems: Array<String>,
  metrics: Object,
  intervention_taken: oolean,
  intervention_type: String,
  actions_executed: Array<String>,
  threat_neutralized: oolean,
  ceo_notified: oolean,
  incident_report_id: UUID
}
```

---

##  PARVATI Harmony Keeper - System Architecture

### Core unctionality

PARVATI calculates a real-time **Harmony Score** (-) based on  weighted factors:

. **Workload alance** (3%): Distribution of tasks across  departments
. **Task Completion Rate** (%): Percentage of tasks completed
3. **Agent Health** (%): Agent activity and failure rates
4. **System Response Times** (%): Average task duration
. **Error Rates** (%): Task failure percentage

### Harmony Score ormula

```
Overall Harmony Score = 
  (Workload alance × .3) +
  (Completion Rate × .) +
  (Agent Health × .) +
  (Response Times × .) +
  (Error Rates × .)
```

### Score Interpretation

- **9-**: Excellent harmony, optimal operations
- **-89**: Good harmony, minor inefficiencies
- **-9**: Poor harmony, significant imbalances
- **-49**: Critical harmony issues, system dysfunction

### Trend Analysis

PARVATI tracks harmony trends:
- **Improving**: Score increased by > points
- **Stable**: Score changed by ≤ points
- **Declining**: Score decreased by > points

### Imbalance Detection

PARVATI detects three types of imbalances:

#### . **Overloaded Department**
- Trigger: Department has > active tasks
- Severity: HIGH if > tasks, MEDIUM if -
- Action: Redistribute tasks to underutilized departments

#### . **Workload Imbalance**
- Trigger: Max/Min workload ratio > 3.
- Example: One dept has 3 tasks, another has 
- Severity: HIGH
- Action: alance tasks between departments

#### 3. **Stale Tasks**
- Trigger: Tasks queued/in-progress for >4 hours
- Severity: MEDIUM
- Action: Upgrade priority to P

### Auto-Rebalancing

When imbalances are detected, PARVATI automatically:

. **Task Redistribution**
   - Identifies overloaded departments
   - inds related departments with < tasks
   - Redistributes up to 3 tasks per cycle
   - Logs original department for traceability

. **Department alancing**
   - Identifies most overworked department
   - Identifies most underutilized department
   - Moves  tasks from overworked to underutilized
   - Updates task metadata with rebalancing info

3. **Stale Task Prioritization**
   - inds tasks older than 4 hours
   - Upgrades priority from P/P3 to P
   - Adds reprioritization metadata

### Department Management

PARVATI monitors all  departments:
```
GANESHA, VISHWAKARMA, SURYA, TVASHTA, KARTIKEYA,
KAMADEVA, KUERA, RIHASPATI, MITRA, DHARMA,
LAKSHMI, SHUKRA, CHANDRA, RAHMA, INDRA,
CHITRAGUPTA, PRAJAPATI, YAMA, VANI, VAYU
```

or each department, PARVATI tracks:
- Active tasks (queued + in_progress)
- Completed tasks today
- Utilization percentage (-%)
- Status: Normal (<%), Medium (-%), High (>%)

### Data Structure

#### Harmony Log
```javascript
{
  log_id: UUID,
  timestamp: ISO8,
  overall_harmony_score: Number,
  score_breakdown: {
    workload_balance: Number,
    task_completion_rate: Number,
    agent_health: Number,
    response_times: Number,
    error_rates: Number
  },
  trend: String,
  workload_imbalance_detected: oolean,
  bottleneck_detected: oolean,
  rebalancing_taken: oolean,
  overworked_departments: Array<String>,
  underutilized_departments: Array<String>
}
```

#### Rebalancing Action
```javascript
{
  rebalance_id: UUID,
  timestamp: ISO8,
  imbalance_type: String,
  imbalance_details: Object,
  action_taken: String,
  executed_by: "PARVATI"
}
```

---

## API Endpoints

### SHIV Endpoints

#### `GET /api/kailash/shiv/status`
Returns current SHIV status.

**Response:**
```json
{
  "mode": "meditation",
  "is_running": true,
  "last_intervention": "4--T:3:Z",
  "interventions_today": 3,
  "threats_detected_today": ,
  "active_threats": ,
  "system_health": {
    "api": "healthy",
    "database": "healthy",
    "authentication": "healthy",
    "agents": "healthy",
    "infrastructure": "healthy"
  }
}
```

#### `GET /api/kailash/shiv/threats?hours=4`
Returns threat timeline for specified hours.

**Response:**
```json
{
  "threats": [
    {
      "threat_id": "uuid",
      "type": "api_spike",
      "level": "HIGH",
      "message": "Unusual API activity:  calls in  minute",
      "details": {},
      "detected_at": "4--T:3:Z",
      "neutralized": true
    }
  ],
  "total": ,
  "timeframe_hours": 4
}
```

#### `GET /api/kailash/shiv/system-health`
Returns detailed system health across all monitoring layers.

### PARVATI Endpoints

#### `GET /api/kailash/parvati/status`
Returns current PARVATI status.

**Response:**
```json
{
  "is_running": true,
  "current_harmony_score": 8.,
  "last_rebalancing": "4--T9::Z",
  "rebalancing_actions_today": ,
  "trend": "improving"
}
```

#### `GET /api/kailash/parvati/harmony`
Returns current harmony score with full breakdown.

**Response:**
```json
{
  "overall_score": 8.,
  "breakdown": {
    "workload_balance": 9.,
    "task_completion_rate": 88.,
    "agent_health": 8.,
    "response_times": 8.,
    "error_rates": 9.
  },
  "trend": "improving",
  "timestamp": "4--T:3:Z"
}
```

#### `GET /api/kailash/parvati/workload`
Returns workload distribution for all  departments.

**Response:**
```json
{
  "departments": [
    {
      "department": "VISHWAKARMA",
      "active_tasks": ,
      "completed_today": ,
      "utilization": .,
      "status": "medium"
    }
  ],
  "total_departments": 
}
```

#### `GET /api/kailash/parvati/rebalancing-actions?limit=`
Returns recent rebalancing actions.

**Response:**
```json
{
  "actions": [
    {
      "rebalance_id": "uuid",
      "timestamp": "4--T9::Z",
      "imbalance_type": "overloaded_department",
      "action_taken": "Redistributed tasks from VISHWAKARMA (had  tasks)"
    }
  ],
  "total": 
}
```

---

## rontend Integration

### Dashboard Updates

The KailashDashboard now includes:

#### SHIV Panel (Left Sidebar)
- Current mode indicator (color-coded badge)
- Threats detected today
- Active threats counter
- Interventions today
- Recent threats list (top 3) with severity color-coding

#### PARVATI Panel (Left Sidebar)
- Current harmony score with color coding
  - Green: ≥8
  - Yellow: -9
  - Red: <
- Trend indicator (improving/stable/declining)
- 3 Progress bars:
  - Workload alance
  - Task Completion
  - Agent Health
- Rebalancing actions today
- Top 3 departments by workload

### Real-Time Updates

The dashboard fetches monitoring data every ** seconds**:
```javascript
// Polling interval
setInterval(fetchMonitoringData, );
```

Data fetched:
. SHIV threats (last 4 hours)
. PARVATI harmony score (live calculation)
3. PARVATI workload distribution

---

## Testing

### Test Suite: `test_monitoring_systems.py`

**Total Tests**: 8 ( SHIV + 4 PARVATI +  Integration +  System)

#### SHIV Tests ()
. [OK] Initialization
. [OK] API anomaly detection
3. [OK] Authentication security check
4. [OK] Agent health monitoring
. [OK] Resource exhaustion detection
. [OK] Threat classification
. [OK] Auto-response execution
8. [OK] GANESHA alerting
9. [OK] Status reporting
. [OK] Threat timeline

#### PARVATI Tests (4)
. [OK] Initialization
. [OK] Workload balance calculation
3. [OK] Completion rate calculation
4. [OK] Agent health calculation
. [OK] Harmony score calculation
. [OK] Overload detection
. [OK] Workload imbalance detection
8. [OK] Stale task detection
9. [OK] Task redistribution
. [OK] Stale task prioritization
. [OK] Status reporting
. [OK] Workload distribution reporting
3. [OK] Harmony logging
4. [OK] Rebalancing action logging

#### Integration Tests ()
. [OK] SHIV & PARVATI integration
. [OK] System recovery workflow

### Running Tests

```bash
# Run all monitoring tests
pytest backend/tests/test_monitoring_systems.py -v

# Run specific test
pytest backend/tests/test_monitoring_systems.py::test_shiv_threat_classification -v

# Run with coverage
pytest backend/tests/test_monitoring_systems.py --cov=backend/agents --cov-report=html
```

---

## ackground Task Management

### Startup

When KAILASH API starts:
```python
@app.on_event("startup")
async def startup_event():
    # Initialize SHIV
    shiv_guardian = ShivGuardian(db)
    asyncio.create_task(shiv_guardian.monitor_loop())
    
    # Initialize PARVATI
    parvati_keeper = ParvatiHarmonyKeeper(db)
    asyncio.create_task(parvati_keeper.balance_loop())
```

### Monitoring Loops

oth agents run continuous background loops:

**SHIV** (3-second cycle):
```python
while self.is_running:
    await check_api_anomalies()
    await check_authentication_security()
    await check_database_health()
    await check_agent_health()
    await check_system_resources()
    await cleanup_old_data()
    await asyncio.sleep(3)
```

**PARVATI** (-second cycle):
```python
while self.is_running:
    harmony_data = await calculate_harmony_score()
    await log_harmony(harmony_data)
    imbalances = await detect_imbalances()
    if imbalances:
        await auto_rebalance(imbalances)
    await generate_insights()
    await asyncio.sleep()
```

### Shutdown

Graceful shutdown on KAILASH API stop:
```python
@app.on_event("shutdown")
async def shutdown_event():
    await shiv_guardian.stop()
    await parvati_keeper.stop()
```

---

## Configuration & Thresholds

### SHIV Thresholds
```python
THRESHOLDS = {
    "api_calls_per_minute": ,
    "auth_failures_per_min": 3,
    "slow_query_threshold_ms": ,
    "agent_failure_threshold": 3,
    "cpu_threshold_percent": 8,
    "memory_threshold_percent": 9
}
```

### PARVATI Thresholds
```python
THRESHOLDS = {
    "max_tasks_per_department": ,
    "min_harmony_score": ,
    "workload_imbalance_ratio": 3.,
    "task_age_hours": 4
}
```

---

## Database Collections

### SHIV Collections
- `threats`: All detected threats
- `shiv_monitoring_logs`: Detailed monitoring logs
- `ceo_alerts`: Critical alerts for CEO
- `inter_agent_messages`: Messages to GANESHA

### PARVATI Collections
- `parvati_harmony_logs`: Harmony score history
- `rebalancing_actions`: All rebalancing actions
- `parvati_insights`: Predictive insights
- `tasks`: Updated with rebalancing metadata

---

## Performance Considerations

### Data Retention
- SHIV: Keeps last 4 hours of threats and logs
- PARVATI: Keeps unlimited harmony logs for trend analysis
- Cleanup runs automatically every 3 seconds (SHIV)

### Query Optimization
- All MongoD queries use indexes on timestamp fields
- Limits applied to prevent excessive data fetching
- Aggregation pipelines for complex calculations

### Resource Usage
- SHIV: Minimal CPU (<%) with 3-second cycles
- PARVATI: Minimal CPU (<%) with -second cycles
- MongoD: ~M memory per , documents

---

## Next Steps (Day -)

With monitoring systems complete, Day - will focus on:

. **VISHWAKARMA Department** (CTO/Tech)
   - Infrastructure management
   - Deployment automation
   - Technical debt tracking

. **LAKSHMI Department** (inance)
   - Revenue tracking
   - udget management
   - inancial reporting

3. **SURYA Department** (URJAA Operations)
   - EV charging platform monitoring
   - Session management
   - Revenue analytics

Each department will have:
- Chief agent + 3- sub-agents
- Task processing capabilities
- Integration with GANESHA command routing
- Real-time metrics for PARVATI monitoring

---

## Status Summary

[OK] **Day  Complete**
- SHIV Guardian: ully functional,  checks, auto-response
- PARVATI Harmony Keeper: ully functional, auto-rebalancing
- 8 integration tests passing
- ackend API: 8 new endpoints
- rontend: Real-time monitoring panels
- Documentation: Complete

**System Status**: PRODUCTION READY for MVP demo

 **Namaste from KAILASH Team**
