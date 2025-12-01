import os
import sys
import pandas as pd
import numpy as np
import pytest
from types import SimpleNamespace

# Add the module directory to sys.path so tests can import Trading_Test2 from the moved folder
MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)
    # Also add project root
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

from trading_fun import trading as Trading_Test2

compute_rsi = Trading_Test2.compute_rsi
load_data = Trading_Test2.load_data
build_dataset = Trading_Test2.build_dataset
parse_args = Trading_Test2.parse_args
main = Trading_Test2.main


def test_compute_rsi_simple():
    s = pd.Series([1, 2, 1, 2, 3, 2, 3, 4, 3, 4])
    rsi = compute_rsi(s, period=2)
    # RSI values should be between 0 and 100
    assert rsi.min() >= 0
    assert rsi.max() <= 100


class DummyDf(pd.DataFrame):
    @property
    def _constructor(self):
        return DummyDf


@pytest.fixture
def sample_price_df():
    dates = pd.date_range(end=pd.Timestamp.today(), periods=400)
    # Create Adj Close series with varying segments to produce both classes for Outperform
    adj_close = np.concatenate([
        np.linspace(10, 20, 200),  # rising
        np.linspace(20, 21, 100),  # slight rise
        np.linspace(21, 18, 100),  # drop
    ])
    data = {
        'Open': adj_close * 0.99,
        'High': adj_close * 1.01,
        'Low': adj_close * 0.98,
        'Close': adj_close,
        'Adj Close': adj_close,
        'Volume': np.ones(400) * 1000
    }
    df = pd.DataFrame(data, index=dates)
    return df


def test_load_data_monkeypatch(monkeypatch, sample_price_df):
    import yfinance as yf

    def fake_download(ticker, period, interval, auto_adjust=False):
        return sample_price_df.copy()

    monkeypatch.setattr(yf, 'download', fake_download)
    df = load_data('FAKE')
    assert 'SMA50' in df.columns or 'SMA200' in df.columns
    assert 'Outperform' in df.columns


def test_build_dataset(monkeypatch, sample_price_df):
    import yfinance as yf

    def fake_download(ticker, period, interval, auto_adjust=False):
        return sample_price_df.copy()

    monkeypatch.setattr(yf, 'download', fake_download)
    data = build_dataset(['FAKE1', 'FAKE2'])
    assert not data.empty
    assert 'Ticker' in data.columns


def test_main_quick(monkeypatch):
    # Monkeypatch build_dataset to avoid network; build a small dataset
    adj_close = np.concatenate([
        np.linspace(10, 20, 200),
        np.linspace(20, 15, 200),
    ])
    df = pd.DataFrame({
        'Adj Close': adj_close,
    }, index=pd.date_range(end=pd.Timestamp.today(), periods=400))

    def fake_download(ticker, period, interval, auto_adjust=False):
        # Return a DataFrame with Adj Close at least
        d = df.copy()
        d['Open'] = d['Adj Close'] * 0.99
        d['High'] = d['Adj Close'] * 1.01
        d['Low'] = d['Adj Close'] * 0.98
        d['Volume'] = 1000
        d['Close'] = d['Adj Close']
        return d

    import yfinance as yf
    monkeypatch.setattr(yf, 'download', fake_download)

    # Monkeypatch build_dataset to return a dataset with both classes
    def fake_build_dataset(tickers_list, period="5y"):
        rows = []
        for t in ['FAKE1', 'FAKE2']:
            for i in range(100):
                rows.append({
                    'SMA50': i * 0.1,
                    'SMA200': i * 0.01,
                    'RSI': 50 + (i % 10),
                    'Volatility': 0.02 + (i % 5) * 0.001,
                    'Momentum_10d': 0.001 * i,
                    'MACD': 0.0,
                    'MACD_signal': 0.0,
                    'BB_upper': 1.01 * i,
                    'BB_lower': 0.99 * i,
                    'Outperform': int(i % 2 == 0),
                    'Ticker': t,
                })
        return pd.DataFrame(rows)

    monkeypatch.setattr(Trading_Test2, 'build_dataset', fake_build_dataset)

    # Run main with a small set
    args = SimpleNamespace(tickers='FAKE1,FAKE2', period='1y', top_n=2, use_xgb=False, quiet=True, rank_period='300d')
    main(args)