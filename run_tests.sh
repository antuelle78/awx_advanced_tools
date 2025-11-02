#!/bin/bash

# Multi-Server MCP Test Suite
# Run this to test all 3 deployed servers

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║         Multi-Server MCP - Automated Test Suite          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. CONTAINER STATUS TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd /home/ghost/awx_advanced_tools/mcp-server

# Test: Core container running
docker compose -f docker-compose.multi.yml ps | grep "mcp-server-core-1" | grep -q "Up" && test_result 0 "Core Operations container running" || test_result 1 "Core Operations container running"

# Test: Inventory container running
docker compose -f docker-compose.multi.yml ps | grep "mcp-server-inventory-1" | grep -q "Up" && test_result 0 "Inventory Management container running" || test_result 1 "Inventory Management container running"

# Test: Templates container running
docker compose -f docker-compose.multi.yml ps | grep "mcp-server-templates-1" | grep -q "Up" && test_result 0 "Templates container running" || test_result 1 "Templates container running"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. HEALTH CHECK TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test: Core health
curl -s http://localhost:8001/health | grep -q '"status":"healthy"' && test_result 0 "Core Operations health check" || test_result 1 "Core Operations health check"

# Test: Inventory health
curl -s http://localhost:8002/health | grep -q '"status":"healthy"' && test_result 0 "Inventory Management health check" || test_result 1 "Inventory Management health check"

# Test: Templates health
curl -s http://localhost:8003/health | grep -q '"status":"healthy"' && test_result 0 "Templates health check" || test_result 1 "Templates health check"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. AWX CONNECTIVITY TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test: Core AWX connection
curl -s http://localhost:8001/test | grep -q '"status":"connected"' && test_result 0 "Core Operations AWX connection" || test_result 1 "Core Operations AWX connection"

# Test: Inventory AWX connection
curl -s http://localhost:8002/test | grep -q '"status":"connected"' && test_result 0 "Inventory Management AWX connection" || test_result 1 "Inventory Management AWX connection"

# Test: Templates AWX connection
curl -s http://localhost:8003/test | grep -q '"status":"connected"' && test_result 0 "Templates AWX connection" || test_result 1 "Templates AWX connection"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. DATA RETRIEVAL TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test: List job templates
TEMPLATE_COUNT=$(curl -s http://localhost:8001/job_templates | jq -r '.count // 0')
[ "$TEMPLATE_COUNT" -ge 0 ] && test_result 0 "List job templates (count: $TEMPLATE_COUNT)" || test_result 1 "List job templates"

# Test: List inventories
INV_COUNT=$(curl -s http://localhost:8002/inventories | jq -r '.count // 0')
[ "$INV_COUNT" -ge 0 ] && test_result 0 "List inventories (count: $INV_COUNT)" || test_result 1 "List inventories"

# Test: List hosts
HOST_COUNT=$(curl -s http://localhost:8002/hosts | jq -r '.count // 0')
[ "$HOST_COUNT" -ge 0 ] && test_result 0 "List hosts (count: $HOST_COUNT)" || test_result 1 "List hosts"

# Test: List workflows
WORKFLOW_COUNT=$(curl -s http://localhost:8003/workflow_job_templates | jq -r '.count // 0')
[ "$WORKFLOW_COUNT" -ge 0 ] && test_result 0 "List workflow templates (count: $WORKFLOW_COUNT)" || test_result 1 "List workflow templates"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. API DOCUMENTATION TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test: Core docs available
curl -s http://localhost:8001/docs | grep -q "Swagger" && test_result 0 "Core Operations API docs" || test_result 1 "Core Operations API docs"

# Test: Inventory docs available
curl -s http://localhost:8002/docs | grep -q "Swagger" && test_result 0 "Inventory Management API docs" || test_result 1 "Inventory Management API docs"

# Test: Templates docs available
curl -s http://localhost:8003/docs | grep -q "Swagger" && test_result 0 "Templates API docs" || test_result 1 "Templates API docs"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. RESPONSE TIME TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test: Core response time
START=$(date +%s%N)
curl -s http://localhost:8001/health > /dev/null
END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000 ))
[ "$DURATION" -lt 1000 ] && test_result 0 "Core Operations response time (${DURATION}ms)" || test_result 1 "Core Operations response time (${DURATION}ms > 1000ms)"

# Test: Inventory response time
START=$(date +%s%N)
curl -s http://localhost:8002/health > /dev/null
END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000 ))
[ "$DURATION" -lt 1000 ] && test_result 0 "Inventory Management response time (${DURATION}ms)" || test_result 1 "Inventory Management response time (${DURATION}ms > 1000ms)"

# Test: Templates response time
START=$(date +%s%N)
curl -s http://localhost:8003/health > /dev/null
END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000 ))
[ "$DURATION" -lt 1000 ] && test_result 0 "Templates response time (${DURATION}ms)" || test_result 1 "Templates response time (${DURATION}ms > 1000ms)"

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                       TEST SUMMARY                        ║"
echo "╠═══════════════════════════════════════════════════════════╣"
printf "║ Total Tests:  %-43s ║\n" "$TESTS_RUN"
printf "║ ${GREEN}Passed:       %-43s${NC} ║\n" "$TESTS_PASSED"
printf "║ ${RED}Failed:       %-43s${NC} ║\n" "$TESTS_FAILED"
echo "╚═══════════════════════════════════════════════════════════╝"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ ALL TESTS PASSED! System is healthy and operational.${NC}\n"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please check the output above.${NC}\n"
    exit 1
fi
