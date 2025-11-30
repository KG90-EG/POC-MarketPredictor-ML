import os
import tempfile
import joblib
from fastapi.testclient import TestClient
from trading_fun import server


class DummyModel:
    def predict_proba(self, X):
        return [[0.5, 0.5] for _ in X]


def create_dummy_model(tmpdir):
    m = DummyModel()
    path = os.path.join(tmpdir, 'prod_model.bin')
    joblib.dump(m, path)
    return path


def test_models_endpoint(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        model_path = create_dummy_model(tmp)
        monkeypatch.setenv('PROD_MODEL_PATH', model_path)
        # Reload server MODEL with new path
        server.MODEL = joblib.load(model_path)
        server.LOADED_MODEL_PATH = model_path
        client = TestClient(server.app)
        r = client.get('/models')
        assert r.status_code == 200
        data = r.json()
        assert data['current_model'] == 'prod_model.bin'
        assert isinstance(data['available_models'], list)


def test_health(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        model_path = create_dummy_model(tmp)
        monkeypatch.setenv('PROD_MODEL_PATH', model_path)
        server.MODEL = joblib.load(model_path)
        server.LOADED_MODEL_PATH = model_path
        client = TestClient(server.app)
        r = client.get('/health')
        assert r.status_code == 200
        assert r.json()['status'] == 'ok'