# KAILASH - Setup Instructions

##  Quick Start (Day - Deliverable)

This will get KAILASH running with GANESHA as your AI Executive Assistant.

---

## Prerequisites

- Docker & Docker Compose installed
- Anthropic API key (get from https://console.anthropic.com/)
- Port 3, 8,  available

---

## Setup Steps

### . Configure Environment Variables

```bash
# Copy the environment template
cp .env.kailash .env

# Edit .env and add your Anthropic API key
# nano .env
# Set: ANTHROPIC_API_KEY=your-key-here
```

### . Start Services with Docker Compose

```bash
# Start all services (MongoD, ackend, rontend)
docker-compose -f docker-compose.kailash.yml up --build

# Or run in background
docker-compose -f docker-compose.kailash.yml up -d --build
```

### 3. Wait for Services to Start

Watch the logs:
```bash
docker-compose -f docker-compose.kailash.yml logs -f
```

You should see:
- [OK] MongoD: Ready for connections
- [OK] ackend: KAILASH API Ready
- [OK] rontend: Compiled successfully

### 4. Access CEO Dashboard

Open browser:
```
http://localhost:3
```

### . Authenticate

Enter CEO Key:
```
494
```

### . Test GANESHA

Try these commands:
```
"Hello GANESHA, what can you help me with?"
"What's the system status?"
"Explain the KAILASH organization structure"
```

---

## Alternative: Run Without Docker

### ackend

```bash
cd backend

# Install Python dependencies
pip install -r requirements_kailash.txt

# Set environment variables
export MONGO_URL="mongodb://localhost:"
export CEO_KEY="494"
export ANTHROPIC_API_KEY="your-key-here"
export JWT_SECRET="your-secret-key"

# Start MongoD separately (if not using Docker)
# mongod --dbpath ./data

# Run backend
python kailash_server.py
# Or: uvicorn kailash_server:app --reload --port 8
```

### rontend

```bash
cd frontend

# Install dependencies
yarn install

# Set environment variable
export REACT_APP_ACKEND_URL="http://localhost:8"

# Start frontend
yarn start
```

---

## Verify Installation

### . Check API Health

```bash
curl http://localhost:8/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "KAILASH API",
  "timestamp": "--T::.Z"
}
```

### . Test Authentication

```bash
curl -X POST http://localhost:8/api/kailash/auth/verify-ceo-key \
  -H "Content-Type: application/json" \
  -d '{"ceo_key": "494"}'
```

Expected: Returns JWT token

### 3. Test GANESHA Command

```bash
# irst, get JWT token from authentication
TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8/api/kailash/ganesha/command \
  -H "Content-Type: application/json" \
  -H "Authorization: earer $TOKEN" \
  -d '{"command": "Hello GANESHA"}'
```

Expected: GANESHA responds with interpretation

---

## Architecture Overview

```
┌─────────────────────────────────────┐
│     CEO Dashboard (React)           │
│     http://localhost:3           │
└──────────────┬──────────────────────┘
               │
               │ HTTP/REST API
               ↓
┌─────────────────────────────────────┐
│  KAILASH API (astAPI)              │
│  http://localhost:8              │
│                                     │
│  • Authentication (JWT)             │
│  • GANESHA Command Processing       │
│  • Dashboard Data                   │
└──────────────┬──────────────────────┘
               │
               ├──────→ Anthropic API (Claude)
               │        GANESHA AI Agent
               │
               └──────→ MongoD
                        localhost:
                        • ceo_commands
                        • tasks
                        • agents
                        • messages
```

---

## Troubleshooting

### MongoD Connection Error

**Error**: `Could not connect to MongoD`

**ix**:
```bash
# Check if MongoD is running
docker ps | grep kailash-mongodb

# Check MongoD logs
docker-compose -f docker-compose.kailash.yml logs mongodb

# Restart MongoD
docker-compose -f docker-compose.kailash.yml restart mongodb
```

### ackend Not Starting

**Error**: `Port 8 already in use`

**ix**:
```bash
# ind process using port 8
lsof -i :8
# Or on Windows: netstat -ano | findstr :8

# Kill the process or change port in docker-compose.kailash.yml
```

### Anthropic API Error

**Error**: `ANTHROPIC_API_KEY not configured`

**ix**:
. Get API key from https://console.anthropic.com/
. Add to `.env` file:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
3. Restart backend:
   ```bash
   docker-compose -f docker-compose.kailash.yml restart backend
   ```

### rontend Not Loading

**Error**: `Cannot connect to backend`

**ix**:
. Verify backend is running: `curl http://localhost:8/api/health`
. Check `REACT_APP_ACKEND_URL` in frontend environment
3. Clear browser cache
4. Restart frontend:
   ```bash
   docker-compose -f docker-compose.kailash.yml restart frontend
   ```

### Authentication ails

**Error**: `Invalid CEO key`

**ix**:
. Verify you're using correct key: `494`
. Check backend logs for errors
3. Verify `CEO_KEY` in `.env` matches what you're entering

---

## Next Steps (Day 3-)

Once this infrastructure is running:

. [OK] **Day - Complete**: GANESHA can receive and respond to commands
. **Day 3-4**: uild GANESHA sub-agents (SARASWATI, KARTIKEYA, NARADA, etc.)
3. **Day **: Implement SHIV & PARVATI basic monitoring
4. **Day -**: uild 3 priority departments (VISHWAKARMA, LAKSHMI, SURYA)

---

## Database Structure

MongoD collections created automatically:

- `ceo_commands`: All CEO commands and GANESHA responses
- `tasks`: Task tracking across departments
- `agents`: Agent registry and status
- `inter_agent_messages`: Communication between agents
- `departments`: Department information
- `shiv_monitoring_logs`: Security monitoring
- `parvati_harmony_logs`: Workload balance tracking
- `auth_logs`: Authentication audit trail

---

## Support

If you encounter issues:

. Check logs: `docker-compose -f docker-compose.kailash.yml logs`
. Verify all environment variables are set
3. Ensure ports are not in use by other services
4. Try restarting services

---

## Success Criteria (Day -)

[OK] You should be able to:
. Run `docker-compose -f docker-compose.kailash.yml up`
. Open http://localhost:3
3. Enter CEO key "494" and authenticate
4. Type "Hello GANESHA" and receive an AI response
. See the command stored in MongoD
. View system status (SHIV, PARVATI, departments)

**If all above work → Day - Infrastructure is COMPLETE** [OK]

---

## Development Mode

All services run with hot-reload enabled:
- **ackend**: Changes to `kailash_server.py` auto-reload
- **rontend**: Changes to React components auto-reload
- **Database**: Data persists in Docker volume

---

**uilt with**: astAPI + React + MongoD + Anthropic Claude
**Project**: KAILASH - AI-Powered Organization
