#!/usr/bin/env bash
# Health Check Script - Verifies all services are running correctly
# Exit codes: 0 = healthy, 1 = unhealthy

set -euo pipefail

cd "$(dirname "$0")/.."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

HEALTHY=true

echo "🏥 POC Market Predictor Health Check"
echo "======================================"
echo ""

# Check Backend (port 8000)
echo -n "🐍 Backend API (port 8000): "
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
    HEALTHY=false
fi

# Check Frontend (port 5173)
echo -n "⚛️  Frontend (port 5173):    "
if curl -sf http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
    HEALTHY=false
fi

# Check API Endpoints
echo ""
echo "📡 API Endpoints:"

# /api/ranking
echo -n "   /api/ranking:          "
if curl -sf http://localhost:8000/api/ranking > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${YELLOW}⚠ Slow/Error${NC}"
fi

# /api/market-regime
echo -n "   /api/market-regime:    "
if curl -sf http://localhost:8000/api/market-regime > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${YELLOW}⚠ Slow/Error${NC}"
fi

# /api/crypto/ranking
echo -n "   /api/crypto/ranking:   "
if curl -sf http://localhost:8000/api/crypto/ranking > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${YELLOW}⚠ Slow/Error${NC}"
fi

# Check PIDs
echo ""
echo "🔧 Process IDs:"
if [ -f logs/.backend.pid ]; then
    BACKEND_PID=$(cat logs/.backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "   Backend PID:  ${GREEN}$BACKEND_PID (running)${NC}"
    else
        echo -e "   Backend PID:  ${RED}$BACKEND_PID (dead)${NC}"
        HEALTHY=false
    fi
else
    echo -e "   Backend PID:  ${YELLOW}No PID file${NC}"
fi

if [ -f logs/.frontend.pid ]; then
    FRONTEND_PID=$(cat logs/.frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "   Frontend PID: ${GREEN}$FRONTEND_PID (running)${NC}"
    else
        echo -e "   Frontend PID: ${RED}$FRONTEND_PID (dead)${NC}"
        HEALTHY=false
    fi
else
    echo -e "   Frontend PID: ${YELLOW}No PID file${NC}"
fi

# Log file sizes
echo ""
echo "📁 Log Files:"
if [ -f logs/backend.log ]; then
    BACKEND_LOG_SIZE=$(du -h logs/backend.log | cut -f1)
    echo "   backend.log:  $BACKEND_LOG_SIZE"
else
    echo "   backend.log:  (not found)"
fi

if [ -f logs/frontend.log ]; then
    FRONTEND_LOG_SIZE=$(du -h logs/frontend.log | cut -f1)
    echo "   frontend.log: $FRONTEND_LOG_SIZE"
else
    echo "   frontend.log: (not found)"
fi

# Summary
echo ""
echo "======================================"
if [ "$HEALTHY" = true ]; then
    echo -e "${GREEN}✅ All services healthy${NC}"
    exit 0
else
    echo -e "${RED}❌ Some services unhealthy${NC}"
    exit 1
fi
