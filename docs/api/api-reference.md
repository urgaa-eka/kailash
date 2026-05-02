# KAILASH AEGIS HU - API Reference

## ase URL

```
https://kailash-ai.in/api
```

## Authentication

All endpoints (except `/health` and `/auth/login`) require JWT token:

```bash
Authorization: earer YOUR_JWT_TOKEN
```

Get token via login endpoint.

---

##  Authentication Endpoints

### POST /auth/login

Login with AEGIS code and password.

**Request**:
```json
{
  "aegis_code": "<REDACTED_AEGIS_CODE>",
  "password": "<REDACTED_PASSWORD>"
}
```

**Response ()**:
```json
{
  "access_token": "eyJeXAiOiJKVQiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "aegis_code": "<REDACTED_AEGIS_CODE>",
    "email": "vivek@go4garage.in",
    "role": "admin"
  }
}
```

**Errors**:
- `4`: Invalid credentials
- `43`: Device blocked ( failed attempts =  min lockout)
- `49`: Rate limit exceeded

### POST /auth/register

Create new user account.

**Request**:
```json
{
  "aegis_code": "NEW34",
  "password": "SecurePass3!",
  "email": "user@go4garage.in",
  "full_name": "User Name"
}
```

### GET /auth/me

Get current authenticated user info.

**Response ()**:
```json
{
  "aegis_code": "<REDACTED_AEGIS_CODE>",
  "email": "vivek@go4garage.in",
  "role": "admin",
  "created_at": "4--T::Z"
}
```

---

##  Department Endpoints

### GET /departments/

List all  departments.

**Response ()**:
```json
[
  {
    "_id": "ffbcf8cd99439",
    "name": "GANESHA",
    "description": "Executive Assistant & Command Router",
    "head_agent": {
      "name": "GANESHA Prime",
      "role": "Executive AI Assistant"
    },
    "sub_agents": [
      {
        "name": "Command Parser",
        "role": "Natural Language Understanding"
      }
    ],
    "status": "active",
    "current_workload": 4,
    "health_score": 9
  }
]
```

### GET /departments/{id}

Get specific department details.

### GET /departments/{id}/health

Get department health metrics.

**Response ()**:
```json
{
  "department_id": "f...",
  "department_name": "GANESHA",
  "health_score": 9,
  "workload": 4,
  "active_tasks": ,
  "completed_today": 8,
  "sub_agents_status": {
    "active": 4,
    "idle": ,
    "error": 
  }
}
```

---

## [OK] Task Endpoints

### POST /tasks/

Create new task.

**Request**:
```json
{
  "title": "Review charging station data",
  "description": "Analyze usage patterns for Q4",
  "priority": "high",
  "department_id": "ffbcf8cd99439",
  "due_date": "4--3T3:9:9Z"
}
```

**Response ()**:
```json
{
  "id": "f...",
  "title": "Review charging station data",
  "status": "pending",
  "created_at": "4--8T::Z"
}
```

### GET /tasks/

List tasks with optional filters.

**Query Parameters**:
- `status`: pending, in_progress, completed, cancelled
- `priority`: low, medium, high, critical
- `department_id`: ilter by department
- `limit`: Max results (default )
- `skip`: Pagination offset

**Example**:
```bash
GET /tasks/?status=pending&priority=high&department_id=f...
```

### PATCH /tasks/{id}

Update task.

**Request**:
```json
{
  "status": "in_progress",
  "priority": "critical"
}
```

### DELETE /tasks/{id}

Delete task (soft delete).

---

##  GANESHA Orchestrator Endpoints

### POST /ganesha/orchestrate

Send request to GANESHA AI Orchestrator (SSE streaming).

**Request**:
```json
{
  "user_message": "Show me project status",
  "conversation_history": []
}
```

**Response**: Server-Sent Events (SSE) stream

