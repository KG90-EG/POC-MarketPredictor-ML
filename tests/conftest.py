"""Pytest configuration and fixtures"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing"""
    import numpy as np
    import pandas as pd

    dates = pd.date_range(start="2023-01-01", periods=250, freq="D")
    data = {
        "Open": np.random.uniform(100, 200, 250),
        "High": np.random.uniform(100, 200, 250),
        "Low": np.random.uniform(100, 200, 250),
        "Close": np.random.uniform(100, 200, 250),
        "Adj Close": np.random.uniform(100, 200, 250),
        "Volume": np.random.randint(1000000, 10000000, 250),
    }
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def mock_model():
    """Mock ML model for testing"""
    from unittest.mock import Mock

    model = Mock()
    model.predict_proba.return_value = [[0.3, 0.7]]
    model.predict.return_value = [1]
    return model


@pytest.fixture(scope="session")
def client():
    """Session-scoped FastAPI test client for API endpoint tests."""
    from src.trading_engine.api.server import app

    with TestClient(app) as test_client:
        yield test_client
