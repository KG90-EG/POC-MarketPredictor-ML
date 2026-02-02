"""
Risk Scoring Module

Calculates individual asset risk scores based on:
1. Volatility (ATR percentile) - 40% weight
2. Drawdown Risk (max drawdown 3 months) - 35% weight
3. Correlation Risk (correlation to SPY) - 25% weight

Philosophy: Every asset must have a quantifiable risk score.
Higher scores = higher risk = smaller position sizes.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class RiskBreakdown:
    """Detailed breakdown of risk score components"""

    volatility_score: int  # 0-100 (ATR-based)
    drawdown_score: int  # 0-100 (max drawdown)
    correlation_score: int  # 0-100 (correlation to SPY)

    # Weighted composite
    composite_score: int  # 0-100
    risk_level: str  # "LOW", "MEDIUM", "HIGH"

    # Raw values
    atr_percentile: float
    max_drawdown_pct: float
    spy_correlation: float

    timestamp: datetime


class RiskScorer:
    """
    Calculates risk scores for individual assets.

    Scoring:
    - Volatility (40%): ATR as percentile of price
    - Drawdown (35%): Maximum drawdown over 3 months
    - Correlation (25%): Correlation to S&P 500

    Risk Levels:
    - LOW: 0-40 (safe for larger positions)
    - MEDIUM: 41-70 (standard position limits)
    - HIGH: 71-100 (reduce position size by 50%)
    """

    # Weights for composite score
    VOLATILITY_WEIGHT = 0.40
    DRAWDOWN_WEIGHT = 0.35
    CORRELATION_WEIGHT = 0.25

    # Risk level thresholds
    LOW_RISK_THRESHOLD = 40
    HIGH_RISK_THRESHOLD = 70

    # Default lookback periods
    VOLATILITY_PERIOD = 14  # 14-day ATR
    DRAWDOWN_PERIOD = 63  # ~3 months trading days
    CORRELATION_PERIOD = 63  # ~3 months

    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize risk scorer.

        Args:
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
        """
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple] = {}  # ticker -> (RiskBreakdown, timestamp)
        self._spy_cache: Optional[pd.DataFrame] = None
        self._spy_cache_time: Optional[datetime] = None

    def get_risk_score(self, ticker: str, use_cache: bool = True) -> RiskBreakdown:
        """
        Get composite risk score for an asset.

        Args:
            ticker: Stock/crypto ticker symbol
            use_cache: Use cached result if available

        Returns:
            RiskBreakdown with all score components
        """
        # Check cache
        if use_cache and ticker in self._cache:
            cached_breakdown, cache_time = self._cache[ticker]
            age = (datetime.now() - cache_time).total_seconds()
            if age < self.cache_ttl:
                logger.debug(f"Using cached risk score for {ticker}")
                return cached_breakdown

        logger.info(f"Calculating risk score for {ticker}...")

        try:
            # Fetch price history
            hist = self._fetch_history(ticker)

            if hist is None or len(hist) < 20:
                logger.warning(f"Insufficient data for {ticker}, using fallback")
                return self._fallback_score(ticker)

            # Calculate individual scores
            volatility_score, atr_percentile = self._calculate_volatility_score(hist)
            drawdown_score, max_drawdown = self._calculate_drawdown_score(hist)
            correlation_score, spy_corr = self._calculate_correlation_score(ticker, hist)

            # Calculate composite score
            composite = int(
                volatility_score * self.VOLATILITY_WEIGHT
                + drawdown_score * self.DRAWDOWN_WEIGHT
                + correlation_score * self.CORRELATION_WEIGHT
            )

            # Determine risk level
            if composite <= self.LOW_RISK_THRESHOLD:
                risk_level = "LOW"
            elif composite <= self.HIGH_RISK_THRESHOLD:
                risk_level = "MEDIUM"
            else:
                risk_level = "HIGH"

            breakdown = RiskBreakdown(
                volatility_score=volatility_score,
                drawdown_score=drawdown_score,
                correlation_score=correlation_score,
                composite_score=composite,
                risk_level=risk_level,
                atr_percentile=atr_percentile,
                max_drawdown_pct=max_drawdown,
                spy_correlation=spy_corr,
                timestamp=datetime.now(),
            )

            # Cache result
            self._cache[ticker] = (breakdown, datetime.now())

            logger.info(
                f"Risk Score {ticker}: {composite}/100 ({risk_level}) | "
                f"Vol: {volatility_score} | DD: {drawdown_score} | Corr: {correlation_score}"
            )

            return breakdown

        except Exception as e:
            logger.error(f"Error calculating risk score for {ticker}: {e}")
            return self._fallback_score(ticker)

    def _fetch_history(self, ticker: str) -> Optional[pd.DataFrame]:
        """Fetch price history for risk calculations."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")

            if hist.empty:
                return None

            return hist

        except Exception as e:
            logger.error(f"Error fetching history for {ticker}: {e}")
            return None

    def _calculate_volatility_score(self, hist: pd.DataFrame) -> tuple:
        """
        Calculate volatility score based on ATR percentile.

        Higher ATR (relative to price) = higher risk score.

        Returns:
            Tuple of (score 0-100, atr_percentile)
        """
        try:
            high = hist["High"]
            low = hist["Low"]
            close = hist["Close"]

            # Calculate True Range
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))

            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # ATR as percentage of current price
            atr = true_range.rolling(self.VOLATILITY_PERIOD).mean().iloc[-1]
            current_price = close.iloc[-1]
            atr_pct = (atr / current_price) * 100

            # Map to 0-100 score
            # Typical ATR% ranges:
            # < 1%: Very low volatility (score ~10)
            # 1-2%: Low volatility (score ~30)
            # 2-4%: Medium volatility (score ~50)
            # 4-6%: High volatility (score ~70)
            # > 6%: Very high volatility (score ~90)

            if atr_pct < 1:
                score = int(atr_pct * 10)  # 0-10
            elif atr_pct < 2:
                score = int(10 + (atr_pct - 1) * 20)  # 10-30
            elif atr_pct < 4:
                score = int(30 + (atr_pct - 2) * 20)  # 30-70
            elif atr_pct < 6:
                score = int(70 + (atr_pct - 4) * 15)  # 70-100
            else:
                score = min(100, int(70 + (atr_pct - 4) * 10))

            return min(100, max(0, score)), atr_pct

        except Exception as e:
            logger.warning(f"Volatility calculation failed: {e}")
            return 50, 2.5  # Default medium volatility

    def _calculate_drawdown_score(self, hist: pd.DataFrame) -> tuple:
        """
        Calculate drawdown score based on max drawdown over period.

        Larger drawdown = higher risk score.

        Returns:
            Tuple of (score 0-100, max_drawdown_pct)
        """
        try:
            close = hist["Close"].iloc[-self.DRAWDOWN_PERIOD :]

            # Calculate running maximum
            running_max = close.expanding().max()

            # Calculate drawdown
            drawdown = (close - running_max) / running_max * 100

            # Max drawdown (most negative value, stored as positive)
            max_dd = abs(drawdown.min())

            # Map to 0-100 score
            # < 5% drawdown: Low risk (score ~20)
            # 5-10%: Medium-low (score ~40)
            # 10-20%: Medium (score ~60)
            # 20-30%: High (score ~80)
            # > 30%: Very high (score ~100)

            if max_dd < 5:
                score = int(max_dd * 4)  # 0-20
            elif max_dd < 10:
                score = int(20 + (max_dd - 5) * 4)  # 20-40
            elif max_dd < 20:
                score = int(40 + (max_dd - 10) * 2)  # 40-60
            elif max_dd < 30:
                score = int(60 + (max_dd - 20) * 2)  # 60-80
            else:
                score = min(100, int(80 + (max_dd - 30)))  # 80-100

            return min(100, max(0, score)), max_dd

        except Exception as e:
            logger.warning(f"Drawdown calculation failed: {e}")
            return 50, 10.0  # Default medium drawdown

    def _calculate_correlation_score(self, ticker: str, hist: pd.DataFrame) -> tuple:
        """
        Calculate correlation score based on correlation to SPY.

        Higher correlation = higher systemic risk score.

        Returns:
            Tuple of (score 0-100, correlation)
        """
        try:
            # Skip correlation for SPY itself
            if ticker.upper() in ["SPY", "^GSPC"]:
                return 50, 1.0

            # Get SPY returns
            spy_returns = self._get_spy_returns()

            if spy_returns is None:
                return 50, 0.5

            # Calculate returns for this asset
            asset_returns = hist["Close"].pct_change().dropna()

            # Align dates
            common_dates = spy_returns.index.intersection(asset_returns.index)

            if len(common_dates) < 20:
                return 50, 0.5

            spy_aligned = spy_returns.loc[common_dates]
            asset_aligned = asset_returns.loc[common_dates]

            # Calculate correlation
            correlation = spy_aligned.corr(asset_aligned)

            if np.isnan(correlation):
                return 50, 0.5

            # Map to 0-100 score
            # High correlation (> 0.8): High systemic risk (score ~80)
            # Medium correlation (0.4-0.8): Medium risk (score ~50)
            # Low correlation (0-0.4): Lower systemic risk (score ~30)
            # Negative correlation: Hedge value (score ~10)

            if correlation < 0:
                score = int(max(0, 20 + correlation * 20))  # 0-20
            elif correlation < 0.4:
                score = int(20 + correlation * 25)  # 20-30
            elif correlation < 0.8:
                score = int(30 + (correlation - 0.4) * 50)  # 30-50
            else:
                score = int(50 + (correlation - 0.8) * 250)  # 50-100

            return min(100, max(0, score)), correlation

        except Exception as e:
            logger.warning(f"Correlation calculation failed: {e}")
            return 50, 0.5

    def _get_spy_returns(self) -> Optional[pd.Series]:
        """Get SPY daily returns (with caching)."""
        # Check cache
        if self._spy_cache is not None and self._spy_cache_time is not None:
            age = (datetime.now() - self._spy_cache_time).total_seconds()
            if age < self.cache_ttl:
                return self._spy_cache

        try:
            spy = yf.Ticker("SPY")
            hist = spy.history(period="6mo")

            if hist.empty:
                return None

            returns = hist["Close"].pct_change().dropna()

            self._spy_cache = returns
            self._spy_cache_time = datetime.now()

            return returns

        except Exception as e:
            logger.error(f"Error fetching SPY data: {e}")
            return None

    def _fallback_score(self, ticker: str) -> RiskBreakdown:
        """Return default medium-risk score when data unavailable."""
        logger.warning(f"Using fallback risk score for {ticker}")

        return RiskBreakdown(
            volatility_score=50,
            drawdown_score=50,
            correlation_score=50,
            composite_score=50,
            risk_level="MEDIUM",
            atr_percentile=2.5,
            max_drawdown_pct=10.0,
            spy_correlation=0.5,
            timestamp=datetime.now(),
        )

    def get_position_size_multiplier(self, risk_score: int) -> float:
        """
        Get position size multiplier based on risk score.

        - LOW risk (0-40): 1.0x (full position)
        - MEDIUM risk (41-70): 0.75x (reduced)
        - HIGH risk (71-100): 0.5x (half position)

        Args:
            risk_score: Composite risk score 0-100

        Returns:
            Position size multiplier (0.5-1.0)
        """
        if risk_score <= self.LOW_RISK_THRESHOLD:
            return 1.0
        elif risk_score <= self.HIGH_RISK_THRESHOLD:
            return 0.75
        else:
            return 0.5

    def clear_cache(self) -> None:
        """Clear all cached risk scores."""
        self._cache.clear()
        self._spy_cache = None
        self._spy_cache_time = None
        logger.info("Risk score cache cleared")


# Singleton instance for shared use
_scorer_instance: Optional[RiskScorer] = None


def get_risk_scorer() -> RiskScorer:
    """Get shared RiskScorer instance."""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = RiskScorer()
    return _scorer_instance
