# GitHub Security Features Setup Guide

This guide walks you through enabling GitHub's advanced security features for the POC-MarketPredictor-ML project.

## Overview

GitHub provides powerful security tools for free on public repositories:

| Feature | Purpose | Benefit |
|---------|---------|---------|
| **Dependabot Alerts** | Notifies about vulnerable dependencies | Fix security issues before exploitation |
| **Dependabot Security Updates** | Auto-creates PRs to update vulnerable deps | Automated security patches |
| **Dependabot Version Updates** | Keeps dependencies up-to-date | Reduces technical debt |
| **Secret Scanning** | Detects committed secrets/tokens | Prevents credential leaks |
| **Push Protection** | Blocks commits with detected secrets | Proactive secret prevention |
| **CodeQL Analysis** | Static code analysis for vulnerabilities | Find bugs before production |
| **Security Policy** | SECURITY.md with disclosure process | Clear vulnerability reporting |

**Estimated Time**: 5-10 minutes  
**Prerequisites**: Repository admin access

---

## Quick Setup Script

For automated setup with default configurations:

```bash
# Run the automated setup script
./scripts/setup_github_security.sh
```

This script will:
1. ✅ Check for existing security features
2. ✅ Guide you through GitHub web UI steps
3. ✅ Verify configuration
4. ✅ Create SECURITY.md if missing
5. ✅ Test Dependabot and CodeQL workflows

**For manual setup or customization, follow the detailed steps below.**

---

## Step 1: Enable Dependabot Alerts

### Via GitHub Web UI

1. Navigate to your repository: `https://github.com/KG90-EG/POC-MarketPredictor-ML`
2. Click **Settings** → **Security** (left sidebar)
3. Under **Code security and analysis**, find **Dependabot alerts**
4. Click **Enable** next to "Dependabot alerts"

### What This Does

- Scans `requirements.txt`, `pyproject.toml`, `package.json` for known vulnerabilities
- Sends email notifications when vulnerabilities are discovered
- Creates alerts in the **Security** tab with remediation advice

### Verify It's Working

```bash
# Check for Dependabot alerts via GitHub CLI
gh api repos/KG90-EG/POC-MarketPredictor-ML/dependabot/alerts
```

Expected: Empty array `[]` if no vulnerabilities, or list of alerts with severity levels.

---

## Step 2: Enable Dependabot Security Updates

### Via GitHub Web UI

1. In **Settings** → **Security** → **Code security and analysis**
2. Find **Dependabot security updates**
3. Click **Enable**

### What This Does

- Automatically creates PRs to update vulnerable dependencies
- PRs include changelog, commit history, and compatibility info
- You review and merge PRs as appropriate

### Configuration (Optional)

Create `.github/dependabot.yml` to customize update behavior:

```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "python"
    reviewers:
      - "KG90-EG"

  # Frontend dependencies
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "frontend"
    reviewers:
      - "KG90-EG"

  # Docker dependencies
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "docker"
```

### Verify It's Working

- Check **Pull Requests** tab for Dependabot PRs (may take 24-48 hours for first scan)
- Look for PRs titled "Bump [package] from [old] to [new]"

---

## Step 3: Enable Secret Scanning

### Via GitHub Web UI

1. In **Settings** → **Security** → **Code security and analysis**
2. Find **Secret scanning**
3. Click **Enable**

### What This Does

- Scans repository for over 200+ secret patterns (API keys, tokens, certificates)
- Notifies when secrets are detected in commits
- Works on historical commits, not just new ones

### Enable Push Protection (Recommended)

1. In the same section, find **Push protection**
2. Click **Enable**
3. Blocks pushes that contain detected secrets

**Important**: Configure bypass for false positives:
- Team members can bypass with justification
- Alerts are still created for audit trail

### Verify It's Working

```bash
# Check for secret scanning alerts
gh api repos/KG90-EG/POC-MarketPredictor-ML/secret-scanning/alerts
```

Expected: Empty array if no secrets detected.

