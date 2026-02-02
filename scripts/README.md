# Scripts Directory

Scripts for server management, maintenance, and automation.

## 🚀 Server Management

### `start.sh`
Start backend (FastAPI) and frontend (Vite) servers.

```bash
./scripts/start.sh
```

### `stop.sh`
Stop all running servers gracefully.

```bash
./scripts/stop.sh
```

### `health_check.sh`
Check if all services are running and healthy.

```bash
./scripts/health_check.sh
```

**Output:**
- Backend API status (port 8000)
- Frontend status (port 5173)
- API endpoint checks
- Process IDs and log file sizes

---

## 🧹 Cleanup Scripts

### `daily_cleanup.sh`
Automated daily cleanup of cache files and logs.

```bash
./scripts/daily_cleanup.sh
```

### `detect_dead_code.sh`
Find unused Python code with vulture.

```bash
./scripts/detect_dead_code.sh
```

### `check_duplicates.sh`
Find duplicate Python code blocks.

```bash
./scripts/check_duplicates.sh
```

### `validate_structure.sh`
Validate repository structure (runs in pre-commit).

```bash
./scripts/validate_structure.sh
```

---

## 🤖 ML Training

### `train_production.py`
Train production ML model on 50 stocks with 20 technical features.

```bash
python scripts/train_production.py
```

### `auto_retrain.py`
Automated model retraining with MLflow tracking.

```bash
python scripts/auto_retrain.py
```

---

## 🔒 Security

### `security_check.sh`
Run security scans (bandit, safety).

```bash
./scripts/security_check.sh
```

---

## 📋 Quick Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `start.sh` | Start all servers | Development |
| `stop.sh` | Stop all servers | End of session |
| `health_check.sh` | Verify services | Debugging |
| `daily_cleanup.sh` | Clean cache/logs | Daily (cron) |
| `detect_dead_code.sh` | Find unused code | Weekly |
| `train_production.py` | Train ML model | Monthly |

---

## 🔄 Automation

### Pre-commit Hook
Structure validation runs automatically before each commit:

```bash
pip install pre-commit
pre-commit install
```

### Cron Jobs (Optional)
```bash
# Daily cleanup at 3 AM
0 3 * * * /path/to/scripts/daily_cleanup.sh

# Weekly dead code report
0 4 * * 0 /path/to/scripts/detect_dead_code.sh
```
