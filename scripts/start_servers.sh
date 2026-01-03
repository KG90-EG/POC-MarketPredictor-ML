#!/usr/bin/env bash
#
# Automated Server Start Script
# Starts backend and frontend servers with health checks and auto-recovery
#
# Usage:
#   ./scripts/start_servers.sh                    # Start both servers
#   ./scripts/start_servers.sh --backend-only     # Start backend only
#   ./scripts/start_servers.sh --frontend-only    # Start frontend only
#   ./scripts/start_servers.sh --stop             # Stop all servers
#   ./scripts/start_servers.sh --status           # Check server status
#
# Environment:
#   BACKEND_PORT=8000    # Backend port (default: 8000)
#   FRONTEND_PORT=5173   # Frontend port (default: 5173)
#   PYTHON_CMD=python3   # Python command (default: python3)
#   MAX_RETRIES=3        # Max startup retries (default: 3)
#   HEALTH_TIMEOUT=30    # Health check timeout in seconds (default: 30)

set -euo pipefail

# ============================================
# Script Directory & Project Root
# ============================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ============================================
# Load Environment Variables from .env
# ============================================
ENV_FILE="$PROJECT_ROOT/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ ERROR: .env file not found at: $ENV_FILE"
    echo ""
    echo "Please create .env from .env.example:"
    echo "  cp .env.example .env"
    echo ""
    echo "Then configure required variables and try again."
    exit 1
fi

# Load .env file (export all variables)
set -a
source "$ENV_FILE"
set +a

echo "✅ Loaded environment from: $ENV_FILE"

# ============================================
# Cleanup Handler (trap for graceful shutdown)
# ============================================
BACKEND_PID=""
FRONTEND_PID=""
CLEANUP_DONE=false

cleanup() {
    if [ "$CLEANUP_DONE" = true ]; then
        return
    fi
    CLEANUP_DONE=true

    echo ""
    log_warning "Cleaning up servers..."

    # Read PIDs from files if not set
    if [ -z "$BACKEND_PID" ] && [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    fi
    if [ -z "$FRONTEND_PID" ] && [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
    fi

    # Stop backend
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        log_info "Stopping backend (PID: $BACKEND_PID)..."
        kill -TERM "$BACKEND_PID" 2>/dev/null || true
        sleep 2
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            kill -KILL "$BACKEND_PID" 2>/dev/null || true
        fi
    fi

    # Stop frontend
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        log_info "Stopping frontend (PID: $FRONTEND_PID)..."
        kill -TERM "$FRONTEND_PID" 2>/dev/null || true
        sleep 2
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            kill -KILL "$FRONTEND_PID" 2>/dev/null || true
        fi
    fi

    # Clean PID files
    rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"

    log_success "Cleanup complete"
}

# Register cleanup on EXIT, INT, TERM (only for main start process, not for --status/--stop)
# Will be enabled in main() for start operations only
TRAP_ENABLED=false

enable_trap() {
    if [ "$TRAP_ENABLED" = false ]; then
        trap cleanup EXIT INT TERM
        TRAP_ENABLED=true
    fi
}

# ============================================
# Colors & Configuration
# ============================================
# ============================================
# Colors & Configuration
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration (with .env fallback to defaults)
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
PYTHON_CMD="${PYTHON_CMD:-python3}"
MAX_RETRIES="${MAX_RETRIES:-3}"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-30}"

# PID files
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"

# Log files
LOG_DIR="$PROJECT_ROOT/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"
STARTUP_LOG="$LOG_DIR/startup.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# ============================================
# Pre-flight Checks
# ============================================

# Check if ports are available
check_ports() {
    log_info "Checking port availability..."

    if is_port_in_use "$BACKEND_PORT"; then
        log_warning "Backend port $BACKEND_PORT is already in use"
        local pid=$(get_process_on_port "$BACKEND_PORT")
        log_info "Process using port: $pid"
        read -p "Kill existing process and continue? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Cannot start - port $BACKEND_PORT is in use"
            exit 1
        fi
        kill_process_on_port "$BACKEND_PORT"
    fi

    if is_port_in_use "$FRONTEND_PORT"; then
        log_warning "Frontend port $FRONTEND_PORT is already in use"
        local pid=$(get_process_on_port "$FRONTEND_PORT")
        log_info "Process using port: $pid"
        read -p "Kill existing process and continue? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Cannot start - port $FRONTEND_PORT is in use"
            exit 1
        fi
        kill_process_on_port "$FRONTEND_PORT"
    fi

    log_success "Ports are available"
}

# Check required model file exists
check_model() {
    if [ -n "${PROD_MODEL_PATH:-}" ]; then
        local model_path="$PROJECT_ROOT/$PROD_MODEL_PATH"
        if [ ! -f "$model_path" ]; then
            log_warning "Model file not found: $model_path"
            log_info "Backend may fail to start if model is required"
            read -p "Continue anyway? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            log_success "Model file found: $PROD_MODEL_PATH"
        fi
    fi
}

# ============================================
# Utility functions
# ============================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$STARTUP_LOG"
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $*"
    log "INFO" "$*"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*"
    log "SUCCESS" "$*"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $*"
    log "WARNING" "$*"
}

