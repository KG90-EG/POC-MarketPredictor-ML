# ReadTheDocs Setup Guide

This guide walks you through setting up professional documentation hosting for the POC-MarketPredictor-ML project on ReadTheDocs.

## Overview

ReadTheDocs provides:
- **Free hosting** for open-source documentation
- **Automatic builds** on every commit
- **Version management** (stable, latest, tagged releases)
- **Search functionality** across all documentation
- **Custom domain support** (optional)
- **PDF/ePub exports** of documentation

**Estimated Time**: 10-15 minutes  
**Prerequisites**: GitHub account with admin access to the repository

---

## Step 1: Sign Up / Log In to ReadTheDocs

1. Visit [readthedocs.org](https://readthedocs.org)
2. Click **"Sign Up"** or **"Log In"**
3. Choose **"Sign in with GitHub"** for seamless integration
4. Authorize ReadTheDocs to access your GitHub account

**What happens**: ReadTheDocs will be able to read your public repositories and set up webhooks for automatic builds.

---

## Step 2: Import Your Project

1. Once logged in, click **"Import a Project"** from your dashboard
2. You should see a list of your GitHub repositories
3. Find **"POC-MarketPredictor-ML"** in the list
4. Click the **"+"** button next to it to import

**Alternative method** (if repo not listed):
1. Click **"Import Manually"**
2. Fill in the details:
   - **Name**: `POC-MarketPredictor-ML`
   - **Repository URL**: `https://github.com/KG90-EG/POC-MarketPredictor-ML`
   - **Repository type**: Git
   - **Default branch**: `main`
3. Click **"Next"**

---

## Step 3: Configure Project Settings

ReadTheDocs will **auto-detect** your configuration from `.readthedocs.yaml` already in the repository.

### Verify Configuration

1. Go to **Admin** → **Advanced Settings**
2. Confirm these settings:
   - **Documentation type**: Sphinx
   - **Python interpreter**: CPython 3.x
   - **Requirements file**: `docs/requirements.txt`
   - **Build verbosity**: Normal

### Important Settings to Check

| Setting | Recommended Value | Purpose |
|---------|-------------------|---------|
| **Default branch** | `main` | Branch to build by default |
| **Default version** | `latest` | Version shown to users by default |
| **Privacy level** | Public | Anyone can view docs |
| **Build on commit** | ✅ Enabled | Auto-build on every push |
| **Build pull requests** | ✅ Enabled | Preview docs in PRs |

---

## Step 4: Trigger First Build

1. From your project dashboard, click **"Build Version"**
2. Select **"latest"** and click **"Build"**
3. Wait 2-5 minutes for the build to complete
4. Monitor the build log for any errors

### Expected Build Output

```
Cloning into 'POC-MarketPredictor-ML'...
Installing dependencies from docs/requirements.txt
Building documentation with Sphinx
Build finished successfully
```

---

## Step 5: Access Your Documentation

Once the build succeeds:

1. Click **"View Docs"** from your dashboard
2. Your documentation will be available at:
   ```
   https://poc-marketpredictor-ml.readthedocs.io/en/latest/
   ```

**Bookmark this URL** and add it to your README.md!

---

## Step 6: Add Badge to README (Optional)

Show off your documentation with a badge:

```markdown
[![Documentation Status](https://readthedocs.org/projects/poc-marketpredictor-ml/badge/?version=latest)](https://poc-marketpredictor-ml.readthedocs.io/en/latest/?badge=latest)
```

This displays: [![Documentation Status](https://readthedocs.org/projects/poc-marketpredictor-ml/badge/?version=latest)](https://poc-marketpredictor-ml.readthedocs.io/en/latest/?badge=latest)

---

## Advanced Configuration

### Enable PDF/ePub Builds

1. Go to **Admin** → **Advanced Settings**
2. Scroll to **Formats**
3. Enable:
   - ✅ PDF
   - ✅ ePub
   - ✅ HTMLZip
4. Save and rebuild

### Set Up Custom Domain (Optional)

1. Go to **Admin** → **Domains**
2. Click **"Add Domain"**
3. Enter your custom domain (e.g., `docs.yourproject.com`)
4. Follow DNS configuration instructions
5. Enable HTTPS (automatic via Let's Encrypt)

### Configure Multiple Versions

ReadTheDocs automatically builds:
- **latest**: Most recent commit on `main`
- **stable**: Most recent tagged release
- **All tags**: Each git tag becomes a version

To manage versions:
1. Go to **Versions**
2. Activate/deactivate specific versions
3. Set default version for new visitors

---

## Troubleshooting

### Build Failed: Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'sphinx_rtd_theme'`

**Solution**:
1. Ensure `docs/requirements.txt` includes all Sphinx dependencies
2. Add missing package: `echo "sphinx-rtd-theme==2.0.0" >> docs/requirements.txt`
3. Commit and push to trigger new build

### Build Failed: Configuration Error

**Error**: `Config file not found`

**Solution**:
1. Verify `.readthedocs.yaml` exists in repository root
2. Check YAML syntax: `yamllint .readthedocs.yaml`
3. Ensure file uses `.yaml` extension (not `.yml`)

### Documentation Not Updating

**Issue**: Pushed changes but docs still show old content

**Solution**:
1. Check webhook: **Admin** → **Integrations** → verify GitHub webhook is active
2. Manually trigger build: **Versions** → **latest** → **Build Version**
3. Clear browser cache or open in incognito mode

### Build Timeout

**Error**: Build exceeds time limit

**Solution**:
1. Reduce documentation size (remove large images, split files)
2. Optimize Sphinx extensions in `docs/conf.py`
3. Contact ReadTheDocs support for build time increase

---

## Webhook Configuration (Automatic)

ReadTheDocs automatically creates a GitHub webhook. To verify:

1. Go to your GitHub repository
2. Navigate to **Settings** → **Webhooks**
3. You should see a ReadTheDocs webhook: `https://readthedocs.org/api/v2/webhook/...`
4. Ensure **Active** is checked and recent deliveries show **200 OK**

---

## Maintenance

### Update Documentation

1. Edit files in `docs/` directory
2. Commit and push to `main`
3. ReadTheDocs automatically rebuilds within 1-2 minutes
4. Check **Builds** tab to monitor progress

### Create Release Version

1. Tag a release: `git tag -a v1.0.0 -m "Release 1.0.0"`
2. Push tag: `git push origin v1.0.0`
3. ReadTheDocs automatically creates `v1.0.0` version
4. Set as "stable" in ReadTheDocs dashboard if desired

### Monitor Build Health

- **Dashboard**: Shows build status for all versions
- **Email notifications**: Configure in **My Settings** → **Notifications**
- **Build logs**: Click any build to view detailed output

---

## Best Practices

1. **Keep docs/ updated**: Always document new features when adding code
2. **Use relative links**: `[Link](../project/BACKLOG.md)` works across environments
3. **Test locally**: Run `make html` in `docs/` before pushing
4. **Version management**: Tag releases for stable documentation snapshots
5. **Review build logs**: Check for warnings even if build succeeds

---

## Resources

- **ReadTheDocs Documentation**: https://docs.readthedocs.io/
- **Sphinx Documentation**: https://www.sphinx-doc.org/
- **Project Dashboard**: https://readthedocs.org/projects/poc-marketpredictor-ml/
- **Support**: https://readthedocs.org/support/

---

## Quick Reference

| Task | Command/Action |
|------|----------------|
| **Local build** | `cd docs && make html` |
| **View local** | Open `docs/_build/html/index.html` |
| **Trigger rebuild** | Push to `main` or click "Build Version" |
| **Check status** | Visit ReadTheDocs dashboard |
| **View live docs** | https://poc-marketpredictor-ml.readthedocs.io/ |

---

## Next Steps

After setting up ReadTheDocs:

1. ✅ Add documentation badge to README.md
2. ✅ Configure email notifications for failed builds
3. ✅ Enable PDF/ePub exports if needed
4. ✅ Set up custom domain (optional)
5. ✅ Create documentation contribution guide
6. ✅ Add to PRODUCTION_READY.md as completed step

**Your documentation is now professional, searchable, and automatically updated!** 🎉
