# FR-005 Completion Checklist

**Feature:** Constitution Config Consolidation  
**Last Updated:** 2026-02-04  
**Status:** 🔴 NOT STARTED  

---

## ✅ Acceptance Criteria

### Phase 0: Planning ✅

- [x] Problem analysis complete
- [x] Spec written
- [x] Plan created
- [x] Tasks broken down
- [x] Constitution check passed
- [x] Timeline defined

**Status:** ✅ COMPLETE

---

### Phase 1: Configuration Files

#### Deliverable 1.1: `pyproject.toml`

- [ ] File created at root
- [ ] `[tool.black]` section complete
  - [ ] `line-length = 100`
  - [ ] `target-version = ["py312"]`
  - [ ] Exclude patterns defined
- [ ] `[tool.isort]` section complete
  - [ ] `profile = "black"`
  - [ ] `line_length = 100`
- [ ] `[tool.pytest.ini_options]` section complete
  - [ ] `testpaths = ["tests"]`
  - [ ] Markers defined
- [ ] File is valid TOML (runs `black`, `isort`, `pytest` successfully)
- [ ] Commit: `"chore: create pyproject.toml with tool configs"`

**Acceptance Criteria:**
- ✅ Black reads config: `black --version && black --check src/` passes
- ✅ isort reads config: `isort --check src/` passes  
- ✅ pytest reads config: `pytest --version` and tests can run
- ✅ No tool version warnings about missing config

**Status:** ⬜ NOT STARTED

---

#### Deliverable 1.2: `.prettierrc.json`

- [ ] File created at root
- [ ] Settings configured:
  - [ ] `"printWidth": 100`
  - [ ] `"trailingComma": "es5"`
  - [ ] `"singleQuote": true`
  - [ ] `"endOfLine": "lf"`
- [ ] File is valid JSON
- [ ] Prettier reads config successfully
- [ ] Commit: `"chore: create .prettierrc.json for frontend"`

**Acceptance Criteria:**
- ✅ Prettier reads config: `npx prettier --version` succeeds
- ✅ No frontend formatting changes needed: `npx prettier --check src/`
- ✅ JSON syntax valid (no parse errors)

**Status:** ⬜ NOT STARTED

---

#### Deliverable 1.3: `.flake8` Documentation

- [ ] All 9 ignore rules documented:
  - [ ] E203: why, when, example
  - [ ] E231: why, when, example
  - [ ] W503: why, when, example
  - [ ] F541: why, when, example
  - [ ] W293: why, when, example
  - [ ] E501: why, when, example
  - [ ] C901: why, when, example
  - [ ] F811: why, when, example
  - [ ] E731: why, when, example
- [ ] File is valid INI format
- [ ] Flake8 reads config: `flake8 --version` succeeds
- [ ] Commit: `"docs(.flake8): document all ignore rules"`

**Acceptance Criteria:**
- ✅ Each rule has comment explaining WHY
- ✅ Each rule has comment explaining WHEN
- ✅ Each rule has code EXAMPLE that triggers it
- ✅ Flake8 still works: `flake8 src/` reads config

**Status:** ⬜ NOT STARTED

---

#### Deliverable 1.4: Version Pinning

- [ ] `requirements.txt` updated:
  - [ ] Python version constraint added: `python>=3.12,<4.0`
  - [ ] flake8 pinned: `flake8==7.3.0`
  - [ ] black pinned: `black==24.3.0`
  - [ ] isort pinned: `isort==5.13.2`
  - [ ] All other linters/formatters pinned
- [ ] Commit: `"fix(deps): pin python and linter versions"`

**Acceptance Criteria:**
- ✅ Python: `python --version` shows 3.12+
- ✅ pip install works: `pip install -r requirements.txt` succeeds
- ✅ Versions match CI (no conflicts)

**Status:** ⬜ NOT STARTED

---

### Phase 2: Deduplication

#### Deliverable 2.1: `.husky/pre-commit`

- [ ] All hardcoded flake8 flags removed
  - [ ] `--max-line-length` GONE
  - [ ] `--extend-ignore` GONE
  - [ ] `--count` GONE
  - [ ] `--statistics` GONE
- [ ] All hardcoded black flags removed
  - [ ] No `--line-length` in hooks
- [ ] All hardcoded isort flags removed
  - [ ] No `--profile` in hooks
