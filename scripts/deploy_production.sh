#!/bin/bash
# Automated Production Deployment Script
# This script automates the entire deployment process

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 POC-MarketPredictor-ML - Automated Deployment${NC}"
echo "=================================================="
echo ""

# Check if required tools are installed
check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    MISSING_DEPS=0
    
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}✗${NC} curl is not installed"
        MISSING_DEPS=$((MISSING_DEPS + 1))
    else
        echo -e "${GREEN}✓${NC} curl installed"
    fi
    
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}✗${NC} jq is not installed (brew install jq)"
        MISSING_DEPS=$((MISSING_DEPS + 1))
    else
        echo -e "${GREEN}✓${NC} jq installed"
    fi
    
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⚠${NC} GitHub CLI not installed (optional: brew install gh)"
    else
        echo -e "${GREEN}✓${NC} GitHub CLI installed"
    fi
    
    if [ $MISSING_DEPS -gt 0 ]; then
        echo -e "${RED}Please install missing dependencies and try again${NC}"
        exit 1
    fi
    
    echo ""
}

# Run security checks
run_security_checks() {
    echo -e "${YELLOW}Running security checks...${NC}"
    
    if [ -f "scripts/security_check.sh" ]; then
        ./scripts/security_check.sh
        if [ $? -ne 0 ]; then
            echo -e "${RED}Security checks failed! Fix issues before deployment.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠${NC} security_check.sh not found, skipping"
    fi
    
    echo ""
}

# Deploy to Railway
deploy_railway() {
    echo -e "${YELLOW}Deploying backend to Railway...${NC}"
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        echo -e "${YELLOW}Installing Railway CLI...${NC}"
        curl -fsSL https://railway.app/install.sh | sh
        export PATH="$HOME/.railway/bin:$PATH"
    fi
    
    # Check if RAILWAY_TOKEN is set
    if [ -z "$RAILWAY_TOKEN" ]; then
        echo -e "${RED}Error: RAILWAY_TOKEN environment variable not set${NC}"
        echo "Get your token from: https://railway.app/account/tokens"
        echo "Then run: export RAILWAY_TOKEN=your-token"
        exit 1
    fi
    
    # Link project or create new one
    if [ ! -f "railway.json" ]; then
        echo -e "${YELLOW}No railway.json found. Linking or creating project...${NC}"
        railway init
    fi
    
    # Deploy
    echo -e "${BLUE}Deploying to Railway...${NC}"
    railway up --detach
    
    # Wait for deployment
    echo "Waiting for deployment to complete..."
    sleep 30
    
    # Get deployment URL
    BACKEND_URL=$(railway status --json | jq -r '.deployments[0].url')
    
    if [ "$BACKEND_URL" == "null" ] || [ -z "$BACKEND_URL" ]; then
        echo -e "${RED}Failed to get backend URL${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓${NC} Backend deployed to: $BACKEND_URL"
    
    # Test health endpoint
    echo "Testing backend health..."
    for i in {1..10}; do
        if curl -f -s "$BACKEND_URL/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Backend is healthy!"
            echo "$BACKEND_URL" > .backend-url
            return 0
        fi
        echo "Waiting for backend... ($i/10)"
        sleep 10
    done
    
    echo -e "${RED}Backend health check failed${NC}"
    exit 1
}

# Deploy to Vercel
deploy_vercel() {
    echo ""
    echo -e "${YELLOW}Deploying frontend to Vercel...${NC}"
    
    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}Installing Vercel CLI...${NC}"
        npm install -g vercel
    fi
    
    # Check if backend URL exists
    if [ ! -f ".backend-url" ]; then
        echo -e "${RED}Backend URL not found. Deploy backend first.${NC}"
        exit 1
    fi
    
    BACKEND_URL=$(cat .backend-url)
    echo "Using backend URL: $BACKEND_URL"
    
    # Change to frontend directory
    cd frontend
    
    # Deploy to Vercel
    echo -e "${BLUE}Deploying to Vercel...${NC}"
    FRONTEND_URL=$(vercel --prod \
        --build-env VITE_API_URL="$BACKEND_URL" \
        --yes \
        --confirm | grep -oP 'https://[^\s]+' | tail -1)
    
    if [ -z "$FRONTEND_URL" ]; then
        echo -e "${RED}Failed to get frontend URL${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓${NC} Frontend deployed to: $FRONTEND_URL"
    echo "$FRONTEND_URL" > ../.frontend-url
    
    cd ..
    
    # Test frontend
    echo "Testing frontend..."
    sleep 10
    if curl -f -s "$FRONTEND_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Frontend is accessible!"
    else
        echo -e "${YELLOW}⚠${NC} Frontend may need a few moments to be fully ready"
    fi
}

