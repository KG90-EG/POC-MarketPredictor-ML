#!/usr/bin/env bash
# Simple stop script

echo "🛑 Stopping servers..."

# Read PIDs
BACKEND_PID=$(cat .backend.pid 2>/dev/null || echo "")
FRONTEND_PID=$(cat .frontend.pid 2>/dev/null || echo "")

# Stop backend
if [ -n "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null || true
    echo "   Stopped backend (PID: $BACKEND_PID)"
fi

# Stop frontend
if [ -n "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null || true
    echo "   Stopped frontend (PID: $FRONTEND_PID)"
fi

# Cleanup
lsof -ti:8000,5173 | xargs kill -9 2>/dev/null || true
rm -f .backend.pid .frontend.pid

echo "✅ Servers stopped"