- [ ] Simplified commands:
  - [ ] `flake8 src/ scripts/ tests/` (reads `.flake8`)
  - [ ] `black --check src/` (reads `pyproject.toml`)
  - [ ] `isort --check-only src/` (reads `pyproject.toml`)
- [ ] Pre-commit runs successfully
- [ ] Commit: `"refactor(.husky): use config files instead of hardcoded flags"`

**Acceptance Criteria:**
- ✅ `pre-commit run --all-files` passes
- ✅ No "config file not found" errors
- ✅ All checks use `.flake8`, `pyproject.toml`

**Status:** ⬜ NOT STARTED

---

#### Deliverable 2.2: `scripts/pre-push.sh`

- [ ] All hardcoded flags removed (same as 2.1)
  - [ ] `--max-line-length` GONE
  - [ ] `--extend-ignore` GONE
  - [ ] `--profile` GONE
- [ ] Simplified commands use config files
- [ ] Script runs successfully
- [ ] Commit: `"refactor(scripts): use config files in pre-push"`

**Acceptance Criteria:**
- ✅ `bash scripts/pre-push.sh` succeeds
- ✅ Tools read from config files
- ✅ No hardcoded `--` flags present

**Status:** ⬜ NOT STARTED

---

#### Deliverable 2.3: GitHub Actions Verification

- [ ] `.github/workflows/quality-gates.yml` checked
- [ ] No hardcoded flags present (should be done from commit 91e9178)
- [ ] Workflow uses config files:
  - [ ] `flake8 src/` (reads `.flake8`)
  - [ ] `black --check` (reads `pyproject.toml`)
  - [ ] `isort --check` (reads `pyproject.toml`)
- [ ] Commit: `"fix(workflows): ensure quality-gates uses config"` (if needed)

**Acceptance Criteria:**
- ✅ Workflow job passes on PR
- ✅ No config-related failures

**Status:** ⬜ NOT STARTED

---

### Phase 3: Documentation

#### Deliverable 3.1: Constitution Update

- [ ] Section XII created: "Configuration Management"
- [ ] Content includes:
  - [ ] Single source of truth principle
  - [ ] Config file strategy
  - [ ] Each tool's config file listed
  - [ ] Why each file exists
  - [ ] When/how to modify rules
- [ ] All 9 flake8 rules documented in table:
  - [ ] E203, E231, W503, F541, W293, E501, C901, F811, E731
  - [ ] Each has: Rule Name, Why Ignored, When, Example Code
- [ ] Python version documented: 3.12+
- [ ] Version bumped: 1.4.0 → 1.5.0
- [ ] Commit: `"docs(constitution): add Configuration Management section v1.5.0"`

**Acceptance Criteria:**
- ✅ Section XII exists in Constitution
- ✅ All 9 rules documented with examples
- ✅ Python version constraint documented
- ✅ Version is 1.5.0
- ✅ Constitution is valid Markdown

**Status:** ⬜ NOT STARTED

---

#### Deliverable 3.2: `docs/CONFIGURATION_GUIDE.md`

- [ ] File created in `docs/CONFIGURATION_GUIDE.md`
- [ ] Sections:
  - [ ] Overview (what configs exist, why)
  - [ ] Backend Config (`.flake8`, `pyproject.toml` details)
  - [ ] Frontend Config (`eslint.config.js`, `.prettierrc.json`)
  - [ ] How to Add a Lint Rule
  - [ ] How to Update Tool Versions
  - [ ] Common Issues & Fixes
  - [ ] FAQ
- [ ] Examples included for each section
- [ ] Markdown valid
- [ ] Commit: `"docs: create CONFIGURATION_GUIDE.md"`

**Acceptance Criteria:**
- ✅ File exists at `docs/CONFIGURATION_GUIDE.md`
- ✅ All main topics covered
- ✅ Examples are complete and runnable
- ✅ Readable and beginner-friendly

**Status:** ⬜ NOT STARTED

---

#### Deliverable 3.3: `README.md` Update

- [ ] README has "Configuration" subsection
- [ ] Subsection includes:
  - [ ] Brief overview of config strategy
  - [ ] Link to `CONFIGURATION_GUIDE.md`
  - [ ] Link to Constitution (XII)
- [ ] Links work correctly
- [ ] Markdown valid
- [ ] Commit: `"docs(README): reference configuration guide"`

**Acceptance Criteria:**
- ✅ README mentions configuration management
- ✅ Links are valid (markdown links)
- ✅ New developers can find config info

**Status:** ⬜ NOT STARTED

---

### Phase 4: Validation & Testing