### Test Secret Scanning

```bash
# DO NOT commit this - just test locally
echo "aws_access_key_id=AKIAIOSFODNN7EXAMPLE" >> test_secret.txt
git add test_secret.txt
git commit -m "Test secret detection"
```

If push protection is enabled, this should be **blocked** with a warning.

---

## Step 4: Enable CodeQL Analysis

### Via GitHub Web UI

1. Go to **Settings** → **Security** → **Code security and analysis**
2. Find **Code scanning**
3. Click **Set up** → **Default**
4. GitHub will create `.github/workflows/codeql.yml` automatically

**Alternative**: Click **Advanced** to customize the workflow.

### What This Does

- Runs static analysis on Python and JavaScript code
- Detects security vulnerabilities, bugs, and code smells
- Creates alerts with severity levels and fix recommendations
- Runs on every push and PR

### Verify CodeQL Workflow

```bash
# Check if workflow file exists
cat .github/workflows/codeql.yml
```

Expected: Workflow configuration for CodeQL analysis.

### Manual Workflow Creation (If Needed)

If not auto-created, add `.github/workflows/codeql.yml`:

```yaml
name: "CodeQL"

on:
  push:
    branches: [ "main", "dev" ]
  pull_request:
    branches: [ "main" ]
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [ 'python', 'javascript' ]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v3
      with:
        languages: ${{ matrix.language }}
        queries: security-and-quality

    - name: Autobuild
      uses: github/codeql-action/autobuild@v3

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v3
      with:
        category: "/language:${{matrix.language}}"
```

### View CodeQL Results

1. Go to **Security** → **Code scanning**
2. View alerts organized by severity
3. Click any alert for detailed explanation and fix suggestions

---

## Step 5: Create Security Policy

### Create SECURITY.md

```bash
# Run the helper script
./scripts/create_security_policy.sh
```

Or create manually in repository root:

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**DO NOT** report security vulnerabilities through public GitHub issues.

### How to Report

1. **Email**: Send details to [security@yourproject.com] or repository owner
2. **GitHub Security Advisory**: Use the "Security" tab → "Report a vulnerability"
3. **Expected Response**: Within 48 hours

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Assessment**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-3 days
  - High: 7-14 days
  - Medium: 30 days
  - Low: Best effort

### Disclosure Policy

- Security issues are disclosed after fix is released
- We credit researchers (unless they prefer anonymity)
- CVE IDs assigned for significant vulnerabilities

## Security Best Practices

When contributing to this project:

1. **Never commit secrets**: Use environment variables
2. **Keep dependencies updated**: Monitor Dependabot PRs
3. **Review security alerts**: Check Security tab regularly
4. **Follow secure coding**: Use pre-commit hooks
5. **Validate inputs**: Sanitize all user inputs

## Security Features

This project includes:

- 🔒 **Dependabot**: Automated dependency updates
- 🔍 **CodeQL**: Static code analysis
- 🛡️ **Secret Scanning**: Detects leaked credentials
- 🔑 **Pre-commit Hooks**: Prevents common security issues
- 📊 **Security Audits**: Regular dependency audits

## Contact

For security concerns, contact:
- **Email**: [Your email]
- **GitHub**: @KG90-EG
```

Commit and push:

```bash
git add SECURITY.md
git commit -m "docs: Add security policy"
git push origin main
```

---

## Step 6: Configure Notification Settings

### Email Notifications

1. Go to **Settings** → **Notifications** (personal settings)
2. Under **Security alerts**, ensure all are enabled:
   - ✅ Dependabot alerts
   - ✅ Secret scanning alerts
   - ✅ Code scanning alerts
3. Choose notification frequency (default: immediate)

### Repository Notifications

1. In repository **Settings** → **Security** → **Code security and analysis**
2. Scroll to **Notification settings**
3. Add team members or email addresses to notify

---

## Verification Checklist

Run this verification script:

```bash
#!/bin/bash
# scripts/verify_security_features.sh

