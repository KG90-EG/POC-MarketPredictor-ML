# Configuration Guide

> **Single Source of Truth** - All tool configurations are centralized in specific files.
> This eliminates config drift and ensures consistency across local development and CI/CD.

## Quick Reference

| Tool       | Config File           | Key Settings                    |
|------------|----------------------|---------------------------------|
| Black      | `pyproject.toml`     | line-length=100, target=py312   |
| isort      | `pyproject.toml`     | profile=black, line-length=100  |
| pytest     | `pyproject.toml`     | testpaths, asyncio_mode=auto    |
| Flake8     | `.flake8`            | max-line-length=100, ignores    |
| Prettier   | `.prettierrc.json`   | printWidth=100, singleQuote     |
| ESLint     | `frontend/eslint.config.js` | React + Hooks rules     |

## Python Configuration

### pyproject.toml

```toml
[tool.black]
line-length = 100
target-version = ["py312"]
include = '\.pyi?$'
extend-exclude = '''/(venv|\.venv|node_modules|\.git|__pycache__|\.mypy_cache)/'''

[tool.isort]
profile = "black"
line_length = 100
known_first_party = ["src", "trading_engine", "backtest", "training"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
asyncio_mode = "auto"
filterwarnings = ["ignore::DeprecationWarning", "ignore::PendingDeprecationWarning"]
addopts = "--ignore=tests/phase1 --ignore=tests/phase2 --ignore=tests/test_crypto.py --ignore=tests/test_integration.py"
```

### .flake8

The `.flake8` file contains all linting rules with full documentation:

```ini
[flake8]
max-line-length = 100

# Each ignore rule is documented with:
# - REASON: Why it's ignored
# - CAN_REENABLE: Conditions to remove
# - EXAMPLE: Code that triggers it

ignore =
    E203,   # Black compatibility (slice whitespace)
    W503,   # Black compatibility (line break before operator)
    F401,   # Unused imports (in __init__.py for re-exports)
    # ... see full .flake8 for complete list
```

**Important:** All Flake8 ignore rules are documented. Before adding a new ignore:
1. Understand WHY it's needed
2. Document the REASON
3. Consider if it can be fixed instead

## Frontend Configuration

### .prettierrc.json (Root)

```json
{
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5"
}
```

### ESLint

ESLint configuration lives in `frontend/eslint.config.js` and extends:
- `eslint:recommended`
- `plugin:react/recommended`
- `plugin:react-hooks/recommended`

## Using the Configuration

### Local Development

All tools automatically read their config files:

```bash
# Format Python code
black src/ scripts/ tests/

# Sort imports
isort src/ scripts/ tests/

# Lint Python
flake8 src/ scripts/ tests/

# Format frontend
cd frontend && npm run format

# Lint frontend
cd frontend && npm run lint
```

**Note:** No need to pass `--line-length` or `--profile` flags - they're in the config files!

### Pre-commit Hook

The pre-commit hook (`.husky/pre-commit`) runs these checks automatically:
1. Flake8 (uses `.flake8`)
2. Black formatting check (uses `pyproject.toml`)
3. Quick pytest run
4. ESLint + Prettier (uses respective configs)

### CI/CD

GitHub Actions workflows also use the config files:
- `quality-gates.yml` - Runs `flake8 src/ scripts/ tests/` (no flags needed)
- `ci.yml` - Runs full test suite via pytest

## Adding a New Tool

1. **Choose the right config file:**
   - Python tools → Add `[tool.toolname]` to `pyproject.toml`
   - JS/TS tools → Add to `frontend/package.json` or separate config

2. **Configure centrally:**
   - Put ALL settings in the config file
   - Don't use CLI flags in scripts

3. **Update this guide:**
   - Add to Quick Reference table
   - Document key settings

4. **Update Constitution:**
   - Add to Section XII if globally applicable

## Troubleshooting

### "My local linting passes but CI fails"

Ensure you're not using different flags locally:
```bash
# Wrong - hardcoded flags
flake8 src/ --max-line-length=100

# Correct - uses .flake8
flake8 src/
```

### "Black and isort conflict"

Both tools use `line-length=100` and isort uses `profile=black`, so they should be compatible.
Always run isort AFTER black, or use `isort --profile black`.

### "New error code appearing"

When upgrading Flake8 or plugins, new rules may trigger. Options:
1. Fix the code (preferred)
2. Add to `.flake8` ignore with documentation (if genuinely problematic)

---

**Reference:** See Constitution Section XII for governance rules.
