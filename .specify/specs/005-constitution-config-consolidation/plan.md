# FR-005 Implementation Plan

**Feature:** Constitution Config Consolidation  
**Duration:** 1-2 Sprints  
**Start Date:** 2026-02-04  
**Target Completion:** 2026-02-11  

---

## 🎯 Phase Overview

### Phase 0: Planning ✅ DONE
- ✅ Problem analysis complete (CONSTITUTION_CONFIG_AUDIT.md)
- ✅ Spec written (spec.md)
- ✅ This plan created
- ⏳ **Next:** Design & review with team

### Phase 1: Configuration Files (EST. 30 min)
Create/Update all config files with proper settings

**Deliverables:**
- `pyproject.toml` with Black, isort, pytest sections
- `.prettierrc.json` with Prettier config
- Updated `.flake8` with complete documentation
- Pin linter versions in requirements.txt

**Key Files to Create/Modify:**
- 📄 Create: `pyproject.toml`
- 📄 Create: `.prettierrc.json`
- 📝 Modify: `.flake8`
- 📝 Modify: `requirements.txt`

### Phase 2: Deduplication (EST. 20 min)
Remove hardcoded config from scripts and workflows

**Deliverables:**
- `.husky/pre-commit` uses config files only
- `scripts/pre-push.sh` uses config files only
- `.github/workflows/quality-gates.yml` uses config files (DONE ✅)

**Key Files to Modify:**
- 📝 Modify: `.husky/pre-commit`
- 📝 Modify: `scripts/pre-push.sh`
- 📝 Verify: `.github/workflows/quality-gates.yml` (already clean)

### Phase 3: Documentation (EST. 30 min)
Update Constitution and create developer guide

**Deliverables:**
- Constitution: "Configuration Management" section
- Document all 9 E-rules with reason + examples
- Create `CONFIGURATION_GUIDE.md`
- Update README.md with config references

**Key Files to Create/Modify:**
- 📝 Modify: `.specify/memory/constitution.md`
- 📄 Create: `CONFIGURATION_GUIDE.md`
- 📝 Modify: `README.md`
- 📄 Create: `docs/CONFIGURATION.md`

### Phase 4: Validation & Testing (EST. 15 min)
Verify consistency and functionality

**Deliverables:**
- Pre-commit hook detects hardcoded config
- All tests pass locally
- All CI tests pass
- Zero config-related failures

**Key Tests:**
- `pytest tests/` - Full test suite green
- `black --check src/` - Uses `pyproject.toml`
- `isort --check src/` - Uses `pyproject.toml`
- `flake8 src/` - Uses `.flake8`
- `npm run lint` - Uses `eslint.config.js`
- `npm run format:check` - Uses `.prettierrc.json`

---

## 📊 Timeline

```
2026-02-04  │ Phase 0: Plan (1 day)
2026-02-05  │ Phase 1: Config Files (1/2 day)
2026-02-05  │ Phase 2: Deduplication (1/2 day)
2026-02-06  │ Phase 3: Documentation (1 day)
2026-02-06  │ Phase 4: Validation (1/2 day)
2026-02-07  │ Testing + Review
2026-02-11  │ Merge to main + Constitution v1.5.0
```

**Total Effort:** ~95 minutes (2-3 focused work sessions)

---

## 🎯 Milestones

### Milestone 1: Config Files Ready
**Date:** 2026-02-05 (EOD)  
**Criteria:**
- ✅ `pyproject.toml` created with all sections
- ✅ `.prettierrc.json` created
- ✅ `.flake8` documented
- ✅ All tools run successfully against new files

**Owner:** @kevingarcia  
**Blocker:** NO (can work in parallel with Phase 2)

### Milestone 2: Deduplication Complete
**Date:** 2026-02-05 (EOD)  
**Criteria:**
- ✅ No hardcoded flags in `.husky/pre-commit`
- ✅ No hardcoded flags in `scripts/pre-push.sh`
- ✅ Pre-commit hook runs successfully
- ✅ Tests pass with new config

