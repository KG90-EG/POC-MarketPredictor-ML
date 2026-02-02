"""
Portfolio Construction & Allocation Management

Implements portfolio-level constraints and risk controls:
- Position size limits (10% stocks, 5% crypto)
- Portfolio exposure limits (70% equities, 20% crypto, 10% cash)
- Correlation analysis for diversification
- Allocation validation and warnings

Philosophy: Prevent concentration risk through enforced limits.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Individual position in portfolio"""

    ticker: str
    asset_type: str  # 'stock' or 'crypto'
    allocation: float  # Percentage (0-100)
    score: float  # Composite score
    signal: str  # BUY, HOLD, SELL
    correlation_risk: Optional[float] = None  # Correlation with portfolio


@dataclass
class PortfolioLimits:
    """Portfolio-level allocation limits"""

    # Position limits
    max_stock_position: float = 10.0  # Max 10% per stock
    max_crypto_position: float = 5.0  # Max 5% per crypto

    # Asset class limits
    max_equity_exposure: float = 70.0  # Max 70% in stocks
    max_crypto_exposure: float = 20.0  # Max 20% in crypto
    min_cash_reserve: float = 10.0  # Min 10% cash

    # Risk limits
    max_correlation: float = 0.7  # Max correlation between positions
    max_concentrated_positions: int = 3  # Max positions >8%


@dataclass
class PortfolioAnalysis:
    """Portfolio analysis results"""

    total_allocation: float
    equity_exposure: float
    crypto_exposure: float
    cash_reserve: float

    positions: List[Position]
    violations: List[str]
    warnings: List[str]

    # Risk metrics
    diversification_score: int  # 0-100
    correlation_matrix: Optional[pd.DataFrame] = None
    concentrated_positions: List[str] = None  # Tickers >8%


