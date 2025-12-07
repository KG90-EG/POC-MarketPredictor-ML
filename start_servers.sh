#!/bin/bash
# Quick Server Restart Script
# Usage: ./start_servers.sh

set -e

PROJECT_DIR="/Users/kevingarcia/Documents/POC-MarketPredictor-ML"
BACKEND_PORT=8000
FRONTEND_PORT=5174

echo "🔄 Stopping existing servers..."
pkill -9 -f "uvicorn" 2>/dev/null || true
pkill -9 -f "vite" 2>/dev/null || true
sleep 2

echo "🚀 Starting backend on port $BACKEND_PORT..."
cd "$PROJECT_DIR"
.venv/bin/python -m uvicorn market_predictor.server:app --host 0.0.0.0 --port $BACKEND_PORT --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

echo "🚀 Starting frontend on port $FRONTEND_PORT..."
cd "$PROJECT_DIR/frontend"
npm run dev > /tmp/frontend.log 2>&1 &
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
