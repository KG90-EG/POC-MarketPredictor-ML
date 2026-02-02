# NFR-002: Non-Functional Requirements

> **Status:** Draft  
> **Created:** 2026-02-02  
> **Author:** Kevin Garcia  
> **Priority:** High

---

## 📋 Overview

Diese Spezifikation definiert die Non-Functional Requirements (NFRs) für den MarketPredictor. NFRs beschreiben **WIE** das System funktionieren soll, nicht **WAS** es tut.

---

## 🎯 User Stories

### NFR-1: Automatischer App-Start
**Als** Entwickler  
**möchte ich** dass die Applikation mit einem einzigen Befehl startet  
**damit** ich keine manuellen Schritte ausführen muss

**Akzeptanzkriterien:**
- [ ] Ein Befehl startet Backend + Frontend gleichzeitig
- [ ] Server starten in korrekter Reihenfolge (DB → Backend → Frontend)
- [ ] Health-Check bestätigt dass alle Services laufen
- [ ] Automatische Port-Bereinigung vor Start (kill stale processes)
- [ ] Graceful Shutdown bei Ctrl+C

---

### NFR-2: Always-On Server (Zero Downtime)
**Als** Benutzer  
**möchte ich** dass alle Server immer verfügbar sind  
**damit** ich jederzeit Predictions abrufen kann

**Akzeptanzkriterien:**
- [ ] Backend antwortet innerhalb 500ms auf Health-Checks
- [ ] Frontend lädt innerhalb 3 Sekunden
- [ ] Automatischer Restart bei Crash (Supervisor/PM2)
- [ ] Logging aller Server-Events
- [ ] Alert bei Server-Ausfall (optional: Email/Slack)

---

### NFR-3: Keine Verzögerung (Performance)
**Als** Trader  
**möchte ich** dass Predictions schnell zurückkommen  
**damit** ich zeitkritische Entscheidungen treffen kann

**Akzeptanzkriterien:**
- [ ] Prediction-Endpoint antwortet in < 2 Sekunden
- [ ] Batch-Predictions (10 Stocks) in < 10 Sekunden
- [ ] Frontend-Rendering ohne sichtbares Flackern
- [ ] Caching für wiederholte Anfragen

---

### NFR-4: Hohe Testabdeckung
**Als** Entwickler  
**möchte ich** automatische Tests mit hoher Coverage  
**damit** Regressionen früh erkannt werden

**Akzeptanzkriterien:**
- [ ] Minimum 80% Code-Coverage
- [ ] Alle kritischen Pfade getestet (Predictions, Trading, Risk)
- [ ] Unit-Tests laufen in < 2 Minuten
- [ ] Integration-Tests für API-Endpoints
- [ ] Frontend-Tests mit Vitest

---

### NFR-5: CI/CD Pipeline
**Als** Entwickler  
**möchte ich** dass CI/CD Jobs sauber durchlaufen  
**damit** nur funktionierender Code deployt wird

**Akzeptanzkriterien:**
- [ ] GitHub Actions Workflow definiert
- [ ] Pipeline läuft bei jedem Push/PR
- [ ] Stages: Lint → Test → Build → Deploy
- [ ] Keine Warnungen in der Pipeline (treat warnings as errors)
- [ ] Automatische Deployment zu Staging bei main-Branch

---

### NFR-6: Pre-Commit Validierung
**Als** Entwickler  
**möchte ich** dass vor jedem Commit geprüft wird  
**damit** kein kaputter Code ins Repository kommt

**Akzeptanzkriterien:**
- [ ] Pre-Commit Hook installiert (husky)
- [ ] Flake8 Linting (Python)
- [ ] Black Formatting (Python)
- [ ] ESLint + Prettier (Frontend)
- [ ] Tests müssen bestehen
- [ ] Keine Secrets im Code (secret-scanning)

---

### NFR-7: Automatische Code-Bereinigung
**Als** Entwickler  
**möchte ich** dass nicht verwendeter Code automatisch entfernt wird  
**damit** die Codebase sauber und wartbar bleibt

**Akzeptanzkriterien:**
- [ ] Dead-Code-Detector läuft täglich (Cron 23:00)
- [ ] Unbenutzte Dateien werden archiviert (nicht gelöscht)
- [ ] Duplicate-Checker erkennt redundanten Code
- [ ] Vulture für Python Dead-Code-Detection
- [ ] Report wird generiert mit gefundenen Issues

---

## 📊 Success Metrics

| NFR | Metrik | Zielwert | Aktuell |
|-----|--------|----------|---------|
| NFR-1 | Start-Zeit | < 30 Sekunden | ❓ |
| NFR-2 | Uptime | 99.9% | ❓ |
| NFR-3 | Prediction Latency | < 2s | ❓ |
| NFR-4 | Code Coverage | ≥ 80% | ~70% |
| NFR-5 | CI Success Rate | 100% | ❓ |
| NFR-6 | Pre-Commit Pass Rate | 100% | ~60% |
| NFR-7 | Dead Code Files | 0 | 12 archived |

---

## 🔗 Dependencies

- Constitution v1.1.0 (Principle IX: Pre-Commit Validation)
- Existing scripts: `daily_cleanup.sh`, `check_duplicates.sh`
- Husky pre-commit hooks (already installed)

---

## 📝 Notes

- NFRs sind crosscutting concerns - sie betreffen alle Features
- Priorisierung: NFR-6 (Pre-Commit) > NFR-4 (Tests) > NFR-5 (CI/CD) > Rest
