# Archive Manifest

**Date:** 2026-01-06 07:14:44  
**Reason:** Repository cleanup - removing unused code and data  
**Total Items Archived:** 18

## Archived Items

### scripts/train_watchlist.py
- **Type:** file
- **Size:** 4.6 KB
- **Reason:** Legacy training script
- **Archived to:** `archive/code/scripts/train_watchlist.py`

### scripts/push_model_to_s3.py
- **Type:** file
- **Size:** 600.0 B
- **Reason:** S3 deployment not used
- **Archived to:** `archive/code/scripts/push_model_to_s3.py`

### scripts/create_and_push.sh
- **Type:** file
- **Size:** 938.0 B
- **Reason:** Unused in current application
- **Archived to:** `archive/code/scripts/create_and_push.sh`

### scripts/setup_github_security.sh
- **Type:** file
- **Size:** 6.8 KB
- **Reason:** Unused in current application
- **Archived to:** `archive/code/scripts/setup_github_security.sh`

### scripts/security_check.sh
- **Type:** file
- **Size:** 4.1 KB
- **Reason:** Unused in current application
- **Archived to:** `archive/code/scripts/security_check.sh`

### scripts/deploy_production.sh
- **Type:** file
- **Size:** 9.4 KB
- **Reason:** Replaced by automated CI/CD
- **Archived to:** `archive/code/scripts/deploy_production.sh`

### scripts/setup_production.sh
- **Type:** file
- **Size:** 3.7 KB
- **Reason:** Unused in current application
- **Archived to:** `archive/code/scripts/setup_production.sh`

### data/analytics/
- **Type:** directory
- **Size:** 720.3 MB
- **Reason:** Old analytics data
- **Archived to:** `archive/data/analytics`

### mlruns/0/
- **Type:** directory
- **Size:** 1.3 MB
- **Reason:** Old MLflow experiments
- **Archived to:** `archive/mlruns/0`

### mlruns/115743457976521189/
- **Type:** directory
- **Size:** 890.0 B
- **Reason:** Old MLflow experiments
- **Archived to:** `archive/mlruns/115743457976521189`

### mlruns/194387609133238263/
- **Type:** directory
- **Size:** 48.2 KB
- **Reason:** Old MLflow experiments
- **Archived to:** `archive/mlruns/194387609133238263`

### mlruns/280234249061794636/
- **Type:** directory
- **Size:** 250.0 B
- **Reason:** Old MLflow experiments
- **Archived to:** `archive/mlruns/280234249061794636`

### mlruns/298350913811895006/
- **Type:** directory
- **Size:** 245.0 B
- **Reason:** Old MLflow experiments
- **Archived to:** `archive/mlruns/298350913811895006`

### mlruns/428310941844255435/
- **Type:** directory
- **Size:** 247.0 B
- **Reason:** Old MLflow experiments
- **Archived to:** `archive/mlruns/428310941844255435`

### examples/
- **Type:** directory
- **Size:** 3.1 KB
- **Reason:** Example code not used in production
- **Archived to:** `archive/code/examples/examples`

### config/
- **Type:** directory
- **Size:** 1.7 KB
- **Reason:** Essential configs moved to root
- **Archived to:** `archive/config/config`

### docker-compose.monitoring.yml
- **Type:** file
- **Size:** 2.2 KB
- **Reason:** Monitoring config moved to monitoring/
- **Archived to:** `archive/deployment/docker-compose.monitoring.yml`

### Dockerfile
- **Type:** file
- **Size:** 698.0 B
- **Reason:** Not using Docker deployment currently
- **Archived to:** `archive/deployment/Dockerfile`


## Active Codebase (After Cleanup)

### Core Application
- `src/trading_engine/server.py` - Main FastAPI server
- `src/trading_engine/market_regime.py` - Market regime detection
- `src/trading_engine/composite_scoring.py` - Composite scoring system
- `src/trading_engine/crypto.py` - Cryptocurrency ranking
- `src/trading_engine/ml/` - Machine learning modules

### Frontend
- `frontend/src/` - React application
- `frontend/src/components/` - UI components

### Configuration
- `pyproject.toml` - Project metadata
- `pytest.ini` - Test configuration
- `requirements.txt` - Python dependencies

### Documentation (Active)
- `docs/BACKLOG.md` - Project backlog and weekly progress
- `docs/DECISION_SUPPORT_SYSTEM_REQUIREMENTS.md` - Master requirements
- `README.md` - Main documentation

## Restoration

To restore any archived item:
```bash
# Example: Restore training scripts
cp -r archive/code/training/ ./training/
```

## Notes

- All archived items are preserved for historical reference
- Archive can be safely deleted if disk space is needed
- Essential configurations were copied to root before archiving
- Documentation was already archived in previous cleanup
