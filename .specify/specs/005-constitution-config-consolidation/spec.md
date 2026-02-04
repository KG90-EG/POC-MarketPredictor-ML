# FR-005: Constitution Config Consolidation

**Feature ID:** 005-constitution-config-consolidation  
**Status:** 🔴 NOT STARTED  
**Priority:** CRITICAL (Quality Gate Blocker)  
**Owner:** Kevin Garcia  
**Created:** 2026-02-04  

---

## 🎯 Problem Statement

### Current State (Broken)

Our configuration is **scattered and duplicated** across 4+ locations:

1. ✅ `.flake8` (source of truth SHOULD BE)
2. ⚠️ `.husky/pre-commit` (hardcoded flake8 flags)
3. ⚠️ `scripts/pre-push.sh` (hardcoded flake8 flags)
4. ❌ `pyproject.toml` (MISSING - Black/isort config)
5. ❌ `.prettierrc.json` (MISSING - Prettier config)
6. ❌ Constitution (NO CONFIG DOCUMENTATION)

### Impact

**Problem 1: Maintenance Nightmare**
- Change `.flake8` → must also change 2 scripts + 1 workflow
- Easy to forget = inconsistent CI/CD failures
- Happened 5+ times in last 2 days

**Problem 2: No Documentation**
- Why is E231 ignored? Unknown
- New developers can't understand rules
- Reintroduction of fixed bugs likely

**Problem 3: Missing Configs**
- Black formatting unspecified (could differ locally vs CI)
- isort config missing
- Prettier config missing
- Python version mismatch (3.11+ vs actual 3.12/3.14)

**Problem 4: Constitution Incomplete**
- Doesn't mention `.pyproject.toml` or `.prettierrc.json`
- No explanation of config strategy
- No single source of truth documented

### Why It Matters

- 🔴 **Quality Gate Blocker**: Workflow failures waste ~30 min/week
- 🟠 **Onboarding Blocker**: New developers confused by multiple config sources
- 🟠 **Maintenance Debt**: Every tool update requires 4+ file changes
- 🟡 **Consistency Risk**: Local ≠ CI failures hard to debug

---

## ✅ Solution Overview

### Goal

**Single Source of Truth for ALL configuration:**
- Each rule appears in EXACTLY ONE file
- Constitution documents the strategy
- CI/CD and pre-commit hooks reference config files (no hardcoding)
- Python version consistent everywhere

### Key Principles

