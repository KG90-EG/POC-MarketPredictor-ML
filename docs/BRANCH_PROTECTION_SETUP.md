# Branch Protection Rules Configuration

Dieses Dokument erklärt, wie du Branch Protection Rules in GitHub aktivierst, um sicherzustellen, dass ALLE CI/CD-Checks bestehen müssen, bevor Code gemerged werden kann.

## 🛡️ Warum Branch Protection?

**Technische Sicherstellung:**
- ❌ **Ohne Protection**: CI kann fehlschlagen, Code wird trotzdem gemerged
- ✅ **Mit Protection**: Merge-Button ist deaktiviert, bis alle Checks ✅ sind

## 🔧 Einrichtung (GitHub UI)

### Schritt 1: Repository Settings öffnen
```
1. Gehe zu: https://github.com/KG90-EG/POC-MarketPredictor-ML
2. Klicke auf "Settings" (oben rechts)
3. Sidebar: "Branches" (unter "Code and automation")
```

### Schritt 2: Branch Protection Rule erstellen
```
1. Klicke "Add branch protection rule"
2. Branch name pattern: main
```

### Schritt 3: Erforderliche Checks konfigurieren

**✅ Aktiviere diese Optionen:**

#### Require a pull request before merging
- [x] Require a pull request before merging
  - [x] Require approvals: 1
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners

#### Require status checks to pass before merging
- [x] Require status checks to pass before merging
  - [x] Require branches to be up to date before merging
  
**Status checks to require (wähle alle):**
  - [x] Backend Quality (backend-quality)
  - [x] Backend Tests (backend-tests)
  - [x] Frontend Quality (frontend-quality)
  - [x] Frontend Tests (frontend-tests)
  - [x] Docker Build (docker-build)
  - [x] Repository Structure (structure-check)
  - [x] Documentation (docs-check)
  - [x] Enforce Tests (enforce-tests)
  - [x] Enforce Formatting (enforce-formatting)
  - [x] Enforce Linting (enforce-linting)
  - [x] Enforce Security (enforce-security)
  - [x] Enforce Docker Build (enforce-docker)

#### Zusätzliche Sicherheitseinstellungen
- [x] Require conversation resolution before merging
- [x] Require signed commits (optional, für höhere Sicherheit)
- [x] Require linear history
- [x] Include administrators (auch Admins müssen die Rules befolgen!)

#### Restrictions
- [x] Restrict who can push to matching branches
  - Nur bestimmte Teams/User erlauben

### Schritt 4: Regel speichern
```
Klicke "Create" / "Save changes"
```

## 🔧 Einrichtung (GitHub CLI)

Alternativ per Command Line:

```bash
# GitHub CLI installieren (falls nicht vorhanden)
brew install gh

# Authentifizieren
gh auth login

# Branch Protection aktivieren
gh api repos/KG90-EG/POC-MarketPredictor-ML/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["backend-quality","backend-tests","frontend-quality","frontend-tests","docker-build","structure-check","docs-check","enforce-tests","enforce-formatting","enforce-linting","enforce-security","enforce-docker"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":1}' \
  --field restrictions=null
```

## 🔧 Einrichtung (Terraform/IaC)

Für Infrastructure as Code:

```hcl
resource "github_branch_protection" "main" {
  repository_id = "POC-MarketPredictor-ML"
  pattern       = "main"

  required_status_checks {
    strict = true
    contexts = [
      "backend-quality",
      "backend-tests",
      "frontend-quality",
      "frontend-tests",
      "docker-build",
      "structure-check",
      "docs-check",
      "enforce-tests",
      "enforce-formatting",
      "enforce-linting",
      "enforce-security",
      "enforce-docker",
    ]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews           = true
    require_code_owner_reviews      = true
    required_approving_review_count = 1
  }

  enforce_admins = true
  
  require_signed_commits = true
  require_linear_history = true
  require_conversation_resolution = true
}
```

## 📊 Wie funktioniert das?

### Workflow:

```
1. Developer erstellt Branch: feature/new-endpoint
   └─> Macht Änderungen
   
2. Developer öffnet Pull Request
   └─> Triggert automatisch alle CI/CD Workflows
   
3. CI/CD läuft:
   ├─ Quality Gates Workflow
   │  ├─ Backend Quality ⏳
   │  ├─ Backend Tests ⏳
   │  ├─ Frontend Quality ⏳
   │  ├─ Frontend Tests ⏳
   │  ├─ Docker Build ⏳
   │  ├─ Structure Check ⏳
   │  └─ Documentation ⏳
   │
   └─ Pre-Merge Workflow
      ├─ Enforce Tests ⏳
      ├─ Enforce Formatting ⏳
      ├─ Enforce Linting ⏳
      ├─ Enforce Security ⏳
      └─ Enforce Docker ⏳

4a. Wenn ALLE Checks ✅:
    └─> Merge-Button wird GRÜN
    └─> "Merge pull request" ist möglich
    
4b. Wenn EIN Check ❌:
    └─> Merge-Button ist GESPERRT
    └─> "Merging is blocked" - Fehler müssen gefixt werden
```

