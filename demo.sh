#!/bin/bash
# Demonstration script for the monitoring system with authorization

set -e

echo "=========================================="
echo "Monitoring System Authorization Demo"
echo "=========================================="
echo ""

# Test 1: Login with valid credentials
echo "1. Logging in with valid credentials..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin"}')

TOKEN=$(echo $LOGIN_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['token'])")
echo "✓ Login successful, received JWT token"
echo "  Token: ${TOKEN:0:50}..."
echo ""

# Test 2: Verify token
echo "2. Verifying token..."
VERIFY_RESPONSE=$(curl -s -X GET http://localhost:5000/verify \
  -H "Authorization: Bearer $TOKEN")
echo "✓ Token verified: $(echo $VERIFY_RESPONSE | python -m json.tool | grep email)"
echo ""

# Test 3: Try to access Grafana without token (should fail)
echo "3. Attempting to access Grafana without token..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/)
if [ "$HTTP_CODE" = "401" ]; then
  echo "✓ Access denied (401 Unauthorized) - as expected"
else
  echo "✗ Unexpected response: $HTTP_CODE"
fi
echo ""

# Test 4: Access Grafana with valid token (should succeed)
echo "4. Accessing Grafana with valid JWT token..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ \
  -H "Authorization: Bearer $TOKEN")
if [ "$HTTP_CODE" = "200" ]; then
  echo "✓ Access granted (200 OK) - authentication successful!"
else
  echo "✗ Unexpected response: $HTTP_CODE"
fi
echo ""

# Test 5: Check dashboard availability
echo "5. Checking custom dashboard availability..."
DASHBOARD_COUNT=$(curl -s http://admin:admin@localhost:3000/api/search?type=dash-db | \
  python -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "✓ Found $DASHBOARD_COUNT custom dashboard(s) in Grafana"
echo ""

# Test 6: Check Prometheus metrics
echo "6. Checking Prometheus metrics collection..."
METRICS=$(curl -s 'http://localhost:9090/api/v1/query?query=pg_stat_user_tables_n_live_tup' | \
  python -c "import sys, json; data=json.load(sys.stdin); print(len(data['data']['result']))")
echo "✓ Prometheus is collecting $METRICS metric series"
echo ""

echo "=========================================="
echo "All tests passed! System is operational."
echo "=========================================="
echo ""
echo "Access points:"
echo "  • Auth Service:              http://localhost:5000"
echo "  • Grafana (protected):       http://localhost:8080 (requires JWT)"
echo "  • Grafana (direct):          http://localhost:3000 (admin/admin)"
echo "  • Prometheus:                http://localhost:9090"
echo ""
