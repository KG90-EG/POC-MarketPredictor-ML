#!/usr/bin/env bash

###############################################################################
# GitHub Security Features Setup Helper
#
# This script helps you enable GitHub Security Features for your repository.
# Some features require manual activation via GitHub's web interface.
#
# Usage: ./scripts/setup_github_security.sh
###############################################################################

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Repository info
REPO_OWNER="KG90-EG"
REPO_NAME="POC-MarketPredictor-ML"
REPO_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  GitHub Security Features Setup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"

# Function to check if GitHub CLI is installed
check_gh_cli() {
    if command -v gh &> /dev/null; then
        echo -e "${GREEN}✓${NC} GitHub CLI found"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} GitHub CLI not found"
        return 1
    fi
}

# Function to check GitHub CLI authentication
check_gh_auth() {
    if gh auth status &> /dev/null; then
        echo -e "${GREEN}✓${NC} GitHub CLI authenticated"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} GitHub CLI not authenticated"
        return 1
    fi
}

# Function to check security features via GitHub API
check_security_features() {
    local feature=$1
    local endpoint=$2

    if gh api "repos/${REPO_OWNER}/${REPO_NAME}${endpoint}" --jq ".${feature}" 2>/dev/null | grep -q "true"; then
        echo -e "${GREEN}✓ Enabled${NC}"
        return 0
    else
        echo -e "${RED}✗ Disabled${NC}"
        return 1
    fi
}

echo -e "${BLUE}[1/3] Checking GitHub CLI...${NC}\n"

if check_gh_cli && check_gh_auth; then
    echo -e "\n${BLUE}[2/3] Checking current security settings...${NC}\n"

    echo -n "  Dependabot alerts:        "
    check_security_features "security_and_analysis.dependabot_alerts.status" "" || true

    echo -n "  Dependabot security:      "
    check_security_features "security_and_analysis.dependabot_security_updates.status" "" || true

    echo -n "  Secret scanning:          "
    check_security_features "security_and_analysis.secret_scanning.status" "" || true

    echo -n "  Secret scanning push:     "
    check_security_features "security_and_analysis.secret_scanning_push_protection.status" "" || true

    echo -e "\n${YELLOW}Note:${NC} Code scanning (CodeQL) status requires workflow file check\n"

    # Check if CodeQL workflow exists
    if [ -f ".github/workflows/codeql.yml" ] || [ -f ".github/workflows/codeql-analysis.yml" ]; then
        echo -e "  Code scanning (CodeQL):   ${GREEN}✓ Workflow configured${NC}"
    else
        echo -e "  Code scanning (CodeQL):   ${RED}✗ No workflow found${NC}"
    fi
else
    echo -e "${YELLOW}GitHub CLI not available. Manual setup required.${NC}\n"
fi

echo -e "\n${BLUE}[3/3] Setup Instructions${NC}\n"

echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  MANUAL SETUP REQUIRED${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}\n"

echo -e "GitHub Security Features must be enabled via the web interface.\n"

echo -e "${GREEN}Step 1: Open Security Settings${NC}"
echo -e "  ${BLUE}→${NC} ${REPO_URL}/settings/security_analysis\n"

echo -e "${GREEN}Step 2: Enable the following features:${NC}\n"

echo -e "  ${YELLOW}☐${NC} Dependabot alerts"
echo -e "     Automatic vulnerability notifications for dependencies"
echo -e "     Click: 'Enable' button\n"

echo -e "  ${YELLOW}☐${NC} Dependabot security updates"
echo -e "     Automatic PRs to fix security vulnerabilities"
echo -e "     Click: 'Enable' button\n"

echo -e "  ${YELLOW}☐${NC} Secret scanning"
echo -e "     Detect tokens, passwords, and other secrets in commits"
echo -e "     Click: 'Enable' button\n"

echo -e "  ${YELLOW}☐${NC} Secret scanning push protection"
echo -e "     Prevent pushing commits with detected secrets"
echo -e "     Click: 'Enable' button\n"

echo -e "  ${YELLOW}☐${NC} Code scanning (CodeQL)"
echo -e "     Automated code security analysis"
echo -e "     Click: 'Set up' → 'Default' → 'Enable CodeQL'\n"

echo -e "${GREEN}Step 3: Configure Notifications${NC}"
echo -e "  ${BLUE}→${NC} https://github.com/settings/notifications\n"
echo -e "  Check: 'Email' or 'Web and Mobile' for security alerts\n"

echo -e "${GREEN}Step 4: Verify Setup${NC}"
echo -e "  Run this script again to check enabled features:\n"
echo -e "    ${BLUE}./scripts/setup_github_security.sh${NC}\n"

echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}\n"

# Optional: Open browser automatically
read -p "Open GitHub Security Settings in browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v open &> /dev/null; then
        # macOS
        open "${REPO_URL}/settings/security_analysis"
    elif command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open "${REPO_URL}/settings/security_analysis"
    elif command -v start &> /dev/null; then
        # Windows
        start "${REPO_URL}/settings/security_analysis"
    else
        echo -e "\n${YELLOW}Please manually open:${NC} ${REPO_URL}/settings/security_analysis"
    fi
fi

echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Additional Resources${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}\n"

echo -e "  📚 Dependabot docs:     https://docs.github.com/en/code-security/dependabot"
echo -e "  🔐 Secret scanning:     https://docs.github.com/en/code-security/secret-scanning"
echo -e "  🔍 CodeQL:              https://docs.github.com/en/code-security/code-scanning"
echo -e "  📖 Security overview:   ${REPO_URL}/security\n"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"