#### Test 4.1: Full Local Test Suite ✅

- [ ] `python -m pytest tests/ -v` passes
- [ ] `black --check src/ scripts/` passes (0 files reformatted)
- [ ] `isort --check src/ scripts/` passes (no changes needed)
- [ ] `flake8 src/ scripts/ tests/` passes (or only pre-existing)
- [ ] `npm run lint` passes in frontend/
- [ ] `npm run format:check` passes in frontend/
- [ ] Commit: `"test: verify all linting passes with consolidated config"`

**Acceptance Criteria:**
- ✅ pytest: All tests green (103 tests pass, 2 skipped OK)
- ✅ black: 0 files would be reformatted
- ✅ isort: No import changes needed
- ✅ flake8: 0 violations (ignores in `.flake8` work)
- ✅ eslint: 0 errors in frontend
- ✅ prettier: All files formatted correctly

**Status:** ⬜ NOT STARTED

---

#### Test 4.2: Pre-Commit Hook ✅

- [ ] `pre-commit run --all-files` passes
- [ ] No "config file not found" errors
- [ ] No hardcoded flag errors
- [ ] All tools read from config files
- [ ] Commit: `"test: verify pre-commit hook uses consolidated config"`

**Acceptance Criteria:**
- ✅ Pre-commit hook succeeds
- ✅ Tools read correct config files
- ✅ No version mismatches

**Status:** ⬜ NOT STARTED

---

#### Test 4.3: GitHub Actions Dry Run ✅

- [ ] Create test PR (don't merge)
- [ ] Watch GitHub Actions run
- [ ] `quality-gates.yml` job passes
- [ ] No config-related failures
- [ ] No "file not found" errors
- [ ] Revert test commit
- [ ] Commit: `"ci: verify quality-gates workflow passes"`

**Acceptance Criteria:**
- ✅ GitHub Actions quality-gates job passes
- ✅ All checks (flake8, black, isort, eslint) pass
- ✅ Local ≈ GitHub Actions (consistency)

**Status:** ⬜ NOT STARTED

---

#### Test 4.4: Integration Test ✅

- [ ] Make test commit with minor change
- [ ] Run `pre-commit run --all-files` locally (pass)
- [ ] Push to PR
- [ ] GitHub Actions runs (pass)
- [ ] Zero config-related failures
- [ ] Revert test commit
- [ ] Commit: `"test: final integration verification"`

**Acceptance Criteria:**
- ✅ Local pre-commit passes
- ✅ GitHub Actions passes
- ✅ Zero config-related issues
- ✅ Config strategy working end-to-end

**Status:** ⬜ NOT STARTED

---

## 📊 Overall Progress

### Summary

**Phase 0: Planning** ✅ COMPLETE
- 6/6 criteria met

**Phase 1: Configuration Files** ⬜ NOT STARTED
- 0/4 deliverables complete

**Phase 2: Deduplication** ⬜ NOT STARTED
- 0/3 deliverables complete

**Phase 3: Documentation** ⬜ NOT STARTED
- 0/3 deliverables complete

**Phase 4: Validation** ⬜ NOT STARTED
- 0/4 tests passed

---

### Completion Status

| Phase | Progress | Status |
|-------|----------|--------|
| 0: Planning | 6/6 (100%) | ✅ COMPLETE |
| 1: Config | 0/4 (0%) | ⬜ NOT STARTED |
| 2: Dedup | 0/3 (0%) | ⬜ NOT STARTED |
| 3: Docs | 0/3 (0%) | ⬜ NOT STARTED |
| 4: Test | 0/4 (0%) | ⬜ NOT STARTED |
| **TOTAL** | **6/21 (29%)** | **⬜ IN PLANNING** |

---

## 🎯 Final Sign-Off

### Acceptance Gates

**Before Merge:**
- [ ] All 21 checklist items complete (100%)
- [ ] Constitution v1.5.0 with config section
- [ ] Zero config-related CI failures
- [ ] Developers can run tools locally with config files
- [ ] Configuration guide available

**Before Production:**
- [ ] Feature merged to main
- [ ] 1 week of zero config failures (monitoring)
- [ ] New developer successfully uses config (if available)

---

## 📝 Notes

- Update this checklist as you complete each task
- Mark items with ✅ when done
- Update status at top when phase complete
- Comment if blockers encountered

---

**Feature Owner:** @kevingarcia  
**Last Status Update:** 2026-02-04  
**Next Review:** After Phase 1 complete  
