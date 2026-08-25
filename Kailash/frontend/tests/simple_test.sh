#!/bin/bash

echo "🚀 Frontend Route Testing"
echo "=========================="

BASE_URL="http://localhost:3000"

ROUTES=(
  "/dashboard:Dashboard"
  "/kailash:KAILASH"
  "/dashboard/executive:Executive Dashboard"
  "/ganesha-analytics:Analytics"
  "/departments:Departments"
  "/department/ganesha:GANESHA Detail"
  "/department/prajapati:PRAJAPATI Detail"
  "/department/chitragupta:CHITRAGUPTA Detail"
)

PASSED=0
FAILED=0

for route_info in "${ROUTES[@]}"; do
  IFS=':' read -r path name <<< "$route_info"
  echo ""
  echo "📍 Testing: $name ($path)"
  
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$path")
  
  if [ "$status" = "200" ]; then
    echo "✅ $name: PASS (HTTP $status)"
    ((PASSED++))
  else
    echo "❌ $name: FAIL (HTTP $status)"
    ((FAILED++))
  fi
done

echo ""
echo "============================================================"
echo "📊 TEST RESULTS SUMMARY"
echo "============================================================"
echo "Total: $((PASSED + FAILED)) | Passed: $PASSED | Failed: $FAILED"
echo "Success Rate: $(awk "BEGIN {printf \"%.1f\", ($PASSED/($PASSED+$FAILED))*100}")%"
echo "============================================================"

exit $FAILED
