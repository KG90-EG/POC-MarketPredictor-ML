# NFR-002: Tasks

> **Total Tasks:** 15  
> **Estimated Time:** ~13 Stunden  
> **Last Updated:** 2026-02-02

---

## Phase 1: Developer Experience (Day 1-2)

### Task 1.1: Create `start_all.sh`
- [ ] Script erstellen das Backend + Frontend startet
- [ ] Port-Cleanup vor Start (kill stale processes)
- [ ] Warten auf Backend-Health bevor Frontend startet
- [ ] Trap für SIGINT (Ctrl+C) graceful shutdown
- [ ] Farbige Ausgabe für Status

### Task 1.2: Create `stop_all.sh`
- [ ] Script für sauberes Herunterfahren
- [ ] Alle Prozesse auf Port 8000 + 5173 beenden
- [ ] Bestätigung dass alles gestoppt ist

### Task 1.3: Create `health_check.sh`
- [ ] Prüfe Backend: `curl localhost:8000/health`
- [ ] Prüfe Frontend: `curl localhost:5173`
- [ ] Exit-Code 0 nur wenn beide OK
- [ ] Timeout nach 30 Sekunden

### Task 1.4: Update Pre-Commit Hook
- [ ] Black nur bei geänderten Python-Dateien
- [ ] Flake8 mit `--select=E9,F63,F7,F82` (nur kritische)
- [ ] ESLint nur bei geänderten JS/JSX-Dateien
- [ ] Schnelle Tests überspringen (optional flag)

### Task 1.5: Document Startup Process
- [ ] README.md aktualisieren mit `./scripts/start_all.sh`
- [ ] Troubleshooting für häufige Probleme

---

## Phase 2: Quality Gates (Day 3-4)

### Task 2.1: Create Flake8 Config
- [ ] `config/flake8.ini` erstellen
- [ ] Ignoriere non-kritische Warnungen (W, E1, E2, E3)
- [ ] max-line-length = 100
- [ ] exclude: venv, node_modules, migrations

### Task 2.2: Create GitHub Actions CI
- [ ] `.github/workflows/ci.yml` erstellen
- [ ] Matrix: Python 3.11, 3.12, 3.14
- [ ] Cache pip dependencies
- [ ] Parallel: lint + test + build

### Task 2.3: Add Test Coverage Report
- [ ] pytest-cov konfigurieren
- [ ] Minimum 80% Coverage für PR-Merge
- [ ] Coverage Badge in README

### Task 2.4: Frontend Test Pipeline
- [ ] Vitest in CI integrieren
- [ ] Build-Step für Production-Check

### Task 2.5: Secrets Scanning
- [ ] gitleaks oder trufflehog einrichten
- [ ] Pre-Commit Hook für Secrets
- [ ] CI-Job für Secret-Scanning

### Task 2.6: CI Notifications
- [ ] Slack/Discord Webhook bei Failure (optional)
- [ ] GitHub Status Checks required for merge

---

## Phase 3: Automation (Day 5-6)

### Task 3.1: Optimize Daily Cleanup Cron
- [ ] Logging verbessern
- [ ] Email-Report bei gefundenen Issues (optional)
- [ ] Launchd plist für macOS erstellen

### Task 3.2: Weekly Dead Code Report
- [ ] GitHub Action für wöchentlichen Report
- [ ] Vulture Integration
- [ ] Issue erstellen mit gefundenen Dead-Code-Stellen

### Task 3.3: Dependency Update Checker
- [ ] Dependabot konfigurieren
- [ ] Renovate als Alternative prüfen
- [ ] Automatische PRs für Updates

### Task 3.4: Documentation
- [ ] CONTRIBUTING.md erstellen
- [ ] Pre-Commit Setup Anleitung
- [ ] CI/CD Dokumentation

---

## 📊 Progress Tracker

| Phase | Completed | Total | Progress |
|-------|-----------|-------|----------|
| Phase 1 | 0 | 5 | ⬜⬜⬜⬜⬜ |
| Phase 2 | 0 | 6 | ⬜⬜⬜⬜⬜⬜ |
| Phase 3 | 0 | 4 | ⬜⬜⬜⬜ |
| **Total** | **0** | **15** | **0%** |

---

## 🚀 Quick Start

```bash
# Task 1.1 starten:
cd /Users/kevingarcia/Documents/POC-MarketPredictor-ML
# Implementiere scripts/start_all.sh
```

---

## ✅ Definition of Done

Jeder Task ist fertig wenn:
1. Code implementiert
2. Getestet (manuell oder automatisch)
3. Dokumentiert (falls user-facing)
4. Committed ohne Fehler
