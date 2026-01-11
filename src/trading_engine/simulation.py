"""
Trading Simulation Engine - Paper Trading with AI Decisions

This module implements a paper trading simulation where users can test
ML model predictions with virtual capital. The AI automatically makes
buy/sell decisions based on prediction confidence.

Features:
- Auto-trading based on ML predictions
- Portfolio tracking (cash, holdings, P&L)
- Trade history with reasons
- Performance metrics (ROI, win rate)

Usage:
    sim = TradingSimulation(user_id="user123", initial_capital=10000)
    recommendations = sim.get_ai_recommendations()
    for rec in recommendations:
        sim.execute_trade(rec['ticker'], rec['action'], quantity=10,
                         price=current_price, reason=rec['reason'])
    metrics = sim.get_performance_metrics()
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class TradingSimulation:
    """
    Paper trading simulation engine.

    Manages virtual portfolio, executes trades based on AI recommendations,
    and tracks performance metrics.
    """

    def __init__(
        self,
        simulation_id: int,
        user_id: str,
        initial_capital: float,
        current_cash: float,
        positions: Dict[str, dict],
        trades: List[dict],
        created_at: datetime,
    ):
        """
        Initialize trading simulation.

        Args:
            simulation_id: Unique simulation identifier
            user_id: User identifier
            initial_capital: Starting capital amount
            current_cash: Current available cash
            positions: Current holdings {ticker: {quantity, avg_cost, current_price}}
            trades: Historical trades
            created_at: Simulation creation timestamp
        """
        self.simulation_id = simulation_id
        self.user_id = user_id
        self.initial_capital = initial_capital
        self.cash = current_cash
        self.positions = positions  # {ticker: {quantity, avg_cost, current_price}}
        self.trades = trades
        self.created_at = created_at

    def get_ai_recommendations(
        self, predictions: List[Dict], current_prices: Dict[str, float]
    ) -> List[Dict]:
        """
        Generate buy/sell recommendations based on ML predictions.

        Trading Rules:
        1. BUY if: confidence > 65%, position doesn't exist, < 10 positions total
        2. SELL if: confidence < 40% OR stop-loss (-10%) OR take-profit (+20%)
        3. Max 10 positions (diversification)
        4. Position size: Equal weight

        Args:
            predictions: List of {ticker, confidence, signal} dicts
            current_prices: Dict of {ticker: current_price}

        Returns:
            List of recommendations: [{action, ticker, confidence, reason}]
        """
        recommendations = []

        # BUY opportunities: High confidence stocks not in portfolio
        buy_candidates = [
            p
            for p in predictions
            if p["confidence"] > 0.65 and p["ticker"] not in self.positions
        ]

        # Sort by confidence, limit to available slots
        max_positions = 10
        available_slots = max_positions - len(self.positions)
        buy_candidates = sorted(
            buy_candidates, key=lambda x: x["confidence"], reverse=True
        )[:available_slots]

        allocation_per_position = self.cash / max_positions if max_positions else 0

        for pred in buy_candidates:
            current_price = current_prices.get(pred["ticker"])
            if not current_price or current_price <= 0:
                logger.warning(
                    "No valid price for %s, skipping buy recommendation", pred["ticker"]
                )
                continue

            quantity = int(allocation_per_position // current_price)
            if quantity < 1:
                quantity = 1 if current_price <= self.cash else 0

            if quantity < 1:
                logger.info(
                    "Skipping %s buy recommendation due to insufficient cash (price=$%.2f)",
                    pred["ticker"],
                    current_price,
                )
                continue

            recommendations.append(
                {
                    "action": "BUY",
                    "ticker": pred["ticker"],
                    "confidence": pred["confidence"],
                    "reason": f"High ML confidence ({pred['confidence']:.1%}), strong buy signal",
                    "price": current_price,
                    "quantity": quantity,
                }
            )

        # SELL opportunities: Check existing positions
        for ticker, position in self.positions.items():
            current_price = current_prices.get(ticker)
            if not current_price:
                logger.warning(f"No current price for {ticker}, skipping sell check")
                continue

            # Update position's current price
            position["current_price"] = current_price

            # Find current prediction for this ticker
            current_pred = next((p for p in predictions if p["ticker"] == ticker), None)

            if not current_pred:
                logger.warning(f"No prediction for {ticker}, skipping")
                continue

            # Calculate P&L percentage
            pnl_pct = (current_price - position["avg_cost"]) / position["avg_cost"]

            # SELL reasons
            if current_pred["confidence"] < 0.40:
                recommendations.append(
                    {
                        "action": "SELL",
                        "ticker": ticker,
                        "confidence": current_pred["confidence"],
                        "reason": f"Low confidence ({current_pred['confidence']:.1%}), exit position",
                        "price": current_price,
                        "quantity": position["quantity"],
                    }
                )

            elif pnl_pct <= -0.10:
                recommendations.append(
                    {
                        "action": "SELL",
                        "ticker": ticker,
                        "confidence": current_pred["confidence"],
                        "reason": f"Stop-loss triggered ({pnl_pct:.1%})",
                        "price": current_price,
                        "quantity": position["quantity"],
                    }
                )

            elif pnl_pct >= 0.20:
                recommendations.append(
                    {
                        "action": "SELL",
                        "ticker": ticker,
                        "confidence": current_pred["confidence"],
                        "reason": f"Take-profit triggered ({pnl_pct:.1%})",
                        "price": current_price,
                        "quantity": position["quantity"],
                    }
                )

        return recommendations

    def execute_trade(
        self,
        ticker: str,
        action: str,
        quantity: int,
        price: float,
        reason: str,
        ml_confidence: Optional[float] = None,
    ) -> Dict:
        """
        Execute a buy or sell trade.

        Args:
            ticker: Stock ticker symbol
            action: 'BUY' or 'SELL'
            quantity: Number of shares
            price: Execution price per share
            reason: Trade reason/rationale
            ml_confidence: ML prediction confidence (optional)

        Returns:
            Trade record dict

        Raises:
            ValueError: If insufficient cash/shares or invalid action
        """
        if action not in ["BUY", "SELL"]:
            raise ValueError(f"Invalid action: {action}")

        timestamp = datetime.now()

        if action == "BUY":
            cost = quantity * price
            if cost > self.cash:
                raise ValueError(
                    f"Insufficient cash: need ${cost:.2f}, have ${self.cash:.2f}"
                )

            # Execute buy
            self.cash -= cost

            if ticker in self.positions:
                # Average down
                pos = self.positions[ticker]
                total_quantity = pos["quantity"] + quantity
                total_cost = pos["avg_cost"] * pos["quantity"] + cost
                self.positions[ticker] = {
                    "quantity": total_quantity,
                    "avg_cost": total_cost / total_quantity,
                    "current_price": price,
                }
            else:
                # New position
                self.positions[ticker] = {
                    "quantity": quantity,
                    "avg_cost": price,
                    "current_price": price,
                }

            logger.info(
                f"BUY {quantity} {ticker} @ ${price:.2f} " f"(total: ${cost:.2f})"
            )

        elif action == "SELL":
            if ticker not in self.positions:
                raise ValueError(f"No position to sell: {ticker}")

            pos = self.positions[ticker]
            if quantity > pos["quantity"]:
                raise ValueError(
                    f"Insufficient shares: need {quantity}, have {pos['quantity']}"
                )

            # Execute sell
            proceeds = quantity * price
            self.cash += proceeds

            # Calculate realized P&L
            cost_basis = pos["avg_cost"] * quantity
            realized_pnl = proceeds - cost_basis

            if quantity == pos["quantity"]:
                # Close entire position
                del self.positions[ticker]
            else:
                # Partial sell
                self.positions[ticker]["quantity"] -= quantity

            logger.info(
                f"SELL {quantity} {ticker} @ ${price:.2f} "
                f"(proceeds: ${proceeds:.2f}, P&L: ${realized_pnl:.2f})"
            )

        # Record trade
        trade = {
            "timestamp": timestamp,
            "ticker": ticker,
            "action": action,
            "quantity": quantity,
            "price": price,
            "reason": reason,
            "ml_confidence": ml_confidence,
        }
        self.trades.append(trade)

        return trade

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value (cash + holdings).

        Args:
            current_prices: Dict of {ticker: current_price}

        Returns:
            Total portfolio value
        """
        # Update positions with current prices
        for ticker, position in self.positions.items():
            if ticker in current_prices:
                position["current_price"] = current_prices[ticker]

        holdings_value = sum(
            pos["quantity"] * pos["current_price"] for pos in self.positions.values()
        )

        return self.cash + holdings_value

    def get_performance_metrics(self, current_prices: Dict[str, float]) -> Dict:
        """
        Calculate performance metrics.

        Args:
            current_prices: Dict of {ticker: current_price}

        Returns:
            Dict with performance metrics: {
                current_value, roi, roi_percent, total_pnl,
                win_rate, total_trades, winning_trades, losing_trades
            }
        """
        current_value = self.get_portfolio_value(current_prices)
        total_pnl = current_value - self.initial_capital
        roi = total_pnl / self.initial_capital if self.initial_capital > 0 else 0

        # Calculate win rate from closed positions (paired buy/sell)
        winning_trades = 0
        losing_trades = 0

        # Group trades by ticker
        ticker_trades = {}
        for trade in self.trades:
            ticker = trade["ticker"]
            if ticker not in ticker_trades:
                ticker_trades[ticker] = []
            ticker_trades[ticker].append(trade)

        # Calculate P&L for each closed position
        for ticker, trades in ticker_trades.items():
            buys = [t for t in trades if t["action"] == "BUY"]
            sells = [t for t in trades if t["action"] == "SELL"]

            # Simple matching: pair buys and sells
            for sell in sells:
                # Find corresponding buy (FIFO)
                if buys:
                    buy = buys[0]
                    pnl = (sell["price"] - buy["price"]) * sell["quantity"]

                    if pnl > 0:
                        winning_trades += 1
                    else:
                        losing_trades += 1

                    # Remove matched quantity from buy
                    if buy["quantity"] == sell["quantity"]:
                        buys.pop(0)
                    else:
                        buy["quantity"] -= sell["quantity"]

        total_closed_trades = winning_trades + losing_trades
        win_rate = (
            winning_trades / total_closed_trades if total_closed_trades > 0 else 0
        )

        return {
            "current_value": current_value,
            "roi": roi,
            "roi_percent": roi * 100,
            "total_pnl": total_pnl,
            "win_rate": win_rate,
            "win_rate_percent": win_rate * 100,
            "total_trades": len(self.trades),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "open_positions": len(self.positions),
        }

    def to_dict(self) -> Dict:
        """
        Convert simulation to dictionary for serialization.

        Returns:
            Dict representation of simulation state
        """
        return {
            "simulation_id": self.simulation_id,
            "user_id": self.user_id,
            "initial_capital": self.initial_capital,
            "cash": self.cash,
            "positions": self.positions,
            "trades": [
                {**trade, "timestamp": trade["timestamp"].isoformat()}
                for trade in self.trades
            ],
            "created_at": self.created_at.isoformat(),
        }


def calculate_position_size(
    available_cash: float,
    current_price: float,
    max_positions: int = 10,
    reserve_cash_pct: float = 0.10,
) -> int:
    """
    Calculate optimal position size for a trade.

    Uses equal-weight allocation strategy with cash reserve.

    Args:
        available_cash: Available cash for trading
        current_price: Stock price per share
        max_positions: Maximum number of positions to hold
        reserve_cash_pct: Percentage of cash to keep in reserve

    Returns:
        Number of shares to buy
    """
    # Reserve 10% cash
    investable_cash = available_cash * (1 - reserve_cash_pct)

    # Equal weight allocation
    allocation_per_position = investable_cash / max_positions

    # Calculate shares (round down)
    quantity = int(allocation_per_position / current_price)

    return max(1, quantity)  # Minimum 1 share
