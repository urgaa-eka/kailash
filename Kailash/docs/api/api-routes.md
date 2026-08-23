# KAILASH API ROUTE SPECIICATIONS

**ase URL**: `/api/kailash`

**Authentication**: All routes require CEO Key verification

---

##  AUTHENTICATION

### POST `/api/kailash/auth/verify-ceo-key`
Verify CEO authentication key

**Request**:
```json
{
  "ceo_key": "494"
}
```

**Response (Success)**:
```json
{
  "success": true,
  "session_token": "jwt-token-here",
  "expires_in": 84,
  "ceo_id": "uuid",
  "message": "CEO authenticated successfully"
}
```

**Response (ailure)**:
```json
{
  "success": false,
  "error": "Invalid CEO key"
}
```

---

##  GANESHA - CEO COMMAND INTERACE

### POST `/api/kailash/ganesha/command`
Submit a command to GANESHA

**Headers**:
```
Authorization: earer {session_token}
```

**Request**:
```json
{
  "command": "Show me yesterday's revenue for URJAA",
  "context": {
    "previous_commands": ["array of recent commands for context"],
    "current_focus": "string, optional"
  }
}
```

**Response**:
```json
{
  "success": true,
  "command_id": "uuid",
  "interpreted_command": {
    "intent": "retrieve_revenue_data",
    "entities": {
      "product": "URJAA",
      "time_period": "yesterday",
      "metric": "revenue"
    },
    "priority": "P",
    "departments_involved": ["SURYA", "LAKSHMI", "CHANDRA"],
    "estimated_time": "- minutes"
  },
  "status": "processing",
  "message": "I understand. etching yesterday's URJAA revenue. I've asked SURYA, LAKSHMI, and CHANDRA to collaborate. I'll notify you when ready.",
  "ganesha_response": "On it! I'm coordinating with SURYA (URJAA), LAKSHMI (inance), and CHANDRA (Analytics) to compile this data. Expected in 3 minutes."
}
```

---

### GET `/api/kailash/ganesha/command/:command_id`
Get status of a specific command

**Response**:
```json
{
  "command_id": "uuid",
  "status": "completed",
  "result": {
    "success": true,
    "data": {
      "urjaa_revenue_yesterday": 4,
      "currency": "INR",
      "date": "--",
      "breakdown": {
        "charging_sessions": 4,
        "average_transaction": 9.4,
        "peak_hours": "PM-9PM"
      }
    },
    "generated_by": ["SURYA", "LAKSHMI", "CHANDRA"],
    "quality_checked": true,
    "approved_by": "CHITRAGUPTA"
  },
  "execution_time_seconds": ,
  "timestamp_completed": "--T:34:Z"
}
```

---

### GET `/api/kailash/ganesha/commands/recent`
Get recent CEO commands

**Query Parameters**:
- `limit` (optional, default: )
- `status` (optional: pending | in_progress | completed | failed)

**Response**:
```json
{
  "commands": [
    {
      "command_id": "uuid",
      "raw_command": "Show me yesterday's revenue",
      "status": "completed",
      "timestamp": "ISODate",
      "execution_time_seconds": 
    }
  ],
  "total": 4,
  "page": 
}
```

---

##  DASHOARD DATA

### GET `/api/kailash/dashboard/overview`
Get CEO dashboard overview

**Response**:
```json
{
  "timestamp": "ISODate",
  "system_health": {
    "status": "green",
    "uptime_percentage": 99.98,
    "active_agents": 8,
    "offline_agents": ,
    "active_tasks": 3,
    "completed_today": 
  },
  "shiv_status": {
    "mode": "meditation",
    "last_intervention": " days ago",
    "threats_today": ,
    "threats_neutralized_this_month": 
  },
  "parvati_status": {
    "harmony_score": 9,
    "trend": "improving",
    "last_rebalancing": "4 hours ago",
    "rebalancing_actions_today": 
  },
  "business_metrics": {
    "urjaa": {
      "revenue_today": 8,
      "sessions_today": 4,
      "active_stations": 4
    },
    "go4garage": {
      "bookings_today": ,
      "revenue_today": 8
    },
    "ignition": {
      "active_users": 34,
      "new_installs_today": 34
    }
  },
  "urgent_items": [
    {
      "type": "approval_needed",
      "task_id": "uuid",
      "title": "Partnership proposal from DISCOM Delhi",
      "department": "MITRA",
      "priority": "P"
    }
  ]
}
```

---

