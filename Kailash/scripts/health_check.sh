#!/bin/bash
# KAILASH Health Check Script
# Domain: kailash-ai.in

set -e

echo "🏥 KAILASH Health Check Starting..."

# Check backend health
echo "Checking backend health..."
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health || echo "000")

if [ "$BACKEND_HEALTH" = "200" ]; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed (HTTP $BACKEND_HEALTH)"
    exit 1
fi

# Check frontend (if running)
echo "Checking frontend..."
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "000")

if [ "$FRONTEND_HEALTH" = "200" ]; then
    echo "✅ Frontend is healthy"
else
    echo "⚠️ Frontend not responding (HTTP $FRONTEND_HEALTH)"
fi

# Check database connectivity
echo "Checking database..."
python3 -c "
import os
import pymongo
try:
    client = pymongo.MongoClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017'), serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print('✅ Database is healthy')
except Exception as e:
    print(f'❌ Database health check failed: {e}')
    exit(1)
"

echo "🎉 All health checks passed!"
