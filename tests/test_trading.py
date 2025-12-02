"""Tests for trading functions"""

import pandas as pd
import numpy as np
from market_predictor.trading import (
    compute_rsi,
    compute_macd,
    compute_bollinger,
    compute_momentum,
    features,
)


class TestTechnicalIndicators:
    """Test technical indicator calculations"""

    def test_compute_rsi(self):
        """Test RSI calculation"""
        # Create sample price data
        prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
        rsi = compute_rsi(prices, period=5)

        assert isinstance(rsi, pd.Series)
        assert len(rsi) == len(prices)
        # RSI should be between 0 and 100
        assert rsi.dropna().min() >= 0
        assert rsi.dropna().max() <= 100

    def test_compute_macd(self):
        """Test MACD calculation"""
        prices = pd.Series(np.random.uniform(100, 200, 100))
        macd, signal = compute_macd(prices)

        assert isinstance(macd, pd.Series)
        assert isinstance(signal, pd.Series)
        assert len(macd) == len(prices)
        assert len(signal) == len(prices)

    def test_compute_bollinger(self):
        """Test Bollinger Bands calculation"""
        prices = pd.Series(np.random.uniform(100, 200, 50))
        upper, lower = compute_bollinger(prices)

        assert isinstance(upper, pd.Series)
        assert isinstance(lower, pd.Series)
        assert len(upper) == len(prices)
        assert len(lower) == len(prices)
        # Upper band should be above lower band (where not NaN)
        valid_idx = ~(upper.isna() | lower.isna())
        assert (upper[valid_idx] >= lower[valid_idx]).all()

    def test_compute_momentum(self):
        """Test momentum calculation"""
        prices = pd.Series([100, 102, 104, 103, 105, 107, 106, 108, 110, 109])
        momentum = compute_momentum(prices, period=5)

        assert isinstance(momentum, pd.Series)
        assert len(momentum) == len(prices)

    def test_features_list(self):
        """Test that features list is properly defined"""
        assert isinstance(features, list)
        assert len(features) > 0
        expected_features = [
            "SMA50",
            "SMA200",
            "RSI",
            "Volatility",
            "Momentum_10d",
            "MACD",
            "MACD_signal",
            "BB_upper",
            "BB_lower",
        ]
        for feat in expected_features:
            assert feat in features, f"Missing feature: {feat}"


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_rsi_with_constant_prices(self):
        """Test RSI with constant prices (no change)"""
        prices = pd.Series([100] * 20)
        rsi = compute_rsi(prices, period=14)
        # RSI should be 0 or 50 or NaN for constant prices depending on implementation
        assert rsi.dropna().empty or ((rsi.dropna() >= 0) & (rsi.dropna() <= 100)).all()

    def test_macd_with_short_series(self):
        """Test MACD with short series"""
        prices = pd.Series([100, 101, 102])
        macd, signal = compute_macd(prices)
        # Should return series of same length
        assert len(macd) == 3
        assert len(signal) == 3

    def test_bollinger_with_insufficient_data(self):
        """Test Bollinger Bands with insufficient data"""
        prices = pd.Series([100, 101])
        upper, lower = compute_bollinger(prices, window=20)
        # Should return series with NaN values
        assert upper.isna().all()
        assert lower.isna().all()