### GET `/api/kailash/dashboard/briefing/latest`
Get latest CEO briefing

**Query Parameters**:
- `type` (optional: morning | midday | evening)

**Response**:
```json
{
  "briefing_id": "uuid",
  "briefing_type": "morning",
  "timestamp": "--T8::Z",
  "summary": "Good morning! System health is excellent. All  departments operational.  tasks completed yesterday with 9% harmony score. URJAA revenue up % vs yesterday.  items need your attention.",
  "system_health": { /* same as dashboard overview */ },
  "tasks_completed_yesterday": ,
  "tasks_pending": 3,
  "urgent_items": [ /* array */ ],
  "department_highlights": [
    {
      "department": "KAMADEVA",
      "achievement": "Campaign generated 34 leads",
      "metric": "+4% vs last week"
    }
  ],
  "tomorrow_focus": [
    " AM: DISCOM Delhi partnership call",
    "URJAA v. feature development continues",
    "Q3 financial report finalization"
  ]
}
```

---

##  DEPARTMENTS & AGENTS

### GET `/api/kailash/departments`
Get all departments

**Response**:
```json
{
  "departments": [
    {
      "department_id": "uuid",
      "name": "GANESHA - Executive Assistant",
      "chief_deity": "GANESHA (गणेश)",
      "tier": "TIER_",
      "status": "active",
      "health_score": 98,
      "active_tasks": ,
      "capacity_utilization": .4,
      "sub_agents_count": 
    }
  ],
  "total": ,
  "by_tier": {
    "SUPREME": ,
    "TIER_": ,
    "TIER_": ,
    "TIER_3": 4,
    "TIER_4": 4,
    "TIER_": 
  }
}
```

---

### GET `/api/kailash/departments/:department_id`
Get specific department details

**Response**:
```json
{
  "department_id": "uuid",
  "name": "GANESHA - Executive Assistant",
  "chief_deity": "GANESHA (गणेश)",
  "chief_agent": {
    "agent_id": "uuid",
    "name": "GANESHA",
    "status": "active",
    "current_task": "Processing CEO command #4"
  },
  "sub_agents": [
    {
      "agent_id": "uuid",
      "name": "SARASWATI",
      "role": "Command Interpreter",
      "status": "active",
      "workload": 
    }
  ],
  "responsibilities": ["array"],
  "performance": {
    "tasks_completed_today": 3,
    "success_rate": .98,
    "average_completion_time_seconds": 4
  }
}
```

---

### GET `/api/kailash/agents/:agent_id/status`
Get specific agent status

**Response**:
```json
{
  "agent_id": "uuid",
  "name": "SARASWATI",
  "department": "GANESHA - Executive Assistant",
  "status": "busy",
  "current_task": {
    "task_id": "uuid",
    "title": "Interpret CEO command #4",
    "progress": ,
    "started_at": "ISODate"
  },
  "workload": ,
  "performance": {
    "tasks_completed": 4,
    "success_rate": .99,
    "average_response_time_ms": 8
  }
}
```

---

##  TASKS

### GET `/api/kailash/tasks`
Get tasks (with filters)

**Query Parameters**:
- `status` (optional: queued | in_progress | completed | failed)
- `department` (optional)
- `priority` (optional: P | P | P | P3 | P4)
- `assigned_to` (optional: agent_id)
- `limit` (default: )
- `page` (default: )

**Response**:
```json
{
  "tasks": [
    {
      "task_id": "uuid",
      "title": "Generate URJAA revenue report",
      "department": "CHANDRA",
      "assigned_to": "KASHYAPA",
      "status": "in_progress",
      "priority": "P",
      "progress": ,
      "created_at": "ISODate"
    }
  ],
  "total": 34,
  "page": ,
  "pages": 
}
```

---

### GET `/api/kailash/tasks/:task_id`
Get specific task details

**Response**:
```json
{
  "task_id": "uuid",
  "command_id": "uuid",
  "title": "Generate URJAA revenue report",
  "description": "Compile yesterday's revenue data for URJAA platform",
  "type": "analysis",
  "priority": "P",
  "assigned_to": {
    "agent_id": "uuid",
    "name": "KASHYAPA",
    "department": "CHANDRA"
  },
  "status": "in_progress",
  "progress": ,
  "started_at": "ISODate",
  "estimated_completion": "ISODate",
  "result": null,
  "dependencies": [],
  "blocking": []
}
```

---

### POST `/api/kailash/tasks/:task_id/approve`
CEO approval for tasks requiring it