### Beispiel PR-Ansicht:

```
❌ Some checks were not successful

Required status checks (13/13):
  ✅ backend-quality
  ✅ backend-tests
  ✅ frontend-quality
  ❌ frontend-tests (failed)
  ✅ docker-build
  ✅ structure-check
  ✅ docs-check
  ✅ enforce-tests
  ✅ enforce-formatting
  ❌ enforce-linting (failed)
  ✅ enforce-security
  ✅ enforce-docker
  ✅ merge-ready

🚫 Merging is blocked
   This branch has not met the requirements to merge.
```

## 🚀 Sofortige Aktivierung (Empfohlen)

**Quick Setup via GitHub UI:**

1. Gehe zu: https://github.com/KG90-EG/POC-MarketPredictor-ML/settings/branches
2. Klicke "Add branch protection rule"
3. Branch name pattern: `main`
4. Aktiviere:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
     - ✅ Require branches to be up to date
   - ✅ Require conversation resolution before merging
   - ✅ Include administrators
5. Wähle **alle** Status Checks (erscheinen nach erstem CI-Run)
6. Klicke "Create"

## 🔍 Verifizierung

Nach der Aktivierung:

```bash
# Check ob Protection aktiv ist
gh api repos/KG90-EG/POC-MarketPredictor-ML/branches/main/protection | jq

# Erwartete Ausgabe:
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "backend-quality",
      "backend-tests",
      ...
    ]
  },
  "enforce_admins": {
    "enabled": true
  }
}
```

## 📋 Checkliste

Stelle sicher, dass:

- [ ] Branch Protection Rule für `main` erstellt
- [ ] Alle 13 Status Checks als required markiert
- [ ] "Require branches to be up to date" aktiviert
- [ ] "Include administrators" aktiviert
- [ ] Pre-commit hooks installiert: `pre-commit install`
- [ ] Team über neue Rules informiert

## 🆘 Troubleshooting

### Status Checks erscheinen nicht in der Liste

**Problem:** GitHub zeigt keine Status Checks zum Auswählen.

**Lösung:**
1. Erstelle einen Test-PR
2. Warte bis CI einmal durchgelaufen ist
3. Gehe zurück zu Branch Protection Settings
4. Jetzt sollten alle Checks sichtbar sein

### Merge-Button trotz Fehler grün

**Problem:** Merge ist möglich, obwohl Checks fehlschlagen.

**Lösung:**
1. Überprüfe "Include administrators" ist aktiviert
2. Stelle sicher, dass die Check-Namen exakt übereinstimmen
3. Verifiziere "Require status checks to pass" ist aktiviert

### CI schlägt immer fehl

**Problem:** Tests/Linting schlagen konstant fehl.

**Lösung:**
```bash
# Lokal alle Checks ausführen
cd /Users/kevingarcia/Documents/POC-MarketPredictor-ML

# Backend
black --line-length=127 src/ scripts/ tests/
isort --profile black --line-length 127 src/ scripts/ tests/
flake8 src/ scripts/ tests/ --max-line-length=127
pytest tests/

# Frontend
cd frontend
npm run format
npm run lint:fix
npm run test
cd ..

# Docker
docker build -t market-predictor:test .

# Commit
git add -A
git commit -m "fix: resolve CI issues"
git push
```

## 📚 Weitere Ressourcen

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Status Checks Documentation](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)
- [Pre-commit Hooks Guide](https://pre-commit.com/)

## 🎯 Nächste Schritte

Nach der Aktivierung:

1. **Teste mit einem PR:**
   ```bash
   git checkout -b test/branch-protection
   echo "test" >> README.md
   git add README.md
   git commit -m "test: verify branch protection"
   git push -u origin test/branch-protection
   # Öffne PR auf GitHub
   ```

2. **Vergewissere, dass Merge blockiert ist** wenn Checks fehlschlagen

3. **Dokumentiere** den Prozess für das Team

4. **Aktiviere Notifications** für gescheiterte CI-Runs

---

**✅ Nach dieser Einrichtung:** Es ist **technisch unmöglich**, Code zu mergen, wenn auch nur EIN Check fehlschlägt! 🎯
