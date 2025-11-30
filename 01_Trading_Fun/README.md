# Trading_Test2

Kleines Python-Projekt, das Aktienhistorische Daten zieht und einfache ML-Modelle benutzt, um eine "Buy-List" basierend auf einer Outperformance-Logik zu erzeugen.

## Inhalt
- `Trading_Test2.py` — Hauptskript, CLI mittels `argparse`.
- `requirements.txt` — benötigte Python-Pakete.

## Setup
1. Python 3.10+ wird empfohlen.
2. Installiere Abhängigkeiten (empfohlen in einem virtuellen Environment):

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

3. Auf macOS: Wenn du `xgboost` nutzen möchtest, installiere `libomp`:

```bash
brew install libomp
```

## Beispiel: Ausführung
```bash
python3 Trading_Test2.py --tickers AAPL,MSFT,NVDA --top-n 5
```

Optionen:
- `--tickers`: Kommagetrennte Liste von Ticker-Symbolen.
- `--period`: Historischer Zeitraum für Training (Standard `5y`).
- `--rank-period`: Zeitraum für Ranking (Standard `300d`).
- `--top-n`: Anzahl Top-Ergebnisse.
- `--use-xgb`: Wenn true: Versucht XGBoost, sonst RandomForest.
- `--quiet`: Weniger Logging.

## Tests
Die Testdateien verwenden `pytest`. Führe Tests mit:

```bash
pytest -q
```

## Wie kann der Algo selbstständig lernen? (High-level guide)
Hier ein kurzes Vorgehen, um den Algo zu einem autonom lernenden System zu machen:

1. Daten-Infrastruktur
   - Kontinuierlich Daten abrufen (scheduled jobs), z. B. mit Airflow/Prefect/cron.
   - Stabile, versionierte Storage (S3 / GCS / lokale Dateisystem mit Versions-Policy).

2. Backtesting und Evaluation
   - Führe automatisierte Backtests mit historischen Daten (ausgelagerte Funktionen), benutz Metriken wie CAGR, Sharpe Ratio, Max Drawdown.
   - Identifiziere Overfitting mit Cross-Validation, TimeSeries-split, Rolling-window.

3. Re-Training-Strategie
   - Festgelegte Retrain-Intervalle (z. B. wöchentlich/monatlich) oder datengetriggerte Re-Training-Events.
   - Verwende Performance-Monitore (z. B. live PnL vs. expected PnL) oder Daten-Drift-Detection, um Retrain anzustoßen.

4. Modellverwaltung
   - Nutze ein Modell-Register (z. B. MLflow) zur Versionierung, Evaluierung und zur Verwaltung von Produktionsmodellen.
   - Führe A/B-Tests oder Canary-Deployments beim Wechsel auf ein neues Modell durch.

5. Automatisierung und Monitoring
   - CI/CD für Modelle: automatisch testen, paketieren und deployen (Container).
   - Überwachung: Data pipeline health, Model-prediction drift, Latency, Exceptions.

6. Sicherheit & Risk Controls
   - Position-Sizing-Logiken, Max-Risiko-Limits, Circuit-Breaker.
   - Eine „human-in-the-loop“-Policy für signifikante Änderungen.

7. Real-time vs Batch
   - Echte Live-Adaptation (online learning) ist möglich (z. B. `river` lib) — aber erfordert striktes Monitoring.
   - Empfohlener Einstieg: Batch-Retraining mit regelmäßiger Evaluierung.

## Nächste Schritte (optional / automatisch)
- Erstelle ein Airflow/DAG oder Prefect Flow, um die folgenden Schritte regelmäßig auszuführen:
  1. Daten-Update
  2. Retrain + Backtest
  3. Evaluierung und Modell-Import in den Registry
  4. Deployment / Rollout wenn freigegeben
- Optional: Instrumentation mit MLflow oder einrichten eines leichtgewichtigen Monitoring-Dashboards.

## CI/CD + Pipeline (Kurz)

- Es gibt eine Beispiel-GitHub-Actions-Workflow-Datei `.github/workflows/ci.yml`.
- Die Actions führen Tests per `pytest` aus und führen zusätzlich ein leichtes Trainingsskript (`training/trainer.py`) aus.
- Für ein produktives Setup empfehle ich:
   - Ein Repositorium in GitHub erstellen.
   - Secrets/Keys für Cloud-Provider (z. B. S3) oder MLFlow-Server in GitHub Secrets hinterlegen.
   - MLflow/Artifact-Storage für Modell-Registrierung und -Versionierung konfigurieren.

## Modell-Training & Persistenz


## MLflow (Optional)

   - Setze `MLFLOW_TRACKING_URI` als Environment-Var auf eine Remote/Postgres-/S3-Lösung oder nutze das lokale `mlruns/`-Verzeichnis
   - In `train_model()` `mlflow.sklearn.log_model()` aufrufen mit den Parametern und Metriken.

   ## Online learning (Optional)

   We included a small online learning prototype `training/online_trainer.py` using the `river` library for streaming updates. This is experimental and useful to test online learning ideas. Run with:
   ```bash
   # install river
   pip install river
   python training/online_trainer.py
   ```


## Docker

## MLflow Integration (kurz)

1. Stelle MLflow-Tracing-Adresse bereit (z.B. `file:./mlruns` oder ein Remote-Server). Setze `MLFLOW_TRACKING_URI` als ENV-Variable oder GitHub Secret.
2. Die CI-Aktion setzt `MLFLOW_TRACKING_URI` aus Secrets, falls vorhanden.
3. `training/trainer.py` verwendet MLflow, um Metriken und das trainierte Modell als Artefakt zu loggen.
4. Beispiel lokal:
```bash
# Set a local mlruns folder
export MLFLOW_TRACKING_URI=file:./mlruns
python training/trainer.py
mlflow ui --backend-store-uri file:./mlruns --default-artifact-root ./mlruns
```


```bash
docker build -t trading_fun:latest .
docker run --rm trading_fun:latest --tickers AAPL,MSFT --top-n 5
```


---
Wenn du möchtest, erledige ich jetzt:
- (A) `requirements.txt` (erledigt),
- (B) `pytest`-Tests (gleich implementiert),
- (C) `README.md` (erledigt),

und als nächste Schritte:
- CI-Integration (z. B. GitHub Actions) zum Ausführen von Tests und Linting,
- Optional: MLflow-Integration, Dockerfile, oder Beispiel-Airflow-DAG.

Sag mir, welche dieser Erweiterungen du als nächstes möchtest — ich setze sie dann um.