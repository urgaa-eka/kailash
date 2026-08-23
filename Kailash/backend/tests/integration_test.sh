#!/bin/bash

echo "🚀 Backend Integration Testing"
echo "==============================="

BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

# Get auth token
echo ""
echo "🔐 Testing Authentication..."
TOKEN=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"kailash_code":"<REDACTED_kailash_code>","password":"<REDACTED_PASSWORD>","two_factor_code":"123456"}' \
  | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
  echo "✅ Authentication: PASS"
else
  echo "❌ Authentication: FAIL"
  exit 1
fi

# Test backend endpoints
ENDPOINTS=(
  "/api/health:Health Check"
  "/api/departments:Departments List"
  "/api/departments/ganesha:GANESHA Department"
  "/api/departments/prajapati:PRAJAPATI Department"
  "/api/departments/chitragupta:CHITRAGUPTA Department"
  "/api/departments/ganesha/summary:GANESHA Summary"
  "/api/dashboard/executive:Executive Dashboard"
)

PASSED=0
FAILED=0

echo ""
echo "📡 Testing Backend Endpoints..."
for endpoint_info in "${ENDPOINTS[@]}"; do
  IFS=':' read -r path name <<< "$endpoint_info"
  
  if [ "$path" = "/api/health" ]; then
    status=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL$path")
  else
    status=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL$path" -H "Authorization: Bearer $TOKEN")
  fi
  
  if [ "$status" = "200" ]; then
    echo "✅ $name: PASS (HTTP $status)"
    ((PASSED++))
  else
    echo "❌ $name: FAIL (HTTP $status)"
    ((FAILED++))
  fi
done

# Test frontend-backend integration
echo ""
echo "🔗 Testing Frontend-Backend Integration..."

# Check if frontend can reach backend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/health")

if [ "$FRONTEND_STATUS" = "200" ] && [ "$BACKEND_STATUS" = "200" ]; then
  echo "✅ Frontend-Backend Link: PASS"
  echo "   Frontend: $FRONTEND_URL (HTTP $FRONTEND_STATUS)"
  echo "   Backend: $BACKEND_URL (HTTP $BACKEND_STATUS)"
  ((PASSED++))
else
  echo "❌ Frontend-Backend Link: FAIL"
  echo "   Frontend: HTTP $FRONTEND_STATUS"
  echo "   Backend: HTTP $BACKEND_STATUS"
  ((FAILED++))
fi

# Test CORS
echo ""
echo "🌐 Testing CORS Configuration..."
CORS_HEADER=$(curl -s -I "$BACKEND_URL/api/health" | grep -i "access-control-allow-origin")
if [ -n "$CORS_HEADER" ]; then
  echo "✅ CORS Headers: PASS"
  echo "   $CORS_HEADER"
  ((PASSED++))
else
  echo "❌ CORS Headers: FAIL"
  ((FAILED++))
fi

echo ""
echo "============================================================"
echo "📊 INTEGRATION TEST RESULTS"
echo "============================================================"
echo "Total: $((PASSED + FAILED)) | Passed: $PASSED | Failed: $FAILED"
echo "Success Rate: $(awk "BEGIN {printf \"%.1f\", ($PASSED/($PASSED+$FAILED))*100}")%"
echo "============================================================"

exit $FAILED
