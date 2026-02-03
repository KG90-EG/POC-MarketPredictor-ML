"""
Tests for Risk Scoring Module

Tests:
- Individual score calculations (volatility, drawdown, correlation)
- Composite score weighting
- Risk level classification
- Position size multiplier
- Fallback handling
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest

from src.trading_engine.risk_scoring import RiskBreakdown, RiskScorer, get_risk_scorer


class TestRiskBreakdown:
    """Tests for RiskBreakdown dataclass"""

    def test_risk_breakdown_creation(self):
        """Test creating a RiskBreakdown instance"""
        breakdown = RiskBreakdown(
            volatility_score=40,
            drawdown_score=30,
            correlation_score=50,
            composite_score=40,
            risk_level="MEDIUM",
            atr_percentile=2.5,
            max_drawdown_pct=10.0,
            spy_correlation=0.6,
            timestamp=datetime.now(),
        )

        assert breakdown.volatility_score == 40
        assert breakdown.risk_level == "MEDIUM"
        assert breakdown.composite_score == 40


class TestVolatilityScore:
    """Tests for volatility score calculation"""

    @pytest.fixture
    def scorer(self):
        return RiskScorer(cache_ttl=0)  # No caching for tests

    @pytest.fixture
    def low_volatility_hist(self):
        """Create low volatility price history (ATR ~0.5%)"""
        dates = pd.date_range(end=datetime.now(), periods=50, freq="D")
        # Stable prices with small moves
        base_price = 100.0
        prices = [base_price + np.sin(i * 0.1) * 0.3 for i in range(50)]
        return pd.DataFrame(
            {
                "Open": prices,
                "High": [p + 0.2 for p in prices],
                "Low": [p - 0.2 for p in prices],
                "Close": prices,
                "Volume": [1000000] * 50,
            },
            index=dates,
        )

    @pytest.fixture
    def high_volatility_hist(self):
        """Create high volatility price history (ATR ~5%)"""
        dates = pd.date_range(end=datetime.now(), periods=50, freq="D")
        # Wild price swings
        base_price = 100.0
        prices = [base_price + np.sin(i) * 10 for i in range(50)]
        return pd.DataFrame(
            {
                "Open": prices,
                "High": [p + 3 for p in prices],
                "Low": [p - 3 for p in prices],
                "Close": prices,
                "Volume": [1000000] * 50,
            },
            index=dates,
        )

    def test_volatility_score_range(self, scorer, low_volatility_hist):
        """Volatility score should be between 0 and 100"""
        score, atr_pct = scorer._calculate_volatility_score(low_volatility_hist)

        assert 0 <= score <= 100
        assert atr_pct >= 0

    def test_low_volatility_low_score(self, scorer, low_volatility_hist):
        """Low volatility should result in low risk score"""
        score, _ = scorer._calculate_volatility_score(low_volatility_hist)

        # Low volatility = low score (< 40)
        assert score < 40

    def test_high_volatility_high_score(self, scorer, high_volatility_hist):
        """High volatility should result in high risk score"""
        score, _ = scorer._calculate_volatility_score(high_volatility_hist)

        # High volatility = high score (> 50)
        assert score > 50


class TestDrawdownScore:
    """Tests for drawdown score calculation"""

    @pytest.fixture
    def scorer(self):
        return RiskScorer(cache_ttl=0)

    @pytest.fixture
    def small_drawdown_hist(self):
        """Price history with ~3% max drawdown"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq="D")
        # Mostly upward with small dips
        prices = [100 + i * 0.1 for i in range(100)]
        # Add small 3% drawdown
        prices[50:60] = [prices[50] * 0.97 + i * 0.03 for i in range(10)]
        return pd.DataFrame(
            {
                "Open": prices,
                "High": [p * 1.01 for p in prices],
                "Low": [p * 0.99 for p in prices],
                "Close": prices,
                "Volume": [1000000] * 100,
            },
            index=dates,
        )

    @pytest.fixture
    def large_drawdown_hist(self):
        """Price history with ~25% max drawdown"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq="D")
        # Sharp decline
        prices = [100 if i < 50 else 100 - (i - 50) * 0.5 for i in range(100)]
        return pd.DataFrame(
            {
                "Open": prices,
                "High": [p * 1.01 for p in prices],
                "Low": [p * 0.99 for p in prices],
                "Close": prices,
                "Volume": [1000000] * 100,
            },
            index=dates,
        )

    def test_drawdown_score_range(self, scorer, small_drawdown_hist):
        """Drawdown score should be between 0 and 100"""
        score, max_dd = scorer._calculate_drawdown_score(small_drawdown_hist)

        assert 0 <= score <= 100
        assert max_dd >= 0

    def test_small_drawdown_low_score(self, scorer, small_drawdown_hist):
        """Small drawdown should result in low risk score"""
        score, max_dd = scorer._calculate_drawdown_score(small_drawdown_hist)

        # Small drawdown = low score
        assert score < 50

    def test_large_drawdown_high_score(self, scorer, large_drawdown_hist):
        """Large drawdown should result in high risk score"""
        score, max_dd = scorer._calculate_drawdown_score(large_drawdown_hist)

        # Large drawdown = high score
        assert score > 50


class TestCorrelationScore:
    """Tests for correlation score calculation"""

    @pytest.fixture
    def scorer(self):
        return RiskScorer(cache_ttl=0)

    def test_spy_gets_medium_score(self, scorer):
        """SPY should get medium correlation score (it's the benchmark)"""
        hist = pd.DataFrame(
            {"Close": [100 + i for i in range(100)]},
            index=pd.date_range(end=datetime.now(), periods=100, freq="D"),
        )

        score, corr = scorer._calculate_correlation_score("SPY", hist)

        assert score == 50
        assert corr == 1.0


class TestCompositeScore:
    """Tests for composite risk score calculation"""

    @pytest.fixture
    def scorer(self):
        return RiskScorer(cache_ttl=0)

    def test_composite_weight_sum(self, scorer):
        """Weights should sum to 1.0"""
        total = scorer.VOLATILITY_WEIGHT + scorer.DRAWDOWN_WEIGHT + scorer.CORRELATION_WEIGHT
        assert abs(total - 1.0) < 0.001

    def test_fallback_score(self, scorer):
        """Fallback should return medium risk score"""
        breakdown = scorer._fallback_score("UNKNOWN")

        assert breakdown.composite_score == 50
        assert breakdown.risk_level == "MEDIUM"
        assert breakdown.volatility_score == 50
        assert breakdown.drawdown_score == 50
        assert breakdown.correlation_score == 50


class TestRiskLevels:
    """Tests for risk level classification"""

    @pytest.fixture
    def scorer(self):
        return RiskScorer()

    def test_low_risk_threshold(self, scorer):
        """Scores <= 40 should be LOW risk"""
        assert scorer.LOW_RISK_THRESHOLD == 40

    def test_high_risk_threshold(self, scorer):
        """Scores > 70 should be HIGH risk"""
        assert scorer.HIGH_RISK_THRESHOLD == 70

    def test_position_size_low_risk(self, scorer):
        """LOW risk should get 1.0x position size"""
        multiplier = scorer.get_position_size_multiplier(30)
        assert multiplier == 1.0

    def test_position_size_medium_risk(self, scorer):
        """MEDIUM risk should get 0.75x position size"""
        multiplier = scorer.get_position_size_multiplier(55)
        assert multiplier == 0.75

    def test_position_size_high_risk(self, scorer):
        """HIGH risk should get 0.5x position size"""
        multiplier = scorer.get_position_size_multiplier(85)
        assert multiplier == 0.5


class TestCaching:
    """Tests for caching behavior"""

    def test_cache_clear(self):
        """Cache clear should empty all cached data"""
        scorer = RiskScorer()
        scorer._cache["TEST"] = ("mock", datetime.now())

        scorer.clear_cache()

        assert len(scorer._cache) == 0
        assert scorer._spy_cache is None


class TestSingletonPattern:
    """Tests for singleton scorer instance"""

    def test_get_risk_scorer_returns_instance(self):
        """get_risk_scorer should return a RiskScorer"""
        scorer = get_risk_scorer()
        assert isinstance(scorer, RiskScorer)

    def test_get_risk_scorer_returns_same_instance(self):
        """get_risk_scorer should return the same instance"""
        scorer1 = get_risk_scorer()
        scorer2 = get_risk_scorer()
        assert scorer1 is scorer2


class TestIntegration:
    """Integration tests with mocked yfinance"""

    @pytest.fixture
    def mock_history(self):
        """Create mock price history"""
        dates = pd.date_range(end=datetime.now(), periods=150, freq="D")
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(150) * 0.5)

        return pd.DataFrame(
            {
                "Open": prices - 0.5,
                "High": prices + 1,
                "Low": prices - 1,
                "Close": prices,
                "Volume": [1000000] * 150,
            },
            index=dates,
        )

    @patch("src.trading_engine.risk_scoring.yf.Ticker")
    def test_get_risk_score_with_mock(self, mock_ticker, mock_history):
        """Test full risk score calculation with mocked data"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.history.return_value = mock_history
        mock_ticker.return_value = mock_stock

        scorer = RiskScorer(cache_ttl=0)
        breakdown = scorer.get_risk_score("AAPL", use_cache=False)

        assert isinstance(breakdown, RiskBreakdown)
        assert 0 <= breakdown.composite_score <= 100
        assert breakdown.risk_level in ["LOW", "MEDIUM", "HIGH"]
        assert breakdown.timestamp is not None

    @patch("src.trading_engine.risk_scoring.yf.Ticker")
    def test_handles_empty_history(self, mock_ticker):
        """Test handling of empty price history"""
        mock_stock = Mock()
        mock_stock.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_stock

        scorer = RiskScorer(cache_ttl=0)
        breakdown = scorer.get_risk_score("INVALID", use_cache=False)

        # Should return fallback
        assert breakdown.composite_score == 50
        assert breakdown.risk_level == "MEDIUM"

    @patch("src.trading_engine.risk_scoring.yf.Ticker")
    def test_handles_api_error(self, mock_ticker):
        """Test handling of API errors"""
        mock_ticker.side_effect = Exception("API Error")

        scorer = RiskScorer(cache_ttl=0)
        breakdown = scorer.get_risk_score("ERROR", use_cache=False)

        # Should return fallback
        assert breakdown.composite_score == 50
        assert breakdown.risk_level == "MEDIUM"
