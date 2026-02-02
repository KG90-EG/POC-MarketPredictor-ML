# NFR-010: ML Training Pipeline

> **Status:** Draft  
> **Created:** 2026-02-02  
> **Author:** Kevin Garcia  
> **Priority:** Medium  
> **Type:** Non-Functional Requirement

---

## 📋 Overview

Automatisierte Machine Learning Pipeline für kontinuierliches Model-Training, Hyperparameter-Optimierung, Versioning und Deployment. Ziel ist langfristige Modellqualität ohne manuelle Intervention.

---

## 🎯 User Stories

### NFR-10.1: Automatisches Model-Retraining
**Als** System  
**möchte ich** das ML-Model regelmässig neu trainieren  
**damit** es mit aktuellen Marktdaten arbeitet

**Akzeptanzkriterien:**
- [ ] Scheduled Retraining (wöchentlich oder monatlich)
- [ ] Training nur wenn genug neue Daten vorhanden
- [ ] Training-Job läuft im Hintergrund (nicht blocking)
- [ ] Notification bei Training-Completion

---

### NFR-10.2: Model Versioning
**Als** Entwickler  
**möchte ich** alle Model-Versionen tracken  
**damit** ich bei Problemen rollback machen kann

**Akzeptanzkriterien:**
- [ ] Jedes Model hat eindeutige Version (v1.0.0, v1.1.0, ...)
- [ ] Metrics pro Version gespeichert (accuracy, f1, etc.)
- [ ] Rollback zu vorheriger Version möglich
- [ ] Model-Artefakte in MLflow oder S3 gespeichert

---

### NFR-10.3: A/B Testing für Models
**Als** Data Scientist  
**möchte ich** neue Models gegen Production testen  
**damit** ich sicher bin dass neue Version besser ist

**Akzeptanzkriterien:**
- [ ] Shadow Mode: Neues Model läuft parallel
- [ ] Metrics-Vergleich automatisch
- [ ] Promotion nur wenn neues Model besser
- [ ] Automatische Alerts bei Performance-Drop

---

### NFR-10.4: Drift Detection
**Als** System  
**möchte ich** erkennen wenn sich Daten-Distribution ändert  
**damit** ich Retraining triggern kann

**Akzeptanzkriterien:**
- [ ] Feature Drift Detection (PSI, KS-Test)
- [ ] Prediction Drift Detection
- [ ] Alert bei signifikantem Drift
- [ ] Optional: Auto-Retrigger Training

---

### NFR-10.5: Hyperparameter-Optimierung
**Als** System  
**möchte ich** automatisch beste Hyperparameter finden  
**damit** Model-Qualität maximiert wird

**Akzeptanzkriterien:**
- [ ] Optuna oder Ray Tune Integration
- [ ] Bayesian Optimization (nicht Grid Search)
- [ ] Zeit/Resource-Limits definiert
- [ ] Best params in `best_hyperparameters.json` gespeichert

---

## 🏗️ Technical Architecture

### Pipeline Stages:
```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Data Fetch  │ → │  Feature    │ → │  Training   │ → │ Evaluation  │
│ (yfinance)  │   │ Engineering │   │ (XGBoost)   │   │ (Backtest)  │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
                                            │
                                            ▼
                                    ┌─────────────┐
                                    │  MLflow     │
                                    │ (Versioning)│
                                    └─────────────┘
                                            │
                                            ▼
                                    ┌─────────────┐
                                    │  Promotion  │
                                    │ (if better) │
                                    └─────────────┘
```

### Tools:
| Component | Tool | Status |
|-----------|------|--------|
| Versioning | MLflow | ✅ Exists |
| Scheduling | GitHub Actions / Cron | 🔧 To Setup |
| Hyperparameter | Optuna | 🔧 To Add |
| Drift Detection | Evidently AI | 🔧 To Add |
| Storage | Local / S3 | ✅ Exists |

### Existing Assets:
- `src/training/` - Training scripts
- `mlruns/` - MLflow experiment tracking
- `best_hyperparameters.json` - Current best params
- `models/` - Saved model files

---

## 📅 Implementation Phases

### Phase 1: Manual Pipeline (Current)
- Training scripts exist
- MLflow tracking works
- Manual execution required

### Phase 2: Scheduled Training
- GitHub Actions workflow for weekly training
- Auto-commit new model if better
- Slack/Email notification

### Phase 3: Full Automation
- Drift detection triggers retraining
- A/B testing for model promotion
- Auto-rollback on performance drop

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Neues Model schlechter | Predictions verschlechtern sich | A/B Testing, Rollback |
| Training zu teuer (Zeit) | Blocking andere Prozesse | Background Jobs, Limits |
| Overfitting auf neue Daten | Model generalisiert nicht | Cross-Validation, Holdout |
| Drift false positives | Unnötiges Retraining | Thresholds tunen |

---

## 📊 Success Metrics

| Metrik | Zielwert |
|--------|----------|
| Training Duration | < 30 Minuten |
| Model Accuracy | > 65% |
| Drift Detection Latency | < 24h |
| Rollback Time | < 5 Minuten |
| Retraining Frequency | 1x pro Monat (min) |

---

## 🔗 Dependencies

- MLflow (bereits installiert)
- Optuna (zu installieren)
- GitHub Actions (bereits vorhanden)
- Sufficient training data (6+ months)

---

## 📝 Notes

- Priorität: NFR-10.1 (Scheduled Training) zuerst
- A/B Testing und Drift Detection sind "nice-to-have"
- Existierende `src/training/` Scripts wiederverwenden
- Nicht zu früh optimieren - einfach starten, dann iterieren
