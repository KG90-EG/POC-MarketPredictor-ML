#!/usr/bin/env bash
# Quick test script for server startup

set -euo pipefail

# Get project root (one level up from scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🧹 Cleaning up old processes..."
lsof -ti:8000,5173 | xargs kill -9 2>/dev/null || true
sleep 2

echo ""
echo "🚀 Starting Backend..."
python3 -m uvicorn src.trading_engine.server:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

echo ""
echo "🚀 Starting Frontend..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
cd ..

echo ""
echo "⏳ Waiting for servers (10s)..."
for i in {1..10}; do
    echo -n "."
    sleep 1
done
echo ""

echo ""
echo "📊 Checking Status..."
echo "===================="

# Check Backend
if lsof -i:8000 > /dev/null 2>&1; then
    echo "✅ Backend: Running on port 8000"
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "   Health: OK"
    else
        echo "   Health: Not ready yet"
    fi
else
    echo "❌ Backend: Not running"
fi

# Check Frontend
if lsof -i:5173 > /dev/null 2>&1; then
    echo "✅ Frontend: Running on port 5173"
else
    echo "❌ Frontend: Not running"
fi

echo ""
echo "📍 URLs:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 To stop:"
echo "   make kill-ports"
echo ""
echo "📄 Logs:"
echo "   tail -f logs/backend.log"
echo "   tail -f logs/frontend.log"