log_error() {
    echo -e "${RED}✗${NC} $*" >&2
    log "ERROR" "$*"
}

#
# Process management
#

is_port_in_use() {
    local port=$1
    lsof -ti:"$port" >/dev/null 2>&1
}

get_process_on_port() {
    local port=$1
    lsof -ti:"$port" 2>/dev/null || echo ""
}

kill_process_on_port() {
    local port=$1
    local pid=$(get_process_on_port "$port")

    if [ -n "$pid" ]; then
        log_warning "Port $port is in use by PID $pid, killing..."
        kill -9 "$pid" 2>/dev/null || true
        sleep 1

        if is_port_in_use "$port"; then
            log_error "Failed to free port $port"
            return 1
        fi
        log_success "Port $port freed"
    fi
    return 0
}

cleanup_port() {
    local port=$1
    local service=$2

    if is_port_in_use "$port"; then
        log_warning "$service port $port is already in use"
        read -p "Kill existing process? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill_process_on_port "$port"
        else
            log_error "Cannot start $service - port $port is in use"
            return 1
        fi
    fi
    return 0
}

save_pid() {
    local pid=$1
    local pid_file=$2
    echo "$pid" > "$pid_file"
    log_info "Saved PID $pid to $pid_file"
}

read_pid() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        cat "$pid_file"
    fi
}

is_process_running() {
    local pid=$1
    kill -0 "$pid" 2>/dev/null
}

#
# Health checks
#

wait_for_health() {
    local url=$1
    local service=$2
    local timeout=$HEALTH_TIMEOUT
    local elapsed=0

    log_info "Waiting for $service to be healthy..."

    while [ $elapsed -lt $timeout ]; do
        if curl -sf "$url" >/dev/null 2>&1; then
            log_success "$service is healthy!"
            return 0
        fi
        sleep 1
        elapsed=$((elapsed + 1))
        printf "."
    done

    echo
    log_error "$service health check timeout after ${timeout}s"
    return 1
}

check_backend_health() {
    local response=$(curl -sf "http://localhost:$BACKEND_PORT/health" 2>/dev/null || echo "")
    if echo "$response" | grep -q "healthy"; then
        return 0
    fi
    return 1
}

check_frontend_health() {
    curl -sf "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1
}

#
# Backend server
#

start_backend() {
    log_info "Starting backend server on port $BACKEND_PORT..."

    # Enable cleanup trap
    enable_trap

    # Check Python
    if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
        log_error "Python not found: $PYTHON_CMD"
        log_info "Try: export PYTHON_CMD=python or python3"
        return 1
    fi

    # Check if already running
    local existing_pid=$(read_pid "$BACKEND_PID_FILE")
    if [ -n "$existing_pid" ] && is_process_running "$existing_pid"; then
        log_warning "Backend already running (PID: $existing_pid)"
        if check_backend_health; then
            log_success "Backend is healthy"
            return 0
        else
            log_warning "Backend unhealthy, restarting..."
            kill "$existing_pid" 2>/dev/null || true
            sleep 2
        fi
    fi

    # Cleanup port
    cleanup_port "$BACKEND_PORT" "Backend" || return 1

    # Check virtual environment
    if [ ! -d "$PROJECT_ROOT/.venv" ] && [ ! -d "$PROJECT_ROOT/venv" ]; then
        log_warning "No virtual environment found"
        log_info "Consider creating one: python3 -m venv .venv"
    fi

    # Start server
    cd "$PROJECT_ROOT"
    export PYTHONPATH="${PROJECT_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
    log_info "Running: $PYTHON_CMD -m uvicorn src.trading_engine.server:app --host 0.0.0.0 --port $BACKEND_PORT"

    nohup "$PYTHON_CMD" -m uvicorn src.trading_engine.server:app \
        --host 0.0.0.0 --port "$BACKEND_PORT" \
        > "$BACKEND_LOG" 2>&1 &

    local pid=$!
    save_pid "$pid" "$BACKEND_PID_FILE"
    BACKEND_PID=$pid  # Store for cleanup trap

    # Wait for startup (backend takes longer with reload mode)
    sleep 8

    # Check if still running
    if ! is_process_running "$pid"; then
        log_error "Backend failed to start"
        log_info "Check logs: tail -f $BACKEND_LOG"
        return 1
    fi

    # Health check
    if wait_for_health "http://localhost:$BACKEND_PORT/health" "Backend"; then
        log_success "Backend started successfully (PID: $pid)"
        log_info "Backend URL: http://localhost:$BACKEND_PORT"
        log_info "API Docs: http://localhost:$BACKEND_PORT/docs"
        log_info "Logs: tail -f $BACKEND_LOG"
        return 0
    else
        log_error "Backend health check failed"
        log_info "Check logs: tail -f $BACKEND_LOG"
        kill "$pid" 2>/dev/null || true
        return 1
    fi
}

