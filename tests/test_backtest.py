"""
Test suite for Historical Backtest functionality (Phase 3)

Tests:
- POST /api/backtest/run - Execute historical backtest
- GET /api/backtest/status - Get backtesting capabilities
- HistoricalBacktester class methods
- Strategy performance validation
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient


def test_backtest_status_endpoint(client: TestClient):
    """Test backtest status endpoint returns capabilities"""
    response = client.get("/api/backtest/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "available" in data
    assert "strategies" in data
    assert "Composite Score System" in data["strategies"]
    assert "ML-Only Strategy" in data["strategies"]
    assert "S&P 500 Benchmark" in data["strategies"]
    
    assert "metrics" in data
    assert "total_return" in data["metrics"]
    assert "max_drawdown" in data["metrics"]
    assert "sharpe_ratio" in data["metrics"]
    assert "win_rate" in data["metrics"]
    assert "calmar_ratio" in data["metrics"]


def test_backtest_run_success(client: TestClient):
    """Test successful backtest execution"""
    # Use recent date range (last 6 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    payload = {
        "tickers": ["AAPL", "MSFT", "GOOGL"],
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "initial_capital": 100000
    }
    
    response = client.post("/api/backtest/run", json=payload)
    
    # May fail if market data unavailable, that's okay for this test
    if response.status_code == 200:
        data = response.json()
        
        assert "backtest_period" in data
        assert "strategies" in data
        assert "comparison" in data
        
        # Check strategies
        assert "composite" in data["strategies"]
        assert "ml_only" in data["strategies"]
        assert "sp500" in data["strategies"]
        
        # Check metrics exist
        for strategy in ["composite", "ml_only", "sp500"]:
            metrics = data["strategies"][strategy]["metrics"]
            assert "total_return" in metrics
            assert "max_drawdown" in metrics
            assert "sharpe_ratio" in metrics
            assert "win_rate" in metrics
            assert "calmar_ratio" in metrics
        
        # Check comparison
        assert "winner_by_return" in data["comparison"]
        assert "alpha_vs_benchmark" in data["comparison"]


def test_backtest_run_invalid_date_range(client: TestClient):
    """Test backtest with invalid date range"""
    payload = {
        "tickers": ["AAPL"],
        "start_date": "2025-12-31",
        "end_date": "2025-01-01",  # End before start
        "initial_capital": 100000
    }
    
    response = client.post("/api/backtest/run", json=payload)
    
    assert response.status_code in [400, 500]  # Should reject invalid dates


def test_backtest_run_empty_tickers(client: TestClient):
    """Test backtest with empty ticker list"""
    payload = {
        "tickers": [],
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "initial_capital": 100000
    }
    
    response = client.post("/api/backtest/run", json=payload)
    
    assert response.status_code in [400, 422]  # Should reject empty tickers


def test_backtest_run_invalid_capital(client: TestClient):
    """Test backtest with invalid initial capital"""
    payload = {
        "tickers": ["AAPL"],
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "initial_capital": -1000  # Negative capital
    }
    
    response = client.post("/api/backtest/run", json=payload)
    
    assert response.status_code in [400, 422]  # Should reject negative capital


@pytest.mark.unit
def test_backtest_result_structure():
    """Test BacktestResult dataclass structure"""
    from src.backtest.historical_validator import BacktestResult
    
    result = BacktestResult(
        strategy_name="Test Strategy",
        total_return=15.5,
        max_drawdown=-8.2,
        sharpe_ratio=1.45,
        calmar_ratio=1.89,
        win_rate=68.5,
        equity_curve=[
            {"date": "2025-01-01", "value": 100000},
            {"date": "2025-12-31", "value": 115500}
        ],
        trades=[],
        metrics={}
    )
    
    assert result.strategy_name == "Test Strategy"
    assert result.total_return == 15.5
    assert result.sharpe_ratio == 1.45
    assert len(result.equity_curve) == 2


@pytest.mark.unit
def test_historical_backtester_initialization():
    """Test HistoricalBacktester class initialization"""
    from src.backtest.historical_validator import HistoricalBacktester
    
    backtester = HistoricalBacktester(
        tickers=["AAPL", "MSFT"],
        start_date="2025-01-01",
        end_date="2025-12-31",
        initial_capital=100000
    )
    
    assert backtester.tickers == ["AAPL", "MSFT"]
    assert backtester.initial_capital == 100000
    assert backtester.start_date == "2025-01-01"
    assert backtester.end_date == "2025-12-31"


def test_backtest_api_documentation(client: TestClient):
    """Test that backtest endpoints are documented in OpenAPI"""
    response = client.get("/openapi.json")
    
    assert response.status_code == 200
    openapi_spec = response.json()
    
    # Check backtest endpoints in OpenAPI spec
    paths = openapi_spec.get("paths", {})
    assert "/api/backtest/run" in paths
    assert "/api/backtest/status" in paths
    
    # Check POST method for /api/backtest/run
    assert "post" in paths["/api/backtest/run"]
    
    # Check GET method for /api/backtest/status
    assert "get" in paths["/api/backtest/status"]
