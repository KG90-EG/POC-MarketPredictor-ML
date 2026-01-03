# Repository Maintenance Scripts

This directory contains scripts for maintaining a clean and organized repository.

## 🧹 Cleanup Scripts

### `deep_cleanup.sh`

**Purpose**: Deep cleanup of outdated files, duplicates, and cache

**What it cleans**:

- ✗ History/archive folders (`docs/history/`, `.archive/`)
- ✗ Duplicate documentation files
- ✗ Old model files (keeps only `prod_model.bin`)
- ✗ Unused deployment configs (netlify, render, heroku)
- ✗ Old MLflow runs (keeps last 10)
- ✗ Python cache (`__pycache__/`, `*.pyc`)
- ✗ Temp files (`.DS_Store`, root-level logs/pids)
- ✗ Empty directories
- ✓ Auto-organizes misplaced documentation

**Usage**:

```bash
# Direct
./scripts/deep_cleanup.sh

# Via Makefile (recommended)
make deep-clean
```

**Safety**: Safe to run repeatedly - only removes actual clutter

**Frequency**: Run monthly or before major releases

---

### `cleanup_repo.sh`

**Purpose**: Quick reorganization of misplaced files

**What it does**:

- Moves files from root to correct subfolders
- Organizes config files
- Moves documentation to `docs/`
- Moves temp files to `logs/`

**Usage**:

```bash
./scripts/cleanup_repo.sh
# or
make cleanup-structure
```

**Frequency**: Run when you notice files in wrong locations

---

### `validate_structure.sh`

**Purpose**: Validate repository structure (no changes made)

**What it checks**:

- Files in root directory (only essential files allowed)
- Documentation placement
- Config file organization

**Usage**:

```bash
./scripts/validate_structure.sh
# or
make check-structure
```

**Frequency**: Run before commits (automated via pre-commit hook)

---

## 📋 Other Scripts

### `train_production.py`

Train production ML model on 30 US stocks with 20 technical features

```bash
python3 scripts/train_production.py
# or
make train-model
```

### `deploy_production.sh`

Deploy to production (Railway)

```bash
./scripts/deploy_production.sh
```

### `test_application.sh`

Run full application test suite

```bash
./scripts/test_application.sh
```

---

## 🔄 Automation

### Pre-commit Hook

Structure validation runs automatically before each commit:

```bash
pip install pre-commit
pre-commit install
```

### GitHub Actions

`.github/workflows/structure-check.yml` validates structure on every push/PR

---

## 📊 Maintenance Workflow

**Monthly**:

```bash
make deep-clean        # Remove outdated files
make check-structure   # Verify organization
git status             # Review changes
git add -A
git commit -m "chore: monthly cleanup"
```

**Before Major Release**:

```bash
make deep-clean
make test
make check-structure
# Review and commit
```

**When Files Are Misplaced**:

```bash
make cleanup-structure
```

---

## 🎯 Quick Reference

| Command | Purpose | Frequency |
|---------|---------|-----------|
| `make deep-clean` | Remove outdated/duplicate files | Monthly |
| `make cleanup-structure` | Reorganize misplaced files | As needed |
| `make check-structure` | Validate structure | Before commits |
| `make clean` | Remove Python cache only | Daily |

---

## 📖 Documentation

See `docs/development/REPOSITORY_STRUCTURE.md` for full structure guidelines.