# Update CORS configuration
update_cors() {
    echo ""
    echo -e "${YELLOW}Updating CORS configuration...${NC}"
    
    if [ ! -f ".frontend-url" ]; then
        echo -e "${RED}Frontend URL not found${NC}"
        exit 1
    fi
    
    FRONTEND_URL=$(cat .frontend-url)
    
    # Check if already configured
    if grep -q "$FRONTEND_URL" trading_fun/server.py; then
        echo -e "${GREEN}✓${NC} CORS already configured"
        return 0
    fi
    
    # Create backup
    cp trading_fun/server.py trading_fun/server.py.bak
    
    # Add CORS origin (macOS compatible)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "/# Production - Add your deployed frontend URLs below:/a\\
        \"$FRONTEND_URL\",
" trading_fun/server.py
    else
        sed -i "/# Production - Add your deployed frontend URLs below:/a\        \"$FRONTEND_URL\"," trading_fun/server.py
    fi
    
    echo -e "${GREEN}✓${NC} CORS configuration updated"
    
    # Commit and push
    echo "Committing CORS update..."
    git add trading_fun/server.py
    git commit -m "chore: add $FRONTEND_URL to CORS origins [automated]" || echo "No changes to commit"
    git push origin main
    
    echo -e "${GREEN}✓${NC} Changes pushed to GitHub"
    
    # Redeploy backend with updated CORS
    echo "Redeploying backend with updated CORS..."
    railway up --detach
    sleep 30
    
    echo -e "${GREEN}✓${NC} Backend redeployed with new CORS settings"
}

# Run production tests
run_production_tests() {
    echo ""
    echo -e "${YELLOW}Running production tests...${NC}"
    
    BACKEND_URL=$(cat .backend-url)
    
    if [ -f "scripts/test_deployment.sh" ]; then
        ./scripts/test_deployment.sh "$BACKEND_URL"
    else
        echo -e "${YELLOW}⚠${NC} test_deployment.sh not found, skipping tests"
    fi
}

# Create deployment summary
create_summary() {
    echo ""
    echo -e "${BLUE}=================================================="
    echo -e "           Deployment Summary"
    echo -e "==================================================${NC}"
    echo ""
    
    BACKEND_URL=$(cat .backend-url 2>/dev/null || echo "N/A")
    FRONTEND_URL=$(cat .frontend-url 2>/dev/null || echo "N/A")
    
    echo -e "${GREEN}✅ Deployment Complete!${NC}"
    echo ""
    echo "Backend URL:  $BACKEND_URL"
    echo "Frontend URL: $FRONTEND_URL"
    echo ""
    echo "API Documentation: ${BACKEND_URL}/docs"
    echo "Health Check:      ${BACKEND_URL}/health"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Test the frontend in your browser"
    echo "2. Verify all features work correctly"
    echo "3. Monitor Railway logs for any errors"
    echo "4. Check Vercel analytics"
    echo "5. Set up custom domain (optional)"
    echo ""
    
    # Save summary to file
    cat > deployment-summary.txt << EOF
POC-MarketPredictor-ML Deployment Summary
==========================================

Deployed: $(date)

URLs:
- Backend:  $BACKEND_URL
- Frontend: $FRONTEND_URL

Resources:
- API Docs: ${BACKEND_URL}/docs
- Health:   ${BACKEND_URL}/health

Platform Dashboards:
- Railway: https://railway.app
- Vercel:  https://vercel.com

Status: ✅ Deployed Successfully
EOF
    
    echo -e "${GREEN}Deployment summary saved to: deployment-summary.txt${NC}"
}

# Cleanup
cleanup() {
    echo ""
    echo "Cleaning up temporary files..."
    rm -f .backend-url .frontend-url
}

# Main deployment flow
main() {
    # Set trap for cleanup on exit
    trap cleanup EXIT
    
    # Step 1: Check dependencies
    check_dependencies
    
    # Step 2: Security checks
    run_security_checks
    
    # Step 3: Deploy backend
    deploy_railway
    
    # Step 4: Deploy frontend
    deploy_vercel
    
    # Step 5: Update CORS
    update_cors
    
    # Step 6: Run tests
    run_production_tests
    
    # Step 7: Create summary
    create_summary
    
    echo -e "${GREEN}🎉 Deployment automation complete!${NC}"
}

# Parse command line arguments
case "${1:-}" in
    --backend-only)
        check_dependencies
        run_security_checks
        deploy_railway
        ;;
    --frontend-only)
        check_dependencies
        deploy_vercel
        ;;
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --backend-only   Deploy only backend to Railway"
        echo "  --frontend-only  Deploy only frontend to Vercel"
        echo "  --help, -h       Show this help message"
        echo ""
        echo "Environment variables required:"
        echo "  RAILWAY_TOKEN    Your Railway API token"
        echo ""
        ;;
    *)
        main
        ;;
esac