**Request**:
```json
{
  "ceo_key": "494",
  "approved": true,
  "notes": "Optional notes from CEO"
}
```

**Response**:
```json
{
  "success": true,
  "task_id": "uuid",
  "status": "approved",
  "message": "Task approved. Execution will proceed.",
  "notified_agents": ["GANESHA", "agent_id_who_submitted"]
}
```

---

##  SHIV - SYSTEM MONITORING

### GET `/api/kailash/shiv/status`
Get SHIV guardian status

**Response**:
```json
{
  "mode": "meditation",
  "last_intervention": " days ago",
  "last_intervention_type": "security_patch",
  "threats_detected_today": ,
  "threats_neutralized_today": ,
  "threats_this_month": ,
  "current_monitoring": {
    "infrastructure": "healthy",
    "application": "healthy",
    "security": "healthy",
    "data_integrity": "healthy",
    "agent_behavior": "healthy"
  },
  "recent_alerts": []
}
```

---

### GET `/api/kailash/shiv/logs`
Get SHIV monitoring logs

**Query Parameters**:
- `severity` (optional: P | P | P | P3)
- `layer` (optional: infrastructure | application | security | data_integrity | agent_behavior)
- `from_date` (optional)
- `to_date` (optional)
- `limit` (default: )

**Response**:
```json
{
  "logs": [
    {
      "log_id": "uuid",
      "timestamp": "ISODate",
      "severity": "P3",
      "layer": "application",
      "anomaly_detected": true,
      "anomaly_type": "Slow query detected",
      "intervention_taken": true,
      "actions": ["Query optimization applied"],
      "threat_neutralized": true
    }
  ],
  "total": 4
}
```

---

### GET `/api/kailash/shiv/incidents`
Get critical incidents

**Response**:
```json
{
  "incidents": [
    {
      "incident_id": "uuid",
      "timestamp": "ISODate",
      "severity": "P",
      "type": "security",
      "title": "SQL Injection Attack Attempt",
      "status": "resolved",
      "detected_by": "SHIV",
      "actions_taken": ["IP blocked", "Tokens revoked", "WA updated"],
      "resolution_time_seconds": ,
      "ceo_notified": true
    }
  ]
}
```

---

##  PARVATI - HARMONY MONITORING

### GET `/api/kailash/parvati/status`
Get PARVATI harmony status

**Response**:
```json
{
  "current_harmony_score": 9,
  "trend": "improving",
  "score_breakdown": {
    "workload_balance": 9,
    "communication_efficiency": 8,
    "ceo_satisfaction": 9,
    "agent_performance": 8,
    "collaboration": 88
  },
  "last_rebalancing": "4 hours ago",
  "rebalancing_actions_today": ,
  "current_issues": [],
  "recommendations": [
    "Consider adding sub-agent to LAKSHMI (inance showing sustained high load)"
  ]
}
```

---

### GET `/api/kailash/parvati/logs`
Get harmony logs

**Query Parameters**:
- `from_date` (optional)
- `to_date` (optional)
- `limit` (default: )

**Response**:
```json
{
  "logs": [
    {
      "log_id": "uuid",
      "timestamp": "ISODate",
      "overall_harmony_score": 9,
      "workload_imbalance_detected": false,
      "bottleneck_detected": false,
      "rebalancing_taken": false,
      "ceo_sentiment": {
        "frustration_level": ,
        "satisfaction_level": 9,
        "sentiment_trend": "stable"
      }
    }
  ]
}
```

---

### GET `/api/kailash/parvati/workload-distribution`
Get current workload distribution across departments

**Response**:
```json
{
  "timestamp": "ISODate",
  "departments": [
    {
      "department": "VISHWAKARMA",
      "active_tasks": ,
      "capacity_utilization": .,
      "status": "balanced"
    },
    {
      "department": "LAKSHMI",
      "active_tasks": 9,
      "capacity_utilization": .,
      "status": "high_load"
    }
  ],
  "balance_score": 9,
  "recommendations": []
}
```

---

##  INTER-AGENT COMMUNICATION

### GET `/api/kailash/messages`
Get inter-agent messages (for debugging/transparency)

**Query Parameters**:
- `from_agent` (optional)
- `to_agent` (optional)
- `related_task_id` (optional)
- `limit` (default: )

**Response**:
```json
{
  "messages": [
    {
      "message_id": "uuid",
      "from": "GANESHA",
      "to": "SURYA",
      "subject": "Task Assignment: URJAA Revenue Report",
      "timestamp": "ISODate",
      "read": true,
      "requires_response": false
    }
  ]
}
```