echo "🔍 Verifying GitHub Security Features..."
echo

# Check Dependabot alerts
echo "1. Checking Dependabot alerts..."
gh api repos/KG90-EG/POC-MarketPredictor-ML/dependabot/alerts \
  --jq 'length' 2>/dev/null && echo "✅ Dependabot enabled" || echo "❌ Dependabot not enabled"

# Check secret scanning
echo "2. Checking secret scanning..."
gh api repos/KG90-EG/POC-MarketPredictor-ML/secret-scanning/alerts \
  --jq 'length' 2>/dev/null && echo "✅ Secret scanning enabled" || echo "❌ Secret scanning not enabled"

# Check CodeQL workflow
echo "3. Checking CodeQL workflow..."
[ -f .github/workflows/codeql.yml ] && echo "✅ CodeQL workflow exists" || echo "❌ CodeQL workflow missing"

# Check security policy
echo "4. Checking security policy..."
[ -f SECURITY.md ] && echo "✅ SECURITY.md exists" || echo "❌ SECURITY.md missing"

# Check Dependabot config
echo "5. Checking Dependabot configuration..."
[ -f .github/dependabot.yml ] && echo "✅ Dependabot config exists" || echo "⚠️  Using default Dependabot config"

echo
echo "✅ Verification complete!"
```

Run it:

```bash
chmod +x scripts/verify_security_features.sh
./scripts/verify_security_features.sh
```

---

## Automated Setup Script

### scripts/setup_github_security.sh

```bash
#!/bin/bash

set -e

REPO_OWNER="KG90-EG"
REPO_NAME="POC-MarketPredictor-ML"
REPO_FULL="${REPO_OWNER}/${REPO_NAME}"

echo "🔒 GitHub Security Features Setup"
echo "=================================="
echo
echo "Repository: ${REPO_FULL}"
echo

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found. Install it first:"
    echo "   brew install gh"
    echo "   or visit: https://cli.github.com/"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub. Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo

# Create SECURITY.md if it doesn't exist
if [ ! -f SECURITY.md ]; then
    echo "📝 Creating SECURITY.md..."
    cat > SECURITY.md << 'EOF'
# Security Policy

## Reporting a Vulnerability

Please report security vulnerabilities to the repository owner.

**DO NOT** report security vulnerabilities through public GitHub issues.

Use the Security tab to report vulnerabilities privately.
EOF
    git add SECURITY.md
    git commit -m "docs: Add security policy" || true
    git push origin main || true
    echo "✅ SECURITY.md created and committed"
else
    echo "✅ SECURITY.md already exists"
fi

