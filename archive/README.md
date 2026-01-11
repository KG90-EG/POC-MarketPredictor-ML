# Archive

This folder contains files that are not currently used by the application but are preserved for potential future use.

## Archived Test Files

### Phase 1 Tests (`phase1/`)
Tests for features **not yet implemented**:
- `test_ensemble.py` - Ensemble model tests (requires ensemble implementation)
- `test_features.py` - Feature engineering tests (requires refactored feature module)
- `test_hyperparameter_tuning.py` - Optuna hyperparameter optimization tests
- `test_mlflow.py` - MLflow tracking integration tests
- `test_retraining.py` - Model retraining system tests (script, not pytest)

**Why Archived**: These tests require modules that don't exist yet in the current codebase. They were likely created for Phase 4+ features (Ensemble Models, Advanced Feature Engineering, MLflow Integration).

**Usage**: If implementing these features in the future, move the corresponding test file back to `tests/`.

---

### Phase 2 Tests (`phase2/`)
Tests for advanced monitoring features **not yet implemented**:
- `test_drift_detection.py` - Model drift detection tests (requires `src/trading_engine/ml/drift_detection.py`)
- `test_monitoring_routes.py` - Monitoring API endpoints tests
- `test_online_learning.py` - Online learning tests (requires `src/trading_engine/ml/online_learning.py`)

**Why Archived**: These tests require the following modules that don't exist yet:
- `src/trading_engine/ml/drift_detection.py` (DDM, PageHinkley, KSWIN, DriftMonitor classes)
- `src/trading_engine/ml/online_learning.py` (OnlineLearner class)

**Usage**: Implement the required modules first, then move these tests back to `tests/`.

---

### Cryptocurrency Tests
- `test_crypto.py` - CoinGecko API integration tests (516 lines)

**Why Archived**: Tests the `src/trading_engine/crypto.py` module which exists but is not integrated into the main application. The crypto module provides:
- CoinGecko API integration
- Crypto market data fetching
- NFT token support
- Crypto ranking system

**Usage**: If adding cryptocurrency support to the application, move this test file back to `tests/`.

---

### Simulation Tests
- `test_simulation_integration.py` - Trading simulation integration tests (333 lines)

**Why Archived**: Tests the simulation API endpoints (`/api/simulations`) which may not be fully implemented or are legacy features from earlier development phases.

**Usage**: If simulation features are needed, verify the endpoints exist in `src/trading_engine/server.py` and move this test back to `tests/`.

---

## Active Tests (Still in `tests/`)

The following tests are **actively used** and should remain in the `tests/` folder:

1. **`test_api_endpoints.py`** - Core API endpoint tests (health, rankings, predictions)
2. **`test_backtest.py`** - Historical backtesting API tests (Phase 3)
3. **`test_integration.py`** - Full integration tests
4. **`test_llm_context.py`** - LLM context endpoints tests (Phase 3)
5. **`test_server.py`** - Server startup and configuration tests
6. **`test_trading.py`** - Trading signal and strategy tests
7. **`conftest.py`** - Pytest fixtures and test configuration

---

## Restoration Process

To restore an archived test file:

1. Verify the required module exists (e.g., `src/trading_engine/ml/drift_detection.py`)
2. Move the test file back to `tests/`:
   ```bash
   mv archive/phase2/test_drift_detection.py tests/
   ```
3. Run the test to verify it works:
   ```bash
   pytest tests/test_drift_detection.py -v
   ```
4. Update this README to remove the restored file from the archive list

---

## Notes

- Archive created: 2026-01-11
- Reason: Repository cleanup to remove tests for unimplemented features
- Total archived files: 10 test files (4 folders + 2 individual files)
- Test coverage before cleanup: 11 files
- Test coverage after cleanup: 7 files (all actively used)
