# 🎯 Server Management - Clean & Simple

## Quick Start

```bash
./scripts/start.sh    # Start servers (1 second)
./scripts/stop.sh     # Stop servers
```

## What We Built

✅ **Simple Scripts** - No complexity, just works  
✅ **Fast** - Servers start immediately  
✅ **Makefile Integration** - `make start` / `make stop`  
✅ **Docker Support** - Optional for production  
✅ **Comprehensive Docs** - Everything documented  

## File Structure

```text
├── scripts/
│   ├── start.sh                # ⭐ Main start script (USE THIS)
│   ├── stop.sh                 # ⭐ Stop script
│   ├── test_servers.sh         # Test/verify servers
│   └── ...                     # Other utility scripts
├── Makefile                    # Command hub
├── docker-compose.yml          # Docker setup (optional)
└── docs/
    ├── SERVER_MANAGEMENT.md    # Full documentation
    └── IMPROVEMENTS_SUMMARY.md # What we built
```

    └── IMPROVEMENTS_SUMMARY.md # What we built

```

## Daily Usage

### Start Application

```bash
./start.sh
# Wait ~15 seconds for warmup
# Open http://localhost:5173
```

### Verify Running

```bash
make status
# or
curl http://localhost:8000/health
```

### View Logs

```bash
make logs               # All logs
tail -f logs/backend.log    # Just backend
tail -f logs/frontend.log   # Just frontend
```

### Stop Application

```bash
./stop.sh
# or
make stop
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make start` | Start servers |
| `make stop` | Stop servers |
| `make status` | Check status |
| `make logs` | View all logs |
| `make health` | Test health endpoints |
| `make kill-ports` | Force kill port processes |
| `make help` | See all commands |

## Docker (Optional)

```bash
make docker-up      # Start with Docker
make docker-down    # Stop Docker
make docker-logs    # View Docker logs
```

## Environment Variables

Required in `.env`:

```env
PROD_MODEL_PATH=models/prod_model.bin
```

Optional:

```env
BACKEND_PORT=8000
FRONTEND_PORT=5173
USE_REDIS=false
OPENAI_API_KEY=sk-...
```

## Troubleshooting

### Ports in use

```bash
make ports          # See what's using ports
make kill-ports     # Kill processes
```

### Servers won't start

```bash
# Check .env exists
ls -la .env

# Check logs
tail -f logs/backend.log
tail -f logs/frontend.log
```

### Model not found

```bash
# Train a model first
python training/train.py

# Or update .env
nano .env  # Set PROD_MODEL_PATH
```

## Success Criteria

✅ `./scripts/start.sh` completes in ~1 second  
✅ Frontend accessible at <http://localhost:5173>  
✅ Backend healthy at <http://localhost:8000/health>  
✅ `./scripts/stop.sh` cleans up all processes  
✅ No manual intervention needed  

## That's It

Simple, fast, reliable. Just `./scripts/start.sh` and go! 🚀
