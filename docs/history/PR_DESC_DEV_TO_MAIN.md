## PR: Merge `dev` into `main`

### Summary
This PR merges the `dev` branch, which introduces a full ML workflow, backend API, and React frontend interface for ranking tickers, along with CI automation and documentation enhancements.

### Key Additions
1. Python package `market_predictor` with feature engineering (RSI, SMA, MACD, Bollinger Bands, Momentum) and model training (XGBoost fallback to RandomForest if missing libomp).
2. FastAPI server (`market_predictor/server.py`) exposing endpoints: `/health`, `/predict_raw`, `/predict_ticker/{ticker}`, `/ranking`.
3. React + Vite frontend (`frontend/`) consuming `/ranking`.
4. Training utilities (`training/`): `trainer.py`, `evaluate_and_promote.py`, `drift_check.py`, `online_trainer.py`.
5. Backtesting helper (`backtest/backtester.py`).
6. CI workflows: `.github/workflows/ci.yml` and scheduled promotion/training in `promotion.yml`.
7. Model artifact and MLflow integration (local or remote tracking).
8. Expanded tests in `01_Trading_Fun/tests` (7 passing, 1 skipped for environment compatibility).
9. Documentation improvements (`README.md`) and dependency management (`requirements.txt`, `pyproject.toml`).
10. Archival of legacy scripts in `archive/`.

### Dependency Notes
- macOS users may need `brew install libomp cmake` for XGBoost and pyarrow (MLflow optional extras).
- Fallback classifier ensures functionality even without XGBoost.

### CI
- Runs lint (if configured), tests, optional frontend build, and can build/push Docker image if GHCR credentials provided.

### Follow-Up (Optional Future Work)
- Add PR template file.
- Add Netlify/Vercel deployment for frontend.
- Add performance monitoring and A/B model rollout.
- Integrate S3/Cloud artifact storage secrets.

### Checklist
- [x] All tests pass locally.
- [x] Updated README.
- [x] Requirements aligned.
- [x] Dev branch pushed.

---
Please review and merge when ready.