#!/bin/bash
# Deep Repository Audit & Cleanup
# Safe to run repeatedly - only cleans actual clutter
#
# Usage: ./scripts/deep_cleanup.sh
#        make deep-clean

set -e
cd "$(dirname "$0")/.."

echo "🔍 REPOSITORY DEEP CLEANUP"
echo "============================"
echo ""
echo "Safely removing outdated files, duplicates, and cache..."
echo ""

# Track what we're deleting
DELETED_COUNT=0

# Function to delete and log
delete_file() {
    local file="$1"
    local reason="$2"
    if [ -f "$file" ] || [ -d "$file" ]; then
        rm -rf "$file"
        echo "   ✗ Deleted: $file"
        echo "      Reason: $reason"
        DELETED_COUNT=$((DELETED_COUNT + 1))
    fi
}

echo "1️⃣ Checking for History/Archive Folders"
echo "────────────────────────────────────────────────────"
if [ -d "docs/history" ]; then
    echo "   Found history folder with outdated docs"
    rm -rf docs/history
    echo "   ✗ Deleted: docs/history/"
    DELETED_COUNT=$((DELETED_COUNT + 1))
fi

if [ -d ".archive" ]; then
    echo "   Found archive folder"
    rm -rf .archive
    echo "   ✗ Deleted: .archive/"
    DELETED_COUNT=$((DELETED_COUNT + 1))
fi

if [ $DELETED_COUNT -eq 0 ]; then
    echo "   ✓ No history/archive folders found"
fi

echo ""
echo "2️⃣ Removing Duplicate/Outdated Documentation"
echo "────────────────────────────────────────────────────"
INITIAL_COUNT=$DELETED_COUNT

# Deployment duplicates (check common patterns)
delete_file "docs/deployment/DEPLOYMENT.md" "Duplicate of DEPLOYMENT_GUIDE.md"
delete_file "docs/deployment/BACKEND_DEPLOYMENT.md" "Outdated, consolidated"
delete_file "docs/deployment/FRONTEND_DEPLOYMENT.md" "Outdated, consolidated"
delete_file "docs/deployment/PRODUCTION_DEPLOYMENT.md" "Duplicate of PRODUCTION_READY.md"
delete_file "docs/deployment/AUTOMATED_DEPLOYMENT.md" "Outdated automation docs"

# Features duplicates
delete_file "docs/features/PHASE_1_SUMMARY.md" "Historical phase doc"
delete_file "docs/features/PHASE1_WATCHLISTS_SUMMARY.md" "Historical phase doc"
delete_file "docs/features/TRADING_SIGNALS_ENHANCEMENT.md" "Consolidated"

# Root docs level
delete_file "docs/IMPROVEMENTS_SUMMARY.md" "Outdated summary"
delete_file "docs/TRAINING_GUIDE.md" "Duplicate (exists in getting-started/)"
delete_file "docs/SERVER_MANAGEMENT.md" "Outdated"

# Development duplicates
delete_file "docs/development/MODEL_RETRAINING_SUMMARY.md" "Outdated summary"

# Old HTML/RST files
delete_file "docs/index.html" "Outdated HTML"
delete_file "docs/index.rst" "Outdated RST"

if [ $DELETED_COUNT -eq $INITIAL_COUNT ]; then
    echo "   ✓ No duplicate docs found"
fi

echo ""
echo "3️⃣ Cleaning Old Model Files"
echo "────────────────────────────────────────────────────"
INITIAL_COUNT=$DELETED_COUNT

if [ -d "models" ]; then
    cd models
    # Keep only prod_model.bin and README.md
    for model in *.bin; do
        if [ -f "$model" ] && [ "$model" != "prod_model.bin" ]; then
            rm "$model"
            echo "   ✗ Deleted old model: $model"
            DELETED_COUNT=$((DELETED_COUNT + 1))
        fi
    done
    cd ..
fi

if [ $DELETED_COUNT -eq $INITIAL_COUNT ]; then
    echo "   ✓ Only current model exists"
fi

echo ""
echo "4️⃣ Cleaning Unused Deployment Configs"
echo "────────────────────────────────────────────────────"
INITIAL_COUNT=$DELETED_COUNT

# Remove configs for platforms we don't use
delete_file "config/deployment/netlify.toml" "Unused platform"
delete_file "config/deployment/render.yaml" "Unused platform"
delete_file "config/deployment/Procfile" "Unused platform (Heroku)"
delete_file "frontend/netlify.toml" "Unused platform"
delete_file "frontend/vercel.json" "Unused platform"