class PortfolioManager:
    """
    Manages portfolio construction and validates allocation limits.

    Ensures:
    1. No single stock >10% of portfolio
    2. No single crypto >5% of portfolio
    3. Total equity exposure ≤70%
    4. Total crypto exposure ≤20%
    5. Min 10% cash reserve
    6. Correlation risk management
    """

    def __init__(self, limits: Optional[PortfolioLimits] = None):
        """Initialize portfolio manager with limits"""
        self.limits = limits or PortfolioLimits()

    def validate_allocation(
        self, positions: List[Dict], current_portfolio: Optional[Dict] = None
    ) -> PortfolioAnalysis:
        """
        Validate proposed allocations against portfolio limits.

        Args:
            positions: List of proposed positions with allocation, asset_type, etc.
            current_portfolio: Optional existing portfolio for rebalancing

        Returns:
            PortfolioAnalysis with violations and warnings
        """
        violations = []
        warnings = []
        position_objects = []

        # Convert to Position objects
        for pos in positions:
            position_objects.append(
                Position(
                    ticker=pos["ticker"],
                    asset_type=pos.get("asset_type", "stock"),
                    allocation=pos.get("allocation", 0.0),
                    score=pos.get("composite_score", pos.get("score", 0.0)),
                    signal=pos.get("signal", "HOLD"),
                )
            )

        # Calculate totals
        total_allocation = sum(p.allocation for p in position_objects)
        equity_exposure = sum(p.allocation for p in position_objects if p.asset_type == "stock")
        crypto_exposure = sum(p.allocation for p in position_objects if p.asset_type == "crypto")
        cash_reserve = 100.0 - total_allocation

        # Validate position limits
        for pos in position_objects:
            if pos.asset_type == "stock" and pos.allocation > self.limits.max_stock_position:
                violations.append(
                    f"⛔ {pos.ticker}: {pos.allocation:.1f}% exceeds stock limit "
                    f"({self.limits.max_stock_position}%)"
                )
            elif pos.asset_type == "crypto" and pos.allocation > self.limits.max_crypto_position:
                violations.append(
                    f"⛔ {pos.ticker}: {pos.allocation:.1f}% exceeds crypto limit "
                    f"({self.limits.max_crypto_position}%)"
                )

        # Validate asset class limits
        if equity_exposure > self.limits.max_equity_exposure:
            violations.append(
                f"⛔ Equity exposure: {equity_exposure:.1f}% exceeds limit "
                f"({self.limits.max_equity_exposure}%)"
            )

        if crypto_exposure > self.limits.max_crypto_exposure:
            violations.append(
                f"⛔ Crypto exposure: {crypto_exposure:.1f}% exceeds limit "
                f"({self.limits.max_crypto_exposure}%)"
            )

        if cash_reserve < self.limits.min_cash_reserve:
            warnings.append(
                f"⚠️ Cash reserve: {cash_reserve:.1f}% below minimum "
                f"({self.limits.min_cash_reserve}%)"
            )

        # Check for concentrated positions (>8%)
        concentrated = [p.ticker for p in position_objects if p.allocation > 8.0]
        if len(concentrated) > self.limits.max_concentrated_positions:
            warnings.append(
                f"⚠️ Too many concentrated positions: {len(concentrated)} positions >8% "
                f"(limit: {self.limits.max_concentrated_positions})"
            )

        # Calculate diversification score
        diversification_score = self._calculate_diversification_score(
            position_objects, equity_exposure, crypto_exposure, concentrated
        )

        return PortfolioAnalysis(
            total_allocation=total_allocation,
            equity_exposure=equity_exposure,
            crypto_exposure=crypto_exposure,
            cash_reserve=cash_reserve,
            positions=position_objects,
            violations=violations,
            warnings=warnings,
            diversification_score=diversification_score,
            concentrated_positions=concentrated,
        )

    def _calculate_diversification_score(
        self,
        positions: List[Position],
        equity_exposure: float,
        crypto_exposure: float,
        concentrated: List[str],
    ) -> int:
        """
        Calculate diversification score (0-100).

        Higher score = better diversification
        """
        score = 100.0

        # Penalty for concentration
        if len(positions) < 5:
            score -= 20  # Too few positions
        elif len(positions) > 20:
            score -= 10  # Too many positions (management overhead)

        # Penalty for concentrated positions
        score -= len(concentrated) * 5  # -5 points per concentrated position

        # Penalty for asset class imbalance
        if equity_exposure > 60 or crypto_exposure > 15:
            score -= 10

        # Penalty for under-diversification within asset class
        if len([p for p in positions if p.asset_type == "stock"]) < 5:
            score -= 15

        # Bonus for balanced exposure
        if 50 <= equity_exposure <= 60 and 10 <= crypto_exposure <= 15:
            score += 10

        return max(0, min(100, int(score)))

    def calculate_correlation_risk(
        self, positions: List[Dict], price_history: Dict[str, pd.DataFrame]
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Calculate correlation matrix for positions.

        Args:
            positions: List of positions
            price_history: Dict mapping ticker -> DataFrame with 'Close' prices

        Returns:
            Tuple of (correlation_matrix, high_correlation_warnings)
        """
        warnings = []

        # Extract returns for each position
        returns_data = {}
        for pos in positions:
            ticker = pos["ticker"]
            if ticker in price_history:
                df = price_history[ticker]
                if "Close" in df.columns and len(df) > 1:
                    returns = df["Close"].pct_change().dropna()
                    if len(returns) > 30:  # Need sufficient data
                        returns_data[ticker] = returns

        if len(returns_data) < 2:
            logger.warning("Insufficient data for correlation analysis")
            return None, []

        # Align returns on common dates
        returns_df = pd.DataFrame(returns_data)
        returns_df = returns_df.dropna()

        if len(returns_df) < 30:
            logger.warning("Insufficient overlapping data for correlation")
            return None, []

        # Calculate correlation matrix
        corr_matrix = returns_df.corr()

        # Find high correlations (excluding diagonal)
        for i in range(len(corr_matrix)):
            for j in range(i + 1, len(corr_matrix)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > self.limits.max_correlation:
                    ticker1 = corr_matrix.index[i]
                    ticker2 = corr_matrix.columns[j]
                    warnings.append(
                        f"⚠️ High correlation between {ticker1} and {ticker2}: "
                        f"{corr_value:.2f} (limit: {self.limits.max_correlation})"
                    )

        return corr_matrix, warnings

    def suggest_rebalancing(
        self, current_positions: List[Dict], target_allocation: float = 100.0
    ) -> List[Dict]:
        """
        Suggest portfolio rebalancing to meet limits.

        Args:
            current_positions: Current portfolio positions
            target_allocation: Target total allocation percentage

        Returns:
            List of rebalancing actions
        """
        actions = []

        # Validate current portfolio
        analysis = self.validate_allocation(current_positions)

        if not analysis.violations and not analysis.warnings:
            return [{"action": "HOLD", "message": "Portfolio within limits"}]

        # Address violations
        for violation in analysis.violations:
            if "exceeds stock limit" in violation:
                ticker = violation.split(":")[0].replace("⛔ ", "")
                current = next(p for p in current_positions if p["ticker"] == ticker)
                target = self.limits.max_stock_position
                reduce = current["allocation"] - target
                actions.append(
                    {
                        "action": "REDUCE",
                        "ticker": ticker,
                        "current": current["allocation"],
                        "target": target,
                        "reduction": reduce,
                        "reason": "Exceeds position limit",
                    }
                )

            elif "exceeds crypto limit" in violation:
                ticker = violation.split(":")[0].replace("⛔ ", "")
                current = next(p for p in current_positions if p["ticker"] == ticker)
                target = self.limits.max_crypto_position
                reduce = current["allocation"] - target
                actions.append(
                    {
                        "action": "REDUCE",
                        "ticker": ticker,
                        "current": current["allocation"],
                        "target": target,
                        "reduction": reduce,
                        "reason": "Exceeds position limit",
                    }
                )

            elif "Equity exposure" in violation:
                # Suggest reducing equity positions proportionally
                equity_positions = [p for p in current_positions if p.get("asset_type") == "stock"]
                total_reduction = analysis.equity_exposure - self.limits.max_equity_exposure

                for pos in sorted(equity_positions, key=lambda x: x.get("score", 0)):
                    # Reduce lowest-scoring positions first
                    reduction = min(
                        pos["allocation"] * 0.2,  # Max 20% reduction per position
                        total_reduction,
                    )
                    if reduction > 0.5:  # Only if meaningful reduction
                        actions.append(
                            {
                                "action": "REDUCE",
                                "ticker": pos["ticker"],
                                "current": pos["allocation"],
                                "target": pos["allocation"] - reduction,
                                "reduction": reduction,
                                "reason": "Reduce equity exposure",
                            }
                        )
                        total_reduction -= reduction
                        if total_reduction < 0.5:
                            break

        return actions

    def get_allocation_recommendation(
        self, ticker: str, score: float, signal: str, asset_type: str = "stock"
    ) -> float:
        """
        Get recommended allocation for a single position.

        Args:
            ticker: Stock/crypto ticker
            score: Composite score (0-100)
            signal: Trading signal
            asset_type: 'stock' or 'crypto'

        Returns:
            Recommended allocation percentage
        """
        # Base allocation based on signal and score
        if signal == "STRONG_BUY" and score >= 85:
            base = 10.0 if asset_type == "stock" else 5.0
        elif signal == "BUY" and score >= 65:
            base = 7.5 if asset_type == "stock" else 3.5
        elif signal == "HOLD":
            base = 5.0 if asset_type == "stock" else 2.0
        else:
            base = 0.0

        # Apply position limit
        max_limit = (
            self.limits.max_stock_position
            if asset_type == "stock"
            else self.limits.max_crypto_position
        )

        return min(base, max_limit)


# Global instance
_portfolio_manager: Optional[PortfolioManager] = None


def get_portfolio_manager() -> PortfolioManager:
    """Get or create global portfolio manager instance"""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager()
    return _portfolio_manager