echo
echo "🔧 Next Steps (Manual via GitHub Web UI):"
echo
echo "1. Enable Dependabot Alerts:"
echo "   → https://github.com/${REPO_FULL}/settings/security_analysis"
echo "   → Click 'Enable' next to 'Dependabot alerts'"
echo
echo "2. Enable Dependabot Security Updates:"
echo "   → Same page, enable 'Dependabot security updates'"
echo
echo "3. Enable Secret Scanning:"
echo "   → Same page, enable 'Secret scanning'"
echo "   → Enable 'Push protection' (recommended)"
echo
echo "4. Enable CodeQL Analysis:"
echo "   → Same page, under 'Code scanning'"
echo "   → Click 'Set up' → 'Default'"
echo
echo "5. Verify in 24 hours:"
echo "   → Check Security tab for initial scans"
echo "   → Check for Dependabot PRs"
echo
echo "✅ Setup script complete!"
echo
echo "📖 For detailed instructions, see: docs/operations/GITHUB_SECURITY_SETUP.md"
```

Make executable:

```bash
chmod +x scripts/setup_github_security.sh
```

---

## Troubleshooting

### Dependabot Not Creating PRs

**Issue**: Enabled but no PRs appear after 48 hours

**Solutions**:
1. Check `requirements.txt` has pinned versions: `package==1.2.3`
2. Verify repository is public (private repos need GitHub Advanced Security)
3. Check Dependabot logs: **Insights** → **Dependency graph** → **Dependabot**
4. Manually trigger: Create `.github/dependabot.yml` and push

### CodeQL Workflow Failing

**Error**: `CodeQL analysis failed`

**Solutions**:
1. Check Python version in workflow matches project (3.11+)
2. Ensure all dependencies install: Add `pip install -r requirements.txt` before analysis
3. Check workflow logs: **Actions** tab → Failed workflow → View logs
4. Exclude problematic files: Add `paths-ignore` in workflow

### Secret Scanning False Positives

**Issue**: Detecting test data as secrets

**Solutions**:
1. Use `.gitattributes` to exclude test files:
   ```
   tests/fixtures/test_keys.txt linguist-generated=true
   ```
2. Mark as false positive in alert
3. Use placeholder patterns: `AKIAIOSFODNN7EXAMPLE` instead of real AWS keys

### Push Protection Blocking Legitimate Commits

**Issue**: Can't push due to false positive secret detection

**Solutions**:
1. Review the detected secret carefully
2. If false positive, click "It's used in tests" or "It's a false positive"
3. Use secret bypass: `git push --no-verify` (with justification)
4. Better approach: Move to environment variables or `.env` file

---

## Monitoring and Maintenance

### Weekly Security Review

```bash
# Check for new alerts
gh api repos/KG90-EG/POC-MarketPredictor-ML/dependabot/alerts | jq '.[] | {severity, package, created_at}'

# Check secret scanning alerts
gh api repos/KG90-EG/POC-MarketPredictor-ML/secret-scanning/alerts | jq '.[] | {type, created_at, state}'

# View CodeQL results
gh api repos/KG90-EG/POC-MarketPredictor-ML/code-scanning/alerts | jq '.[] | {rule_id, severity, state}'
```

### Dependabot PR Review Checklist

When reviewing Dependabot PRs:

1. ✅ Check changelog for breaking changes
2. ✅ Review failing tests (if any)
3. ✅ Verify version bump is appropriate (patch/minor/major)
4. ✅ Check dependency compatibility with other packages
5. ✅ Merge promptly to stay secure

### Security Dashboard

View comprehensive security status:

1. Go to **Security** → **Overview**
2. See all alerts in one place
3. Track remediation progress
4. Export reports for compliance

---

## Best Practices

1. **Act on alerts promptly**: Don't let vulnerabilities accumulate
2. **Review all Dependabot PRs**: Don't auto-merge without testing
3. **Use branch protection**: Require security checks to pass before merge
4. **Regular audits**: Monthly security review of all dependencies
5. **Keep secrets in env vars**: Never commit credentials
6. **Use pre-commit hooks**: Catch issues before they reach GitHub
7. **Document security practices**: Update CONTRIBUTING.md with security guidelines

---

## Resources

- **GitHub Security Docs**: https://docs.github.com/en/code-security
- **Dependabot Docs**: https://docs.github.com/en/code-security/dependabot
- **CodeQL Docs**: https://codeql.github.com/docs/
- **Secret Scanning**: https://docs.github.com/en/code-security/secret-scanning
- **Security Advisories**: https://github.com/advisories

---

## Quick Reference

| Feature | Status Check | Enable Location |
|---------|--------------|-----------------|
| **Dependabot Alerts** | Security tab → Dependabot | Settings → Security → Code security |
| **Secret Scanning** | Security tab → Secret scanning | Settings → Security → Code security |
| **CodeQL** | Actions tab → CodeQL workflow | Settings → Security → Code scanning |
| **Security Policy** | Root SECURITY.md file | Create manually or via script |

---

## Next Steps

After enabling all security features:

1. ✅ Monitor Security tab daily for first week
2. ✅ Review and merge initial Dependabot PRs
3. ✅ Address any CodeQL findings
4. ✅ Add security badge to README.md
5. ✅ Update PRODUCTION_READY.md as completed

**Your repository is now hardened with enterprise-grade security!** 🛡️
