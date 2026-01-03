#!/usr/bin/env bash
# Simple, reliable server startup script

set -euo pipefail

# Get project root (one level up from scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Load environment
if [ ! -f .env ]; then
    echo "❌ .env file missing. Copy .env.example to .env first."
    exit 1
fi

set -a
source .env
set +a

# Kill old processes
echo "🧹 Cleaning old processes..."
lsof -ti:8000,5173 | xargs kill -9 2>/dev/null || true
sleep 1

# Start backend
echo "🚀 Starting backend on port 8000..."
python3 -m uvicorn src.trading_engine.server:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid
echo "   PID: $BACKEND_PID"

# Start frontend
echo "🚀 Starting frontend on port 5173..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo $FRONTEND_PID > .frontend.pid
echo "   PID: $FRONTEND_PID"

echo ""
echo "✅ Servers starting..."
echo ""
echo "📍 URLs (ready in ~15 seconds):"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📋 Commands:"
echo "   Check status:  make status"
echo "   View logs:     make logs"
echo "   Stop servers:  make stop"
echo ""
