import pytest
try:
    import fastapi  # noqa: F401
except Exception:
    pytest.skip("fastapi/pydantic not usable in this environment, skipping server tests", allow_module_level=True)
from fastapi.testclient import TestClient
from trading_fun import server
import joblib
import os
import numpy as np
import pandas as pd


class DummyModel:
    def predict_proba(self, X):
        # Ignore feature count; return fixed probability
        return [[0.4, 0.6] for _ in X]


def test_health_and_predict_raw(monkeypatch, tmp_path):
    dummy = DummyModel()
    # Write dummy model to models/prod_model.bin
    models_dir = tmp_path / 'models'
    models_dir.mkdir()
    model_path = models_dir / 'prod_model.bin'
    joblib.dump(dummy, str(model_path))
    monkeypatch.setenv('PROD_MODEL_PATH', str(model_path))
    server.MODEL = dummy
    server.LOADED_MODEL_PATH = str(model_path)
    # reload server module to pick up monkeypatched environment
    client = TestClient(server.app)
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['model_loaded'] == True
    payload = {'features': {'SMA50': 10.0, 'SMA200': 20.0, 'RSI': 50.0, 'Volatility': 0.01, 'Momentum_10d': 0.001, 'MACD': 0.0, 'MACD_signal': 0.0, 'BB_upper': 22.0, 'BB_lower': 18.0}}
    r2 = client.post('/predict_raw', json=payload)
    assert r2.status_code == 200
    assert 'prob' in r2.json()


def test_ranking_endpoint(monkeypatch, tmp_path):
    dummy = DummyModel()
    models_dir = tmp_path / 'models'
    models_dir.mkdir()
    model_path = models_dir / 'prod_model.bin'
    import joblib
    joblib.dump(dummy, str(model_path))
    monkeypatch.setenv('PROD_MODEL_PATH', str(model_path))
    server.MODEL = dummy
    server.LOADED_MODEL_PATH = str(model_path)
    # Monkeypatch yfinance.download to deterministic small frame
    import yfinance as yf

    def fake_download(ticker, period='300d', auto_adjust=False):
        import pandas as pd
        import numpy as np
        idx = pd.date_range(end=pd.Timestamp.today(), periods=10)
        prices = np.linspace(100, 110, 10)
        return pd.DataFrame({'Adj Close': prices}, index=idx)

    monkeypatch.setattr(yf, 'download', fake_download)
    client = TestClient(server.app)
    r = client.get('/ranking?tickers=AAPL,MSFT')
    assert r.status_code == 200
    assert 'ranking' in r.json()
