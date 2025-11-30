import pandas as pd
import numpy as np
import pytest
from trading_fun import trading as trading_mod


def test_load_data_has_new_features(monkeypatch):
    dates = pd.date_range(end=pd.Timestamp.today(), periods=250)
    prices = np.linspace(10, 50, 250)
    df = pd.DataFrame({
        'Adj Close': prices,
        'Open': prices * 0.99,
        'High': prices * 1.01,
        'Low': prices * 0.98,
        'Close': prices,
        'Volume': np.ones(250) * 1000
    }, index=dates)

    import yfinance as yf
    def fake_download(ticker, period, interval, auto_adjust=False):
        return df.copy()

    monkeypatch.setattr(yf, 'download', fake_download)
    ld = trading_mod.load_data('FAKE', period='1y')
    for col in ['Momentum_10d', 'MACD', 'MACD_signal', 'BB_upper', 'BB_lower']:
        assert col in ld.columns


def test_train_model_returns_metrics(monkeypatch):
    # create dataset with features & Outperform
    rows = []
    for i in range(400):
        rows.append({'SMA50': 1.0*i, 'SMA200': 1.0*i, 'RSI': 50, 'Volatility': 0.01, 'Momentum_10d': 0.001*i, 'MACD': 0.0, 'MACD_signal': 0.0, 'BB_upper': 1.0*i, 'BB_lower': 0.9*i, 'Outperform': int(i % 2 == 0)})
    data = pd.DataFrame(rows)
    model, metrics = trading_mod.train_model(data, model_type='rf')
    assert 'accuracy' in metrics and 'f1' in metrics and 'cv_mean' in metrics


def test_backtester_simple():
    from backtest.backtester import from_predictions
    prices = np.linspace(10, 20, 200)
    probs = np.zeros(200)
    # set first few probabilities to 1 to simulate buys
    probs[0:5] = 1.0
    df, metrics = from_predictions(probs, prices, threshold=0.5)
    assert metrics['num_trades'] == 5
    assert metrics['total_pnl'] > 0
