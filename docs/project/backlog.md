# Project Backlog - POC-MarketPredictor-ML

**Last Updated**: February 2025
**Project Status**: Beta (actively stabilizing)
**Current Version**: 0.9.0 (backend + frontend in sync)

---

## 🎯 Current Priorities (P0/P1)

1) **Paper-Trading Simulation Hardening (P0)**
   - Tighten the existing simulation engine (`market_predictor/simulation.py`, `market_predictor/simulation_db.py`) with clearer lifecycle docs, request/response validation, and error instrumentation.
   - Ship minimal API docs for the eight simulation endpoints already exposed in `server.py`.
   - Add smoke tests that cover create → recommend → trade → history flows.

2) **Reliability & Coverage (P0)**
   - Grow automated coverage for trading rules (confidence thresholds, stop-loss / take-profit) and database behaviour (concurrent writes, rollbacks).
   - Stand up a thin E2E path (Playwright or Cypress) for the main frontend flow: ranking load → simulate trade → view history.

3) **Data & Multi-User Readiness (P1)**
   - Migrate the simulation/watchlist data stores from SQLite to PostgreSQL with migrations.
   - Introduce authentication + user scoping to isolate simulations, watchlists, and alerts.
   - Document the migration plan and rollback strategy.

4) **Operational Maturity (P1)**
   - Add environment-specific configs (dev/stage/prod) with sensible defaults.
   - Wire metrics and structured logs for simulations, WebSocket traffic, and alert delivery.
   - Confirm the deployment story (Railway/Render/Docker) end-to-end with a checklist.

---

## 🧭 Near-Term Deliverables (6-8 days)

| Item | Owner | ETA | Notes |
| --- | --- | --- | --- |
| Simulation API reference (FastAPI docs + examples) | Backend | 2 days | Documented in `docs/index.md` + OpenAPI annotations |
| Simulation regression tests | QA | 2 days | Pytest coverage for thresholds, sizing, DB writes |
| Frontend happy-path E2E | Frontend | 2 days | Single CI-friendly Playwright run |
| Postgres migration plan | Platform | 1 day | SQLAlchemy migrations + rollback steps |
| Deployment validation | Platform | 1 day | Railway/Render/Docker smoke checklist |

---

## ✅ Recently Completed

- Added core simulation + persistence modules with buy/sell rules.
- Documented backend/ frontend entry points in `README.md`.
- Cleaned up duplicate documentation and consolidated specs.

---

## 🔭 Deferred / Nice-to-Have

- Export & share (CSV/PDF) for simulation history once the API stabilizes.
- Real-time WebSocket updates for live P&L after database migration.
- Benchmarking dashboards once Prometheus/Grafana are wired for simulations.

---

## 📚 Documentation Links

- [Repository README](../../README.md)
- [Documentation Index](../index.md)
- [Architecture Spec](../architecture/SPECIFICATION.md)
- [Deployment Guide](../deployment/DEPLOYMENT_GUIDE.md)
