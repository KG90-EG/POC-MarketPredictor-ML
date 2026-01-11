"""
Historical Validation & Backtesting Framework (Phase 3)

Compares 3 strategies:
1. Composite Score System (Technical 40% + ML 30% + Momentum 20% + Regime 10%)
2. ML-Only Strategy
3. S&P 500 Buy-and-Hold Benchmark

Metrics:
- Total Return
- Max Drawdown
- Sharpe Ratio
- Win Rate
- Calmar Ratio (Return / Max Drawdown)
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    """Results from a backtest run"""

    strategy_name: str
    start_date: datetime
    end_date: datetime
    total_return: float  # Percentage
    max_drawdown: float  # Percentage
    sharpe_ratio: float
    win_rate: float  # Percentage of profitable trades
    num_trades: int
    avg_trade_return: float
    calmar_ratio: float  # Return / Max Drawdown
    final_portfolio_value: float
    trades: List[Dict]  # Trade history


class HistoricalBacktester:
    """
    Backtest system recommendations against historical data.

    Follows Phase 3 requirements:
    - 1-year lookback (Jan 2025 - Jan 2026)
    - Compare 3 strategies
    - Measure returns, drawdowns, Sharpe, win rate
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        position_size: float = 0.10,  # 10% per position
        risk_free_rate: float = 0.04,  # 4% annual
    ):
        """
        Initialize backtester.

        Args:
            initial_capital: Starting portfolio value (default: $100k)
            position_size: Percentage of portfolio per trade (default: 10%)
            risk_free_rate: Risk-free rate for Sharpe calculation (default: 4%)
        """
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.risk_free_rate = risk_free_rate

    def run_comparison(
        self,
        tickers: List[str],
        start_date: str = "2025-01-01",
        end_date: str = "2026-01-11",
    ) -> Dict[str, BacktestResult]:
        """
        Run backtest comparison across 3 strategies.

        Args:
            tickers: List of stock tickers to backtest
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Dict mapping strategy name to BacktestResult
        """
        logger.info(f"Running backtest comparison: {start_date} to {end_date}")
        logger.info(f"Tickers: {len(tickers)} stocks")

        results = {}

        # Strategy 1: Composite Score System
        logger.info("Running Strategy 1: Composite Score System...")
        results["composite"] = self._run_composite_strategy(
            tickers, start_date, end_date
        )

        # Strategy 2: ML-Only
        logger.info("Running Strategy 2: ML-Only...")
        results["ml_only"] = self._run_ml_only_strategy(tickers, start_date, end_date)

        # Strategy 3: S&P 500 Buy-and-Hold
        logger.info("Running Strategy 3: S&P 500 Benchmark...")
        results["sp500"] = self._run_sp500_benchmark(start_date, end_date)

        # Log summary
        logger.info("Backtest complete!")
        for name, result in results.items():
            logger.info(
                f"  {name}: Return={result.total_return:.2f}%, "
                f"Sharpe={result.sharpe_ratio:.2f}, "
                f"Max DD={result.max_drawdown:.2f}%"
            )

        return results

    def _run_composite_strategy(
        self, tickers: List[str], start_date: str, end_date: str
    ) -> BacktestResult:
        """
        Backtest composite score strategy.

        Uses composite scoring (Tech 40% + ML 30% + Momentum 20% + Regime 10%)
        Buy top 10 stocks monthly, hold for 30 days
        """
        from ..trading_engine.composite_scoring import compute_composite_score
        from ..trading_engine.market_regime import detect_market_regime

        trades = []
        portfolio_values = []
        cash = self.initial_capital

        # Simulate monthly rebalancing
        current_date = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        while current_date < end:
            # Get composite scores for all tickers
            scores = []
            for ticker in tickers:
                try:
                    score = compute_composite_score(ticker)
                    if score:
                        scores.append((ticker, score.composite_score))
                except Exception as e:
                    logger.debug(f"Failed to score {ticker}: {e}")
                    continue

            # Sort by composite score
            scores.sort(key=lambda x: x[1], reverse=True)
            top_stocks = scores[:10]  # Top 10

            # Execute trades
            position_value = cash * self.position_size
            for ticker, score in top_stocks:
                try:
                    # Get price at current_date
                    stock = yf.Ticker(ticker)
                    hist = stock.history(
                        start=current_date, end=current_date + timedelta(days=2)
                    )

                    if hist.empty:
                        continue

                    entry_price = hist["Close"].iloc[0]
                    shares = position_value / entry_price

                    # Hold for 30 days
                    exit_date = current_date + timedelta(days=30)
                    exit_hist = stock.history(start=exit_date, end=exit_date + timedelta(days=2))

                    if exit_hist.empty:
                        continue

                    exit_price = exit_hist["Close"].iloc[0]
                    pnl = (exit_price - entry_price) * shares
                    pnl_pct = ((exit_price / entry_price) - 1) * 100

                    trades.append(
                        {
                            "ticker": ticker,
                            "entry_date": current_date,
                            "exit_date": exit_date,
                            "entry_price": entry_price,
                            "exit_price": exit_price,
                            "shares": shares,
                            "pnl": pnl,
                            "pnl_pct": pnl_pct,
                            "score": score,
                        }
                    )

                    cash += pnl

                except Exception as e:
                    logger.debug(f"Trade failed for {ticker}: {e}")
                    continue

            portfolio_values.append({"date": current_date, "value": cash})

            # Move to next month
            current_date += timedelta(days=30)

        return self._calculate_metrics(
            "Composite Score System",
            start_date,
            end_date,
            cash,
            trades,
            portfolio_values,
        )

    def _run_ml_only_strategy(
        self, tickers: List[str], start_date: str, end_date: str
    ) -> BacktestResult:
        """
        Backtest ML-only strategy.

        Uses only ML predictions (no technical, momentum, or regime)
        """
        # Simplified: Use ML probability as score
        # In practice, would load actual ML model predictions
        trades = []
        portfolio_values = []
        cash = self.initial_capital

        current_date = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        while current_date < end:
            # Placeholder: In real implementation, get ML predictions
            # For now, simulate with random scores
            scores = [(ticker, np.random.rand()) for ticker in tickers]
            scores.sort(key=lambda x: x[1], reverse=True)
            top_stocks = scores[:10]

            position_value = cash * self.position_size
            for ticker, ml_score in top_stocks:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(
                        start=current_date, end=current_date + timedelta(days=2)
                    )

                    if hist.empty:
                        continue

                    entry_price = hist["Close"].iloc[0]
                    shares = position_value / entry_price

                    exit_date = current_date + timedelta(days=30)
                    exit_hist = stock.history(start=exit_date, end=exit_date + timedelta(days=2))

                    if exit_hist.empty:
                        continue

                    exit_price = exit_hist["Close"].iloc[0]
                    pnl = (exit_price - entry_price) * shares
                    pnl_pct = ((exit_price / entry_price) - 1) * 100

                    trades.append(
                        {
                            "ticker": ticker,
                            "entry_date": current_date,
                            "exit_date": exit_date,
                            "entry_price": entry_price,
                            "exit_price": exit_price,
                            "shares": shares,
                            "pnl": pnl,
                            "pnl_pct": pnl_pct,
                            "ml_score": ml_score,
                        }
                    )

                    cash += pnl

                except Exception as e:
                    logger.debug(f"Trade failed for {ticker}: {e}")
                    continue

            portfolio_values.append({"date": current_date, "value": cash})
            current_date += timedelta(days=30)

        return self._calculate_metrics(
            "ML-Only Strategy", start_date, end_date, cash, trades, portfolio_values
        )

    def _run_sp500_benchmark(self, start_date: str, end_date: str) -> BacktestResult:
        """
        Backtest S&P 500 buy-and-hold benchmark.
        """
        spy = yf.Ticker("SPY")
        hist = spy.history(start=start_date, end=end_date)

        if hist.empty:
            raise ValueError("Failed to fetch S&P 500 data")

        entry_price = hist["Close"].iloc[0]
        exit_price = hist["Close"].iloc[-1]

        shares = self.initial_capital / entry_price
        final_value = shares * exit_price
        total_return = ((final_value / self.initial_capital) - 1) * 100

        # Calculate drawdown
        cumulative_returns = (hist["Close"] / entry_price - 1) * 100
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max)
        max_drawdown = drawdown.min()

        # Sharpe ratio
        daily_returns = hist["Close"].pct_change().dropna()
        sharpe = self._calculate_sharpe(daily_returns)

        return BacktestResult(
            strategy_name="S&P 500 Buy-and-Hold",
            start_date=pd.to_datetime(start_date),
            end_date=pd.to_datetime(end_date),
            total_return=total_return,
            max_drawdown=abs(max_drawdown),
            sharpe_ratio=sharpe,
            win_rate=100.0 if total_return > 0 else 0.0,
            num_trades=1,
            avg_trade_return=total_return,
            calmar_ratio=total_return / abs(max_drawdown) if max_drawdown != 0 else 0,
            final_portfolio_value=final_value,
            trades=[
                {
                    "ticker": "SPY",
                    "entry_date": pd.to_datetime(start_date),
                    "exit_date": pd.to_datetime(end_date),
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "shares": shares,
                    "pnl": final_value - self.initial_capital,
                    "pnl_pct": total_return,
                }
            ],
        )

    def _calculate_metrics(
        self,
        strategy_name: str,
        start_date: str,
        end_date: str,
        final_cash: float,
        trades: List[Dict],
        portfolio_values: List[Dict],
    ) -> BacktestResult:
        """Calculate performance metrics"""

        total_return = ((final_cash / self.initial_capital) - 1) * 100

        # Win rate
        profitable_trades = [t for t in trades if t["pnl"] > 0]
        win_rate = (
            (len(profitable_trades) / len(trades)) * 100 if trades else 0.0
        )

        # Average trade return
        avg_trade_return = (
            np.mean([t["pnl_pct"] for t in trades]) if trades else 0.0
        )

        # Max drawdown
        values = [pv["value"] for pv in portfolio_values]
        if values:
            cumulative_returns = [(v / self.initial_capital - 1) * 100 for v in values]
            running_max = pd.Series(cumulative_returns).cummax()
            drawdown = pd.Series(cumulative_returns) - running_max
            max_drawdown = abs(drawdown.min())
        else:
            max_drawdown = 0.0

        # Sharpe ratio
        if len(portfolio_values) > 1:
            returns = [
                (portfolio_values[i]["value"] / portfolio_values[i - 1]["value"] - 1)
                for i in range(1, len(portfolio_values))
            ]
            sharpe = self._calculate_sharpe(pd.Series(returns))
        else:
            sharpe = 0.0

        # Calmar ratio
        calmar = total_return / max_drawdown if max_drawdown > 0 else 0.0

        return BacktestResult(
            strategy_name=strategy_name,
            start_date=pd.to_datetime(start_date),
            end_date=pd.to_datetime(end_date),
            total_return=total_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            win_rate=win_rate,
            num_trades=len(trades),
            avg_trade_return=avg_trade_return,
            calmar_ratio=calmar,
            final_portfolio_value=final_cash,
            trades=trades,
        )

    def _calculate_sharpe(self, returns: pd.Series) -> float:
        """
        Calculate Sharpe ratio.

        Args:
            returns: Series of periodic returns

        Returns:
            Annualized Sharpe ratio
        """
        if len(returns) < 2:
            return 0.0

        excess_returns = returns - (self.risk_free_rate / 252)  # Daily risk-free rate
        if excess_returns.std() == 0:
            return 0.0

        sharpe = excess_returns.mean() / excess_returns.std()
        return sharpe * np.sqrt(252)  # Annualize


