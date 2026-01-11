#!/usr/bin/env bash
# Quick Server Status Check

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "📊 Server Status Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check backend
if lsof -i:8000 2>/dev/null | grep -q LISTEN; then
    echo -e "${GREEN}✓ Backend:${NC}  Running on port 8000"
    if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "  ${BLUE}└─${NC} Health check: ${GREEN}OK${NC}"
    else
        echo -e "  ${BLUE}└─${NC} Health check: ${YELLOW}Starting...${NC}"
    fi
else
    echo -e "${RED}✗ Backend:${NC}  Not running"
fi

echo ""

# Check frontend
if lsof -i:5173 2>/dev/null | grep -q LISTEN; then
    echo -e "${GREEN}✓ Frontend:${NC} Running on port 5173"
    if curl -sf http://localhost:5173 >/dev/null 2>&1; then
        echo -e "  ${BLUE}└─${NC} HTTP check: ${GREEN}OK${NC}"
    else
        echo -e "  ${BLUE}└─${NC} HTTP check: ${YELLOW}Starting...${NC}"
    fi
else
    echo -e "${RED}✗ Frontend:${NC} Not running"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Show URLs if both running
if lsof -i:8000 2>/dev/null | grep -q LISTEN && lsof -i:5173 2>/dev/null | grep -q LISTEN; then
    echo -e "${GREEN}✅ All systems operational${NC}"
    echo ""
    echo "🔗 Access URLs:"
    echo -e "  ${BLUE}Frontend:${NC}  http://localhost:5173"
    echo -e "  ${BLUE}Backend:${NC}   http://localhost:8000"
    echo -e "  ${BLUE}API Docs:${NC}  http://localhost:8000/docs"
else
    echo -e "${YELLOW}⚠️  Some services not running${NC}"
    echo ""
    echo "Start servers: ./scripts/start_simple.sh"
fi

echo ""
