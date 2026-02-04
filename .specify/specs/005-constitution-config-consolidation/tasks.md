# FR-005 Tasks

**Feature:** Constitution Config Consolidation  
**Status:** 🔴 NOT STARTED  
**Total Tasks:** 15  
**Estimated Effort:** ~95 minutes  

---

## 📋 Task List

### Phase 1: Configuration Files (30 min)

#### Task 1.1: Create `pyproject.toml`
**Priority:** 🔴 CRITICAL  
**Effort:** 10 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Create new `pyproject.toml` with sections for Black, isort, and pytest

**Steps:**
1. Create file at root: `/pyproject.toml`
2. Add `[tool.black]` section:
   - `line-length = 100`
   - `target-version = ["py312"]`
   - Exclude patterns for `.git`, `.venv`, etc.
3. Add `[tool.isort]` section:
   - `profile = "black"`
   - `line_length = 100`
   - `skip_gitignore = true`
4. Add `[tool.pytest.ini_options]` section:
   - `testpaths = ["tests"]`
   - `python_files = "test_*.py"`
   - `addopts = "--tb=short --strict-markers"`
5. Commit: `"chore: create pyproject.toml with tool configs"`

**Validation:**
- ✅ File exists at root
- ✅ All sections present
- ✅ Black runs: `black --check src/` (uses config)
- ✅ isort runs: `isort --check src/` (uses config)

**Dependencies:** None

---

#### Task 1.2: Create `.prettierrc.json`
**Priority:** 🔴 CRITICAL  
**Effort:** 5 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Create Prettier config file for consistent frontend formatting

**Steps:**
1. Create file at root: `/.prettierrc.json`
2. Set `printWidth: 100` (match line-length)
3. Set `trailingComma: "es5"` (modern but compatible)
4. Set `singleQuote: true` (consistent with JS style)
5. Set `endOfLine: "lf"` (Unix line endings)
6. Commit: `"chore: create .prettierrc.json for frontend formatting"`

**Validation:**
- ✅ File exists at root
- ✅ Prettier reads config: `npx prettier --check src/`
- ✅ No formatting conflicts in frontend/

**Dependencies:** None

---

#### Task 1.3: Document `.flake8` Rules
**Priority:** 🔴 CRITICAL  
**Effort:** 10 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Update `.flake8` with documentation for each ignore rule

**Current State:**
- 9 rules are ignored, but no explanation

**Steps:**
1. Open `.flake8`
2. For EACH of the 9 rules, add comment explaining:
   - **WHY**: The reason for ignoring
   - **WHEN**: When it applies
   - **EXAMPLE**: Code that triggers the rule
3. Rules to document:
   - E203, E231, W503, F541, W293, E501, C901, F811, E731
4. Commit: `"docs(.flake8): document all ignore rules with reason + examples"`

**Example Format:**
```ini
# E231 - missing whitespace after ':' 
#   WHY: f-string format specs like {price:.2f} are valid in Black
#   WHEN: Always applies when using f-string formatting
#   EXAMPLE: logger.debug(f"Price: {price:.2f}")
```

**Validation:**
- ✅ All 9 rules documented
- ✅ Each has WHY, WHEN, EXAMPLE
- ✅ File is valid INI format
- ✅ Flake8 reads config: `flake8 --version`

**Dependencies:** None

---

#### Task 1.4: Pin Linter Versions & Python Version
**Priority:** 🟠 HIGH  
**Effort:** 5 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Update `requirements.txt` to pin versions and add Python constraint

**Steps:**
1. Open `requirements.txt`
2. Add Python version constraint at top:
   ```
   # Pin Python version for consistency
   python>=3.12,<4.0
   ```
3. Pin linter versions (they should already be pinned):
   - `flake8==7.3.0` (not range)
   - `black==24.3.0` (not range)
   - `isort==5.13.2` (not range)
4. Commit: `"fix(deps): pin python and linter versions for consistency"`

**Validation:**
- ✅ Python version specified
- ✅ All linters pinned to specific versions
- ✅ `pip install -r requirements.txt` works
- ✅ `python --version` shows 3.12+

