#!/usr/bin/env bash
# Simple & Reliable Server Start Script
# Starts backend and frontend servers that stay running

set -euo pipefail

cd "$(dirname "$0")/.."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting POC Market Predictor Servers${NC}"
echo ""

# Create logs directory
mkdir -p logs

# Check .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file missing${NC}"
    exit 1
fi

# Clean old processes
echo "🧹 Cleaning old processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
sleep 1

# Start backend in background
echo -e "🐍 Starting Backend (port 8000)..."
python3 -m uvicorn src.trading_engine.server:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info \
    >> logs/backend.log 2>&1 &

BACKEND_PID=$!
echo $BACKEND_PID > logs/.backend.pid
echo -e "${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"

# Wait a moment for backend to initialize
sleep 3

# Start frontend in background
echo -e "⚛️  Starting Frontend (port 5173)..."
cd frontend
npm run dev >> ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/.frontend.pid
cd ..
echo -e "${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID)"

echo ""
echo -e "${GREEN}✅ Servers Started!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}Frontend:${NC}  http://localhost:5173"
echo -e "${BLUE}Backend:${NC}   http://localhost:8000"
echo -e "${BLUE}API Docs:${NC}  http://localhost:8000/docs"
echo ""
echo "📋 Commands:"
echo "  View logs:  make logs"
echo "  Stop:       ./scripts/stop.sh"
echo "  Status:     make status"
echo ""
echo -e "${YELLOW}💡 Note: Servers are running in background${NC}"
echo ""
