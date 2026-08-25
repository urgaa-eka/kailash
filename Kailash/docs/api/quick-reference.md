#  KAILASH AEGIS HU - Quick Reference Guide

**One-page reference for common tasks and information**

---

##  Login Credentials

```
AEGIS Code: <REDACTED_AEGIS_CODE>
Password:   <REDACTED_PASSWORD>
A Code:   Any  digits (e.g., 34)
```

---

##  URLs

| Service | URL | Description |
|---------|-----|-------------|
| **rontend** | http://localhost:3 | React application |
| **ackend API** | http://localhost:8/api | astAPI server |
| **API Docs** | http://localhost:8/api/docs | Swagger UI |
| **Health Check** | http://localhost:8/api/health | Service status |

---

##  Application low

```
. Login Page (/)
   ↓ Enter credentials
. A Modal
   ↓ Enter  digits
3. Applications Hub (/applications)
   ↓ Choose KAILASH
4. KAILASH Dashboard (/kailash)
   ├──  Departments
   ├── GANESHA Panel (RED button)
   ├── SHIV Guardian
   └── PARVATI Harmony
```

---

## ️ Service Commands

### Start Services
```bash
sudo supervisorctl start all
```

### Check Status
```bash
sudo supervisorctl status
```

### Restart Services
```bash
# All services
sudo supervisorctl restart all

# Individual services
sudo supervisorctl restart frontend
sudo supervisorctl restart backend
```

### View Logs
```bash
# ackend
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/backend.err.log

# rontend
tail -f /var/log/supervisor/frontend.out.log
```

---

##  API Quick Reference

### Authentication
```bash
# Login
curl -X POST http://localhost:8/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"aegis_code":"<REDACTED_AEGIS_CODE>","password":"<REDACTED_PASSWORD>"}'

# Get current user
curl -X GET http://localhost:8/api/auth/me \
  -H "Authorization: earer YOUR_TOKEN"
```

### Departments
```bash
# List all departments
curl -X GET http://localhost:8/api/departments/ \
  -H "Authorization: earer YOUR_TOKEN"

# Get specific department
curl -X GET http://localhost:8/api/departments/ganesha \
  -H "Authorization: earer YOUR_TOKEN"
```

### Tasks
```bash
# List tasks
curl -X GET http://localhost:8/api/tasks/ \
  -H "Authorization: earer YOUR_TOKEN"

# Create task
curl -X POST http://localhost:8/api/tasks/ \
  -H "Authorization: earer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Task","description":"Description","priority":"high","assigned_department":"ganesha"}'
```

---

##  Key iles & Directories

### Documentation (Root)
```
/app/
├── MASTER_DOCUMENTATION.md      ← Complete reference
├── APPLICATION_LOW_GUIDE.md    ← low guide
├── README.md                    ← Project README
├── KAILASH_README.md            ← KAILASH guide
└── test_result.md               ← Testing history
```

### Code
```
/app/
├── frontend/                    ← React app
│   └── src/
│       ├── components/         ← React components
│       └── pages/              ← Page components
│
└── backend/                     ← astAPI app
    └── app/
        ├── api/                ← API routes
        ├── core/               ← Core functionality
        └── models/             ← Data models
```

### Documentation (Detailed)
```
/app/docs/
├── API_REERENCE.md            ← API docs
├── PRODUCTION_DEPLOYMENT.md    ← Deployment
├── PHASE3_SUMMARY.md           ← Phase 3 features
├── QUICK_REERENCE.md          ← This file
└── archived/                   ← Old reports (8 files)
```

### Tests
```
/app/tests/
└── scripts/                    ← Test scripts ( files)
```

---

##  Color Palette

```css
Primary:   #A3D  (Go4Garage lue)
Accent:    #C3  (Electric Yellow)
Success:   #98  (Green)
Error:     #E4444  (Red)
Warning:   #9E  (Orange)
```

---

## ️  AI Departments

. **GANESHA** - Supreme AI Orchestrator
. **VISHWAKARMA** - Master Architect
3. **SURYA** - Solar Energy Guardian
4. **TVASHTA** - Precision Manufacturing
. **KARTIKEYA** - Strategic Command
. **KAMADEVA** - rand Design
. **KUERA** - inancial Intelligence
8. **LAKSHMI** - Revenue Growth
9. **RIHASPATI** - Legal & Governance
. **MITRA** - Partnership Relations
. **DHARMA** - Ethics & CSR
. **SHUKRA** - Market Intelligence
3. **CHANDRA** - Service Excellence
4. **RAHMA** - R&D Innovation
. **INDRA** - Quality Assurance
. **CHITRAGUPTA** - Data Analytics
. **PRAJAPATI** - Human Resources
8. **YAMA** - Risk Management
9. **VANI** - Knowledge Management
. **VAYU** - Logistics & leet

---

##  Environment Variables

### rontend (.env)
```bash
REACT_APP_ACKEND_URL=http://localhost:8/api
```

### ackend (.env)
```bash
MONGO_URL=mongodb://localhost:/kailash
SECRET_KEY=your_secret_key
ANTHROPIC_API_KEY=sk-ant-api3-...
```

---

##  Known Issues

. **GANESHA AI Command Processing**
   - Issue: `/api/ganesha/command` returns  error
   - Workaround: Use `/api/ganesha/orchestrate` instead [OK]

. **Server Header**
   - Issue: Shows "uvicorn,KAILASH/."
   - Impact: Cosmetic only [WARN]

---

##  Testing Status

- **rontend**: [OK] % (All pages working)
- **ackend**: [OK] 8% (4/ tests passed)
- **Overall**:  Production Ready (9%)

---

##  Support

- **Email**: Connect@go4garage.in
- **Technical**: cto@go4garage.in
- **Emergency**: 89389

---

##  Quick Links

| Link | Description |
|------|-------------|
| [MASTER_DOCUMENTATION.md](../MASTER_DOCUMENTATION.md) | Complete reference guide |
| [APPLICATION_LOW_GUIDE.md](../APPLICATION_LOW_GUIDE.md) | Detailed flow guide |
| [API_REERENCE.md](API_REERENCE.md) | ull API documentation |
| [test_result.md](../test_result.md) | Testing history |

---

**Made with ❤️ for India's EV Revolution** 🇮🇳⚡

**Version**: ..  
**Last Updated**: November , 4
