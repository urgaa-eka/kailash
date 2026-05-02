#!/bin/bash

echo "🚀 Backend-Frontend Integration Testing (Preview)"
echo "=================================================="

BACKEND_URL="https://ganesha-v2-api.preview.emergentagent.com"
FRONTEND_URL="https://ganesha-v2-api.preview.emergentagent.com"

# Test backend health
echo ""
echo "🏥 Testing Backend Health..."
HEALTH=$(curl -s "$BACKEND_URL/api/health" | jq -r '.status')
if [ "$HEALTH" = "healthy" ]; then
  echo "✅ Backend Health: PASS"
else
  echo "❌ Backend Health: FAIL"
  exit 1
fi

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
  "/api/departments:Departments List"
  "/api/departments/ganesha:GANESHA"
  "/api/departments/prajapati:PRAJAPATI"
  "/api/departments/chitragupta:CHITRAGUPTA"
  "/api/departments/chandra:CHANDRA"
  "/api/departments/shukra:SHUKRA"
  "/api/departments/dharma:DHARMA"
  "/api/departments/mitra:MITRA"
  "/api/departments/vani:VANI"
  "/api/departments/ganesha/summary:GANESHA Summary"
  "/api/dashboard/executive:Executive Dashboard"
)

PASSED=2
FAILED=0

echo ""
echo "📡 Testing Backend Endpoints..."
for endpoint_info in "${ENDPOINTS[@]}"; do
  IFS=':' read -r path name <<< "$endpoint_info"
  
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL$path" -H "Authorization: Bearer $TOKEN")
  
  if [ "$status" = "200" ]; then
    echo "✅ $name: PASS"
    ((PASSED++))
  else
    echo "❌ $name: FAIL (HTTP $status)"
    ((FAILED++))
  fi
done

# Test frontend
echo ""
echo "🌐 Testing Frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$FRONTEND_STATUS" = "200" ]; then
  echo "✅ Frontend: PASS (HTTP $FRONTEND_STATUS)"
  ((PASSED++))
else
  echo "❌ Frontend: FAIL (HTTP $FRONTEND_STATUS)"
  ((FAILED++))
fi

# Test CORS
echo ""
echo "🔗 Testing CORS Configuration..."
CORS=$(curl -s -I "$BACKEND_URL/api/health" | grep -i "access-control-allow-origin")
if [ -n "$CORS" ]; then
  echo "✅ CORS: PASS"
  ((PASSED++))
else
  echo "❌ CORS: FAIL"
  ((FAILED++))
fi

echo ""
echo "============================================================"
echo "📊 INTEGRATION TEST RESULTS"
echo "============================================================"
echo "Total: $((PASSED + FAILED)) | Passed: $PASSED | Failed: $FAILED"
echo "Success Rate: $(awk "BEGIN {printf \"%.1f\", ($PASSED/($PASSED+$FAILED))*100}")%"
echo "============================================================"
echo ""
echo "🔗 Links:"
echo "   Backend: $BACKEND_URL"
echo "   Frontend: $FRONTEND_URL"
echo "============================================================"

exit $FAILED
