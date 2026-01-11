#!/bin/bash
# Complete Repository Cleanup Script
# Removes cache, old files, and organizes structure
# Safe to run repeatedly

set -e
cd "$(dirname "$0")/.."

echo "🧹 REPOSITORY CLEANUP"
echo "══════════════════════════════════════════════════════"
echo ""

DELETED_COUNT=0

# Function to safely delete
safe_delete() {
    local path="$1"
    local reason="$2"
    if [ -e "$path" ]; then
        rm -rf "$path"
        echo "   ✓ Removed: $path ($reason)"
        DELETED_COUNT=$((DELETED_COUNT + 1))
    fi
}

# ============================================================
# 1. Python Cache Files
# ============================================================
echo "1️⃣  Removing Python cache files..."
CACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l | tr -d ' ')
if [ "$CACHE_COUNT" -gt 0 ]; then
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    echo "   ✓ Removed $CACHE_COUNT __pycache__ directories"
    DELETED_COUNT=$((DELETED_COUNT + CACHE_COUNT))
else
    echo "   ✓ No Python cache found"
fi

# ============================================================
# 2. Pytest Cache
# ============================================================
echo ""
echo "2️⃣  Cleaning pytest cache..."
PYTEST_COUNT=$(find . -type d -name ".pytest_cache" -not -path "./.pytest_cache" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYTEST_COUNT" -gt 0 ]; then
    find . -type d -name ".pytest_cache" -not -path "./.pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    echo "   ✓ Removed $PYTEST_COUNT pytest cache directories"
    DELETED_COUNT=$((DELETED_COUNT + PYTEST_COUNT))
else
    echo "   ✓ No pytest cache found"
fi

# ============================================================
# 3. OS-Specific Files
# ============================================================
echo ""
echo "3️⃣  Removing OS-specific files..."
DS_COUNT=$(find . -type f -name ".DS_Store" 2>/dev/null | wc -l | tr -d ' ')
if [ "$DS_COUNT" -gt 0 ]; then
    find . -type f -name ".DS_Store" -delete 2>/dev/null || true
    echo "   ✓ Removed $DS_COUNT .DS_Store files"
    DELETED_COUNT=$((DELETED_COUNT + DS_COUNT))
else
    echo "   ✓ No .DS_Store files found"
fi

# Thumbs.db (Windows)
find . -type f -name "Thumbs.db" -delete 2>/dev/null || true

# ============================================================
# 4. Old Model Files (keep only prod_model.bin)
# ============================================================
echo ""
echo "4️⃣  Cleaning old model files..."
if [ -d "models" ]; then
    cd models
    OLD_MODELS=0
    for file in *.bin *.pkl; do
        if [ -f "$file" ] && [ "$file" != "prod_model.bin" ]; then
            rm -f "$file"
            echo "   ✓ Removed old model: $file"
            OLD_MODELS=$((OLD_MODELS + 1))
            DELETED_COUNT=$((DELETED_COUNT + 1))
        fi
    done

    # Clean old feature files
    for file in *_features.txt; do
        if [ -f "$file" ]; then
            rm -f "$file"
            OLD_MODELS=$((OLD_MODELS + 1))
            DELETED_COUNT=$((DELETED_COUNT + 1))
        fi
    done

    cd ..
    if [ $OLD_MODELS -eq 0 ]; then
        echo "   ✓ Only current model exists"
    fi
else
    echo "   ⚠️  models/ directory not found"
fi

# ============================================================
# 5. MLflow Runs (keep last 5)
# ============================================================
echo ""
echo "5️⃣  Cleaning old MLflow runs..."
if [ -d "mlruns" ]; then
    # Count experiment directories (excluding 0 which is default)
    RUN_COUNT=$(find mlruns -mindepth 2 -maxdepth 2 -type d 2>/dev/null | wc -l | tr -d ' ')

    if [ "$RUN_COUNT" -gt 5 ]; then
        echo "   Found $RUN_COUNT runs, keeping last 5..."
        find mlruns -mindepth 2 -maxdepth 2 -type d 2>/dev/null | \
            sort | \
            head -n $((RUN_COUNT - 5)) | \
            xargs rm -rf
        DELETED=$((RUN_COUNT - 5))
        echo "   ✓ Removed $DELETED old experiment runs"
        DELETED_COUNT=$((DELETED_COUNT + DELETED))
    else
        echo "   ✓ Only $RUN_COUNT runs (keeping all)"
    fi
else
    echo "   ⚠️  mlruns/ directory not found"
fi

# ============================================================
# 6. Temporary & Log Files
# ============================================================
echo ""
echo "6️⃣  Organizing temporary files..."

# Move PID files to logs/
if [ -f ".backend.pid" ]; then
    mkdir -p logs
    mv .backend.pid logs/ 2>/dev/null || true
    echo "   ✓ Moved .backend.pid → logs/"
fi

if [ -f ".frontend.pid" ]; then
    mkdir -p logs
    mv .frontend.pid logs/ 2>/dev/null || true
    echo "   ✓ Moved .frontend.pid → logs/"
fi

# Remove old log files from root
safe_delete "training_output.log" "should be in logs/"
safe_delete "debug.log" "should be in logs/"
safe_delete "server.log" "should be in logs/"

# Clean old logs (keep last 7 days)
if [ -d "logs" ]; then
    find logs -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
fi

# ============================================================
# 7. Node Modules (optional - uncomment if needed)
# ============================================================
echo ""
echo "7️⃣  Checking node_modules..."
if [ -d "frontend/node_modules" ]; then
    SIZE=$(du -sh frontend/node_modules 2>/dev/null | cut -f1)
    echo "   ℹ️  node_modules size: $SIZE"
    echo "   💡 Run 'rm -rf frontend/node_modules && cd frontend && npm install' to refresh"
else
    echo "   ⚠️  node_modules not found (run 'cd frontend && npm install')"
fi

# ============================================================
# 8. Empty Directories
# ============================================================
echo ""
echo "8️⃣  Removing empty directories..."
EMPTY_DIRS=$(find . -type d -empty \
    -not -path "./.git/*" \
    -not -path "./.venv/*" \
    -not -path "./node_modules/*" \
    -not -path "./frontend/node_modules/*" \
    2>/dev/null || true)

if [ -n "$EMPTY_DIRS" ]; then
    EMPTY_COUNT=0
    echo "$EMPTY_DIRS" | while read dir; do
        if [ -n "$dir" ] && [ -d "$dir" ]; then
            rmdir "$dir" 2>/dev/null && echo "   ✓ Removed empty: $dir" && EMPTY_COUNT=$((EMPTY_COUNT + 1)) || true
        fi
    done
else
    echo "   ✓ No empty directories found"
fi

# ============================================================
# 9. Verify Critical Directories
# ============================================================
echo ""
echo "9️⃣  Verifying directory structure..."
MISSING=0

check_dir() {
    if [ ! -d "$1" ]; then
        echo "   ⚠️  Missing: $1"
        MISSING=$((MISSING + 1))
    fi
}

check_dir "src/trading_engine"
check_dir "frontend/src"
check_dir "tests"
check_dir "docs"
check_dir "logs"
check_dir "models"

if [ $MISSING -eq 0 ]; then
    echo "   ✓ All critical directories present"
fi

# ============================================================
# Summary
# ============================================================
echo ""
echo "══════════════════════════════════════════════════════"
echo "✅ CLEANUP COMPLETE"
echo "══════════════════════════════════════════════════════"
echo ""
if [ $DELETED_COUNT -gt 0 ]; then
    echo "📊 Removed/Organized: $DELETED_COUNT items"
else
    echo "📊 Repository already clean"
fi
echo ""
echo "Next steps:"
echo "  make start    # Start servers"
echo "  make test     # Run tests"
echo "  git status    # See changes"
echo ""
