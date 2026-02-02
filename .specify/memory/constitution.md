# Market Predictor ML Constitution

## Core Principles

### I. Decision Support Only - NIEMALS Empfehlungen
Das System ist ein **Entscheidungsunterstützungssystem**, KEIN Beratungssystem.
- NIEMALS direkte Kauf/Verkauf-Empfehlungen ausgeben
- Immer als "Signal" oder "Score" formulieren, nie als "Empfehlung"
- User trifft finale Entscheidung - System liefert nur Daten
- Disclaimer bei jeder Ausgabe: "Dies ist keine Anlageberatung"

### II. Quantitative Signals Dominieren
Scoring-Formel ist unveränderlich:
- **Technical Signals: 40%** (RSI, MACD, Bollinger, ADX)
- **ML Probability: 30%** (Random Forest Prediction)
- **Momentum: 20%** (Multi-Period: 10d, 30d, 60d)
- **Market Regime: 10%** (VIX + S&P 500 Trend)

Diese Gewichtung darf NUR durch Constitution-Amendment geändert werden.

### III. LLM als Kontext-Provider - Strikte Grenzen
LLM (OpenAI) darf:
- ✅ News zusammenfassen (max. 3 Sätze)
- ✅ Risiko-Events identifizieren
- ✅ Score um **±5% maximum** anpassen

LLM darf NICHT:
- ❌ Scores überschreiben oder ignorieren
- ❌ Direkte Kauf/Verkauf-Aussagen machen
- ❌ Quantitative Signale widersprechen

### IV. Market Regime Hat Veto-Recht
Wenn Market Regime = "RISK_OFF":
- **Alle BUY-Signale werden blockiert**
- UI zeigt "DEFENSIVE MODE ACTIVE"
- Position Limits werden auf 50% reduziert

Keine Ausnahmen. Kapitalschutz > Gewinnchancen.

### V. Position Limits Sind Unverletzlich
- **Einzelaktie**: Maximum 10% des Portfolios
- **Einzelcrypto**: Maximum 5% des Portfolios
- **Gesamtaktien**: Maximum 70% des Portfolios
- **Gesamtcrypto**: Maximum 20% des Portfolios
- **Cash Reserve**: Minimum 10% des Portfolios

Bei Risk-Off werden alle Limits auf 50% reduziert.

### VI. Explainability Ist Pflicht
Jeder Score muss erklärbar sein:
- Top 3 positive Faktoren anzeigen
- Top 3 Risiko-Faktoren anzeigen
- User muss verstehen WARUM ein Score hoch/niedrig ist
- "Black Box" Ausgaben sind verboten

### VII. Test-First Development
- Jedes neue Feature braucht Tests VOR dem Merge
- Minimum 80% Test-Coverage für neue Code-Paths
- Tests müssen grün sein bevor PR merged wird
- Integration Tests für alle API-Endpoints

### VIII. Clean Codebase
- Unused Code wird täglich archiviert (23:00 Cron)
- Keine Backup-Files im Repository (.bak, .tmp, ~)
- Jede neue Datei wird auf Duplikate geprüft
- Stale Files (>90 Tage ohne Änderung) werden reviewed

### IX. Pre-Commit Validation - Keine Broken Builds
**Vor JEDEM Commit müssen folgende Checks bestehen:**

1. **Backend Validation**
   - `python3 -m pytest tests/` - Alle Tests grün
   - `flake8 src/` - Keine Linting-Fehler
   - `black --check src/` - Code korrekt formatiert

2. **Frontend Validation**
   - `npx eslint src/` - Keine ESLint-Fehler (Errors = Blocker)
   - `npm run build` - Build muss erfolgreich sein
   - JSX Syntax korrekt (kein unescaptes `<` oder `>`)

3. **Integration Check**
   - Backend startet ohne Fehler
   - Frontend startet ohne Fehler
   - Health-Endpoint erreichbar

**Warum?** 
- CI/CD Pipelines dürfen NIEMALS wegen vermeidbarer Fehler failen
- Broken UI ist inakzeptabel für Production
- Zeit für Debugging = Zeit für Features verloren

**Konsequenz bei Verstoß:**
- Commit wird revertiert
- Issue wird erstellt für Root Cause Analysis
- Kein Blame, aber Prozess wird verbessert

### X. Living Documentation
Nach jedem Feature-Commit müssen relevante Docs aktualisiert werden:

1. **README.md** - Bei neuen Features, Commands, oder API-Änderungen
2. **TRADER_GUIDE.md** - Bei user-facing Features
3. **openapi.json** - Bei API-Endpoint Änderungen (auto-generiert)
4. **ADR erstellen** - Bei Architektur-Entscheidungen

**Regel:** Code ohne aktuelle Doku ist nicht fertig.

**Ausnahmen:**
- Reine Bugfixes (kein neues Feature)
- Refactoring ohne Funktionsänderung
- Test-Only Commits

## Technology Constraints

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ML**: scikit-learn Random Forest
- **Data**: yfinance für Marktdaten
- **Cache**: In-Memory (InMemoryCache)
- **LLM**: OpenAI GPT-4o-mini

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: CSS Modules
- **Charts**: Recharts
- **State**: React hooks (kein Redux)

### Infrastructure
- **VCS**: Git + GitHub
- **CI/CD**: GitHub Actions
- **Deployment**: Docker / Railway
- **Monitoring**: Prometheus + Grafana

## Quality Gates

### Before Commit (MANDATORY)
1. ✅ Backend tests pass (`python3 -m pytest tests/`)
2. ✅ No Python linting errors (`flake8 src/`)
3. ✅ No ESLint errors in frontend (`npx eslint src/`)
4. ✅ Frontend builds successfully (`npm run build`)
5. ✅ Python formatted (`black src/`)
6. ✅ Frontend formatted (`npm run format`)

### Before Merge
1. ✅ All Quality Gates from "Before Commit" pass
2. ✅ No new unused files (daily cleanup)
3. ✅ Constitution compliance verified
4. ✅ Spec-Kit Checklist completed (if applicable)

### Before Production
1. ✅ Full test suite green
2. ✅ Health check passing
3. ✅ Market regime API responding
4. ✅ Model loaded and validated
5. ✅ All endpoints return valid responses

## Governance

- Constitution supersedes all other documentation
- Amendments require explicit approval and version bump
- All code reviews must verify Constitution compliance
- Violations are blockers - no exceptions

**Version**: 1.2.0 | **Updated**: 2026-02-02 | **Owner**: Kevin Garcia
