# 🚀 Quick Start Guide

## First Time Setup

```bash
# 1. Clone & navigate
cd /path/to/POC-MarketPredictor-ML

# 2. Run setup (creates venv, installs deps, checks .env)
make setup

# 3. Configure .env (if needed)
nano .env  # Add your API keys, model path, etc.
```

## Start the Application

**Simple - just run:**

```bash
./start.sh
```

**Done!** Servers start in 1 second. Your app is ready in ~15 seconds.

### Access Your Application

- **Frontend:** <http://localhost:5173>
- **Backend API:** <http://localhost:8000>
- **API Docs:** <http://localhost:8000/docs>

### Verify Everything Works

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl -I http://localhost:5173
```

### Stop the Application

```bash
./stop.sh
```

## Alternative: Using Make

```bash
make start    # Start servers
make stop     # Stop servers
make status   # Check status
make logs     # View logs
```

## All Commands

```bash
make help           # See all available commands
make setup          # Initial setup
make start          # Start servers
make stop           # Stop servers
make restart        # Restart servers
make status         # Check status
make health         # Check health endpoints
make logs           # View all logs
make test           # Run tests
make clean          # Clean temp files
make ports          # Check port usage
make kill-ports     # Force kill processes on ports
```

## Docker (Optional)

```bash
# Start with Docker
make docker-up      # Includes Backend, Frontend, Redis

# View logs
make docker-logs

# Stop
make docker-down

# Start monitoring (Prometheus + Grafana)
make monitor-up
```

## Troubleshooting

### Port already in use

```bash
make ports          # See what's using the ports
make kill-ports     # Kill processes on ports 8000 & 5173
```

### .env missing

```bash
cp .env.example .env
# Then edit .env with your settings
```

### Model not found

```bash
# Option 1: Train a model
python training/train.py

# Option 2: Update .env
# Set PROD_MODEL_PATH to your model location
```

## URLs

- **Frontend**: <http://localhost:5173>
- **Backend API**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>
- **Prometheus**: <http://localhost:9090> (if monitoring stack is running)
- **Grafana**: <http://localhost:3000> (admin/admin123)

## Environment Variables

Required in `.env`:

```env
PROD_MODEL_PATH=models/prod_model.bin
```

Optional:

```env
USE_REDIS=false
RATE_LIMIT_RPM=60
BACKEND_PORT=8000
FRONTEND_PORT=5173
OPENAI_API_KEY=sk-...
```

See `.env.example` for all options.

## Need Help?

```bash
# Script help
./scripts/start_servers.sh --help

# Makefile help
make help

# Full documentation
cat docs/SERVER_MANAGEMENT.md
```
