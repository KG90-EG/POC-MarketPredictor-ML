#!/bin/bash
# Repository Cleanup Script
# Moves loose files into proper subdirectories

set -e
cd "$(dirname "$0")"

echo "🧹 Starting Repository Cleanup..."
echo ""

# 1. Move config files
echo "1️⃣ Moving config files..."
mkdir -p config/ml
if [ -f "best_hyperparameters.json" ]; then
    mv best_hyperparameters.json config/ml/
    echo "   ✓ best_hyperparameters.json → config/ml/"
fi

# 2. Move documentation
echo ""
echo "2️⃣ Moving documentation..."
if [ -f "MODEL_RETRAINING_SUMMARY.md" ]; then
    mv MODEL_RETRAINING_SUMMARY.md docs/development/
    echo "   ✓ MODEL_RETRAINING_SUMMARY.md → docs/development/"
fi
if [ -f "QUICKSTART.md" ]; then
    mv QUICKSTART.md docs/getting-started/
    echo "   ✓ QUICKSTART.md → docs/getting-started/"
fi
if [ -f "README_SERVERS.md" ]; then
    mv README_SERVERS.md docs/deployment/
    echo "   ✓ README_SERVERS.md → docs/deployment/"
fi
if [ -f "TRADING_SIGNALS_ENHANCEMENT.md" ]; then
    mv TRADING_SIGNALS_ENHANCEMENT.md docs/features/
    echo "   ✓ TRADING_SIGNALS_ENHANCEMENT.md → docs/features/"
fi

# 3. Clean up temp files
echo ""
echo "3️⃣ Cleaning temp files..."
if [ -f ".backend.pid" ]; then
    mv .backend.pid logs/
    echo "   ✓ .backend.pid → logs/"
fi
if [ -f ".frontend.pid" ]; then
    mv .frontend.pid logs/
    echo "   ✓ .frontend.pid → logs/"
fi
if [ -f "training_output.log" ]; then
    mv training_output.log logs/
    echo "   ✓ training_output.log → logs/"
fi

echo ""
echo "✅ Repository cleanup complete!"
echo ""
echo "📁 Final root directory structure:"
ls -1 | grep -v "^\." | head -15
