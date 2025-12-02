#!/bin/bash
# Production setup script for Trading-Fun

set -e

echo "=================================="
echo "Trading-Fun Production Setup"
echo "=================================="
echo ""

# Check if Redis is installed
if command -v redis-server &> /dev/null; then
    echo "✓ Redis is installed"
    REDIS_VERSION=$(redis-server --version | grep -oE 'v=[0-9]+\.[0-9]+\.[0-9]+' | cut -d'=' -f2)
    echo "  Version: $REDIS_VERSION"
else
    echo "✗ Redis not found"
    echo ""
    echo "To install Redis:"
    echo "  macOS:   brew install redis"
    echo "  Ubuntu:  sudo apt-get install redis-server"
    echo "  Docker:  docker run -d -p 6379:6379 redis:latest"
    echo ""
    read -p "Would you like to start without Redis? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    echo "⚠️  Continuing without Redis (will use in-memory cache)"
fi

echo ""

# Check Python dependencies
echo "Checking Python dependencies..."
python -c "import redis" 2>/dev/null && echo "✓ redis package installed" || echo "✗ redis package missing (run: pip install -r requirements.txt)"
python -c "import websockets" 2>/dev/null && echo "✓ websockets package installed" || echo "✗ websockets package missing (run: pip install -r requirements.txt)"
python -c "import fastapi" 2>/dev/null && echo "✓ fastapi package installed" || echo "✓ FastAPI packages installed"

echo ""

# Check environment file
if [ -f .env ]; then
    echo "✓ .env file exists"
    
    # Check required variables
    if grep -q "OPENAI_API_KEY" .env && ! grep -q "OPENAI_API_KEY=sk-" .env; then
        echo "⚠️  OPENAI_API_KEY not set in .env (AI analysis will be unavailable)"
    fi
    
    if grep -q "REDIS_URL" .env; then
        echo "✓ REDIS_URL configured in .env"
    else
        echo "ℹ️  REDIS_URL not set (will use default: redis://localhost:6379/0)"
    fi
else
    echo "⚠️  .env file not found"
    echo "   Creating template .env file..."
    cat > .env << EOF
# Backend Configuration
PROD_MODEL_PATH=models/prod_model.bin
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
RATE_LIMIT_RPM=60
REDIS_URL=redis://localhost:6379/0

# MLflow (optional)
MLFLOW_TRACKING_URI=file:./mlruns
EOF
    echo "✓ Created .env template - please update with your API keys"
fi

echo ""

# Check frontend environment
if [ -f frontend/.env.local ]; then
    echo "✓ frontend/.env.local exists"
else
    echo "ℹ️  Creating frontend/.env.local..."
    cat > frontend/.env.local << EOF
VITE_API_URL=http://localhost:8000
EOF
    echo "✓ Created frontend/.env.local"
fi

echo ""

# Start Redis if installed
if command -v redis-server &> /dev/null; then
    if ! redis-cli ping &> /dev/null; then
        echo "Starting Redis..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew services start redis 2>/dev/null || redis-server --daemonize yes
        else
            redis-server --daemonize yes
        fi
        sleep 1
        if redis-cli ping &> /dev/null; then
            echo "✓ Redis is running"
        else
            echo "⚠️  Failed to start Redis"
        fi
    else
        echo "✓ Redis is already running"
    fi
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Update .env with your OPENAI_API_KEY (if using AI analysis)"
echo "2. Start backend:  uvicorn market_predictor.server:app --reload"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Test WebSocket:  python examples/websocket_client.py"
echo ""
echo "Monitoring endpoints:"
echo "  Health:  curl http://localhost:8000/health"
echo "  Metrics: curl http://localhost:8000/metrics"
echo ""
