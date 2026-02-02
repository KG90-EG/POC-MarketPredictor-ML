# NFR-002: Tasks

> **Total Tasks:** 15  
> **Estimated Time:** ~13 Stunden  
> **Last Updated:** 2026-02-02

---

## Phase 1: Developer Experience ✅ DONE

### Task 1.1: Create `start_all.sh` ✅
- [x] Script erstellen das Backend + Frontend startet → `scripts/start.sh` existiert
- [x] Port-Cleanup vor Start (kill stale processes)
- [x] Warten auf Backend-Health bevor Frontend startet
- [x] Farbige Ausgabe für Status

### Task 1.2: Create `stop_all.sh` ✅
- [x] Script für sauberes Herunterfahren → `scripts/stop.sh` existiert
- [x] Alle Prozesse auf Port 8000 + 5173 beenden
- [x] Bestätigung dass alles gestoppt ist

### Task 1.3: Create `health_check.sh` ✅
- [x] Prüfe Backend: `curl localhost:8000/health`
- [x] Prüfe Frontend: `curl localhost:5173`
- [x] Exit-Code 0 nur wenn beide OK
- [x] Timeout nach 30 Sekunden

### Task 1.4: Update Pre-Commit Hook ✅
- [x] Black mit line-length=100
- [x] Flake8 mit konsistenten Ignore-Regeln
- [x] isort Integration
- [x] Secrets Detection (detect-secrets)

### Task 1.5: Document Startup Process ✅
- [x] README.md aktualisiert mit Quick Start
- [x] scripts/README.md mit allen Scripts dokumentiert

---

## Phase 2: Quality Gates ✅ DONE

### Task 2.1: Create Flake8 Config ✅
- [x] `.flake8` erstellt (statt config/flake8.ini)
- [x] max-line-length = 100
- [x] Konsistente Ignore-Regeln

### Task 2.2: GitHub Actions CI ✅
- [x] `.github/workflows/quality-gates.yml` existiert
- [x] Python 3.12 Checks
- [x] Frontend Build + Test

### Task 2.3: Test Coverage Report ✅
- [x] pytest-cov konfiguriert
- [x] Coverage Report in CI
- [x] Artifacts uploaded

### Task 2.4: Frontend Test Pipeline ✅
- [x] Vitest in CI integriert
- [x] Build-Step für Production-Check

### Task 2.5: Secrets Scanning ✅
- [x] detect-secrets in pre-commit config
- [x] Bandit security checks in CI

### Task 2.6: CI Notifications ✅
- [x] GitHub Status Checks konfiguriert
- [x] Quality Summary Job

---

## Phase 3: Automation ✅ DONE

### Task 3.1: Daily Cleanup Scripts ✅
- [x] `scripts/daily_cleanup.sh` existiert
- [x] `scripts/detect_dead_code.sh` existiert
- [x] Dokumentation in scripts/README.md

### Task 3.2: Dead Code Detection ✅
- [x] Vulture Script erstellt
- [x] Kann manuell oder per Cron laufen

### Task 3.3: Dependency Update Checker ✅
- [x] `.github/dependabot.yml` erstellt
- [x] Python, npm, GitHub Actions, Docker
- [x] Weekly schedule configured

### Task 3.4: Documentation ✅
- [x] README.md aktualisiert
- [x] scripts/README.md erstellt
- [x] Pre-Commit bereits dokumentiert

---

## 📊 Progress Tracker

| Phase | Completed | Total | Progress |
|-------|-----------|-------|----------|
| Phase 1 | 5 | 5 | ✅✅✅✅✅ |
| Phase 2 | 6 | 6 | ✅✅✅✅✅✅ |
| Phase 3 | 4 | 4 | ✅✅✅✅ |
| **Total** | **15** | **15** | **100%** |

---

## 🚀 Next: Phase 4 & 5 (Future)

Mögliche Erweiterungen:
- **Phase 4:** Performance Monitoring (Prometheus, Grafana)
- **Phase 5:** Advanced Testing (Load tests, E2E tests)

---

## ✅ Definition of Done

Jeder Task ist fertig wenn:
1. Code implementiert
2. Getestet (manuell oder automatisch)
3. Dokumentiert (falls user-facing)
4. Committed ohne Fehler
