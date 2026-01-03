# ============================================
# POC-MarketPredictor-ML Makefile
# ============================================
# Source of truth for all common commands
# Usage: make <target>

.PHONY: help setup install clean start stop restart status logs test docker-up docker-down docker-logs health check-env

# Default target
.DEFAULT_GOAL := help

# ============================================
# Configuration
# ============================================
PYTHON := python3
VENV := .venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PYTEST := $(VENV_BIN)/pytest
BACKEND_PORT := 8000
FRONTEND_PORT := 5173
FRONTEND_DIR := frontend

# Check if .env exists
ENV_FILE := .env
ifeq (,$(wildcard $(ENV_FILE)))
    $(warning ⚠️  .env file not found! Copy .env.example to .env)
endif

# ============================================
# Help
# ============================================
help: ## Show this help message
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║   POC-MarketPredictor-ML - Available Commands              ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make setup          # Initial setup (first time)"
	@echo "  make start          # Start backend + frontend"
	@echo "  make logs           # View server logs"
	@echo "  make test           # Run tests"

# ============================================
# Environment Setup
# ============================================
setup: check-env install ## Complete initial setup (venv + deps + .env check)
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Review .env configuration"
	@echo "  2. Run: make start"

check-env: ## Check if .env file exists
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "❌ .env file not found!"; \
		echo ""; \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "✅ Created .env file"; \
		echo "⚠️  Please review and configure .env before starting servers"; \
		exit 1; \
	fi
	@echo "✅ .env file exists"

venv: ## Create virtual environment
	@if [ ! -d $(VENV) ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV); \
		echo "✅ Virtual environment created"; \
	else \
		echo "✅ Virtual environment already exists"; \
	fi

install: venv ## Install Python dependencies
	@echo "Installing backend dependencies..."
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "✅ Backend dependencies installed"
	@echo ""
	@if [ -d $(FRONTEND_DIR) ] && [ -f $(FRONTEND_DIR)/package.json ]; then \
		echo "Installing frontend dependencies..."; \
		cd $(FRONTEND_DIR) && npm install; \
		echo "✅ Frontend dependencies installed"; \
	fi

# ============================================
# Server Management (Local)
# ============================================
start: check-env ## Start both backend and frontend servers
	@./scripts/start.sh

start-backend: check-env ## Start backend only
	@echo "🚀 Starting backend..."
	@./scripts/start_servers.sh --backend-only

start-frontend: check-env ## Start frontend only
	@echo "🚀 Starting frontend..."
	@./scripts/start_servers.sh --frontend-only

stop: ## Stop all servers
stop: ## Stop all servers
	@./scripts/stop.sh
restart: stop start ## Restart all servers

status: ## Check server status
status: ## Check server status
	@echo "📊 Server Status"
	@echo "================"
	@echo ""
	@if lsof -ti:8000 > /dev/null 2>&1; then \
		echo "✅ Backend:  Running on port 8000"; \
		curl -sf http://localhost:8000/health > /dev/null && echo "   Health: OK" || echo "   Health: Starting..."; \
	else \
		echo "❌ Backend:  Not running"; \
	fi
	@echo ""
	@if lsof -ti:5173 > /dev/null 2>&1; then \
		echo "✅ Frontend: Running on port 5173"; \
	else \
		echo "❌ Frontend: Not running"; \
	fi
health: ## Check server health endpoints
	@echo "Checking backend health..."
	@curl -sf http://localhost:$(BACKEND_PORT)/health && echo " ✅ Backend OK" || echo " ❌ Backend down"
	@echo "Checking frontend..."
	@curl -sf http://localhost:$(FRONTEND_PORT) >/dev/null && echo " ✅ Frontend OK" || echo " ❌ Frontend down"

# ============================================
# Logs
# ============================================
logs: ## Tail all logs
	@tail -f logs/backend.log logs/frontend.log logs/startup.log 2>/dev/null || \
		echo "⚠️  No log files found. Start the servers first."

logs-backend: ## Tail backend logs
	@tail -f logs/backend.log 2>/dev/null || \
		echo "⚠️  Backend log not found. Start backend first."

logs-frontend: ## Tail frontend logs
	@tail -f logs/frontend.log 2>/dev/null || \
		echo "⚠️  Frontend log not found. Start frontend first."

