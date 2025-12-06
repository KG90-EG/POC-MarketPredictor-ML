# POC-MarketPredictor-ML

A FastAPI + React proof of concept for ranking equities/crypto with ML signals and simulating trades. The project is currently in **beta**: core flows exist, but stability, documentation, and tests are being expanded.

## Status

- **Backend/Frontend:** aligned at v0.9.0; simulation endpoints are available but need hardening.
- **Data:** SQLite by default; PostgreSQL migration and authentication are planned.
- **Docs:** See [`docs/project/backlog.md`](docs/project/backlog.md) for the active priority list.

## Key Features

- Stock & crypto ranking endpoints (FastAPI in `market_predictor/server.py`).
- Paper-trading simulation engine with configurable buy/sell rules (`market_predictor/simulation.py`).
- React (Vite) frontend with dark/light theme and localization support.
- Training scripts and utilities for refreshing models (`training/`, `scripts/`).

## Quick Start

### Requirements
- Python 3.10–3.12
- Node.js 18+

### Install & Run
```bash
# Backend
pip install -r requirements.txt
uvicorn market_predictor.server:app --reload

# Frontend (in a new terminal)
cd frontend
npm install
npm run dev
```
Open <http://localhost:5173> to use the UI.

### Tests
```bash
pytest            # backend tests
# (Frontend E2E with Playwright/Cypress planned; add them once simulation flow is stable.)
```

## Architecture at a Glance

- **Backend:** FastAPI app (`market_predictor/server.py`) orchestrating ranking, prediction, watchlists, and simulations. Supporting modules for trading logic, caching, metrics, alerts, and WebSockets.
- **Frontend:** React app consuming the backend APIs, including simulation endpoints.
- **Data:** SQLite persistence for simulations and watchlists; PostgreSQL migration is a P1 item.

More detail is available in [`docs/architecture/SPECIFICATION.md`](docs/architecture/SPECIFICATION.md).

## Documentation

- Backlog & priorities: [`docs/project/backlog.md`](docs/project/backlog.md)
- Documentation index: [`docs/index.md`](docs/index.md)
- Deployment guide: [`docs/deployment/DEPLOYMENT_GUIDE.md`](docs/deployment/DEPLOYMENT_GUIDE.md)
- History/notes: [`docs/history`](docs/history)

Keep README and the backlog in sync when you add features or adjust scope.
