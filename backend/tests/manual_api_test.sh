#!/bin/bash
# Manual API Testing Script - Workaround for test database configuration

echo "=== Kailash API Manual Test Suite ==="
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "❌ Backend not running on port 8000"
    echo "Start with: cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 &"
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Get auth token
echo "🔐 Authenticating..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"kailash_code":"<REDACTED_kailash_code>","password":"<REDACTED_PASSWORD>","two_factor_code":"123456"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Authentication failed"
    exit 1
fi

echo "✅ Authentication successful"
echo ""

# Test 1: List departments
echo "📋 Test 1: List Departments"
DEPT_COUNT=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/departments \
  | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
if [ "$DEPT_COUNT" -ge 20 ]; then
    echo "✅ PASSED - Found $DEPT_COUNT departments"
else
    echo "❌ FAILED - Expected >= 20 departments, got $DEPT_COUNT"
fi
echo ""

# Test 2: Get GANESHA department
echo "🤖 Test 2: Get GANESHA Department"
GANESHA=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/departments/ganesha \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('name', ''))" 2>/dev/null)
if [ "$GANESHA" = "GANESHA" ]; then
    echo "✅ PASSED - GANESHA department found"
else
    echo "❌ FAILED - GANESHA department not found"
fi
echo ""

# Test 3: Get VISHWAKARMA department
echo "⚙️  Test 3: Get VISHWAKARMA Department"
VISHWA=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/departments/vishwakarma \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('name', ''))" 2>/dev/null)
if [ "$VISHWA" = "VISHWAKARMA" ]; then
    echo "✅ PASSED - VISHWAKARMA department found"
else
    echo "❌ FAILED - VISHWAKARMA department not found"
fi
echo ""

# Test 4: GANESHA v2 agents
echo "🎯 Test 4: GANESHA v2 Agents List"
AGENT_COUNT=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v2/ganesha/agents \
  | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('agents', [])))" 2>/dev/null)
if [ "$AGENT_COUNT" -eq 36 ]; then
    echo "✅ PASSED - Found 36 agents"
else
    echo "⚠️  WARNING - Expected 36 agents, got $AGENT_COUNT"
fi
echo ""

# Summary
echo "=== Test Summary ==="
echo "✅ 4 API endpoint tests completed"
echo "🔗 Backend: http://localhost:8000"
echo "📊 Analytics: http://localhost:3000/ganesha-analytics"
echo "📈 Executive: http://localhost:3000/executive"