logs-clean: ## Clean all log files
	@rm -f logs/*.log
	@echo "✅ Logs cleaned"

# ============================================
# Development
# ============================================
test: ## Run all tests
	@echo "Running tests..."
	@if [ -d $(VENV) ]; then \
		$(PYTEST) tests/ -v; \
	else \
		$(PYTHON) -m pytest tests/ -v; \
	fi

test-watch: ## Run tests in watch mode
	@$(PYTEST) tests/ -v --watch

lint: ## Run linting
	@echo "Running flake8..."
	@$(VENV_BIN)/flake8 src/ tests/ --max-line-length=120 --exclude=.venv

format: ## Format code with black
	@echo "Formatting code..."
	@$(VENV_BIN)/black src/ tests/

format-check: ## Check code formatting
	@$(VENV_BIN)/black src/ tests/ --check

# ============================================
# Docker (Optional - for Production/CI)
# ============================================
docker-build: ## Build Docker images
	@echo "Building Docker images..."
	@docker-compose -f docker-compose.yml build

docker-up: ## Start services with Docker Compose
	@echo "Starting Docker services..."
	@docker-compose -f docker-compose.yml up -d
	@echo "✅ Services started"
	@docker-compose -f docker-compose.yml ps

docker-down: ## Stop Docker services
	@echo "Stopping Docker services..."
	@docker-compose -f docker-compose.yml down

docker-logs: ## View Docker logs
	@docker-compose -f docker-compose.yml logs -f

docker-restart: docker-down docker-up ## Restart Docker services

docker-ps: ## Show running containers
	@docker-compose -f docker-compose.yml ps

# Monitoring stack
monitor-up: ## Start monitoring stack (Prometheus, Grafana)
	@echo "Starting monitoring stack..."
	@docker-compose -f docker-compose.monitoring.yml up -d
	@echo "✅ Monitoring started"
	@echo "   Prometheus: http://localhost:9090"
	@echo "   Grafana:    http://localhost:3000 (admin/admin123)"

monitor-down: ## Stop monitoring stack
	@docker-compose -f docker-compose.monitoring.yml down

monitor-logs: ## View monitoring logs
	@docker-compose -f docker-compose.monitoring.yml logs -f

# ============================================
# Cleanup
# ============================================
clean: ## Clean temporary files and caches
	@echo "Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name ".DS_Store" -delete
	@rm -f logs/.backend.pid logs/.frontend.pid
	@echo "✅ Cleaned"

clean-all: clean logs-clean ## Deep clean (includes logs and venv)
	@echo "Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "Removing node_modules..."
	@rm -rf $(FRONTEND_DIR)/node_modules
	@echo "✅ Deep clean complete"

# ============================================
# Repository Structure
# ============================================
check-structure: ## Validate repository structure
	@echo "🔍 Checking repository structure..."
	@./scripts/validate_structure.sh

cleanup-structure: ## Auto-fix repository structure (move misplaced files)
	@echo "🧹 Reorganizing files..."
	@./scripts/cleanup_repo.sh

deep-clean: ## Deep cleanup (remove outdated files, duplicates, old models, cache)
	@echo "🧹 Running deep cleanup..."
	@./scripts/deep_cleanup.sh

# ============================================
# Port Management
# ============================================
ports: ## Check which processes are using backend/frontend ports
	@echo "Checking ports..."
	@echo "Backend ($(BACKEND_PORT)):"
	@lsof -i:$(BACKEND_PORT) || echo "  Port free"
	@echo ""
	@echo "Frontend ($(FRONTEND_PORT)):"
	@lsof -i:$(FRONTEND_PORT) || echo "  Port free"

kill-ports: ## Kill processes on backend/frontend ports
	@echo "Killing processes on ports $(BACKEND_PORT) and $(FRONTEND_PORT)..."
	@lsof -ti:$(BACKEND_PORT),$(FRONTEND_PORT) | xargs kill -9 2>/dev/null || true
	@echo "✅ Ports cleared"

# ============================================
# Quick Commands
# ============================================
dev: start ## Alias for 'make start'

serve: start ## Alias for 'make start'

run: start ## Alias for 'make start'

down: stop ## Alias for 'make stop'

# ============================================
# Model Training
# ============================================
train-model: ## Train production model on all DEFAULT_STOCKS (50 stocks)
	@echo "🤖 Starting model training..."
	@$(PYTHON) scripts/train_production.py

train-watchlist: ## Train model on your watchlist stocks
	@echo "🤖 Training model on watchlist stocks..."
	@$(PYTHON) scripts/train_watchlist.py

auto-retrain-setup: ## Setup automatic weekly retraining (Sunday 2am)
	@echo "📅 Setting up automatic retraining..."
	@$(PYTHON) scripts/auto_retrain.py --schedule weekly --day sun --time "02:00" &
	@echo "✅ Auto-retraining scheduler started in background"
	@echo "   Schedule: Weekly on Sunday at 02:00"
	@echo "   Logs: logs/auto_retrain.log"

auto-retrain-daily: ## Setup automatic daily retraining (2am)
	@echo "📅 Setting up daily automatic retraining..."
	@$(PYTHON) scripts/auto_retrain.py --schedule daily --time "02:00" &
	@echo "✅ Auto-retraining scheduler started in background"
	@echo "   Schedule: Daily at 02:00"
	@echo "   Logs: logs/auto_retrain.log"

auto-retrain-now: ## Run training immediately and setup weekly schedule
	@echo "🚀 Running immediate training + setting up weekly schedule..."
	@$(PYTHON) scripts/auto_retrain.py --schedule weekly --day sun --time "02:00" --run-now &
	@echo "✅ Training started and scheduler running in background"

mlflow-ui: ## Start MLflow UI to view training metrics
	@echo "🔬 Starting MLflow UI..."
	@$(PYTHON) -m mlflow ui --port 5000
	@echo "   Open http://localhost:5000 in your browser"
