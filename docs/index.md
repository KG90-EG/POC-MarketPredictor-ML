# POC-MarketPredictor-ML Documentation

**Status:** Beta (simulation + ranking flows available; hardening under way)

This site captures the essentials for developing, deploying, and stabilizing the project. Start here, then dive into the linked guides.

---

## Quick Links

- [Backlog & Priorities](project/backlog.md)
- [Architecture Spec](architecture/SPECIFICATION.md)
- [Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)
- [Getting Started](../README.md)
- [Historical Notes](history/)

---

## What’s Implemented

- FastAPI backend providing ranking, prediction, watchlist, and simulation endpoints (see `market_predictor/server.py`).
- React (Vite) frontend consuming the backend APIs with dark/light theme and localization support.
- Paper-trading simulation engine with SQLite persistence (`simulation.py`, `simulation_db.py`).
- Scripts for training and data refresh tasks (`training/`, `scripts/`).

---

## Active Work (P0/P1)

- Harden the simulation API and document request/response contracts.
- Add regression tests for trading thresholds, persistence, and concurrency edge cases.
- Plan PostgreSQL migration + authentication for multi-user isolation.
- Validate deployments (Docker, Render/Railway, Netlify) with smoke tests and logging/metrics.

Refer to `project/backlog.md` for owners and timelines.

---

## Testing & Tooling

- Backend: `pytest` (targeting simulation, ranking, and database helpers)
- Frontend: Vite + React testing; E2E via Playwright/Cypress (planned)
- Linting/formatting: see `pyproject.toml` and frontend ESLint config

---

## Support

File issues or questions in the repo. Keep documentation changes synced with the backlog and README so users have a single source of truth.
