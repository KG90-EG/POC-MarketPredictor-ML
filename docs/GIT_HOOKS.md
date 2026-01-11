# Git Hooks Setup

## Pre-Commit Checks aktiviert ✅

Dieses Repository nutzt Git Hooks für automatische Code-Quality-Checks vor jedem Commit.

## Was wird geprüft?

Vor jedem `git commit` werden automatisch folgende Checks durchgeführt:

### ✅ Python Checks
- **Flake8 Linting**: Code-Style und potenzielle Fehler
- **Black Formatting**: Einheitliche Code-Formatierung
- **Pytest Tests**: Schnelle Smoke-Tests

### ✅ Frontend Checks (wenn vorhanden)
- **ESLint**: JavaScript/React Code-Quality
- **Prettier**: Code-Formatierung

### ✅ Sicherheit
- **Large File Detection**: Verhindert versehentliches Pushen von großen Dateien (>50MB)

## Installation

Die Hooks werden automatisch installiert mit:

```bash
make setup
```

Oder manuell:

```bash
git config core.hooksPath .husky
chmod +x .husky/pre-commit
```

## Verwendung

### Normaler Commit
```bash
git add .
git commit -m "feat: neue Funktion"
```

Die Pre-Commit-Checks laufen automatisch. Bei Fehlern wird der Commit abgebrochen.

### Checks überspringen (Notfall)
```bash
git commit --no-verify -m "fix: hotfix"
```

⚠️ **Hinweis**: Nur in Ausnahmefällen verwenden! Die Checks helfen, Fehler zu vermeiden.

## Fehler beheben

### Python Formatierung
```bash
black src/trading_engine/ src/backtest/ scripts/
```

### Frontend Formatierung
```bash
cd frontend
npm run format
```

### Tests lokal ausführen
```bash
pytest tests/ -v
```

## Output-Beispiel

```
🔍 Running pre-commit checks...

Running Python linting...
✓ Flake8 passed

Checking Python formatting...
✓ Black formatting OK

Running Python tests...
✓ Tests passed

Checking frontend...
✓ ESLint passed
✓ Prettier formatting OK

Checking for large files...
✓ No large files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ All pre-commit checks passed!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Konfiguration anpassen

Die Hook-Konfiguration findest du in:
- `.husky/pre-commit` - Hauptskript
- `.github/workflows/ci.yml` - CI/CD Pipeline (sollte identisch sein)

## Deaktivieren

Falls du die Hooks dauerhaft deaktivieren möchtest:

```bash
git config --unset core.hooksPath
```

Zum Reaktivieren:

```bash
git config core.hooksPath .husky
```

## Warum Git Hooks?

✅ **Frühe Fehlererkennung**: Fehler werden sofort beim Commit erkannt, nicht erst in der CI/CD Pipeline

✅ **Zeit sparen**: Keine fehlgeschlagenen GitHub Actions mehr wegen einfacher Formatierungsfehler

✅ **Konsistenz**: Alle Entwickler haben die gleichen Qualitätsstandards

✅ **Automatisch**: Kein manuelles Ausführen von Tests/Linting vor Commits nötig

## Troubleshooting

### Hook wird nicht ausgeführt
```bash
# Prüfen ob konfiguriert
git config core.hooksPath

# Sollte ausgeben: .husky
```

### Permission Denied
```bash
chmod +x .husky/pre-commit .husky/_/husky.sh
```

### Checks dauern zu lange
Die Checks sind auf Geschwindigkeit optimiert (nur relevante Tests). Bei Bedarf kannst du einzelne Checks in `.husky/pre-commit` auskommentieren.

---

**Tipp**: Die Pre-Commit-Checks sind identisch mit der CI/CD Pipeline. Wenn der Commit lokal erfolgreich ist, wird auch die GitHub Action erfolgreich sein! 🚀