1. **DRY (Don't Repeat Yourself)**
   - Config in ONE place
   - Tools reference that place

2. **Explicit Documentation**
   - EVERY ignore rule: WHY + WHEN
   - Version constraints documented
   - Tool versions pinned

3. **Automated Enforcement**
   - Pre-commit checks for hardcoded config
   - CI/CD fails if config duplicated
   - Linter versions pinned in requirements.txt

### Success Criteria

- ✅ All config files created (`.flake8`, `pyproject.toml`, `.prettierrc.json`)
- ✅ All hardcoded flags removed from scripts/workflows
- ✅ Constitution updated with config strategy
- ✅ Each rule documented with reason
- ✅ Python version consistent + documented
- ✅ Pre-commit detects config duplication
- ✅ All tests pass (local + CI)

---

## 📋 Scope

### IN Scope

#### Backend Configuration
- `.flake8` - complete with all 9 ignore rules documented
- `pyproject.toml` - Black, isort, pytest config
- Python version specification (3.12+)
- Pin all linter versions in requirements.txt

#### Frontend Configuration
- `.prettierrc.json` - standardize formatting
- eslint config reference (already exists)

#### Process Configuration
- `.husky/pre-commit` - remove all hardcoded flags
- `scripts/pre-push.sh` - remove all hardcoded flags
- Auto-detection in CI/CD for hardcoded config

#### Documentation
- Constitution: Add "Configuration Management" section
- Document EACH ignore rule
- Create CONFIGURATION_GUIDE.md for developers

### OUT of Scope

- Changing linting rules (only consolidating them)
- Changing tool versions (only documenting them)
- New tools (only organizing existing ones)
- Backend code refactoring
- Frontend component changes

---

## 🔗 Dependencies

### Constitution Dependencies
- Constitution v1.4.0 (Principle IX: Pre-Commit Validation)
- Constitution v1.4.0 (Principle XI: Clean Repository Structure)

### External Tools
- flake8 6.0.0 → 7.3.0+ (now unified)
- Black 24.3.0 (linting tool)
- isort 5.13.2 (import sorting)
- Prettier (frontend formatting)
- pytest 8.4.0 (testing)

### Artifacts
- `.specify/CONSTITUTION_CONFIG_AUDIT.md` (problem analysis)
- Current workflows (will be simplified)
- Current hooks (will be cleaned)

---

## 📊 Acceptance Criteria

### Phase 0 Complete (This Spec)
- ✅ Spec written and reviewed
- ✅ Plan created with timeline
- ✅ Tasks broken down
- ✅ Constitution check passed

### Phase 1 Complete (Config Files)
- ✅ `pyproject.toml` created with Black config
  - `line-length = 100`
  - `target-version = ["py312"]`
  - isort section present
  - pytest section present
- ✅ `.prettierrc.json` created
  - `printWidth: 100`
  - `trailingComma: "es5"`
  - Consistent with `.flake8`

### Phase 2 Complete (Deduplication)
- ✅ `.husky/pre-commit` removes hardcoded flake8 flags
  - Uses: `flake8 src/` (references `.flake8`)
  - Uses: `black --check src/` (references `pyproject.toml`)
- ✅ `scripts/pre-push.sh` same as above
- ✅ `.github/workflows/quality-gates.yml` uses config files (DONE ✅)

### Phase 3 Complete (Documentation)
- ✅ Constitution has "Configuration Management" section
- ✅ Each ignore rule documented:
  - `E203`: Why, When, Example
  - `E231`: Why, When, Example
  - (all 9 rules)
- ✅ Python version documented (3.12+)
- ✅ `CONFIGURATION_GUIDE.md` created for developers

### Phase 4 Complete (Validation)
- ✅ Pre-commit hook detects hardcoded config
- ✅ All local tests pass
- ✅ All CI tests pass
- ✅ Configuration consistent (local = CI)
- ✅ Zero workflow failures due to config

---

## 📝 Notes

### Why This Order?

1. **Phase 0 (Planning)**: Get agreement on approach
2. **Phase 1 (Files)**: Create missing config files
3. **Phase 2 (Dedup)**: Remove hardcoded config
4. **Phase 3 (Docs)**: Document why & when rules apply
5. **Phase 4 (Validation)**: Ensure consistency

### Why This Matters?

- Every day we don't fix this = 30 min wasted on CI failures
- New developers onboard with confusion
- Risk of re-introducing fixed bugs
- Maintenance burden grows with each tool update

### Known Risks

- Might need to update CI/CD if it caches old config
- Prettier config might conflict with existing styling
- pytest.ini might duplicate config from pyproject.toml
- Python 3.12 might have new deprecations

### Questions for Review

1. Should pytest config go in `pyproject.toml` or stay in `pytest.ini`?
2. Should we add pre-commit hook to detect hardcoded flags?
3. Should we version-pin tools (flake8==7.3.0) or allow ranges (flake8>=7.0,<8.0)?
4. Should we auto-generate config from Constitution?

---

## 📚 Related Documentation

- `.specify/CONSTITUTION_CONFIG_AUDIT.md` - Problem analysis
- `.specify/memory/constitution.md` - Current Constitution
- `.github/workflows/quality-gates.yml` - CI/CD workflow
- `.husky/pre-commit` - Pre-commit hooks

---

## ✨ Next Steps

1. **Review this spec** - Is approach correct?
2. **Create plan.md** - Define phases & timeline
3. **Break into tasks** - Specific actions for each phase
4. **Execute** - Follow plan.md + tasks.md
5. **Validate** - Use checklist.md

---

## 🎓 Learning Outcomes

After completing this feature, developers will understand:
- How configuration files work together
- Why each rule is needed
- How to add new linting rules properly
- How to maintain configuration consistency
- How to debug CI/CD config issues

---

**Status:** Ready for Phase 0 Review  
**Effort Estimate:** ~95 minutes  
**Risk Level:** LOW (configuration only, no logic changes)  
**Blocking:** Quality gates, developer onboarding  
