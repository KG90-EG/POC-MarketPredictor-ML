"""
Market Regime Detection Module

Implements regime-aware decision making based on:
1. VIX volatility levels (risk-on vs risk-off)
2. S&P 500 trend classification (bull vs bear market)
3. Composite regime score (0-100)

Philosophy: Market regime MUST influence capital allocation decisions.
Risk-off regimes should block BUY signals to protect capital.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class RegimeState:
    """Current market regime state"""

    # Volatility regime
    vix_value: float
    volatility_regime: str  # "LOW", "MEDIUM", "HIGH"
    volatility_score: int  # 0-100 (higher = safer)

    # Trend regime
    sp500_price: float
    ma_50: float
    ma_200: float
    trend_regime: str  # "BULL", "NEUTRAL", "BEAR"
    trend_score: int  # 0-100 (higher = bullish)

    # Composite regime
    regime_score: int  # 0-100 (weighted average)
    regime_status: str  # "RISK_ON", "NEUTRAL", "RISK_OFF"
    allow_buys: bool  # True if regime allows new BUY signals

    # Metadata
    timestamp: datetime
    recommendation: str  # Human-readable recommendation


class MarketRegimeDetector:
    """
    Detects current market regime and provides risk-adjusted decision rules.

    Regime Scoring:
    - Volatility (40%): VIX levels
    - Trend (60%): S&P 500 moving averages

    Decision Rules:
    - RISK_ON (score >= 70): Normal operations, allow BUY signals
    - NEUTRAL (40-69): Cautious mode, reduce position sizes
    - RISK_OFF (< 40): Defensive mode, block all BUY signals
    """

    # VIX thresholds (volatility index)
    VIX_LOW = 15  # Below: calm market
    VIX_MEDIUM = 25  # 15-25: normal volatility
    VIX_HIGH = 30  # 25-30: elevated volatility
    VIX_EXTREME = 40  # Above: panic/crisis

    # Regime score thresholds
    RISK_ON_THRESHOLD = 70
    RISK_OFF_THRESHOLD = 40

    def __init__(self, cache_ttl: int = 300):
        """
        Initialize regime detector.

        Args:
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
        """
        self.cache_ttl = cache_ttl
        self._cached_regime: Optional[RegimeState] = None
        self._cache_timestamp: Optional[datetime] = None

    def get_regime(self, use_cache: bool = True) -> RegimeState:
        """
        Get current market regime state.

        Args:
            use_cache: Use cached regime if available and fresh

        Returns:
            RegimeState with current market conditions
        """
        # Check cache
        if use_cache and self._is_cache_valid():
            logger.debug("Using cached regime state")
            return self._cached_regime

        logger.info("Fetching fresh market regime data...")

        # Fetch VIX and S&P 500 data
        vix_data = self._fetch_vix()
        sp500_data = self._fetch_sp500()

        # Calculate volatility regime
        vix_value = vix_data["current"]
        volatility_regime, volatility_score = self._classify_volatility(vix_value)

        # Calculate trend regime
        sp500_price = sp500_data["current"]
        ma_50 = sp500_data["ma_50"]
        ma_200 = sp500_data["ma_200"]
        trend_regime, trend_score = self._classify_trend(sp500_price, ma_50, ma_200)

        # Calculate composite regime score (weighted)
        regime_score = int(volatility_score * 0.4 + trend_score * 0.6)

        # Determine overall regime status
        if regime_score >= self.RISK_ON_THRESHOLD:
            regime_status = "RISK_ON"
            allow_buys = True
            recommendation = "Normal operations. Market conditions favorable for new positions."
        elif regime_score >= self.RISK_OFF_THRESHOLD:
            regime_status = "NEUTRAL"
            allow_buys = True
            recommendation = "Cautious mode. Reduce position sizes by 50%. Monitor closely."
        else:
            regime_status = "RISK_OFF"
            allow_buys = False
            recommendation = "Defensive mode. BLOCK all new BUY signals. Protect capital."

        # Create regime state
        regime = RegimeState(
            vix_value=vix_value,
            volatility_regime=volatility_regime,
            volatility_score=volatility_score,
            sp500_price=sp500_price,
            ma_50=ma_50,
            ma_200=ma_200,
            trend_regime=trend_regime,
            trend_score=trend_score,
            regime_score=regime_score,
            regime_status=regime_status,
            allow_buys=allow_buys,
            timestamp=datetime.now(),
            recommendation=recommendation,
        )

        # Cache the result
        self._cached_regime = regime
        self._cache_timestamp = datetime.now()

        logger.info(
            f"Market Regime: {regime_status} (Score: {regime_score}/100) | "
            f"VIX: {vix_value:.1f} ({volatility_regime}) | "
            f"Trend: {trend_regime} | "
            f"BUY Signals: {'ALLOWED' if allow_buys else 'BLOCKED'}"
        )

        return regime

    def _fetch_vix(self) -> Dict[str, float]:
        """
        Fetch current VIX (volatility index) value.

        Returns:
            Dict with current VIX value and recent history
        """
        try:
            vix = yf.Ticker("^VIX")
            hist = vix.history(period="5d")

            if hist.empty:
                logger.warning("VIX data unavailable, using default (20)")
                return {"current": 20.0, "avg_5d": 20.0}

            current = float(hist["Close"].iloc[-1])
            avg_5d = float(hist["Close"].mean())

            return {"current": current, "avg_5d": avg_5d}

        except Exception as e:
            logger.error(f"Error fetching VIX: {e}")
            # Default to moderate volatility if fetch fails
            return {"current": 20.0, "avg_5d": 20.0}

    def _fetch_sp500(self) -> Dict[str, float]:
        """
        Fetch S&P 500 price and moving averages.

        Returns:
            Dict with current price, 50-day MA, 200-day MA
        """
        try:
            sp500 = yf.Ticker("^GSPC")  # S&P 500 index
            hist = sp500.history(period="1y")

            if hist.empty or len(hist) < 200:
                logger.warning("S&P 500 data insufficient, using defaults")
                return {"current": 5000.0, "ma_50": 5000.0, "ma_200": 5000.0}

            current = float(hist["Close"].iloc[-1])
            ma_50 = float(hist["Close"].rolling(50).mean().iloc[-1])
            ma_200 = float(hist["Close"].rolling(200).mean().iloc[-1])

            return {"current": current, "ma_50": ma_50, "ma_200": ma_200}

        except Exception as e:
            logger.error(f"Error fetching S&P 500: {e}")
            return {"current": 5000.0, "ma_50": 5000.0, "ma_200": 5000.0}

    def _classify_volatility(self, vix: float) -> Tuple[str, int]:
        """
        Classify volatility regime based on VIX level.

        Args:
            vix: Current VIX value

        Returns:
            Tuple of (regime_name, score_0_to_100)
        """
        if vix < self.VIX_LOW:
            # Very low volatility - calm market
            return "LOW", 100
        elif vix < self.VIX_MEDIUM:
            # Normal volatility
            # Linear scale: VIX 15 = 100, VIX 25 = 60
            score = int(100 - ((vix - self.VIX_LOW) / (self.VIX_MEDIUM - self.VIX_LOW)) * 40)
            return "MEDIUM", max(60, score)
        elif vix < self.VIX_HIGH:
            # Elevated volatility - caution
            # Linear scale: VIX 25 = 60, VIX 30 = 40
            score = int(60 - ((vix - self.VIX_MEDIUM) / (self.VIX_HIGH - self.VIX_MEDIUM)) * 20)
            return "HIGH", max(40, score)
        elif vix < self.VIX_EXTREME:
            # High volatility - risk-off
            # Linear scale: VIX 30 = 40, VIX 40 = 20
            score = int(40 - ((vix - self.VIX_HIGH) / (self.VIX_EXTREME - self.VIX_HIGH)) * 20)
            return "HIGH", max(20, score)
        else:
            # Extreme volatility - panic
            return "EXTREME", 10

    def _classify_trend(self, price: float, ma_50: float, ma_200: float) -> Tuple[str, int]:
        """
        Classify trend regime based on moving average relationships.

        Args:
            price: Current S&P 500 price
            ma_50: 50-day moving average
            ma_200: 200-day moving average

        Returns:
            Tuple of (regime_name, score_0_to_100)

        Trend Classification:
        - BULL: price > ma_50 > ma_200 (golden cross)
        - NEUTRAL: mixed signals
        - BEAR: price < ma_50 < ma_200 (death cross)
        """
        price_above_50 = price > ma_50
        price_above_200 = price > ma_200
        ma_50_above_200 = ma_50 > ma_200

        # Calculate distance percentages
        price_vs_50_pct = ((price - ma_50) / ma_50) * 100
        price_vs_200_pct = ((price - ma_200) / ma_200) * 100
        ma_50_vs_200_pct = ((ma_50 - ma_200) / ma_200) * 100

        # Strong bull market
        if price_above_50 and price_above_200 and ma_50_above_200:
            # Score based on strength of trend
            base_score = 80
            # Bonus for being well above MAs
            bonus = min(20, int((price_vs_50_pct + price_vs_200_pct) / 2))
            return "BULL", min(100, base_score + bonus)

        # Strong bear market
        elif not price_above_50 and not price_above_200 and not ma_50_above_200:
            # Score based on depth of bear market
            base_score = 20
            # Penalty for being far below MAs
            penalty = min(10, int(abs((price_vs_50_pct + price_vs_200_pct) / 2)))
            return "BEAR", max(10, base_score - penalty)

        # Neutral - mixed signals
        else:
            # Calculate score based on position relative to MAs
            if price_above_200:
                score = 60 + int(price_vs_200_pct)
            else:
                score = 40 + int(price_vs_200_pct)

            return "NEUTRAL", max(30, min(70, score))

    def _is_cache_valid(self) -> bool:
        """Check if cached regime is still valid"""
        if self._cached_regime is None or self._cache_timestamp is None:
            return False

        age = (datetime.now() - self._cache_timestamp).total_seconds()
        return age < self.cache_ttl

    def get_regime_summary(self) -> str:
        """
        Get human-readable regime summary for UI display.

        Returns:
            Formatted string with regime status and key metrics
        """
        regime = self.get_regime()

        status_emoji = {
            "RISK_ON": "🟢",
            "NEUTRAL": "🟡",
            "RISK_OFF": "🔴",
        }

        return (
            f"{status_emoji.get(regime.regime_status, '⚪')} {regime.regime_status} "
            f"(Score: {regime.regime_score}/100) | "
            f"VIX: {regime.vix_value:.1f} ({regime.volatility_regime}) | "
            f"Trend: {regime.trend_regime}"
        )

    def adjust_allocation(self, base_allocation: float, regime: Optional[RegimeState] = None) -> float:
        """
        Adjust recommended allocation based on regime.

        Args:
            base_allocation: Base allocation percentage (e.g., 10.0 for 10%)
            regime: Optional regime state (fetches if not provided)

        Returns:
            Adjusted allocation percentage
        """
        if regime is None:
            regime = self.get_regime()

        if regime.regime_status == "RISK_OFF":
            # Block all new allocations
            return 0.0
        elif regime.regime_status == "NEUTRAL":
            # Reduce to 50% of normal
            return base_allocation * 0.5
        else:
            # RISK_ON: normal allocation
            return base_allocation


# Global instance
_regime_detector: Optional[MarketRegimeDetector] = None


def get_regime_detector() -> MarketRegimeDetector:
    """Get or create global regime detector instance"""
    global _regime_detector
    if _regime_detector is None:
        _regime_detector = MarketRegimeDetector()
    return _regime_detector


def get_current_regime() -> RegimeState:
    """Convenience function to get current regime"""
    detector = get_regime_detector()
    return detector.get_regime()


def should_allow_buys() -> bool:
    """
    Check if current market regime allows new BUY signals.

    Returns:
        True if regime allows buys, False if risk-off mode
    """
    regime = get_current_regime()
    return regime.allow_buys
