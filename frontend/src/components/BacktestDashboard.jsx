import React, { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { apiClient } from "../api";
import LoadingState from "./LoadingState";
import "./BacktestDashboard.css";

/**
 * Backtest Results Dashboard
 *
 * Features:
 * - Historical backtest comparison (Composite vs ML-Only vs S&P 500)
 * - Equity curves visualization
 * - Performance metrics comparison table
 * - Strategy breakdown analysis
 * - Date range selection for backtesting
 */
function BacktestDashboard() {
  const [backtestData, setBacktestData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Form state
  const [startDate, setStartDate] = useState("2025-01-01");
  const [endDate, setEndDate] = useState("2026-01-11");
  const [initialCapital, setInitialCapital] = useState(100000);
  const [selectedTickers, setSelectedTickers] = useState([
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "TSLA",
    "NVDA",
    "META",
    "JPM",
    "V",
    "WMT",
  ]);

  // Available tickers for selection
  const popularTickers = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "TSLA",
    "NVDA",
    "META",
    "JPM",
    "V",
    "WMT",
    "PG",
    "JNJ",
    "UNH",
    "XOM",
    "BAC",
    "MA",
    "HD",
    "CVX",
    "ABBV",
    "KO",
    "PEP",
    "COST",
    "DIS",
  ];

  // Fetch backtest status on load
  useEffect(() => {
    fetchBacktestStatus();
  }, []);

  const fetchBacktestStatus = async () => {
    try {
      const response = await apiClient.get("/api/backtest/status");
      console.log("Backtest capabilities:", response.data);
    } catch (err) {
      console.error("Failed to fetch backtest status:", err);
    }
  };

  const runBacktest = async () => {
    if (selectedTickers.length === 0) {
      setError("Please select at least one ticker for backtesting");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post("/api/backtest/run", {
        tickers: selectedTickers,
        start_date: startDate,
        end_date: endDate,
        initial_capital: initialCapital,
      });

      setBacktestData(response.data);
    } catch (err) {
      console.error("Backtest failed:", err);
      setError(
        err.response?.data?.detail ||
          "Failed to run backtest. Please check your inputs and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const toggleTicker = (ticker) => {
    if (selectedTickers.includes(ticker)) {
      setSelectedTickers(selectedTickers.filter((t) => t !== ticker));
    } else {
      setSelectedTickers([...selectedTickers, ticker]);
    }
  };

  // Prepare equity curve data for Recharts
  const prepareEquityData = () => {
    if (!backtestData?.strategies) return [];

    const composite = backtestData.strategies.composite;
    const mlOnly = backtestData.strategies.ml_only;
    const sp500 = backtestData.strategies.sp500;

    if (!composite?.equity_curve) return [];

    return composite.equity_curve.map((point, idx) => ({
      date: point.date,
      Composite: point.value,
      "ML Only": mlOnly?.equity_curve?.[idx]?.value || 0,
      "S&P 500": sp500?.equity_curve?.[idx]?.value || 0,
    }));
  };

  // Format currency
  const formatCurrency = (value) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Format percentage
  const formatPercent = (value) => {
    return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
  };

  // Get metric color (green for positive, red for negative)
  const getMetricColor = (value, higherIsBetter = true) => {
    if (value === 0) return "metric-neutral";
    const isPositive = value > 0;
    if (higherIsBetter) {
      return isPositive ? "metric-positive" : "metric-negative";
    } else {
      return isPositive ? "metric-negative" : "metric-positive";
    }
  };

  return (
    <div className="backtest-dashboard">
      <div className="dashboard-header">
        <h2>📊 Historical Backtest Comparison</h2>
        <p className="subtitle">Compare strategy performance over historical periods</p>
      </div>

      {/* Configuration Panel */}
      <div className="config-panel">
        <div className="config-section">
          <h3>Backtest Configuration</h3>

          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="startDate">Start Date</label>
              <input
                id="startDate"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="endDate">End Date</label>
              <input
                id="endDate"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="initialCapital">Initial Capital ($)</label>
              <input
                id="initialCapital"
                type="number"
                value={initialCapital}
                onChange={(e) => setInitialCapital(Number(e.target.value))}
                min="1000"
                step="1000"
                disabled={loading}
              />
            </div>
          </div>

          {/* Ticker Selection */}
          <div className="ticker-selection">
            <h4>Select Stocks ({selectedTickers.length} selected)</h4>
            <div className="ticker-grid">
              {popularTickers.map((ticker) => (
                <button
                  key={ticker}
                  className={`ticker-chip ${selectedTickers.includes(ticker) ? "selected" : ""}`}
                  onClick={() => toggleTicker(ticker)}
                  disabled={loading}
                >
                  {ticker}
                </button>
              ))}
            </div>
          </div>

          <button
            className="run-backtest-btn"
            onClick={runBacktest}
            disabled={loading || selectedTickers.length === 0}
          >
            {loading ? "Running Backtest..." : "🚀 Run Backtest"}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && <LoadingState message="Running historical backtest..." />}

      {/* Results Display */}
      {backtestData && !loading && (
        <div className="results-container">
          {/* Period Summary */}
          <div className="period-summary">
            <h3>Backtest Period</h3>
            <div className="period-info">
              <div className="period-item">
                <span className="label">Start Date:</span>
                <span className="value">{backtestData.backtest_period.start_date}</span>
              </div>
              <div className="period-item">
                <span className="label">End Date:</span>
                <span className="value">{backtestData.backtest_period.end_date}</span>
              </div>
              <div className="period-item">
                <span className="label">Duration:</span>
                <span className="value">{backtestData.backtest_period.duration_days} days</span>
              </div>
            </div>
          </div>

          {/* Equity Curve Chart */}
          <div className="chart-container">
            <h3>Portfolio Value Over Time</h3>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={prepareEquityData()}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="date" stroke="#999" tick={{ fill: "#999" }} />
                <YAxis
                  stroke="#999"
                  tick={{ fill: "#999" }}
                  tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1a1a1a",
                    border: "1px solid #333",
                    borderRadius: "8px",
                  }}
                  formatter={(value) => formatCurrency(value)}
                  labelStyle={{ color: "#fff" }}
                />
                <Legend wrapperStyle={{ color: "#999" }} />
                <Line
                  type="monotone"
                  dataKey="Composite"
                  stroke="#00d4aa"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{ r: 5 }}
                />
                <Line
                  type="monotone"
                  dataKey="ML Only"
                  stroke="#ffd700"
                  strokeWidth={2}
                  dot={false}
                  strokeDasharray="5 5"
                />
                <Line type="monotone" dataKey="S&P 500" stroke="#999" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Performance Metrics Table */}
          <div className="metrics-table-container">
            <h3>Performance Comparison</h3>
            <table className="metrics-table">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>Composite Strategy</th>
                  <th>ML Only</th>
                  <th>S&P 500 Benchmark</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Total Return</td>
                  <td
                    className={getMetricColor(
                      backtestData.strategies.composite.metrics.total_return
                    )}
                  >
                    {formatPercent(backtestData.strategies.composite.metrics.total_return)}
                  </td>
                  <td
                    className={getMetricColor(backtestData.strategies.ml_only.metrics.total_return)}
                  >
                    {formatPercent(backtestData.strategies.ml_only.metrics.total_return)}
                  </td>
                  <td
                    className={getMetricColor(backtestData.strategies.sp500.metrics.total_return)}
                  >
                    {formatPercent(backtestData.strategies.sp500.metrics.total_return)}
                  </td>
                </tr>
                <tr>
                  <td>Max Drawdown</td>
                  <td
                    className={getMetricColor(
                      backtestData.strategies.composite.metrics.max_drawdown,
                      false
                    )}
                  >
                    {formatPercent(backtestData.strategies.composite.metrics.max_drawdown)}
                  </td>
                  <td
                    className={getMetricColor(
                      backtestData.strategies.ml_only.metrics.max_drawdown,
                      false
                    )}
                  >
                    {formatPercent(backtestData.strategies.ml_only.metrics.max_drawdown)}
                  </td>
                  <td
                    className={getMetricColor(
                      backtestData.strategies.sp500.metrics.max_drawdown,
                      false
                    )}
                  >
                    {formatPercent(backtestData.strategies.sp500.metrics.max_drawdown)}
                  </td>
                </tr>
                <tr>
                  <td>Sharpe Ratio</td>
                  <td
                    className={getMetricColor(
                      backtestData.strategies.composite.metrics.sharpe_ratio
                    )}
                  >
                    {backtestData.strategies.composite.metrics.sharpe_ratio.toFixed(2)}
                  </td>
                  <td
                    className={getMetricColor(backtestData.strategies.ml_only.metrics.sharpe_ratio)}
                  >
                    {backtestData.strategies.ml_only.metrics.sharpe_ratio.toFixed(2)}
                  </td>
                  <td
                    className={getMetricColor(backtestData.strategies.sp500.metrics.sharpe_ratio)}
                  >
                    {backtestData.strategies.sp500.metrics.sharpe_ratio.toFixed(2)}
                  </td>
                </tr>
                <tr>
                  <td>Win Rate</td>
                  <td
                    className={getMetricColor(backtestData.strategies.composite.metrics.win_rate)}
                  >
                    {formatPercent(backtestData.strategies.composite.metrics.win_rate)}
                  </td>
                  <td className={getMetricColor(backtestData.strategies.ml_only.metrics.win_rate)}>
                    {formatPercent(backtestData.strategies.ml_only.metrics.win_rate)}
                  </td>
                  <td className={getMetricColor(backtestData.strategies.sp500.metrics.win_rate)}>
                    {formatPercent(backtestData.strategies.sp500.metrics.win_rate)}
                  </td>
                </tr>
                <tr>
                  <td>Calmar Ratio</td>
                  <td
                    className={getMetricColor(
                      backtestData.strategies.composite.metrics.calmar_ratio
                    )}
                  >
                    {backtestData.strategies.composite.metrics.calmar_ratio.toFixed(2)}
                  </td>
                  <td
                    className={getMetricColor(backtestData.strategies.ml_only.metrics.calmar_ratio)}
                  >
                    {backtestData.strategies.ml_only.metrics.calmar_ratio.toFixed(2)}
                  </td>
                  <td
                    className={getMetricColor(backtestData.strategies.sp500.metrics.calmar_ratio)}
                  >
                    {backtestData.strategies.sp500.metrics.calmar_ratio.toFixed(2)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Alpha vs Benchmark */}
          {backtestData.comparison && (
            <div className="comparison-section">
              <h3>Alpha vs Benchmark</h3>
              <div className="comparison-cards">
                <div className="comparison-card">
                  <div className="card-header">
                    <span className="card-icon">🏆</span>
                    <h4>Best Strategy (Return)</h4>
                  </div>
                  <div className="card-content">
                    <div className="winner-name">
                      {backtestData.comparison.winner_by_return.strategy}
                    </div>
                    <div
                      className={`winner-value ${getMetricColor(backtestData.comparison.winner_by_return.return)}`}
                    >
                      {formatPercent(backtestData.comparison.winner_by_return.return)}
                    </div>
                  </div>
                </div>

                <div className="comparison-card">
                  <div className="card-header">
                    <span className="card-icon">📈</span>
                    <h4>Alpha vs S&P 500</h4>
                  </div>
                  <div className="card-content">
                    <div
                      className={`alpha-value ${getMetricColor(backtestData.comparison.alpha_vs_benchmark.alpha)}`}
                    >
                      {formatPercent(backtestData.comparison.alpha_vs_benchmark.alpha)}
                    </div>
                    <div className="alpha-interpretation">
                      {backtestData.comparison.alpha_vs_benchmark.interpretation}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Strategy Breakdown */}
          <div className="strategy-breakdown">
            <h3>Strategy Details</h3>
            <div className="strategy-cards">
              {Object.entries(backtestData.strategies).map(([strategyName, strategyData]) => (
                <div key={strategyName} className="strategy-card">
                  <h4>{strategyName.replace(/_/g, " ").toUpperCase()}</h4>
                  <div className="strategy-metrics">
                    <div className="metric-item">
                      <span className="metric-label">Return:</span>
                      <span className={getMetricColor(strategyData.metrics.total_return)}>
                        {formatPercent(strategyData.metrics.total_return)}
                      </span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Sharpe:</span>
                      <span>{strategyData.metrics.sharpe_ratio.toFixed(2)}</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Drawdown:</span>
                      <span className={getMetricColor(strategyData.metrics.max_drawdown, false)}>
                        {formatPercent(strategyData.metrics.max_drawdown)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Disclaimer */}
          <div className="backtest-disclaimer">
            <h4>⚠️ Important Disclaimer</h4>
            <p>
              Past performance is not indicative of future results. Backtests are based on
              historical data and may not reflect actual trading conditions. Use these results for
              educational purposes only. Always conduct your own research before making investment
              decisions.
            </p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!backtestData && !loading && !error && (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h3>No Backtest Results Yet</h3>
          <p>
            Configure the settings above and click "Run Backtest" to compare strategy performance
            over historical periods.
          </p>
        </div>
      )}
    </div>
  );
}

export default BacktestDashboard;
