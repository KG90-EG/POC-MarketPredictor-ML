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

### Before Merge
1. ✅ All tests pass (`pytest tests/`)
2. ✅ No linting errors (`flake8`, `eslint`)
3. ✅ Code formatted (`black`, `prettier`)
4. ✅ No new unused files (daily cleanup)
5. ✅ Constitution compliance verified

### Before Production
1. ✅ Full test suite green
2. ✅ Health check passing
3. ✅ Market regime API responding
4. ✅ Model loaded and validated

## Governance

- Constitution supersedes all other documentation
- Amendments require explicit approval and version bump
- All code reviews must verify Constitution compliance
- Violations are blockers - no exceptions

**Version**: 1.0.0 | **Ratified**: 2026-02-02 | **Owner**: Kevin Garcia
