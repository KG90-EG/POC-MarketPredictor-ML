# Documentation Reorganization Plan

## Current Status
Documentation is flat in `docs/` directory with mixed concerns.

## New Structure

```
docs/
├── conf.py                          # Sphinx configuration
├── index.rst                        # Main documentation index (Sphinx)
├── index.md                        # Markdown index (GitHub Pages fallback)
│
├── getting-started/                # Quick start guides
│   ├── index.md
│   ├── quick-start.md
│   ├── installation.md
│   └── first-steps.md
│
├── deployment/                     # All deployment docs
│   ├── index.md
│   ├── production-ready.md        → ../PRODUCTION_READY.md (symlink)
│   ├── automated-deployment.md    → ../AUTOMATED_DEPLOYMENT.md (symlink)
│   ├── backend-deployment.md      → BACKEND_DEPLOYMENT.md (moved)
│   └── frontend-deployment.md     → FRONTEND_DEPLOYMENT.md (moved)
│
├── architecture/                   # Architecture Decision Records
│   ├── index.md
│   ├── adr-001-architecture-overview.md     → ADR-001-... (moved)
│   ├── adr-002-model-training-strategy.md   → ADR-002-... (moved)
│   └── adr-003-caching-strategy.md          → ADR-003-... (moved)
│
├── features/                       # Feature documentation
│   ├── index.md
│   ├── production-features.md      → PRODUCTION_FEATURES.md (moved)
│   ├── frontend-components.md      → FRONTEND_COMPONENTS.md (moved)
│   ├── cryptocurrency-portfolio.md  # New: extracted from features
│   └── ai-analysis.md               # New: extracted from features
│
├── operations/                     # Operations & monitoring
│   ├── index.md
│   ├── performance-monitoring.md   → PERFORMANCE_MONITORING.md (moved)
│   ├── security.md                 # New: security best practices
│   ├── testing.md                  # New: testing guide
│   └── troubleshooting.md          # New: common issues
│
├── development/                    # Development guides
│   ├── index.md
│   ├── contributing.md             → ../CONTRIBUTING.md (symlink)
│   ├── code-quality.md
│   ├── testing-guide.md
│   └── accessibility.md            → ACCESSIBILITY_TESTING.md (moved)
│
├── api/                            # API reference
│   ├── index.md
│   ├── endpoints.md                # All API endpoints
│   ├── models.md                   # Request/response models
│   └── websockets.md               # WebSocket API
│
└── history/                        # Historical docs (kept as-is)
    ├── README.md
    ├── IMPLEMENTATION_SUMMARY.md
    ├── ARCHITECTURE_REVIEW.md
    ├── IMPROVEMENTS.md
    └── GITHUB_ACTIONS_FIXES.md
```

## Implementation Steps

### Phase 1: Create Structure (✅ DONE)
- [x] Install Sphinx, sphinx-rtd-theme, myst-parser
- [x] Create conf.py
- [x] Create index.rst with toctree
- [x] Create directory structure

### Phase 2: Move Files
```bash
# Move to architecture/
mv ADR-001-architecture-overview.md architecture/
mv ADR-002-model-training-strategy.md architecture/
mv ADR-003-caching-strategy.md architecture/

# Move to deployment/
mv BACKEND_DEPLOYMENT.md deployment/
mv FRONTEND_DEPLOYMENT.md deployment/

# Move to features/
mv PRODUCTION_FEATURES.md features/
mv FRONTEND_COMPONENTS.md features/

# Move to operations/
mv PERFORMANCE_MONITORING.md operations/

# Move to development/
mv ACCESSIBILITY_TESTING.md development/accessibility.md

# Create symlinks for root-level docs
cd deployment
ln -s ../../PRODUCTION_READY.md production-ready.md
ln -s ../../AUTOMATED_DEPLOYMENT.md automated-deployment.md
cd ..

cd development
ln -s ../../CONTRIBUTING.md contributing.md
cd ..
```

### Phase 3: Create Index Files
Each directory needs an index.md with:
- Overview of the section
- Navigation to sub-documents
- Related sections

### Phase 4: Build & Test
```bash
# Build Sphinx docs
cd docs
sphinx-build -b html . _build

# View locally
open _build/index.html

# Or use sphinx-autobuild for live reload
pip install sphinx-autobuild
sphinx-autobuild . _build --port 8080
```

### Phase 5: Deploy to ReadTheDocs
1. Sign up at https://readthedocs.org
2. Import repository
3. Configure:
   - Documentation path: `docs/`
   - Requirements file: `docs/requirements.txt`
4. Auto-builds on every commit to main

## Benefits of New Structure

✅ **Better Organization**: Logical grouping by purpose
✅ **Easier Navigation**: Clear hierarchy
✅ **Scalable**: Easy to add new docs
✅ **Search-Friendly**: Sphinx provides full-text search
✅ **Versioning**: ReadTheDocs supports version control
✅ **Professional**: Standard documentation structure
✅ **Discoverable**: Each section has clear purpose

## Backward Compatibility

- Keep `index.md` for GitHub Pages
- Symlinks ensure old paths work
- Redirect rules in ReadTheDocs if needed

## Timeline

- **Reorganization**: 30-60 minutes
- **Content Review**: 1-2 hours
- **ReadTheDocs Setup**: 15 minutes
- **Testing**: 30 minutes

**Total**: ~3-4 hours for complete migration
