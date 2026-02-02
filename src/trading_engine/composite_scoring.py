"""
Composite Scoring System for Asset Ranking

Replaces ML-only probability with weighted composite score based on:
- Technical Signals (40%): RSI, MACD, Bollinger Bands, ADX
- ML Probability (30%): Random Forest prediction
- Momentum (20%): Multi-period price momentum
- Market Regime (10%): Regime adjustment factor
- LLM Context (±5% max): News sentiment and catalysts (modifier only)

Philosophy: Quantitative signals dominate; LLM provides context, not decisions.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ScoreBreakdown:
    """Detailed score breakdown for explainability"""

    # Component scores (0-100 each)
    technical_score: float
    ml_score: float
    momentum_score: float
    regime_score: float

    # Final composite
    composite_score: float

    # LLM context (modifier only, ±5% max)
    llm_adjustment: float
    llm_context: Optional[str]

    # Contributing factors (for UI display)
    top_factors: list  # Top 3 positive factors
    risk_factors: list  # Top 3 risk factors

    # Metadata
    signal: str  # BUY, HOLD, SELL
    confidence: int  # 0-100


class CompositeScorer:
    """
    Aggregates multiple signals into single composite score.

    Weighting:
    - Technical Signals: 40%
    - ML Probability: 30%
    - Momentum: 20%
    - Market Regime: 10%
    - LLM Context: ±5% adjustment (strict limit)

    Score Scale: 0-100
    - 80-100: Strong BUY
    - 65-79: BUY
    - 45-64: HOLD
    - 35-44: Consider Selling
    - 0-34: SELL
    """

    # Score weights
    WEIGHT_TECHNICAL = 0.40
    WEIGHT_ML = 0.30
    WEIGHT_MOMENTUM = 0.20
    WEIGHT_REGIME = 0.10

    # Signal thresholds
    STRONG_BUY_THRESHOLD = 80
    BUY_THRESHOLD = 65
    HOLD_MIN_THRESHOLD = 45
    CONSIDER_SELLING_THRESHOLD = 35

    def __init__(self):
        """Initialize composite scorer"""
        pass

    def calculate_technical_score(self, df: pd.DataFrame) -> tuple[float, list, list]:
        """
        Calculate technical analysis score from indicators.

        Args:
            df: DataFrame with technical indicators (last row = current)

        Returns:
            Tuple of (score, positive_factors, negative_factors)
        """
        if df.empty:
            return 50.0, [], []

        row = df.iloc[-1]
        score = 50.0  # Neutral baseline
        positive_factors = []
        negative_factors = []

        # RSI Analysis (0-100 scale)
        if "RSI" in df.columns and not pd.isna(row["RSI"]):
            rsi = row["RSI"]
            if rsi < 30:
                # Oversold - bullish
                score += 10
                positive_factors.append(f"RSI oversold ({rsi:.1f})")
            elif rsi > 70:
                # Overbought - bearish
                score -= 10
                negative_factors.append(f"RSI overbought ({rsi:.1f})")
            elif 40 <= rsi <= 60:
                # Neutral territory
                score += 5
                positive_factors.append(f"RSI neutral ({rsi:.1f})")

        # MACD Crossover
        if all(col in df.columns for col in ["MACD", "MACD_Signal"]):
            macd = row["MACD"]
            signal = row["MACD_Signal"]
            if not pd.isna(macd) and not pd.isna(signal):
                if macd > signal and macd > 0:
                    # Bullish crossover above zero
                    score += 15
                    positive_factors.append("MACD bullish crossover")
                elif macd < signal and macd < 0:
                    # Bearish crossover below zero
                    score -= 15
                    negative_factors.append("MACD bearish crossover")
                elif macd > signal:
                    # Above signal but not strong
                    score += 7
                    positive_factors.append("MACD above signal")

        # Bollinger Bands Position
        if all(col in df.columns for col in ["Close", "BB_Upper", "BB_Lower"]):
            close = row["Close"]
            bb_upper = row["BB_Upper"]
            bb_lower = row["BB_Lower"]
            if not pd.isna(bb_upper) and not pd.isna(bb_lower):
                bb_range = bb_upper - bb_lower
                if bb_range > 0:
                    bb_position = (close - bb_lower) / bb_range
                    if bb_position < 0.2:
                        # Near lower band - potential bounce
                        score += 10
                        positive_factors.append("Near lower Bollinger Band")
                    elif bb_position > 0.8:
                        # Near upper band - potential pullback
                        score -= 10
                        negative_factors.append("Near upper Bollinger Band")

        # ADX Trend Strength
        if "ADX" in df.columns and not pd.isna(row["ADX"]):
            adx = row["ADX"]
            if adx > 25:
                # Strong trend present
                score += 8
                positive_factors.append(f"Strong trend (ADX {adx:.1f})")
            elif adx < 20:
                # Weak trend - risky
                score -= 5
                negative_factors.append(f"Weak trend (ADX {adx:.1f})")

        # Parabolic SAR
        if all(col in df.columns for col in ["Close", "SAR"]):
            close = row["Close"]
            sar = row["SAR"]
            if not pd.isna(sar):
                if close > sar:
                    # Bullish signal
                    score += 7
                    positive_factors.append("Above SAR (bullish)")
                else:
                    # Bearish signal
                    score -= 7
                    negative_factors.append("Below SAR (bearish)")

        # Clamp to 0-100
        return max(0, min(100, score)), positive_factors[:3], negative_factors[:3]

    def calculate_momentum_score(self, df: pd.DataFrame) -> tuple[float, list]:
        """
        Calculate multi-period momentum score.

        Args:
            df: DataFrame with Close prices

        Returns:
            Tuple of (score, factors)
        """
        if df.empty or "Close" not in df.columns:
            return 50.0, []

        factors = []
        score = 50.0  # Neutral baseline

        try:
            prices = df["Close"]

            # 10-day momentum (25% weight)
            if len(prices) >= 10:
                mom_10d = ((prices.iloc[-1] / prices.iloc[-10]) - 1) * 100
                if mom_10d > 5:
                    score += 12.5
                    factors.append(f"10d: +{mom_10d:.1f}%")
                elif mom_10d > 0:
                    score += 6
                    factors.append(f"10d: +{mom_10d:.1f}%")
                elif mom_10d < -5:
                    score -= 12.5
                    factors.append(f"10d: {mom_10d:.1f}%")
                else:
                    score -= 6
                    factors.append(f"10d: {mom_10d:.1f}%")

            # 30-day momentum (35% weight)
            if len(prices) >= 30:
                mom_30d = ((prices.iloc[-1] / prices.iloc[-30]) - 1) * 100
                if mom_30d > 10:
                    score += 17.5
                    factors.append(f"30d: +{mom_30d:.1f}%")
                elif mom_30d > 0:
                    score += 9
                    factors.append(f"30d: +{mom_30d:.1f}%")
                elif mom_30d < -10:
                    score -= 17.5
                    factors.append(f"30d: {mom_30d:.1f}%")
                else:
                    score -= 9
                    factors.append(f"30d: {mom_30d:.1f}%")

            # 60-day momentum (40% weight)
            if len(prices) >= 60:
                mom_60d = ((prices.iloc[-1] / prices.iloc[-60]) - 1) * 100
                if mom_60d > 15:
                    score += 20
                    factors.append(f"60d: +{mom_60d:.1f}%")
                elif mom_60d > 0:
                    score += 10
                    factors.append(f"60d: +{mom_60d:.1f}%")
                elif mom_60d < -15:
                    score -= 20
                    factors.append(f"60d: {mom_60d:.1f}%")
                else:
                    score -= 10
                    factors.append(f"60d: {mom_60d:.1f}%")

        except Exception as e:
            logger.warning(f"Momentum calculation error: {e}")

        return max(0, min(100, score)), factors

    def calculate_composite_score(
        self,
        df: pd.DataFrame,
        ml_probability: float,
        regime_score: int,
        allow_buys: bool = True,
        ticker: str = None,
    ) -> ScoreBreakdown:
        """
        Calculate final composite score.

        Args:
            df: DataFrame with technical indicators and prices
            ml_probability: ML model prediction (0-1)
            regime_score: Market regime score (0-100)
            allow_buys: Whether market regime allows BUY signals
            ticker: Stock ticker for LLM context (optional)

        Returns:
            ScoreBreakdown with complete score analysis
        """
        # Calculate component scores
        technical_score, tech_positive, tech_negative = self.calculate_technical_score(df)
        ml_score = ml_probability * 100  # Convert 0-1 to 0-100
        momentum_score, momentum_factors = self.calculate_momentum_score(df)

        # Calculate weighted composite (base score before LLM adjustment)
        base_composite_score = (
            technical_score * self.WEIGHT_TECHNICAL
            + ml_score * self.WEIGHT_ML
            + momentum_score * self.WEIGHT_MOMENTUM
            + regime_score * self.WEIGHT_REGIME
        )

        # Apply LLM context adjustment (if available)
        llm_adjustment = 0.0
        llm_context_str = None

        if ticker:
            from .llm_context import get_context_provider

            context_provider = get_context_provider()

            if context_provider:
                try:
                    asset_context = context_provider.get_asset_context(
                        ticker=ticker,
                        current_score=base_composite_score,
                        lookback_days=7,
                    )
                    llm_adjustment = asset_context.context_adjustment

                    # Format context string for breakdown
                    llm_context_str = asset_context.news_summary

                    # Add LLM factors to positive/negative lists
                    if asset_context.positive_catalysts:
                        tech_positive.extend(
                            [f"📰 {cat}" for cat in asset_context.positive_catalysts[:2]]
                        )
                    if asset_context.risk_events:
                        tech_negative.extend(
                            [f"⚠️ {risk}" for risk in asset_context.risk_events[:2]]
                        )

                except Exception as e:
                    import logging

                    logging.warning(f"LLM context failed for {ticker}: {e}")

        # Final composite score with LLM adjustment
        composite_score = base_composite_score + llm_adjustment

        # Determine signal
        if not allow_buys and composite_score >= self.BUY_THRESHOLD:
            # Regime override: downgrade BUY to HOLD
            signal = "HOLD"
            tech_negative.append("RISK-OFF: BUY blocked by regime")
        elif composite_score >= self.STRONG_BUY_THRESHOLD:
            signal = "STRONG_BUY"
        elif composite_score >= self.BUY_THRESHOLD:
            signal = "BUY"
        elif composite_score >= self.HOLD_MIN_THRESHOLD:
            signal = "HOLD"
        elif composite_score >= self.CONSIDER_SELLING_THRESHOLD:
            signal = "CONSIDER_SELLING"
        else:
            signal = "SELL"

        # Compile top factors
        all_positive = (
            tech_positive
            + momentum_factors
            + ([f"ML confidence: {ml_score:.0f}%"] if ml_score > 60 else [])
            + ([f"Regime favorable: {regime_score}/100"] if regime_score > 70 else [])
        )

        all_negative = tech_negative + (
            [f"Regime unfavorable: {regime_score}/100"] if regime_score < 40 else []
        )

        return ScoreBreakdown(
            technical_score=round(technical_score, 1),
            ml_score=round(ml_score, 1),
            momentum_score=round(momentum_score, 1),
            regime_score=regime_score,
            composite_score=round(composite_score, 1),
            top_factors=all_positive[:3],
            risk_factors=all_negative[:3],
            signal=signal,
            confidence=int(composite_score),
            llm_adjustment=round(llm_adjustment, 2),
            llm_context=llm_context_str,
        )

    def get_allocation_limit(self, score: float, signal: str, asset_type: str = "stock") -> float:
        """
        Get maximum recommended allocation based on score and asset type.

        Args:
            score: Composite score (0-100)
            signal: Trading signal
            asset_type: 'stock' or 'crypto'

        Returns:
            Maximum allocation percentage
        """
        # Base limits
        base_limits = {"stock": 10.0, "crypto": 5.0}  # 10% per stock  # 5% per crypto

        base = base_limits.get(asset_type, 10.0)

        # Adjust based on signal strength
        if signal == "STRONG_BUY" and score >= 85:
            return base  # Full allocation
        elif signal == "BUY":
            return base * 0.75  # 75% of max
        elif signal == "HOLD":
            return base * 0.5  # 50% of max (for rebalancing)
        else:
            return 0.0  # No new allocation for SELL signals


# Global instance
_composite_scorer: Optional[CompositeScorer] = None


def get_composite_scorer() -> CompositeScorer:
    """Get or create global composite scorer instance"""
    global _composite_scorer
    if _composite_scorer is None:
        _composite_scorer = CompositeScorer()
    return _composite_scorer