**Dependencies:** Task 1.1 (uses pyproject.toml)

---

### Phase 2: Deduplication (20 min)

#### Task 2.1: Clean `.husky/pre-commit`
**Priority:** 🔴 CRITICAL  
**Effort:** 8 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Remove hardcoded flake8 flags, use config files instead

**Current State:**
```bash
flake8 src/trading_engine/ src/backtest/ scripts/ \
  --max-line-length=100 \
  --extend-ignore=C901,E203,W503,F401,... \  # HARDCODED
  --count --statistics
```

**Steps:**
1. Open `.husky/pre-commit`
2. Find all `flake8` commands (search for "flake8 src")
3. Replace with simple version:
   ```bash
   flake8 src/ scripts/ tests/
   ```
   (Remove all `--` flags; they'll come from `.flake8`)
4. Do same for `black --check` → `black --check src/`
5. Do same for `isort --check` → `isort --check-only src/`
6. Commit: `"refactor(.husky): use config files instead of hardcoded flags"`

**Validation:**
- ✅ No `--max-line-length` in file
- ✅ No `--extend-ignore` in file
- ✅ No `--profile` in file
- ✅ Pre-commit runs: `pre-commit run --all-files` (should pass)
- ✅ Flake8 still works with `.flake8` config

**Dependencies:** Task 1.1, 1.3, 1.4

---

#### Task 2.2: Clean `scripts/pre-push.sh`
**Priority:** 🔴 CRITICAL  
**Effort:** 7 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Same as 2.1, but for pre-push script

**Steps:**
1. Open `scripts/pre-push.sh`
2. Find all hardcoded tool flags
3. Replace with simple versions:
   - `flake8 src/ scripts/ tests/`
   - `black --check src/`
   - `isort --check src/`
4. Remove all `--max-line-length`, `--extend-ignore`, etc.
5. Commit: `"refactor(scripts): use config files in pre-push"`

**Validation:**
- ✅ No hardcoded flags
- ✅ Script runs: `bash scripts/pre-push.sh`
- ✅ All checks still pass

**Dependencies:** Task 1.1, 1.3, 1.4

---

#### Task 2.3: Verify GitHub Actions Workflow
**Priority:** 🟠 HIGH  
**Effort:** 5 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Confirm `.github/workflows/quality-gates.yml` uses config files (should be done from commit 91e9178)

**Steps:**
1. Open `.github/workflows/quality-gates.yml`
2. Look for `flake8 src/` with NO `--` flags
3. If it still has hardcoded flags, update it
4. Commit: `"fix(workflows): ensure quality-gates uses config files"` (if needed)

**Validation:**
- ✅ No hardcoded flags in workflow
- ✅ Workflow reads `.flake8`, `pyproject.toml`, etc.
- ✅ GitHub Actions passes (or will after Phase 1)

**Dependencies:** Previous tasks

---

### Phase 3: Documentation (30 min)

#### Task 3.1: Update Constitution
**Priority:** 🔴 CRITICAL  
**Effort:** 15 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Add "Configuration Management" section to Constitution with full documentation

**Steps:**
1. Open `.specify/memory/constitution.md`
2. Add new section "XII. Configuration Management" after "XI"
3. Document:
   - Single Source of Truth principle
   - Each tool's config file
   - Why each file exists
   - When/how to modify
4. Create table of all 9 flake8 ignore rules:
   - Rule name
   - Why ignored
   - When it applies
   - Example code
5. Document Python version (3.12+)
6. Bump version: 1.4.0 → 1.5.0
7. Commit: `"docs(constitution): add Configuration Management section v1.5.0"`

**Content to Add:**
- Config strategy explanation
- Table of config files (tool, file, purpose)
- All 9 flake8 rules with examples
- Python version constraints
- When to amend config rules

**Validation:**
- ✅ Section XII exists
- ✅ All 9 rules documented
- ✅ Python version documented
- ✅ Version bumped to 1.5.0
- ✅ Constitution valid Markdown

**Dependencies:** Task 1.1, 1.2, 1.3

---

#### Task 3.2: Create `CONFIGURATION_GUIDE.md`
**Priority:** 🟠 HIGH  
**Effort:** 10 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Create developer guide for understanding and modifying config

**Steps:**
1. Create `docs/CONFIGURATION_GUIDE.md`
2. Add sections:
   - **Overview**: What configs exist, why
   - **Backend Config**: .flake8, pyproject.toml details
   - **Frontend Config**: eslint, prettier details
   - **Adding a Lint Rule**: How to add new rule
   - **Updating Versions**: How to pin tool versions
   - **Common Issues**: What to do if config breaks
3. Include examples for each section
4. Add FAQ section
5. Commit: `"docs: create CONFIGURATION_GUIDE.md for developers"`

**Validation:**
- ✅ File exists in `docs/`
- ✅ All main topics covered
- ✅ Examples are complete
- ✅ Readable Markdown

**Dependencies:** None

---

#### Task 3.3: Update `README.md`
**Priority:** 🟡 MEDIUM  
**Effort:** 5 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Reference config files and guide in README

**Steps:**
1. Open `README.md`
2. Find "Development" or "Setup" section
3. Add subsection "Configuration":
   - Brief mention of config files
   - Link to CONFIGURATION_GUIDE.md
   - Link to Constitution (XII. Config Management)
4. Commit: `"docs(README): reference configuration guide"`

**Validation:**
- ✅ README mentions config strategy
- ✅ Links work
- ✅ Markdown valid

**Dependencies:** Task 3.2

---

### Phase 4: Validation & Testing (15 min)

#### Task 4.1: Local Full Test Suite
**Priority:** 🔴 CRITICAL  
**Effort:** 8 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Run all linting and testing locally to verify config changes work

**Steps:**
1. Run: `python -m pytest tests/ -v` (should pass)
2. Run: `black --check src/` (uses pyproject.toml)
3. Run: `isort --check src/` (uses pyproject.toml)
4. Run: `flake8 src/ scripts/` (uses .flake8)
5. Run: `cd frontend && npm run lint` (uses eslint.config.js)
6. Run: `cd frontend && npm run format:check` (uses .prettierrc.json)
7. If anything fails, debug and fix
8. Commit: `"test: verify all linting passes with consolidated config"`

**Validation:**
- ✅ pytest: All tests pass
- ✅ black: 0 files would be reformatted
- ✅ isort: No changes needed
- ✅ flake8: 0 violations (or only pre-existing)
- ✅ eslint: 0 errors
- ✅ prettier: All files formatted correctly

**Dependencies:** All Phase 1 & 2 tasks

---

#### Task 4.2: Pre-commit Hook Test
**Priority:** 🟠 HIGH  
**Effort:** 4 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Test pre-commit hook runs successfully with new config

**Steps:**
1. Run: `pre-commit run --all-files`
2. Watch for failures related to:
   - Config files not found
   - Hardcoded flags still present
   - Version mismatches
3. If failures, debug:
   - Check file paths
   - Check .husky/pre-commit script
   - Check requirements.txt versions
4. Fix any issues
5. Commit: `"test: verify pre-commit hook uses consolidated config"`

**Validation:**
- ✅ `pre-commit run --all-files` passes (or only pre-existing issues)
- ✅ No "config file not found" errors
- ✅ Flake8, Black, isort all read from config files

**Dependencies:** Task 2.1, 2.2

---

#### Task 4.3: GitHub Actions Dry Run
**Priority:** 🟠 HIGH  
**Effort:** 3 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Simulate what GitHub Actions will do

**Steps:**
1. Check: `.github/workflows/quality-gates.yml` doesn't have hardcoded flags
2. Mentally trace through:
   - Checkout code ✓
   - Setup Python 3.12 ✓
   - Install requirements ✓
   - Run `flake8 src/ scripts/ tests/` (reads `.flake8`) ✓
   - Run `black --check` (reads `pyproject.toml`) ✓
   - Run `isort --check` (reads `pyproject.toml`) ✓
   - All should pass ✓
3. Create test commit and push to PR (don't merge yet)
4. Watch GitHub Actions run
5. Commit: `"ci: verify quality-gates workflow uses config files"` (if issues found)

**Validation:**
- ✅ GitHub Actions quality-gates job passes
- ✅ No config-related failures
- ✅ Local ≈ GitHub (consistency)

**Dependencies:** All previous tasks

---

#### Task 4.4: Final Integration Test
**Priority:** 🟡 MEDIUM  
**Effort:** 3 min  
**Status:** ⬜ NOT STARTED  

**Description:**
Verify everything works end-to-end

**Steps:**
1. Make a test commit with a minor code change
2. Run locally: `pre-commit run --all-files` (should pass)
3. Push to PR branch
4. Watch GitHub Actions (should pass)
5. Revert test commit: `git reset HEAD~1`
6. Commit: `"test: final integration verification"` (if any fixes needed)

**Validation:**
- ✅ Local pre-commit passes
- ✅ GitHub Actions passes
- ✅ Zero config-related failures
- ✅ Config strategy working end-to-end

**Dependencies:** All previous tasks

---

## 📊 Task Summary

| Phase | Task | Priority | Effort | Status |
|-------|------|----------|--------|--------|
| 1 | Create `pyproject.toml` | 🔴 | 10 min | ⬜ |
| 1 | Create `.prettierrc.json` | 🔴 | 5 min | ⬜ |
| 1 | Document `.flake8` rules | 🔴 | 10 min | ⬜ |
| 1 | Pin versions | 🟠 | 5 min | ⬜ |
| 2 | Clean `.husky/pre-commit` | 🔴 | 8 min | ⬜ |
| 2 | Clean `scripts/pre-push.sh` | 🔴 | 7 min | ⬜ |
| 2 | Verify GA workflow | 🟠 | 5 min | ⬜ |
| 3 | Update Constitution | 🔴 | 15 min | ⬜ |
| 3 | Create config guide | 🟠 | 10 min | ⬜ |
| 3 | Update README | 🟡 | 5 min | ⬜ |
| 4 | Full test suite | 🔴 | 8 min | ⬜ |
| 4 | Pre-commit test | 🟠 | 4 min | ⬜ |
| 4 | GA dry run | 🟠 | 3 min | ⬜ |
| 4 | Integration test | 🟡 | 3 min | ⬜ |
| **Total** | **14 Tasks** | | **~95 min** | **⬜** |

---

## 🚀 Execution Order

### Day 1: Configuration Files + Deduplication
1. Task 1.1: Create `pyproject.toml`
2. Task 1.2: Create `.prettierrc.json`
3. Task 1.3: Document `.flake8`
4. Task 1.4: Pin versions
5. Task 2.1: Clean `.husky/pre-commit`
6. Task 2.2: Clean `scripts/pre-push.sh`
7. Task 4.1: Local full test

### Day 2: Documentation + Validation
1. Task 3.1: Update Constitution
2. Task 3.2: Create config guide
3. Task 3.3: Update README
4. Task 2.3: Verify GA workflow
5. Task 4.2: Pre-commit test
6. Task 4.3: GA dry run
7. Task 4.4: Integration test

---

## ✅ Completion Criteria

All tasks complete when:
- ✅ All 14 tasks have ✅ status
- ✅ All tests pass (local + GitHub Actions)
- ✅ Constitution updated to v1.5.0
- ✅ Zero config-related CI failures
- ✅ Developers understand config strategy

---

## 📞 Support

**Questions about a task?**
- Check the "Description" section
- Refer to plan.md for context
- Look at spec.md for problem details

**Need help?**
- Reference `.specify/CONSTITUTION_CONFIG_AUDIT.md` for problem analysis
- Check `.specify/memory/constitution.md` for current rules
- Ask in commit messages what changed and why

---

**Last Updated:** 2026-02-04  
**Status:** Ready to start Phase 1  
**Owner:** @kevingarcia  