---

##  ANALYTICS & REPORTING

### GET `/api/kailash/analytics/system-performance`
Get system-wide performance metrics

**Query Parameters**:
- `period` (today | week | month)

**Response**:
```json
{
  "period": "today",
  "metrics": {
    "total_commands": 4,
    "total_tasks_created": 34,
    "total_tasks_completed": 89,
    "completion_rate": .8,
    "average_task_time_seconds": 34,
    "ceo_satisfaction_score": 9,
    "system_uptime": .9998,
    "harmony_score_average": 88
  },
  "department_performance": [
    {
      "department": "GANESHA",
      "tasks_completed": 4,
      "success_rate": .,
      "average_time_seconds": 
    }
  ]
}
```

---

### GET `/api/kailash/analytics/business-metrics`
Get business metrics across all products

**Query Parameters**:
- `period` (today | week | month)
- `product` (optional: urjaa | go4garage | ignition)

**Response**:
```json
{
  "period": "today",
  "urjaa": {
    "revenue": 8,
    "transactions": 4,
    "active_stations": 4,
    "uptime": .999
  },
  "go4garage": {
    "revenue": 8,
    "bookings": ,
    "active_garages": 
  },
  "ignition": {
    "active_users": 34,
    "new_installs": 34,
    "dau": 89
  }
}
```

---

##  ADMIN & CONIGURATION

### POST `/api/kailash/admin/agent/create`
Create a new agent (for expansion)

**Request**:
```json
{
  "ceo_key": "494",
  "name": "NEW_AGENT",
  "deity_name": "Sanskrit name",
  "department": "department_id",
  "role": "chief | sub_agent",
  "ai_platform": "claude | gemini | perplexity",
  "system_prompt": "Agent instructions",
  "capabilities": ["array"]
}
```

---

### PATCH `/api/kailash/admin/agent/:agent_id`
Update agent configuration

---

### POST `/api/kailash/admin/department/create`
Create a new department

---

##  WEHOOKS (or Real-time Updates)

### WebSocket `/api/kailash/ws/ceo-feed`
Real-time feed for CEO dashboard

**Connection**:
```javascript
const ws = new WebSocket('wss://your-domain/api/kailash/ws/ceo-feed?token=jwt-token');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.type: 'task_completed' | 'alert' | 'harmony_update' | 'shiv_intervention'
};
```

**Message Types**:
```json
{
  "type": "task_completed",
  "data": {
    "task_id": "uuid",
    "title": "URJAA Revenue Report",
    "result": { /* task result */ }
  }
}

{
  "type": "shiv_alert",
  "data": {
    "severity": "P",
    "message": "Unusual API activity detected",
    "action_taken": "Quarantined"
  }
}

{
  "type": "harmony_update",
  "data": {
    "new_score": 89,
    "change": -,
    "reason": "Workload spike in VISHWAKARMA"
  }
}
```

---

##  RATE LIMITS

- CEO commands:  per hour
- Dashboard data:  requests per hour
- Analytics:  requests per hour
- Admin operations:  per hour

---

## [SECURE] SECURITY

All routes require:
. **Authentication**: JWT token from `/auth/verify-ceo-key`
. **CEO Key verification**: or critical operations
3. **Rate limiting**: As specified above
4. **HTTPS only**: No HTTP allowed in production

---

##  RESPONSE ORMAT STANDARD

All API responses follow this structure:

**Success**:
```json
{
  "success": true,
  "data": { /* response data */ },
  "timestamp": "ISODate",
  "execution_time_ms": 4
}
```

**Error**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* additional error context */ }
  },
  "timestamp": "ISODate"
}
```

---

##  PRIORITY ENDPOINTS OR MVP (Week )

. `/api/kailash/auth/verify-ceo-key` [OK]
. `/api/kailash/ganesha/command` [OK]
3. `/api/kailash/ganesha/command/:command_id` [OK]
4. `/api/kailash/dashboard/overview` [OK]
. `/api/kailash/shiv/status` [OK]
. `/api/kailash/parvati/status` [OK]
. `/api/kailash/departments` [OK]
8. `/api/kailash/tasks` [OK]

**REST O THE ENDPOINTS: Weeks -**

---

**Total API Endpoints**: 3+
**WebSocket Endpoints**: 
**Priority for Day -**: 8 endpoints + WebSocket
