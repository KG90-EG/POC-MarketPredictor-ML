#!/bin/bash
#
# Automated Test Script - POC Market Predictor
# Tests backend health, frontend accessibility, and basic functionality
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:5173"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 POC Market Predictor - Automated Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Track results
PASSED=0
FAILED=0
TESTS=0

# Test function
test_result() {
    TESTS=$((TESTS + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} $2"
        FAILED=$((FAILED + 1))
    fi
}

echo "━━━ Backend Tests ━━━"
echo ""

# Test 1: Backend Health
echo -n "Testing backend health... "
response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health")
test_result $([ "$response" = "200" ] && echo 0 || echo 1) "Backend health endpoint returns 200"

# Test 2: Backend Status
echo -n "Testing backend status... "
status=$(curl -s "$BACKEND_URL/health" | grep -o '"status":"ok"' || echo "")
test_result $([ -n "$status" ] && echo 0 || echo 1) "Backend status is 'ok'"

# Test 3: Model Loaded
echo -n "Testing model loaded... "
model=$(curl -s "$BACKEND_URL/health" | grep -o '"model_loaded":true' || echo "")
test_result $([ -n "$model" ] && echo 0 || echo 1) "ML model is loaded"

# Test 4: OpenAI Configured
echo -n "Testing OpenAI configuration... "
openai=$(curl -s "$BACKEND_URL/health" | grep -o '"openai_configured":true' || echo "")
test_result $([ -n "$openai" ] && echo 0 || echo 1) "OpenAI is configured"

# Test 5: API Endpoints
echo -n "Testing API docs endpoint... "
docs=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs")
test_result $([ "$docs" = "200" ] && echo 0 || echo 1) "API docs accessible at /docs"

echo ""
echo "━━━ Frontend Tests ━━━"
echo ""

# Test 6: Frontend Accessible
echo -n "Testing frontend accessibility... "
frontend=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
test_result $([ "$frontend" = "200" ] && echo 0 || echo 1) "Frontend loads successfully"

# Test 7: React App
echo -n "Testing React app mount... "
react=$(curl -s "$FRONTEND_URL" | grep -o 'id="root"' || echo "")
test_result $([ -n "$react" ] && echo 0 || echo 1) "React root element present"

# Test 8: Title Tag
echo -n "Testing page title... "
title=$(curl -s "$FRONTEND_URL" | grep -o '<title>.*</title>' || echo "")
test_result $([ -n "$title" ] && echo 0 || echo 1) "Page has title tag"

# Test 9: Vite Dev Server
echo -n "Testing Vite dev server... "
vite=$(curl -s "$FRONTEND_URL" | grep -o '@vite/client' || echo "")
test_result $([ -n "$vite" ] && echo 0 || echo 1) "Vite dev server running"

# Test 10: JavaScript Loading
echo -n "Testing JavaScript modules... "
js=$(curl -s "$FRONTEND_URL" | grep -o 'type="module"' || echo "")
test_result $([ -n "$js" ] && echo 0 || echo 1) "JavaScript modules loading"

echo ""
echo "━━━ API Endpoint Tests ━━━"
echo ""

# Test 11: Stock Analysis Endpoint
echo -n "Testing stock analysis endpoint... "
stock_api=$(curl -s -X POST "$BACKEND_URL/api/analyze" \
    -H "Content-Type: application/json" \
    -d '{"ticker":"AAPL","use_openai":false}' \
    -o /dev/null -w "%{http_code}")
test_result $([ "$stock_api" = "200" ] && echo 0 || echo 1) "Stock analysis API works"

# Test 12: Rankings Endpoint
echo -n "Testing rankings endpoint... "
rankings=$(curl -s "$BACKEND_URL/api/rankings" -o /dev/null -w "%{http_code}")
test_result $([ "$rankings" = "200" ] && echo 0 || echo 1) "Rankings API accessible"

# Test 13: Crypto Analysis
echo -n "Testing crypto analysis endpoint... "
crypto=$(curl -s -X POST "$BACKEND_URL/api/analyze_crypto" \
    -H "Content-Type: application/json" \
    -d '{"symbol":"BTC","use_openai":false}' \
    -o /dev/null -w "%{http_code}")
test_result $([ "$crypto" = "200" ] && echo 0 || echo 1) "Crypto analysis API works"

echo ""
echo "━━━ Performance Tests ━━━"
echo ""

# Test 14: Response Time
echo -n "Testing backend response time... "
response_time=$(curl -s -o /dev/null -w "%{time_total}" "$BACKEND_URL/health")
response_ok=$(echo "$response_time < 1.0" | bc)
test_result "$response_ok" "Backend response time < 1s (${response_time}s)"

# Test 15: Frontend Load Time
echo -n "Testing frontend load time... "
frontend_time=$(curl -s -o /dev/null -w "%{time_total}" "$FRONTEND_URL")
frontend_ok=$(echo "$frontend_time < 2.0" | bc)
test_result "$frontend_ok" "Frontend load time < 2s (${frontend_time}s)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test Results Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "Total Tests: ${BLUE}$TESTS${NC}"
echo -e "Passed:      ${GREEN}$PASSED${NC}"
echo -e "Failed:      ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
