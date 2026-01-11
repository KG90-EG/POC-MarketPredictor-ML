# Getting Started

Welcome to POC-MarketPredictor-ML. Use this guide to set up the project quickly and find the right docs for deeper dives.

## What You'll Learn

- How to install and configure the application
- Running your first predictions and simulations
- Where the UI and backend live
- Basic configuration and customization

## Prerequisites

- **Python 3.10-3.12** (recommended for best compatibility)
- **Node.js 18+** (for frontend)
- **Git** (for cloning the repository)
- **Docker** (optional, for containerized deployment)

## Quick Start

From the repository root:

```bash
# Backend
pip install -r requirements.txt
uvicorn market_predictor.server:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173> to use the UI. See the [README](../../README.md) for more context on the flows and endpoints.

## Quick Navigation

- **[Model Training Guide](TRAINING_GUIDE.md)** - Train and evaluate models from the repository
- **[Architecture Spec](../architecture/SPECIFICATION.md)** - System overview and module map
- **[Deployment Guide](../deployment/DEPLOYMENT_GUIDE.md)** - Options for hosting the stack
- **[Simulation API](../api/simulation.md)** - Reference for the current simulation endpoints

## Next Steps

Once you're set up, explore:
- [Production Features](../features/PRODUCTION_FEATURES.md)
- [Project Backlog](../project/backlog.md)
- [Operations Guides](../operations/READTHEDOCS_SETUP.md)
