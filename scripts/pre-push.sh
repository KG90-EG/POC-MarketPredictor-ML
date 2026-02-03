#!/usr/bin/env bash

# Pre-push hook to run quality checks locally before pushing
# Prevents pushing code that will fail CI/CD
# Install: ln -sf ../../scripts/pre-push.sh .git/hooks/pre-push

set -e

echo "🔍 Running pre-push quality checks..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Function to run check
run_check() {
    local name=$1
    local command=$2
    
    echo -n "  ⏳ $name... "
    
    if eval "$command" > /tmp/pre-push-$$.log 2>&1; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${RED}❌${NC}"
        echo "     Error output:"
        cat /tmp/pre-push-$$.log | sed 's/^/     /'
        rm /tmp/pre-push-$$.log
        return 1
    fi
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Must run from repository root!${NC}"
    exit 1
fi

echo "📦 Backend Checks"
echo "═══════════════════"

# Check Python formatting
if ! run_check "Black formatting" "black --check --line-length=100 src/ scripts/ tests/ 2>&1"; then
    echo -e "     ${YELLOW}Fix with: black --line-length=100 src/ scripts/ tests/${NC}"
    FAILED=1
fi

# Check import sorting
if ! run_check "Import sorting" "isort --check-only --profile black --line-length 100 src/ scripts/ tests/ 2>&1"; then
    echo -e "     ${YELLOW}Fix with: isort --profile black --line-length 100 src/ scripts/ tests/${NC}"
    FAILED=1
fi

# Run flake8
if ! run_check "Flake8 linting" "flake8 src/ scripts/ tests/ --max-line-length=100 --extend-ignore=E203,W503,F401,F811,F541,W293,E501,D100,D101,D102,D103,D104,D105,D107,C901,E731 --count 2>&1"; then
    echo -e "     ${YELLOW}Fix linting errors manually${NC}"
    FAILED=1
fi

# Run pytest
if ! run_check "Backend tests" "pytest tests/ --verbose --tb=short --ignore=tests/phase1/ --ignore=tests/phase2/ --ignore=tests/test_crypto.py --ignore=tests/test_integration.py -k 'not (test_ranking or test_predict)' 2>&1"; then
    echo -e "     ${RED}Tests failed! Fix before pushing.${NC}"
    FAILED=1
fi

echo ""
echo "🎨 Frontend Checks"
echo "═══════════════════"

# Check if frontend exists
if [ -d "frontend" ]; then
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "  ${YELLOW}⚠️  Installing frontend dependencies...${NC}"
        npm ci
    fi
    
    # Check Prettier formatting
    if ! run_check "Prettier formatting" "npm run format:check 2>&1"; then
        echo -e "     ${YELLOW}Fix with: cd frontend && npm run format${NC}"
        FAILED=1
    fi
    
    # Run ESLint
    if ! run_check "ESLint" "npm run lint 2>&1"; then
        echo -e "     ${YELLOW}Fix with: cd frontend && npm run lint:fix${NC}"
        FAILED=1
    fi
    
    # Run frontend tests
    if ! run_check "Frontend tests" "npm run test 2>&1"; then
        echo -e "     ${RED}Frontend tests failed! Fix before pushing.${NC}"
        FAILED=1
    fi
    
    cd ..
else
    echo -e "  ${YELLOW}⚠️  Frontend directory not found, skipping...${NC}"
fi

echo ""
echo "🐳 Docker Check"
echo "═══════════════════"

# Check if Dockerfile exists and builds
if [ -f "Dockerfile" ]; then
    if ! run_check "Docker build" "docker build -t market-predictor:pre-push-test . 2>&1"; then
        echo -e "     ${RED}Docker build failed!${NC}"
        FAILED=1
    else
        # Cleanup test image
        docker rmi market-predictor:pre-push-test > /dev/null 2>&1 || true
    fi
else
    echo -e "  ${YELLOW}⚠️  Dockerfile not found, skipping...${NC}"
fi

echo ""
echo "📁 Repository Structure"
echo "════════════════════════"

# Check for loose files in root
LOOSE_FILES=$(find . -maxdepth 1 -type f ! -name ".*" -exec basename {} \; | grep -v -E "^(Dockerfile|LICENSE|Makefile|README.md|requirements.txt|docker-compose.yml|docker-compose.monitoring.yml|CHANGELOG.*|best_hyperparameters.json|pyproject.toml|pytest.ini|backtest|training)$" || true)

if [ -n "$LOOSE_FILES" ]; then
    echo -e "  ${RED}❌ Loose files in root:${NC}"
    echo "$LOOSE_FILES" | sed 's/^/     /'
    echo -e "     ${YELLOW}Move to appropriate subdirectories${NC}"
    FAILED=1
else
    echo -e "  ${GREEN}✅ Repository structure${NC}"
fi

# Cleanup temp files
rm -f /tmp/pre-push-$$.log

echo ""
echo "═══════════════════════════════════════"

if [ $FAILED -eq 1 ]; then
    echo -e "${RED}❌ Pre-push checks FAILED!${NC}"
    echo ""
    echo "Your code has quality issues that will fail CI/CD."
    echo "Please fix the issues above before pushing."
    echo ""
    echo "To bypass this check (NOT RECOMMENDED):"
    echo "  git push --no-verify"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ All pre-push checks PASSED!${NC}"
    echo ""
    echo "Your code is ready to push! 🚀"
    echo ""
    exit 0
fi