**Owner:** @kevingarcia  
**Blocker:** Depends on Milestone 1

### Milestone 3: Documentation Updated
**Date:** 2026-02-06 (EOD)  
**Criteria:**
- ✅ Constitution has new section
- ✅ All 9 rules documented
- ✅ CONFIGURATION_GUIDE.md created
- ✅ README.md references config files

**Owner:** @kevingarcia  
**Blocker:** NO (can work in parallel)

### Milestone 4: All Tests Green
**Date:** 2026-02-06 (EOD)  
**Criteria:**
- ✅ Local: `pytest` green
- ✅ Local: `black`, `isort`, `flake8`, `prettier` green
- ✅ GitHub Actions: All workflows pass
- ✅ Pre-commit: No false positives

**Owner:** @kevingarcia  
**Blocker:** YES (must pass before merge)

### Milestone 5: Constitution v1.5.0
**Date:** 2026-02-11 (EOD)  
**Criteria:**
- ✅ Constitution updated + versioned
- ✅ All changes merged to main
- ✅ Zero config-related CI failures
- ✅ Documentation complete

**Owner:** @kevingarcia  
**Blocker:** YES (feature completion gate)

---

## 🛠️ Technical Approach

### Phase 1: Configuration Files

#### Step 1.1: Create `pyproject.toml`
```toml
[tool.black]
line-length = 100
target-version = ["py312"]
extend-exclude = '''
    /(
      \.git
      | \.venv
      | venv
      | build
      | dist
      | \.egg-info
    )/
'''

[tool.isort]
profile = "black"
line_length = 100
skip_gitignore = true

[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "--tb=short --strict-markers"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration",
]

[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"
```

#### Step 1.2: Create `.prettierrc.json`
```json
{
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

#### Step 1.3: Update `requirements.txt`
Add Python version constraint:
```
# Pin Python version for consistency across environments
python>=3.12,<4.0

# Linting & Formatting
flake8==7.3.0          # Code linting (config in .flake8)
black==24.3.0          # Code formatting (config in pyproject.toml)
isort==5.13.2          # Import sorting (config in pyproject.toml)
# ... rest of requirements
```

### Phase 2: Deduplication

#### Step 2.1: Update `.husky/pre-commit`
**Before:**
```bash
flake8 src/ scripts/ tests/ \
  --max-line-length=100 \
  --extend-ignore=C901,E203,W503,... \
  --count
```

**After:**
```bash
# Uses .flake8 config (NO hardcoded flags)
flake8 src/ scripts/ tests/
black --check src/ scripts/ tests/
isort --check-only src/ scripts/ tests/
```

#### Step 2.2: Update `scripts/pre-push.sh`
Same transformation as above

### Phase 3: Documentation

#### Step 3.1: Add to Constitution

Add new section:
```markdown
## XII. Configuration Management

### Single Source of Truth

Every linting/formatting rule appears in EXACTLY ONE file:

- **Python Linting**: `.flake8` (source of truth)
- **Python Formatting**: `pyproject.toml` [tool.black]
- **Import Sorting**: `pyproject.toml` [tool.isort]
- **Testing**: `pyproject.toml` [tool.pytest]
- **Frontend Linting**: `frontend/eslint.config.js`
- **Frontend Formatting**: `.prettierrc.json`

### Configuration Strategy

