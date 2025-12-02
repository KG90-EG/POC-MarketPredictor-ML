#!/bin/bash
# Deployment Security Checklist Script
# Run this before deploying to production

set -e

echo "🔒 POC-MarketPredictor-ML - Security Checklist"
echo "=============================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counter
ISSUES=0

echo "1. Checking .gitignore..."
if grep -q "\.env" .gitignore && grep -q "__pycache__" .gitignore && grep -q "\.venv" .gitignore; then
    echo -e "${GREEN}✓${NC} .gitignore is properly configured"
else
    echo -e "${RED}✗${NC} .gitignore missing critical entries (.env, __pycache__, .venv)"
    ISSUES=$((ISSUES + 1))
fi

echo ""
echo "2. Checking for exposed secrets in code..."
if git grep -i "sk-proj-" -- "*.py" "*.js" "*.jsx" "*.ts" "*.tsx" 2>/dev/null; then
    echo -e "${RED}✗${NC} Found potential OpenAI API key in code!"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}✓${NC} No exposed API keys found in code"
fi

echo ""
echo "3. Checking for .env file in repository..."
if git ls-files | grep -q "^\.env$"; then
    echo -e "${RED}✗${NC} .env file is tracked by git! Remove it immediately!"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}✓${NC} .env file is not tracked"
fi

echo ""
echo "4. Checking if .env.example exists..."
if [ -f ".env.example" ]; then
    echo -e "${GREEN}✓${NC} .env.example exists"
else
    echo -e "${YELLOW}⚠${NC} .env.example not found (recommended)"
fi

echo ""
echo "5. Checking CORS configuration..."
if grep -q "# Production - Add your deployed frontend URLs" trading_fun/server.py; then
    echo -e "${GREEN}✓${NC} CORS has production placeholder comments"
else
    echo -e "${YELLOW}⚠${NC} CORS configuration may need production URLs"
fi

echo ""
echo "6. Checking for hardcoded credentials..."
if git grep -iE "(password|api_key|secret|token).*=.*['\"][^'\"]{8,}" -- "*.py" "*.js" "*.jsx" 2>/dev/null | grep -v ".example" | grep -v "# " | grep -v ".vite/" | grep -v "node_modules/"; then
    echo -e "${RED}✗${NC} Found potential hardcoded credentials!"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}✓${NC} No obvious hardcoded credentials found"
fi

echo ""
echo "7. Checking Python dependencies..."
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓${NC} requirements.txt exists"
    if command -v pip-audit &> /dev/null; then
        echo "   Running pip-audit..."
        pip-audit -r requirements.txt || echo -e "${YELLOW}⚠${NC} pip-audit found issues (review manually)"
    else
        echo -e "${YELLOW}⚠${NC} pip-audit not installed (run: pip install pip-audit)"
    fi
else
    echo -e "${RED}✗${NC} requirements.txt not found"
    ISSUES=$((ISSUES + 1))
fi

echo ""
echo "8. Checking Node.js dependencies..."
if [ -f "frontend/package.json" ]; then
    echo -e "${GREEN}✓${NC} package.json exists"
    echo "   Running npm audit..."
    (cd frontend && npm audit --production 2>/dev/null) || echo -e "${YELLOW}⚠${NC} npm audit found issues (review manually)"
else
    echo -e "${YELLOW}⚠${NC} package.json not found"
fi

echo ""
echo "9. Checking deployment configs..."
if [ -f "railway.toml" ] && [ -f "Procfile" ]; then
    echo -e "${GREEN}✓${NC} Backend deployment configs exist (railway.toml, Procfile)"
else
    echo -e "${YELLOW}⚠${NC} Some backend deployment configs missing"
fi

if [ -f "frontend/vercel.json" ]; then
    echo -e "${GREEN}✓${NC} Frontend deployment config exists (vercel.json)"
else
    echo -e "${YELLOW}⚠${NC} Frontend deployment config missing"
fi

echo ""
echo "10. Checking for TODO/FIXME comments..."
TODO_COUNT=$(git grep -i "TODO\|FIXME" -- "*.py" "*.js" "*.jsx" 2>/dev/null | wc -l)
if [ "$TODO_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠${NC} Found $TODO_COUNT TODO/FIXME comments (review before deployment)"
else
    echo -e "${GREEN}✓${NC} No TODO/FIXME comments found"
fi

echo ""
echo "=============================================="
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ Security check passed! Ready for deployment.${NC}"
    exit 0
else
    echo -e "${RED}✗ Found $ISSUES security issues. Fix them before deployment!${NC}"
    exit 1
fi