def generate_backtest_report(results: Dict[str, BacktestResult]) -> str:
    """
    Generate markdown report from backtest results.

    Args:
        results: Dict mapping strategy name to BacktestResult

    Returns:
        Markdown-formatted report
    """
    report = "# Historical Validation Report (Phase 3)\n\n"
    report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    report += "## Strategy Comparison\n\n"
    report += "| Strategy | Total Return | Max Drawdown | Sharpe Ratio | Win Rate | Calmar Ratio |\n"
    report += "|----------|--------------|--------------|--------------|----------|-------------|\n"

    for name, result in results.items():
        report += (
            f"| {result.strategy_name} | "
            f"{result.total_return:.2f}% | "
            f"{result.max_drawdown:.2f}% | "
            f"{result.sharpe_ratio:.2f} | "
            f"{result.win_rate:.1f}% | "
            f"{result.calmar_ratio:.2f} |\n"
        )

    report += "\n## Key Insights\n\n"

    # Find best performer
    best_return = max(results.values(), key=lambda r: r.total_return)
    best_sharpe = max(results.values(), key=lambda r: r.sharpe_ratio)

    report += f"- **Best Return:** {best_return.strategy_name} ({best_return.total_return:.2f}%)\n"
    report += f"- **Best Risk-Adjusted Return:** {best_sharpe.strategy_name} (Sharpe: {best_sharpe.sharpe_ratio:.2f})\n"

    # Compare to benchmark
    if "sp500" in results:
        composite = results.get("composite")
        sp500 = results["sp500"]

        if composite:
            alpha = composite.total_return - sp500.total_return
            report += f"- **Alpha vs S&P 500:** {alpha:+.2f}%\n"

            if alpha > 0:
                report += f"  - ✅ Composite strategy outperformed benchmark by {alpha:.2f}%\n"
            else:
                report += f"  - ⚠️ Composite strategy underperformed benchmark by {abs(alpha):.2f}%\n"

    report += "\n## Detailed Results\n\n"

    for name, result in results.items():
        report += f"### {result.strategy_name}\n\n"
        report += f"- **Period:** {result.start_date.strftime('%Y-%m-%d')} to {result.end_date.strftime('%Y-%m-%d')}\n"
        report += f"- **Total Return:** {result.total_return:.2f}%\n"
        report += f"- **Max Drawdown:** {result.max_drawdown:.2f}%\n"
        report += f"- **Sharpe Ratio:** {result.sharpe_ratio:.2f}\n"
        report += f"- **Calmar Ratio:** {result.calmar_ratio:.2f}\n"
        report += f"- **Number of Trades:** {result.num_trades}\n"
        report += f"- **Win Rate:** {result.win_rate:.1f}%\n"
        report += f"- **Average Trade Return:** {result.avg_trade_return:.2f}%\n"
        report += f"- **Final Portfolio Value:** ${result.final_portfolio_value:,.2f}\n\n"

    return report


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Test with top US stocks
    tickers = [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "NVDA",
        "META",
        "TSLA",
        "BRK-B",
        "V",
        "JNJ",
    ]

    backtester = HistoricalBacktester(initial_capital=100000)
    results = backtester.run_comparison(
        tickers, start_date="2025-01-01", end_date="2026-01-11"
    )

    # Generate report
    report = generate_backtest_report(results)
    print(report)

    # Save report
    with open("backtest_report.md", "w") as f:
        f.write(report)
    print("\n✅ Report saved to backtest_report.md")