1. Tools reference config files (never hardcode flags)
2. Each rule is documented with WHY + WHEN
3. Version pinning is mandatory
4. Breaking changes trigger Constitution amendment
```

#### Step 3.2: Document All 9 Rules

In Constitution, add table:
| Rule | Reason | When It Applies | Example |
|------|--------|-----------------|---------|
| E203 | Black compatibility | Always | `x[1 :]` is valid |
| E231 | f-string format specs | Always | `f"{x:.2f}"` is valid |
| ... | ... | ... | ... |

---

## ⚠️ Risks & Mitigations

### Risk 1: Config Conflicts
**Risk:** `pytest.ini` + `pyproject.toml` [pytest] section conflict  
**Mitigation:** Remove duplicate config from pytest.ini, keep only in pyproject.toml  
**Effort:** 5 min  

### Risk 2: Prettier Breaks Existing Code
**Risk:** `.prettierrc.json` formats differently than before  
**Mitigation:** Run Prettier in check-only mode first, review changes  
**Effort:** 10 min  

### Risk 3: CI Cache
**Risk:** GitHub Actions caches old config  
**Mitigation:** Add `cache-busting` commit + clear Actions cache manually  
**Effort:** 5 min  

### Risk 4: Python 3.12 Incompatibility
**Risk:** Some package doesn't support 3.12  
**Mitigation:** Already tested with 3.14, fallback to 3.12 lower bound if needed  
**Effort:** 0 min (already handled)  

---

## 📋 Constitution Check

**Principle IX: Pre-Commit Validation**
- ✅ This feature IMPROVES pre-commit consistency
- ✅ After completion, builds NEVER break due to config

**Principle XI: Clean Repository Structure**
- ✅ Reduces root-level config duplication
- ✅ Makes config strategy explicit

**Principle X: Living Documentation**
- ✅ Constitution updated with new section
- ✅ Configuration guide created

**Verdict:** ✅ **FULLY CONSTITUTION COMPLIANT**

---

## 📞 Communication Plan

### Stakeholders
- Kevin Garcia (owner)
- Future developers (consumers)

### Updates
- Daily: 5-min standup on progress
- After Phase: Brief summary of what changed
- Final: Constitution v1.5.0 release notes

---

## 🎓 Success Definition

**We've succeeded when:**
1. ✅ Config files consolidated (no duplication)
2. ✅ Constitution documents the strategy
3. ✅ New developers understand why each rule exists
4. ✅ Changing a rule requires ONE file edit
5. ✅ Zero "config failed in CI" issues
6. ✅ Local machine ≈ GitHub Actions (consistent)

---

## 📊 Effort Breakdown

| Phase | Task | Effort | Owner |
|-------|------|--------|-------|
| 1 | Create `pyproject.toml` | 10 min | @kevingarcia |
| 1 | Create `.prettierrc.json` | 5 min | @kevingarcia |
| 1 | Update `.flake8` documentation | 10 min | @kevingarcia |
| 1 | Update `requirements.txt` | 5 min | @kevingarcia |
| 2 | Update `.husky/pre-commit` | 5 min | @kevingarcia |
| 2 | Update `scripts/pre-push.sh` | 5 min | @kevingarcia |
| 2 | Test locally | 10 min | @kevingarcia |
| 3 | Update Constitution | 15 min | @kevingarcia |
| 3 | Create CONFIGURATION_GUIDE.md | 10 min | @kevingarcia |
| 3 | Update README.md | 5 min | @kevingarcia |
| 4 | Run all tests | 10 min | @kevingarcia |
| 4 | GitHub Actions review | 5 min | @kevingarcia |
| **Total** | | **~95 min** | |

---

## 🔄 Rollback Plan

If something breaks:

1. **Quick Fix** (5 min)
   - `git revert` last commit
   - Run `pre-commit run --all-files`
   - Verify CI passes

2. **Root Cause** (15 min)
   - Identify which config file has issue
   - Fix locally
   - Run: `black`, `isort`, `flake8`, `prettier`
   - Re-test

3. **Re-deploy** (5 min)
   - Commit fix
   - Push to new branch
   - Create PR for review

---

## 📝 Notes

- This plan is sequential but Phases 1 & 3 can run in parallel
- Phase 4 is blocking (must pass before merge)
- No breaking changes to code/features (config only)
- Constitution version bump: 1.4.0 → 1.5.0

---

**Next Steps:**
1. Review this plan
2. Start Phase 1 immediately
3. Update status here as we progress
4. Reference this plan in commit messages

