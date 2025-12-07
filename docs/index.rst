# POC-MarketPredictor-ML Documentation

A FastAPI + React proof of concept for ranking equities/crypto, simulating trades, and iterating on ML models. The project is in **beta**: core flows work, and documentation and tests are being hardened.

Use this page as the entry point to the rest of the docs and the Sphinx navigation tree.

## Project Snapshot

- Backend + frontend aligned at **v0.9.0** with simulation endpoints available.
- SQLite-backed persistence for simulations and watchlists (PostgreSQL migration planned).
- Documentation index and backlog live in this repository—keep them in sync with code changes.

## Quick Links

- [Repository README](../README.md)
- [Documentation index (markdown)](index.md)
- [Project backlog](project/backlog.md)
- [Simulation API reference](api/simulation.md)
- [Deployment guide](deployment/DEPLOYMENT_GUIDE.md)

---

```{toctree}
:maxdepth: 2
:caption: Overview

index
project/backlog
```

```{toctree}
:maxdepth: 2
:caption: Getting Started

getting-started/index
getting-started/TRAINING_GUIDE
```

```{toctree}
:maxdepth: 2
:caption: Architecture & Decisions

architecture/SPECIFICATION
architecture/ADR-001-architecture-overview
architecture/ADR-002-model-training-strategy
architecture/ADR-003-caching-strategy
```

```{toctree}
:maxdepth: 2
:caption: Deployment

deployment/DEPLOYMENT_GUIDE
deployment/DEPLOYMENT
deployment/PRODUCTION_DEPLOYMENT
deployment/BACKEND_DEPLOYMENT
deployment/FRONTEND_DEPLOYMENT
deployment/AUTOMATED_DEPLOYMENT
deployment/PRODUCTION_READY
```

```{toctree}
:maxdepth: 2
:caption: Features & Flows

features/PHASE_1_SUMMARY
features/PHASE1_WATCHLISTS_SUMMARY
features/BUY_SELL_OPPORTUNITIES
features/FRONTEND_COMPONENTS
features/ALERTS
features/PRODUCTION_FEATURES
```

```{toctree}
:maxdepth: 2
:caption: API & Operations

api/simulation
operations/PERFORMANCE_MONITORING
operations/GITHUB_SECURITY_SETUP
operations/GITHUB_SECRETS
operations/READTHEDOCS_SETUP
```

```{toctree}
:maxdepth: 1
:caption: History

history/README
history/IMPLEMENTATION_SUMMARY
history/ARCHITECTURE_REVIEW
history/IMPROVEMENTS
history/PR_DESC_DEV_TO_MAIN
history/PHASE_2_IMPROVEMENTS
history/REORGANIZATION_PLAN
history/REORGANIZATION_COMPLETE
history/SESSION_SUMMARY_2025_12_02
```

---

Need help? File an issue or start a discussion in the repository.