stop_backend() {
    local pid=$(read_pid "$BACKEND_PID_FILE")

    if [ -z "$pid" ]; then
        log_info "Backend PID file not found"
        kill_process_on_port "$BACKEND_PORT"
        return 0
    fi

    if is_process_running "$pid"; then
        log_info "Stopping backend (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        sleep 2

        if is_process_running "$pid"; then
            log_warning "Backend still running, force killing..."
            kill -9 "$pid" 2>/dev/null || true
        fi

        log_success "Backend stopped"
    else
        log_info "Backend not running"
    fi

    rm -f "$BACKEND_PID_FILE"
}

#
# Frontend server
#

start_frontend() {
    log_info "Starting frontend server on port $FRONTEND_PORT..."

    # Enable cleanup trap
    enable_trap

    # Check npm
    if ! command -v npm >/dev/null 2>&1; then
        log_error "npm not found - please install Node.js"
        return 1
    fi

    # Check if already running
    local existing_pid=$(read_pid "$FRONTEND_PID_FILE")
    if [ -n "$existing_pid" ] && is_process_running "$existing_pid"; then
        log_warning "Frontend already running (PID: $existing_pid)"
        if check_frontend_health; then
            log_success "Frontend is healthy"
            return 0
        else
            log_warning "Frontend unhealthy, restarting..."
            kill "$existing_pid" 2>/dev/null || true
            sleep 2
        fi
    fi

    # Cleanup port
    cleanup_port "$FRONTEND_PORT" "Frontend" || return 1

    # Check node_modules
    if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
        log_info "Installing frontend dependencies..."
        cd "$PROJECT_ROOT/frontend"
        npm install || {
            log_error "Failed to install frontend dependencies"
            return 1
        }
    fi

    # Start server
    cd "$PROJECT_ROOT/frontend"
    log_info "Running: npm run dev"

    nohup npm run dev \
        > "$FRONTEND_LOG" 2>&1 &

    local pid=$!
    save_pid "$pid" "$FRONTEND_PID_FILE"
    FRONTEND_PID=$pid  # Store for cleanup trap

    # Wait for startup
    sleep 5

    # Check if still running
    if ! is_process_running "$pid"; then
        log_error "Frontend failed to start"
        log_info "Check logs: tail -f $FRONTEND_LOG"
        return 1
    fi

    # Health check
    if wait_for_health "http://localhost:$FRONTEND_PORT" "Frontend"; then
        log_success "Frontend started successfully (PID: $pid)"
        log_info "Frontend URL: http://localhost:$FRONTEND_PORT"
        log_info "Logs: tail -f $FRONTEND_LOG"
        return 0
    else
        log_error "Frontend health check failed"
        log_info "Check logs: tail -f $FRONTEND_LOG"
        kill "$pid" 2>/dev/null || true
        return 1
    fi
}

stop_frontend() {
    local pid=$(read_pid "$FRONTEND_PID_FILE")

    if [ -z "$pid" ]; then
        log_info "Frontend PID file not found"
        kill_process_on_port "$FRONTEND_PORT"
        return 0
    fi

    if is_process_running "$pid"; then
        log_info "Stopping frontend (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        sleep 2

        if is_process_running "$pid"; then
            log_warning "Frontend still running, force killing..."
            kill -9 "$pid" 2>/dev/null || true
        fi

        log_success "Frontend stopped"
    else
        log_info "Frontend not running"
    fi

    rm -f "$FRONTEND_PID_FILE"
}