**Event Types**:
- `ganesha_thinking`: Claude is analyzing
- `sending_to_emergent`: Creating code agent prompt
- `emergent_response`: Code generated
- `ganesha_review`: Code review complete
- `task_complete`: Workflow finished
- `error`: Error occurred

### POST /ganesha/quick-action

Trigger quick action buttons.

**Request**:
```json
{
  "action": "status"
}
```

**Actions**: `status`, `review`, `next_steps`, `help`

### GET /ganesha/history

Get conversation history with GANESHA.

**Query Parameters**:
- `limit`: Max results (default )

### GET /ganesha/stats

Get GANESHA usage statistics.

**Response ()**:
```json
{
  "total_commands": 4,
  "completed_commands": 4,
  "success_rate": 9.,
  "estimated_credits_saved": ,
  "efficiency_percentage": 8
}
```

---

##  Analytics Endpoints

### GET /analytics/dashboard

Get dashboard KPI statistics.

**Response ()**:
```json
{
  "total_departments": ,
  "total_sub_agents": 4,
  "active_agents": 4,
  "total_tasks": 4,
  "active_tasks": 4,
  "completed_today": 3,
  "pending_tasks": 38,
  "system_health": 94,
  "average_response_time_ms": 34
}
```

### GET /analytics/shiv-status

Get SHIV Guardian security monitoring data.

**Response ()**:
```json
{
  "guardian": "SHIV",
  "status": "active",
  "security_score": 98,
  "threats_blocked_today": ,
  "failed_login_attempts": ,
  "rate_limit_hits": ,
  "last_security_scan": "4--8T::Z"
}
```

### GET /analytics/parvati-harmony

Get PARVATI harmony and workload balance metrics.

**Response ()**:
```json
{
  "guardian": "PARVATI",
  "status": "active",
  "harmony_score": 9,
  "workload_balance": 88,
  "overloaded_departments": ,
  "underutilized_departments": 3,
  "recommendations": [
    "Consider redistributing tasks from SURYA to VAYU"
  ]
}
```

---

##  System Endpoints

### GET /health

Health check (no authentication required).

**Response ()**:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "..",
  "timestamp": "4--8T:3:Z",
  "company": "Go4Garage",
  "product": "KAILASH AEGIS HU",
  "domain": "kailash-ai.in",
  "departments": ,
  "sub_agents": 4
}
```

### GET /security/stats

Get security statistics (requires authentication).

**Response ()**:
```json
{
  "active_rate_limits": ,
  "blocked_ips": ,
  "blocked_devices": ,
  "accounts_with_failed_attempts": ,
  "total_failed_attempts": 
}
```

---

## [WARN] Rate Limits

- **Per IP**:  requests/minute
- **Per IP**:  requests/hour

Exceeded limits return `49 Too Many Requests`.

---

##  Error Responses

All errors follow this format:

```json
{
  "error": "Error description",
  "error_id": "38",
  "timestamp": "4--8T:3:Z",
  "support": "cto@go4garage.in"
}
```

**Common Status Codes**:
- `4`: ad request
- `4`: Unauthorized (missing/invalid token)
- `43`: orbidden (blocked or insufficient permissions)
- `44`: Not found
- `4`: Validation error
- `49`: Rate limit exceeded
- ``: Internal server error
- `3`: Service unavailable (database down)

---

##  rand Colors (or UI Development)

**Primary**:
- G4G lue: `#A3D`
- Electric Yellow: `#C3`

**ackground**:
- G4G Graphite: `#EE`
- Dark Slate: `#3E`

**Status**:
- Success: `#CC4` (Teal)
- Warning: `#C3` (Yellow)
- Error: `#E4C3C` (Red)

---

##  Support

- **API Documentation**: https://kailash-ai.in/api/docs
- **Admin**: Connect@go4garage.in
- **Technical**: cto@go4garage.in
- **Emergency**: 89389

---

**API Version**: ..  
**Last Updated**: November 4  
**Company**: Go4Garage, Patna, India 🇮🇳  
**Domain**: kailash-ai.in
