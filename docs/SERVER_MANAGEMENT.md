# 🚀 Server Management Guide

This guide explains how to start, stop, and manage the MarketPredictor servers.

## 📋 Quick Start

### Option 1: Using Makefile (Recommended)

```bash
# First time setup
make setup          # Creates venv, installs deps, checks .env

# Start servers
make start          # Start backend + frontend

# View logs
make logs           # Tail all logs

# Stop servers
make stop           # Stop all servers

# Check status
make status         # Show server status
```

### Option 2: Using start_servers.sh Script

```bash
# Start both servers
./scripts/start_servers.sh

# Start backend only
./scripts/start_servers.sh --backend-only

# Start frontend only
./scripts/start_servers.sh --frontend-only

# Stop all servers
./scripts/start_servers.sh --stop

# Check status
./scripts/start_servers.sh --status
```

### Option 3: Using Docker Compose

```bash
# Start with Docker (includes Redis cache)
make docker-up      # Or: docker-compose up -d

# View logs
make docker-logs    # Or: docker-compose logs -f

# Stop services
make docker-down    # Or: docker-compose down
```

## ⚙️ Configuration

### Required: .env File

**The script will NOT start without a `.env` file!**

```bash
# Create from example
cp .env.example .env

# Edit with your settings
nano .env  # or vim, code, etc.
```

**Minimum required variables:**

```env
PROD_MODEL_PATH=models/prod_model.bin
```

**Optional but recommended:**

```env
USE_REDIS=false
RATE_LIMIT_RPM=60
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

## 🔍 Features

### ✅ What the Script Does

1. **Environment Loading**
   - Automatically loads `.env` file
   - Aborts if `.env` is missing
   - Exports all variables for server use

2. **Pre-flight Checks**
   - ✅ Checks if ports are available
   - ✅ Checks if model file exists
   - ✅ Prompts before killing existing processes

3. **Health Monitoring**
   - Waits for backend `/health` endpoint
   - Verifies frontend accessibility
   - Reports status with colored output

4. **Graceful Shutdown**
   - `trap` handlers for `Ctrl+C`, `SIGTERM`, `EXIT`
   - Sends `SIGTERM` first (graceful)
   - Falls back to `SIGKILL` if needed
   - Cleans up PID files

5. **Logging**
   - All output logged to `logs/startup.log`
   - Backend: `logs/backend.log`
   - Frontend: `logs/frontend.log`

## 🐳 Docker Architecture

```yaml
services:
  backend:   # FastAPI server (port 8000)
  frontend:  # Vite dev server (port 5173)
  redis:     # Cache (port 6379)
```

**Networks:**

- `ml-app-network` - Internal communication

**Volumes:**

- `./models` → `/app/models` (read-only)
- `./mlruns` → `/app/mlruns` (MLflow tracking)
- `./logs` → `/app/logs` (persistent logs)
- `redis_data` → Redis persistence

## 📊 Health Checks

### Manual Health Check

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:5173

# Or use Makefile
make health
```

### Docker Health Checks

```bash
# Check container health
docker-compose ps

# Backend container includes automatic health checks
# Interval: 30s, Timeout: 10s, Retries: 3
```

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Check what's using the ports
make ports

# Kill processes on those ports
make kill-ports

# Or manually
lsof -ti:8000,5173 | xargs kill -9
```

### Missing .env File

```bash
❌ ERROR: .env file not found at: /path/to/.env

Please create .env from .env.example:
  cp .env.example .env
```

**Solution:** Create the `.env` file as instructed.

### Model File Not Found

```bash
⚠ Model file not found: models/prod_model.bin
Backend may fail to start if model is required
Continue anyway? (y/N)
```

**Solutions:**

1. Train a model: `python training/train.py`
2. Download a model from S3
3. Update `PROD_MODEL_PATH` in `.env`

### Backend Won't Start

```bash
# Check logs
make logs-backend
# Or
tail -f logs/backend.log

# Common issues:
# - Missing dependencies: make install
# - Port in use: make kill-ports
# - Python version: python3 --version (need 3.10+)
```

### Frontend Won't Start

```bash
# Check logs
make logs-frontend

# Common issues:
# - Missing node_modules: cd frontend && npm install
# - Node version: node --version (need 18+)
```

## 🎯 Best Practices

### Development Workflow

```bash
# Morning routine
git pull
make setup          # Updates deps if needed
make start          # Start servers

# During development
make logs           # Monitor in separate terminal
make restart        # After config changes

# Before commit
make test           # Run tests
make format         # Format code
make lint           # Check linting

# End of day
make stop           # Stop servers
```

### Production Deployment

```bash
# Use Docker for production
make docker-build
make docker-up
make monitor-up     # Start Prometheus + Grafana
```

## 📚 All Available Commands

### Makefile Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all commands |
| `make setup` | Initial setup |
| `make install` | Install dependencies |
| `make start` | Start all servers |
| `make stop` | Stop all servers |
| `make restart` | Restart all servers |
| `make status` | Show server status |
| `make health` | Check health endpoints |
| `make logs` | Tail all logs |
| `make test` | Run tests |
| `make lint` | Run linting |
| `make format` | Format code |
| `make docker-up` | Start Docker services |
| `make docker-down` | Stop Docker services |
| `make monitor-up` | Start monitoring stack |
| `make clean` | Clean temp files |
| `make ports` | Check port usage |
| `make kill-ports` | Kill processes on ports |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_PORT` | 8000 | Backend server port |
| `FRONTEND_PORT` | 5173 | Frontend dev server port |
| `PYTHON_CMD` | python3 | Python command |
| `MAX_RETRIES` | 3 | Max startup retries |
| `HEALTH_TIMEOUT` | 30 | Health check timeout (seconds) |
| `PROD_MODEL_PATH` | - | **Required** - Path to model file |
| `USE_REDIS` | false | Enable Redis cache |
| `REDIS_URL` | - | Redis connection URL |
| `RATE_LIMIT_RPM` | 60 | Rate limit per minute |
| `OPENAI_API_KEY` | - | OpenAI API key |

## 🔐 Security Notes

1. **Never commit `.env`** - It's in `.gitignore`
2. **Use strong passwords** for production Redis
3. **Limit rate limiting** in production (`RATE_LIMIT_RPM`)
4. **Review logs regularly** for suspicious activity
5. **Use HTTPS** in production (nginx/caddy reverse proxy)

## 🆘 Getting Help

```bash
# Script help
./scripts/start_servers.sh --help

# Makefile help
make help

# Check system requirements
python3 --version  # Need 3.10+
node --version     # Need 18+
docker --version   # Optional
```

## 📝 Log Files Location

```
logs/
├── backend.log    # Backend server output
├── frontend.log   # Frontend dev server output
└── startup.log    # Startup script logs
```

## 🎉 Success

When everything works, you'll see:

```
✅ Loaded environment from: /path/to/.env
✅ Ports are available
✅ Model file found: models/prod_model.bin
✅ Backend started successfully (PID: 12345)
✅ Frontend started successfully (PID: 12346)
✅ All servers started successfully!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Backend:  http://localhost:8000
✓ Frontend: http://localhost:5173
ℹ API Docs: http://localhost:8000/docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Servers running. Press Ctrl+C to stop.
```

🎊 **Happy Trading!** 📈
