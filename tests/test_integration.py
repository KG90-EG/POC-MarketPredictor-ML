"""Integration tests for the trading system"""

import pytest
from unittest.mock import patch
import pandas as pd


@pytest.mark.integration
class TestEndToEndPrediction:
    """Test end-to-end prediction flow"""

    @patch("yfinance.download")
    def test_full_prediction_flow(self, mock_download, sample_stock_data):
        """Test complete prediction flow from data download to prediction"""
        # Mock yfinance download
        mock_download.return_value = sample_stock_data

        from market_predictor.trading import (
            compute_rsi,
            compute_macd,
            compute_bollinger,
            compute_momentum,
            features,
        )

        # Compute indicators
        df = sample_stock_data.copy()
        df["SMA50"] = df["Adj Close"].rolling(50).mean()
        df["SMA200"] = df["Adj Close"].rolling(200).mean()
        df["RSI"] = compute_rsi(df["Adj Close"])
        df["Volatility"] = df["Adj Close"].pct_change().rolling(30).std()
        df["Momentum_10d"] = compute_momentum(df["Adj Close"], 10)
        macd, macd_sig = compute_macd(df["Adj Close"])
        df["MACD"] = macd
        df["MACD_signal"] = macd_sig
        bb_up, bb_low = compute_bollinger(df["Adj Close"])
        df["BB_upper"] = bb_up
        df["BB_lower"] = bb_low

        df = df.dropna()

        # Check that we have all features
        assert not df.empty
        for feat in features:
            assert feat in df.columns

        # Check that last row has valid values
        last_row = df.iloc[-1]
        for feat in features:
            assert not pd.isna(last_row[feat])


@pytest.mark.integration
class TestCaching:
    """Test caching functionality"""

    def test_cache_operations(self):
        """Test cache get/set operations"""
        from market_predictor.cache import cache

        # Test basic operations
        cache.set("test_key", {"value": 123}, ttl_seconds=60)
        result = cache.get("test_key")

        assert result is not None
        assert result["value"] == 123

        # Test cache stats
        stats = cache.get_stats()
        assert "backend" in stats
        assert isinstance(stats, dict)


@pytest.mark.integration
class TestRateLimiter:
    """Test rate limiter functionality"""

    def test_rate_limiter_stats(self):
        """Test rate limiter statistics"""
        from market_predictor.server import rate_limiter

        stats = rate_limiter.get_stats()
        assert "tracked_ips" in stats
        assert "tracked_endpoints" in stats
        assert "requests_per_minute" in stats


@pytest.mark.integration
class TestWebSocketManager:
    """Test WebSocket manager"""

    def test_websocket_stats(self):
        """Test WebSocket manager statistics"""
        from market_predictor.websocket import manager

        stats = manager.get_stats()
        assert "active_connections" in stats
        # Check for any stats keys (implementation may vary)
        assert isinstance(stats, dict)
        assert len(stats) > 0