if [ $DELETED_COUNT -eq $INITIAL_COUNT ]; then
    echo "   ✓ Only active deployment configs"
fi

echo ""
echo "5️⃣ Cleaning MLflow Runs (keeping last 10)"
echo "────────────────────────────────────────────────────"
if [ -d "mlruns" ]; then
    RUN_COUNT=$(find mlruns -mindepth 2 -maxdepth 2 -type d 2>/dev/null | wc -l | tr -d ' ')

    if [ "$RUN_COUNT" -gt 10 ]; then
        echo "   Found $RUN_COUNT runs, keeping last 10..."
        find mlruns -mindepth 2 -maxdepth 2 -type d 2>/dev/null | sort | head -n $((RUN_COUNT - 10)) | xargs rm -rf
        DELETED=$((RUN_COUNT - 10))
        echo "   ✗ Deleted $DELETED old experiment runs"
        DELETED_COUNT=$((DELETED_COUNT + DELETED))
    else
        echo "   ✓ Run count ($RUN_COUNT) is manageable"
    fi
fi

echo ""
echo "6️⃣ Removing Cache & Temporary Files"
echo "────────────────────────────────────────────────────"
# Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Pytest cache (except root)
find . -type d -name ".pytest_cache" -not -path "./.pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# OS files
find . -type f -name ".DS_Store" -delete 2>/dev/null || true

# Temp logs in root (should be in logs/)
delete_file "training_output.log" "Should be in logs/"
delete_file "debug.log" "Should be in logs/"

# PID files in root (should be in logs/)
delete_file ".backend.pid" "Should be in logs/"
delete_file ".frontend.pid" "Should be in logs/"

echo "   ✓ Cache cleaned"

echo ""
echo "7️⃣ Removing Empty Directories"
echo "────────────────────────────────────────────────────"
EMPTY_DIRS=$(find . -type d -empty -not -path "./.git/*" -not -path "./.venv/*" -not -path "./node_modules/*" -not -path "./frontend/node_modules/*" 2>/dev/null || true)
if [ -n "$EMPTY_DIRS" ]; then
    echo "$EMPTY_DIRS" | while read dir; do
        if [ -n "$dir" ]; then
            rmdir "$dir" 2>/dev/null && echo "   ✗ Removed: $dir" || true
        fi
    done
else
    echo "   ✓ No empty directories"
fi

echo ""
echo "8️⃣ Auto-organizing Misplaced Documentation"
echo "────────────────────────────────────────────────────"
MOVED_COUNT=0

# Move docs to correct subfolders
if [ -f "docs/FAQ.md" ]; then
    mv docs/FAQ.md docs/getting-started/ 2>/dev/null && echo "   ✓ Moved: FAQ.md → getting-started/" && MOVED_COUNT=$((MOVED_COUNT + 1)) || true
fi

if [ -f "docs/TRADER_GUIDE.md" ]; then
    mv docs/TRADER_GUIDE.md docs/getting-started/ 2>/dev/null && echo "   ✓ Moved: TRADER_GUIDE.md → getting-started/" && MOVED_COUNT=$((MOVED_COUNT + 1)) || true
fi

if [ -f "docs/ACCESSIBILITY_AUDIT.md" ]; then
    mv docs/ACCESSIBILITY_AUDIT.md docs/development/ 2>/dev/null && echo "   ✓ Moved: ACCESSIBILITY_AUDIT.md → development/" && MOVED_COUNT=$((MOVED_COUNT + 1)) || true
fi

# Move any .md files from root to docs/
for mdfile in *.md; do
    if [ -f "$mdfile" ] && [ "$mdfile" != "README.md" ] && [ "$mdfile" != "LICENSE" ]; then
        mv "$mdfile" docs/ 2>/dev/null && echo "   ✓ Moved: $mdfile → docs/" && MOVED_COUNT=$((MOVED_COUNT + 1)) || true
    fi
done

if [ $MOVED_COUNT -eq 0 ]; then
    echo "   ✓ All docs in correct locations"
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ CLEANUP COMPLETE!"
echo "═══════════════════════════════════════════════════"
echo ""
if [ $DELETED_COUNT -gt 0 ]; then
    echo "📊 Removed $DELETED_COUNT items"
else
    echo "📊 Repository already clean!"
fi
echo ""
echo "🎯 Run 'make check-structure' to verify organization"
echo "🎯 Run 'git status' to see changes"
