#!/bin/bash
# Quick Server Restart Script
# Usage: ./start_servers.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$SCRIPT_DIR}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

PYTHON_CMD="python"
if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
  PYTHON_CMD="$PROJECT_DIR/.venv/bin/python"
fi

echo "🔄 Stopping existing servers..."
pkill -9 -f "uvicorn" 2>/dev/null || true
pkill -9 -f "vite" 2>/dev/null || true
sleep 2

echo "🚀 Starting backend on port $BACKEND_PORT..."
cd "$PROJECT_DIR"
"$PYTHON_CMD" -m uvicorn market_predictor.server:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

echo "🚀 Starting frontend on port $FRONTEND_PORT..."
cd "$PROJECT_DIR/frontend"
npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT" > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

sleep 5

echo ""
echo "✅ Servers started!"
echo "📊 Backend:  http://localhost:$BACKEND_PORT (PID: $BACKEND_PID)"
echo "🎨 Frontend: http://localhost:$FRONTEND_PORT (PID: $FRONTEND_PID)"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""
echo "🛑 Stop: pkill -9 -f uvicorn && pkill -9 -f vite"
