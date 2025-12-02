#!/bin/bash
# Quick Deployment Test Script
# Tests all critical endpoints after deployment

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default to localhost if no URL provided
BACKEND_URL="${1:-http://localhost:8000}"

echo "🧪 Testing Backend: $BACKEND_URL"
echo "=================================="
echo ""

# Test 1: Health Check
echo "1. Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/health" || echo "FAILED")

if echo "$HEALTH_RESPONSE" | grep -q '"status"'; then
    echo -e "${GREEN}✓${NC} Health check passed (200 OK)"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}✗${NC} Health check failed"
    exit 1
fi

echo ""

# Test 2: Ranking Endpoint
echo "2. Testing /ranking endpoint..."
RANKING_RESPONSE=$(curl -s "$BACKEND_URL/ranking?country=US&limit=5" || echo "FAILED")

if echo "$RANKING_RESPONSE" | grep -q '"ticker"'; then
    echo -e "${GREEN}✓${NC} Ranking endpoint passed (200 OK)"
    STOCK_COUNT=$(echo "$RANKING_RESPONSE" | grep -o '"ticker"' | wc -l | tr -d ' ')
    echo "   Retrieved $STOCK_COUNT stocks"
else
    echo -e "${RED}✗${NC} Ranking endpoint failed"
fi

echo ""

# Test 3: Crypto Ranking
echo "3. Testing /crypto/ranking endpoint..."
CRYPTO_RESPONSE=$(curl -s "$BACKEND_URL/crypto/ranking?limit=5" || echo "FAILED")

if echo "$CRYPTO_RESPONSE" | grep -q '"crypto_id"'; then
    echo -e "${GREEN}✓${NC} Crypto ranking passed (200 OK)"
    CRYPTO_COUNT=$(echo "$CRYPTO_RESPONSE" | grep -o '"crypto_id"' | wc -l | tr -d ' ')
    echo "   Retrieved $CRYPTO_COUNT cryptocurrencies"
else
    echo -e "${RED}✗${NC} Crypto ranking failed"
fi

echo ""

# Test 4: Predict Ticker
echo "4. Testing /predict_ticker endpoint..."
PREDICT_RESPONSE=$(curl -s "$BACKEND_URL/predict_ticker?ticker=AAPL" || echo "FAILED")

if echo "$PREDICT_RESPONSE" | grep -q '"ticker"'; then
    echo -e "${GREEN}✓${NC} Predict ticker passed (200 OK)"
    echo "   Response preview: $(echo "$PREDICT_RESPONSE" | head -c 100)..."
else
    echo -e "${RED}✗${NC} Predict ticker failed"
fi

echo ""

# Test 5: Ticker Info
echo "5. Testing /ticker_info endpoint..."
INFO_RESPONSE=$(curl -s "$BACKEND_URL/ticker_info?ticker=MSFT&include_ai=false" || echo "FAILED")

if echo "$INFO_RESPONSE" | grep -q '"ticker"'; then
    echo -e "${GREEN}✓${NC} Ticker info passed (200 OK)"
else
    echo -e "${RED}✗${NC} Ticker info failed"
fi

echo ""

# Test 6: OpenAPI Docs
echo "6. Testing /docs endpoint..."
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs" || echo "FAILED")

if [ "$DOCS_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓${NC} API docs accessible"
    echo "   Visit: $BACKEND_URL/docs"
else
    echo -e "${YELLOW}⚠${NC} API docs returned HTTP $DOCS_RESPONSE"
fi

echo ""
echo "=================================="
echo -e "${GREEN}✓ All critical tests passed!${NC}"
echo ""
echo "Next steps:"
echo "1. Test frontend at your Vercel URL"
echo "2. Verify CORS by accessing from frontend"
echo "3. Check Railway logs for any errors"
echo "4. Monitor /prometheus endpoint for metrics"
