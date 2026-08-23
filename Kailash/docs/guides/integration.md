# Integration Guide - Department ID Mismatch Fix

## ✅ Changes Committed

All changes have been committed to your local repository:
- Department ID/name matching fix
- Performance optimizations
- Security enhancements
- System health monitoring

## 🚀 Quick Start - Test the Fix

### 1. Restart Backend Service

```bash
# Option A: Using supervisor (recommended)
sudo supervisorctl restart kailash-backend
sudo supervisorctl status

# Option B: Manual restart
cd /app/backend
pkill -f "uvicorn app.main:app"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
```

### 2. Test Department Endpoints

```bash
# Test with frontend ID (should work now)
curl -X GET "http://localhost:8000/api/departments/ganesha/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test with database ID (should still work)
curl -X GET "http://localhost:8000/api/departments/dept-001/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test with uppercase (should work)
curl -X GET "http://localhost:8000/api/departments/GANESHA/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Test from Frontend

Open your browser and navigate to:
```
http://localhost:3000/department/ganesha
http://localhost:3000/department/vishwakarma
http://localhost:3000/department/surya
```

All department pages should now load correctly!

## 📝 What Was Fixed

### Main Fix: Department ID Matching
**File**: `/app/backend/app/api/departments.py`

All endpoints now support:
- Frontend IDs: `ganesha`, `vishwakarma`, `surya`
- Database IDs: `dept-001`, `dept-002`, `dept-003`
- Any case variation: `GANESHA`, `Ganesha`, `ganesha`

### Endpoints Updated:
1. `GET /api/departments/{id}` - Get department
2. `GET /api/departments/{id}/health` - Health metrics
3. `GET /api/departments/{id}/sub-agents` - Sub-agents
4. `GET /api/departments/{id}/summary` - **Main fix**

## 🔍 Verify the Fix

### Quick Test Script

```bash
# Create test script
cat > /tmp/test_dept_fix.sh << 'EOF'
#!/bin/bash
echo "Testing Department ID Matching..."

# Get auth token (update credentials)
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"aegis_code":"<REDACTED_AEGIS_CODE>","password":"<REDACTED_PASSWORD>","fa_code":"123456"}' \
  | jq -r '.access_token')

echo "Token: ${TOKEN:0:20}..."

# Test frontend ID
echo -e "\n1. Testing frontend ID 'ganesha':"
curl -s "http://localhost:8000/api/departments/ganesha/summary" \
  -H "Authorization: Bearer $TOKEN" | jq '.department'

# Test database ID
echo -e "\n2. Testing database ID 'dept-001':"
curl -s "http://localhost:8000/api/departments/dept-001/summary" \
  -H "Authorization: Bearer $TOKEN" | jq '.department'

# Test uppercase
echo -e "\n3. Testing uppercase 'VISHWAKARMA':"
curl -s "http://localhost:8000/api/departments/VISHWAKARMA/summary" \
  -H "Authorization: Bearer $TOKEN" | jq '.department'

echo -e "\n✅ All tests completed!"
EOF

chmod +x /tmp/test_dept_fix.sh
/tmp/test_dept_fix.sh
```

## 📊 Additional Improvements

### 1. Performance Monitoring
New endpoint: `GET /api/system/health/detailed`
```bash
curl http://localhost:8000/api/system/health/detailed
```

### 2. Security Enhancements
- Fixed HTTP status codes (429, 500)
- Memory leak prevention
- Enhanced threat detection

### 3. System Health
New monitoring endpoints:
- `/api/system/health/detailed` - Full health check
- `/api/system/performance/stats` - Performance metrics
- `/api/system/security/report` - Security report (admin only)

## 🔄 Push to GitHub (Optional)

If you want to push to GitHub:

```bash
cd /app

# Set up GitHub credentials
git remote set-url origin https://YOUR_GITHUB_TOKEN@github.com/G4GURGAA/AEGISHUB.git

# Push changes
git push origin main
```

Or use SSH:
```bash
git remote set-url origin git@github.com:G4GURGAA/AEGISHUB.git
git push origin main
```

## 📚 Documentation

- **[DEPARTMENT_ID_MISMATCH_FIX.md](DEPARTMENT_ID_MISMATCH_FIX.md)** - Detailed fix documentation
- **[CODE_OPTIMIZATION_SUMMARY.md](CODE_OPTIMIZATION_SUMMARY.md)** - All optimizations
- **[deployment_optimization_report.json](deployment_optimization_report.json)** - Deployment report

## ✅ Verification Checklist

- [ ] Backend restarted successfully
- [ ] Department endpoints respond (test with curl)
- [ ] Frontend can load department pages
- [ ] No errors in backend logs
- [ ] All department IDs work (ganesha, dept-001, GANESHA)

## 🆘 Troubleshooting

### Backend won't start
```bash
cd /app/backend
tail -f /app/logs/kailash_production.log
```

### Department still not found
```bash
# Check database
cd /app/backend
python3 -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['kailash_aegis']
    dept = await db.departments.find_one({'name': 'GANESHA'})
    print(f'Found: {dept}')
    client.close()

asyncio.run(check())
"
```

### Clear cache
```bash
# Clear Python cache
find /app/backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find /app/backend -type f -name "*.pyc" -delete
```

---

**Status**: ✅ Ready to test  
**Next Step**: Restart backend and test department endpoints  
**Support**: Check logs at `/app/logs/kailash_production.log`