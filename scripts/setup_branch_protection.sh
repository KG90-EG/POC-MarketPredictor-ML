#!/usr/bin/env bash

# Branch Protection Setup Script
# Requires: GitHub CLI (gh) installed and authenticated
# Install: brew install gh
# Auth: gh auth login

set -e

echo "🛡️ Setting up Branch Protection for main branch..."
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not installed!"
    echo ""
    echo "Install with:"
    echo "  brew install gh"
    echo ""
    echo "Then authenticate:"
    echo "  gh auth login"
    echo ""
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub!"
    echo ""
    echo "Run: gh auth login"
    echo ""
    exit 1
fi

echo "✅ GitHub CLI ready"
echo ""

# Repository info
REPO="KG90-EG/POC-MarketPredictor-ML"
BRANCH="main"

echo "📋 Repository: $REPO"
echo "🌿 Branch: $BRANCH"
echo ""

# Enable branch protection
echo "🔧 Enabling branch protection..."

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/$REPO/branches/$BRANCH/protection" \
  -f required_status_checks[strict]=true \
  -f "required_status_checks[contexts][]=backend-quality" \
  -f "required_status_checks[contexts][]=backend-tests" \
  -f "required_status_checks[contexts][]=frontend-quality" \
  -f "required_status_checks[contexts][]=frontend-tests" \
  -f "required_status_checks[contexts][]=docker-build" \
  -f "required_status_checks[contexts][]=structure-check" \
  -f "required_status_checks[contexts][]=docs-check" \
  -f "required_status_checks[contexts][]=enforce-tests" \
  -f "required_status_checks[contexts][]=enforce-formatting" \
  -f "required_status_checks[contexts][]=enforce-linting" \
  -f "required_status_checks[contexts][]=enforce-security" \
  -f "required_status_checks[contexts][]=enforce-docker" \
  -f "required_status_checks[contexts][]=merge-ready" \
  -f enforce_admins=true \
  -f required_pull_request_reviews[dismiss_stale_reviews]=true \
  -f required_pull_request_reviews[require_code_owner_reviews]=false \
  -f required_pull_request_reviews[required_approving_review_count]=1 \
  -f required_pull_request_reviews[require_last_push_approval]=false \
  -f restrictions=null \
  -F required_linear_history=true \
  -F allow_force_pushes=false \
  -F allow_deletions=false \
  -F required_conversation_resolution=true \
  -F lock_branch=false \
  -F allow_fork_syncing=true

echo ""
echo "✅ Branch protection enabled!"
echo ""

# Verify
echo "🔍 Verifying settings..."
gh api "/repos/$REPO/branches/$BRANCH/protection" | jq '{
  required_status_checks: .required_status_checks.contexts,
  enforce_admins: .enforce_admins.enabled,
  required_reviews: .required_pull_request_reviews.required_approving_review_count,
  linear_history: .required_linear_history.enabled
}'

echo ""
echo "════════════════════════════════════════════════"
echo "✅ Branch Protection successfully configured!"
echo ""
echo "From now on:"
echo "  🚫 Direct pushes to main are blocked"
echo "  ✅ All 13 status checks must pass"
echo "  👥 1 review required before merge"
echo "  📏 Linear history enforced"
echo "  🔒 Applies to administrators too"
echo ""
echo "Test with:"
echo "  git checkout -b test/protection"
echo "  echo 'test' >> README.md"
echo "  git add README.md"
echo "  git commit -m 'test: verify protection'"
echo "  git push -u origin test/protection"
echo "  # Then create PR on GitHub"
echo "════════════════════════════════════════════════"
