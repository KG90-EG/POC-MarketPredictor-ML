# NFR-002: Implementation Plan

> **Version:** 1.0.0  
> **Last Updated:** 2026-02-02

---

## 🏗️ Architecture Decisions

### AD-1: Unified Start Command
**Decision:** Erstelle `scripts/start_all.sh` das alle Services orchestriert

**Rationale:**
- Ein Einstiegspunkt reduziert Komplexität
- Docker Compose wäre ideal, aber zu heavy für Entwicklung
- Shell-Script mit Process-Management (trap für cleanup)

**Implementation:**
```bash
#!/bin/bash
# 1. Kill stale processes
# 2. Start Backend (background)
# 3. Wait for Backend health
# 4. Start Frontend (background)
# 5. Trap SIGINT for graceful shutdown
```

---

### AD-2: Process Supervisor
**Decision:** Verwende `supervisord` oder `pm2` für Production, Shell für Dev

**Rationale:**
- Development: Einfaches Shell-Script reicht
- Production: Supervisor für Auto-Restart bei Crash
- Keine zusätzlichen Dependencies in Dev

**Alternatives Considered:**
- Docker Compose: Zu heavy für schnelle Entwicklung
- systemd: Nur für Linux, nicht macOS-kompatibel

---

### AD-3: Pre-Commit Hook Enhancement
**Decision:** Erweitere bestehenden Husky-Hook mit strikterer Validierung

**Rationale:**
- Husky ist bereits installiert
- Hook muss alle Checks bestehen BEVOR commit erlaubt wird
- `--no-verify` nur in Ausnahmefällen

**Checks in Reihenfolge:**
1. Black (Python formatting)
2. Flake8 (Python linting) - nur kritische Fehler
3. ESLint (Frontend)
4. Prettier (Frontend)
5. Quick Tests (nur betroffene Dateien)

---

### AD-4: CI/CD Pipeline Structure
**Decision:** GitHub Actions mit Matrix-Build

**Pipeline Stages:**
```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Lint   │ → │  Test   │ → │  Build  │ → │ Deploy  │
└─────────┘   └─────────┘   └─────────┘   └─────────┘
```

**Jobs:**
- `lint`: Black, Flake8, ESLint, Prettier
- `test-python`: pytest mit Coverage
- `test-frontend`: vitest
- `build`: Frontend build, Docker image
- `deploy`: Push zu Staging (nur main branch)

---

### AD-5: Dead Code Management
**Decision:** Täglich automatische Analyse, wöchentlich manuelle Review

**Rationale:**
- Automatisches Löschen ist gefährlich
- Archivierung erlaubt Wiederherstellung
- Report für manuelle Entscheidung

**Tools:**
- `vulture` (Python dead code)
- `scripts/detect_dead_code.sh` (bereits vorhanden)
- `scripts/daily_cleanup.sh` (bereits vorhanden)

---

## 📁 File Structure

```
scripts/
├── start_all.sh           # NEW: Unified start command
├── stop_all.sh            # NEW: Graceful shutdown
├── health_check.sh        # NEW: Verify all services running
├── daily_cleanup.sh       # EXISTS: Dead code archiver
├── check_duplicates.sh    # EXISTS: Duplicate finder
└── detect_dead_code.sh    # EXISTS: Dead code detector

.github/workflows/
├── ci.yml                 # NEW: Main CI pipeline
└── cleanup.yml            # NEW: Weekly dead code report

.husky/
└── pre-commit             # MODIFY: Stricter checks

config/
└── flake8.ini             # NEW: Flake8 config (ignore non-critical)
```

---

## 🎯 Implementation Phases

### Phase 1: Developer Experience (Day 1-2)
- `start_all.sh` + `stop_all.sh`
- Health-Check Script
- Verbesserte Pre-Commit Hooks

### Phase 2: Quality Gates (Day 3-4)
- Flake8 Konfiguration (nur kritische Fehler)
- CI/CD Pipeline (GitHub Actions)
- Test-Coverage Report

### Phase 3: Automation (Day 5-6)
- Cron-Job Optimierung
- Dead-Code Reports
- Documentation

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pre-Commit zu streng | Entwickler umgehen mit --no-verify | Balance finden, nur kritische Checks |
| CI zu langsam | Lange Feedback-Loops | Parallele Jobs, Caching |
| False Positives bei Dead Code | Aktiver Code wird archiviert | Manuelle Review vor Löschung |

---

## 📊 Estimated Effort

| Phase | Tasks | Aufwand |
|-------|-------|---------|
| Phase 1 | 5 | 4 Stunden |
| Phase 2 | 6 | 6 Stunden |
| Phase 3 | 4 | 3 Stunden |
| **Total** | **15** | **~13 Stunden** |