#
# Server management
#

start_all() {
    log_info "Starting all servers..."
    echo

    # Enable cleanup trap for graceful shutdown
    enable_trap

    # Pre-flight checks
    check_ports
    check_model
    echo

    local backend_ok=false
    local frontend_ok=false

    # Start backend
    if start_backend; then
        backend_ok=true
    fi

    echo

    # Start frontend
    if start_frontend; then
        frontend_ok=true
    fi

    echo

    # Summary
    if $backend_ok && $frontend_ok; then
        log_success "All servers started successfully!"
        echo
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${GREEN}✓ Backend:${NC}  http://localhost:$BACKEND_PORT"
        echo -e "${GREEN}✓ Frontend:${NC} http://localhost:$FRONTEND_PORT"
        echo -e "${BLUE}ℹ API Docs:${NC} http://localhost:$BACKEND_PORT/docs"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo
        echo "Logs: tail -f logs/backend.log logs/frontend.log"
        echo "Stop: ./scripts/start_servers.sh --stop"
        echo
        return 0
    else
        log_error "Some servers failed to start"
        echo
        echo "Backend: $([ $backend_ok = true ] && echo '✓' || echo '✗')"
        echo "Frontend: $([ $frontend_ok = true ] && echo '✓' || echo '✗')"
        echo
        echo "Check logs in: $LOG_DIR"
        return 1
    fi
}

stop_all() {
    log_info "Stopping all servers..."
    echo

    stop_backend
    echo
    stop_frontend
    echo

    log_success "All servers stopped"
}

show_status() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Server Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo

    # Backend status
    local backend_pid=$(read_pid "$BACKEND_PID_FILE")
    if [ -n "$backend_pid" ] && is_process_running "$backend_pid"; then
        if check_backend_health; then
            echo -e "${GREEN}✓ Backend:${NC} Running (PID: $backend_pid, Port: $BACKEND_PORT) - Healthy"
        else
            echo -e "${YELLOW}⚠ Backend:${NC} Running (PID: $backend_pid, Port: $BACKEND_PORT) - Unhealthy"
        fi
    else
        echo -e "${RED}✗ Backend:${NC} Not running"
    fi

    # Frontend status
    local frontend_pid=$(read_pid "$FRONTEND_PID_FILE")
    if [ -n "$frontend_pid" ] && is_process_running "$frontend_pid"; then
        if check_frontend_health; then
            echo -e "${GREEN}✓ Frontend:${NC} Running (PID: $frontend_pid, Port: $FRONTEND_PORT) - Healthy"
        else
            echo -e "${YELLOW}⚠ Frontend:${NC} Running (PID: $frontend_pid, Port: $FRONTEND_PORT) - Unhealthy"
        fi
    else
        echo -e "${RED}✗ Frontend:${NC} Not running"
    fi

    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

#
# Main
#

show_help() {
    cat << EOF
Market Predictor - Automated Server Start Script

Usage:
  $0 [OPTIONS]

Options:
  --backend-only      Start backend server only
  --frontend-only     Start frontend server only
  --stop              Stop all servers
  --status            Show server status
  --help              Show this help message

Environment Variables:
  BACKEND_PORT        Backend port (default: 8000)
  FRONTEND_PORT       Frontend port (default: 5173)
  PYTHON_CMD          Python command (default: python3)
  MAX_RETRIES         Max startup retries (default: 3)
  HEALTH_TIMEOUT      Health check timeout in seconds (default: 30)

Examples:
  # Start both servers
  $0

  # Start backend only
  $0 --backend-only

  # Use custom ports
  BACKEND_PORT=8080 FRONTEND_PORT=3000 $0

  # Stop all servers
  $0 --stop

  # Check status
  $0 --status

Logs:
  Backend:  $BACKEND_LOG
  Frontend: $FRONTEND_LOG
  Startup:  $STARTUP_LOG

EOF
}

main() {
    local mode="all"

    case "${1:-}" in
        --backend-only)
            mode="backend"
            ;;
        --frontend-only)
            mode="frontend"
            ;;
        --stop)
            stop_all
            exit $?
            ;;
        --status)
            show_status
            exit 0
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        "")
            mode="all"
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac

    case "$mode" in
        backend)
            start_backend
            exit $?
            ;;
        frontend)
            start_frontend
            exit $?
            ;;
        all)
            start_all
            exit $?
            ;;
    esac
}

# Run main function
main "$@"
