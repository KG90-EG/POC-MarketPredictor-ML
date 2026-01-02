import { useState, useEffect } from 'react';
import { apiClient } from '../api';
import ConfirmDialog from './ConfirmDialog';
import './SimulationDashboardV2.css';

/**
 * Modern Trading Simulation Dashboard - V2
 *
 * Features:
 * - Card-based design (aligned with WatchlistManagerV2)
 * - No language selector (handled at app level)
 * - AI Recommendations prominent
 * - Quick trade form with autocomplete
 * - Portfolio holdings as cards
 * - Simplified, user-friendly interface
 */
function SimulationDashboardV2() {
  const [currentSim, setCurrentSim] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [tradeHistory, setTradeHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showHistory, setShowHistory] = useState(false);

  // Form states
  const [newSimCapital, setNewSimCapital] = useState(10000);
  const [tradeForm, setTradeForm] = useState({
    ticker: '',
    action: 'BUY',
    quantity: 10,
    price: 0
  });
  const [resetConfirm, setResetConfirm] = useState(false);

  // Popular stocks for autocomplete
  const popularStocks = [
    { ticker: 'AAPL', name: 'Apple Inc.' },
    { ticker: 'MSFT', name: 'Microsoft' },
    { ticker: 'GOOGL', name: 'Alphabet' },
    { ticker: 'AMZN', name: 'Amazon' },
    { ticker: 'TSLA', name: 'Tesla' },
    { ticker: 'NVDA', name: 'NVIDIA' },
    { ticker: 'META', name: 'Meta' },
    { ticker: 'GC=F', name: 'Gold' },
    { ticker: 'SI=F', name: 'Silver' },
    { ticker: 'CL=F', name: 'Oil' },
  ];

  useEffect(() => {
    if (currentSim) {
      loadPortfolio();
      loadTradeHistory();
    }
  }, [currentSim]);

  const loadPortfolio = async () => {
    if (!currentSim) return;
    try {
      const response = await apiClient.get(`/api/simulations/${currentSim.simulation_id}/portfolio`);
      setPortfolio(response.data);
    } catch (err) {
      console.error('Error loading portfolio:', err);
    }
  };

  const loadTradeHistory = async () => {
    if (!currentSim) return;
    try {
      const response = await apiClient.get(`/api/simulations/${currentSim.simulation_id}/history`);
      setTradeHistory(response.data.trades || []);
    } catch (err) {
      console.error('Error loading trade history:', err);
    }
  };

  const loadRecommendations = async () => {
    if (!currentSim) {
      setError('No simulation loaded');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      console.log('Loading recommendations for sim:', currentSim.simulation_id);
      const response = await apiClient.post(`/api/simulations/${currentSim.simulation_id}/recommendations`);
      console.log('Recommendations response:', response.data);

      if (response.data.recommendations && response.data.recommendations.length > 0) {
        setRecommendations(response.data.recommendations);
        setError(`✓ Loaded ${response.data.recommendations.length} recommendations`);
      } else {
        setRecommendations([]);
        setError('No recommendations available at this time');
      }
    } catch (err) {
      console.error('Recommendations error:', err);
      setError('Failed to load recommendations: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const createSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post('/api/simulations', {
        user_id: 'default_user',
        initial_capital: newSimCapital,
        mode: 'auto'
      });
      setCurrentSim(response.data);
      setNewSimCapital(10000);
    } catch (err) {
      setError('Failed to create simulation: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const executeTrade = async (ticker, action, quantity, price, reason = '', confidence = 0) => {
    if (!currentSim) return;

    setLoading(true);
    setError(null);

    try {
      await apiClient.post(`/api/simulations/${currentSim.simulation_id}/trade`, {
        ticker,
        action,
        quantity,
        price,
        reason,
        confidence
      });

      await Promise.all([loadPortfolio(), loadTradeHistory()]);
      setError(null);
    } catch (err) {
      setError('Trade failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleManualTrade = async (e) => {
    e.preventDefault();
    const { ticker, action, quantity, price } = tradeForm;

    if (!ticker || price <= 0 || quantity <= 0) {
      setError('Please fill all trade fields');
      return;
    }

    await executeTrade(ticker, action, quantity, price, 'Manual trade', 0);

    // Reset form
    setTradeForm({
      ticker: '',
      action: 'BUY',
      quantity: 10,
      price: 0
    });
  };

  const executeRecommendation = async (rec) => {
    const price = rec.price ?? rec.current_price ?? 0;
    const quantity = rec.quantity ?? 10;

    if (!price) {
      setError('Price not available for recommendation');
      return;
    }

    await executeTrade(
      rec.ticker,
      rec.action,
      quantity,
      price,
      rec.reason,
      rec.confidence
    );
  };

  const executeAutoTrade = async () => {
    if (!currentSim) return;
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post(`/api/simulations/${currentSim.simulation_id}/auto-trade`);
      await Promise.all([loadPortfolio(), loadTradeHistory()]);

      const { trades_executed, trades } = response.data;
      if (trades_executed > 0) {
        const summary = trades.map(t => `${t.action} ${t.quantity} ${t.ticker}`).join(', ');
        setError(`✓ ${trades_executed} trades executed: ${summary}`);
      } else {
        setError('No trades recommended at this time');
      }
    } catch (err) {
      setError('Auto trade failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const resetSimulation = async () => {
    if (!currentSim) return;

    setLoading(true);
    try {
      await apiClient.post(`/api/simulations/${currentSim.simulation_id}/reset`);
      await Promise.all([loadPortfolio(), loadTradeHistory()]);
      setResetConfirm(false);
      setError('✓ Simulation reset successfully');
    } catch (err) {
      setError('Reset failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  const formatTimestamp = (value) => {
    return new Date(value).toLocaleString('en-US');
  };

  return (
    <div className="simulation-dashboard-v2">
      {error && (
        <div className={`error-banner ${error.includes('✓') ? 'success' : ''}`}>
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {!currentSim ? (
        // No simulation - show creation form
        <div className="create-simulation-section">
          <div className="card welcome-card">
            <h2>📊 Trading Practice Simulator</h2>
            <p>Start a virtual trading simulation with AI-powered recommendations</p>

            <div className="form-group">
              <label>Initial Capital</label>
              <input
                type="number"
                value={newSimCapital}
                onChange={(e) => setNewSimCapital(Number(e.target.value))}
                min="1000"
                max="1000000"
                step="1000"
              />
              <small>{formatCurrency(newSimCapital)}</small>
            </div>

            <button
              onClick={createSimulation}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Creating...' : '🚀 Start Simulation'}
            </button>
          </div>

          <div className="info-card">
            <h3>Features</h3>
            <ul>
              <li>✓ Virtual trading with real market data</li>
              <li>✓ AI-powered trade recommendations</li>
              <li>✓ Real-time portfolio tracking</li>
              <li>✓ Performance analytics</li>
              <li>✓ Risk-free practice environment</li>
            </ul>
          </div>
        </div>
      ) : (
        // Simulation loaded - show dashboard
        <div className="simulation-content">
          {/* Header with Metrics */}
          <div className="section-header">
            <h2>📊 Trading Simulation</h2>
            <div className="header-actions">
              <button onClick={loadPortfolio} className="btn-icon" title="Refresh">
                🔄
              </button>
              <button onClick={() => setResetConfirm(true)} className="btn-danger-small" title="Reset">
                Reset
              </button>
            </div>
          </div>

          {/* Metric Cards */}
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-icon">💰</div>
              <div className="metric-content">
                <div className="metric-label">Portfolio Value</div>
                <div className="metric-value">
                  {portfolio ? formatCurrency(portfolio.total_value) : '...'}
                </div>
                {portfolio && (
                  <div className={`metric-change ${portfolio.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                    {formatPercent(portfolio.total_pnl_percent)}
                  </div>
                )}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">💵</div>
              <div className="metric-content">
                <div className="metric-label">Cash Available</div>
                <div className="metric-value">
                  {portfolio ? formatCurrency(portfolio.cash) : '...'}
                </div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">📈</div>
              <div className="metric-content">
                <div className="metric-label">Positions</div>
                <div className="metric-value">
                  {portfolio ? portfolio.positions.length : 0}
                </div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">🎯</div>
              <div className="metric-content">
                <div className="metric-label">Win Rate</div>
                <div className="metric-value">
                  {currentSim?.metrics?.win_rate_percent
                    ? `${currentSim.metrics.win_rate_percent.toFixed(1)}%`
                    : 'N/A'}
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Grid */}
          <div className="main-content-grid">
            {/* AI Recommendations Section */}
            <div className="recommendations-section">
              <div className="card">
                <div className="card-header">
                  <h3>🤖 AI Recommendations</h3>
                  <button
                    onClick={loadRecommendations}
                    disabled={loading}
                    className="btn-secondary-small"
                  >
                    {loading ? 'Loading...' : 'Get Recommendations'}
                  </button>
                </div>

                {recommendations.length > 0 ? (
                  <div className="recommendations-list">
                    {recommendations.map((rec, idx) => (
                      <div key={idx} className={`rec-card ${rec.action.toLowerCase()}`}>
                        <div className="rec-header">
                          <span className="rec-action-badge">{rec.action}</span>
                          <span className="rec-ticker">{rec.ticker}</span>
                          <span className="rec-confidence">
                            {(rec.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="rec-reason">{rec.reason}</div>
                        <button
                          onClick={() => executeRecommendation(rec)}
                          className="btn-execute"
                          disabled={loading}
                        >
                          Execute
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={executeAutoTrade}
                      disabled={loading}
                      className="btn-auto-trade"
                    >
                      {loading ? 'Executing...' : '⚡ Execute All'}
                    </button>
                  </div>
                ) : (
                  <div className="empty-state-small">
                    <p>Click "Get Recommendations" to see AI suggestions</p>
                  </div>
                )}
              </div>
            </div>

            {/* Quick Trade Section */}
            <div className="trade-section">
              <div className="card">
                <h3>⚡ Quick Trade</h3>
                <form onSubmit={handleManualTrade}>
                  <div className="form-row">
                    <div className="form-group">
                      <label>Ticker</label>
                      <input
                        type="text"
                        list="ticker-suggestions"
                        value={tradeForm.ticker}
                        onChange={(e) => setTradeForm({...tradeForm, ticker: e.target.value.toUpperCase()})}
                        placeholder="AAPL, GOLD..."
                        required
                      />
                      <datalist id="ticker-suggestions">
                        {popularStocks.map(stock => (
                          <option key={stock.ticker} value={stock.ticker}>
                            {stock.name}
                          </option>
                        ))}
                      </datalist>
                    </div>

                    <div className="form-group">
                      <label>Action</label>
                      <select
                        value={tradeForm.action}
                        onChange={(e) => setTradeForm({...tradeForm, action: e.target.value})}
                      >
                        <option value="BUY">BUY</option>
                        <option value="SELL">SELL</option>
                      </select>
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Quantity</label>
                      <input
                        type="number"
                        value={tradeForm.quantity}
                        onChange={(e) => setTradeForm({...tradeForm, quantity: Number(e.target.value)})}
                        min="1"
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label>Price</label>
                      <input
                        type="number"
                        value={tradeForm.price}
                        onChange={(e) => setTradeForm({...tradeForm, price: Number(e.target.value)})}
                        min="0.01"
                        step="0.01"
                        required
                      />
                    </div>
                  </div>

                  <button type="submit" disabled={loading} className="btn-primary">
                    {loading ? 'Executing...' : 'Execute Trade'}
                  </button>
                </form>
              </div>
            </div>
          </div>

          {/* Portfolio Holdings */}
          <div className="holdings-section">
            <div className="card">
              <h3>📈 Portfolio Holdings</h3>
              {portfolio && portfolio.positions.length > 0 ? (
                <div className="holdings-grid">
                  {portfolio.positions.map((pos) => (
                    <div key={pos.ticker} className="holding-card">
                      <div className="holding-header">
                        <h4>{pos.ticker}</h4>
                        <div className={`pnl-badge ${pos.pnl >= 0 ? 'positive' : 'negative'}`}>
                          {formatPercent(pos.pnl_percent)}
                        </div>
                      </div>
                      <div className="holding-details">
                        <div className="detail-row">
                          <span>Quantity:</span>
                          <strong>{pos.quantity}</strong>
                        </div>
                        <div className="detail-row">
                          <span>Avg Cost:</span>
                          <strong>{formatCurrency(pos.avg_cost)}</strong>
                        </div>
                        <div className="detail-row">
                          <span>Current:</span>
                          <strong>{formatCurrency(pos.current_price)}</strong>
                        </div>
                        <div className="detail-row">
                          <span>Value:</span>
                          <strong>{formatCurrency(pos.value)}</strong>
                        </div>
                        <div className="detail-row">
                          <span>P&L:</span>
                          <strong className={pos.pnl >= 0 ? 'positive' : 'negative'}>
                            {formatCurrency(pos.pnl)}
                          </strong>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state-small">
                  <p>No positions yet. Execute your first trade above!</p>
                </div>
              )}
            </div>
          </div>

          {/* Trade History (Collapsible) */}
          <div className="history-section">
            <div className="card">
              <div className="card-header clickable" onClick={() => setShowHistory(!showHistory)}>
                <h3>📜 Trade History ({tradeHistory.length})</h3>
                <span>{showHistory ? '▼' : '▶'}</span>
              </div>

              {showHistory && tradeHistory.length > 0 && (
                <div className="history-list">
                  {tradeHistory.slice(0, 20).map((trade, idx) => (
                    <div key={idx} className={`history-item ${trade.action.toLowerCase()}`}>
                      <div className="history-main">
                        <span className="history-action">{trade.action}</span>
                        <span className="history-ticker">{trade.ticker}</span>
                        <span className="history-qty">×{trade.quantity}</span>
                        <span className="history-price">@{formatCurrency(trade.price)}</span>
                      </div>
                      <div className="history-meta">
                        <span className="history-time">{formatTimestamp(trade.timestamp)}</span>
                        {trade.reason && <span className="history-reason">{trade.reason}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Reset Confirmation Dialog */}
      <ConfirmDialog
        isOpen={resetConfirm}
        title="Reset Simulation?"
        message="This will delete all trades and reset your portfolio to initial capital. This action cannot be undone."
        confirmText="Reset"
        cancelText="Cancel"
        confirmType="danger"
        onConfirm={resetSimulation}
        onCancel={() => setResetConfirm(false)}
      />
    </div>
  );
}

export default SimulationDashboardV2;
