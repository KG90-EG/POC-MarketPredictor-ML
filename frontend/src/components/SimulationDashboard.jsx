import { useState, useEffect } from 'react';
import { apiClient } from '../api';
import './SimulationDashboard.css';

/**
 * Trading Simulation Dashboard
 *
 * Features:
 * - Create/load simulations with virtual capital
 * - View portfolio holdings and P&L
 * - Get AI trading recommendations
 * - Execute trades manually or automatically
 * - Track performance metrics
 */

function SimulationDashboard() {
  const [simulations, setSimulations] = useState([]);
  const [currentSim, setCurrentSim] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [tradeHistory, setTradeHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Form states
  const [newSimCapital, setNewSimCapital] = useState(10000);
  const [tradeForm, setTradeForm] = useState({
    ticker: '',
    action: 'BUY',
    quantity: 10,
    price: 0
  });

  // Load simulations on mount
  useEffect(() => {
    loadUserSimulations();
  }, []);

  // Load portfolio when simulation changes
  useEffect(() => {
    if (currentSim) {
      loadPortfolio();
      loadTradeHistory();
    }
  }, [currentSim]);

  const loadUserSimulations = async () => {
    try {
      // Note: In production, use actual user_id from auth
      const userId = 'default_user';
      // This endpoint doesn't exist yet, we'll load individual sim for now
      if (currentSim) {
        await loadSimulation(currentSim.simulation_id);
      }
    } catch (err) {
      console.error('Error loading simulations:', err);
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

      const newSim = response.data;
      setCurrentSim(newSim);
      setNewSimCapital(10000); // Reset form

      // Show success message
      alert(`Simulation #${newSim.simulation_id} erstellt mit $${newSim.initial_capital.toLocaleString()}`);
    } catch (err) {
      setError('Fehler beim Erstellen der Simulation: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadSimulation = async (simId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get(`/api/simulations/${simId}`);
      setCurrentSim(response.data);
    } catch (err) {
      setError('Fehler beim Laden der Simulation: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadPortfolio = async () => {
    if (!currentSim) return;

    try {
      const response = await apiClient.get(`/api/simulations/${currentSim.simulation_id}/portfolio`);
      setPortfolio(response.data);
    } catch (err) {
      console.error('Error loading portfolio:', err);
      setError('Fehler beim Laden des Portfolios');
    }
  };

  const loadRecommendations = async () => {
    if (!currentSim) return;

    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post(`/api/simulations/${currentSim.simulation_id}/recommendations`);
      setRecommendations(response.data.recommendations || []);
    } catch (err) {
      setError('Fehler beim Laden der Empfehlungen: ' + err.message);
    } finally {
      setLoading(false);
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

  const executeTrade = async (ticker, action, quantity, price, reason, mlConfidence = null) => {
    if (!currentSim) return;

    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post(
        `/api/simulations/${currentSim.simulation_id}/trades`,
        {
          ticker,
          action,
          quantity,
          price,
          reason,
          ml_confidence: mlConfidence
        }
      );

      // Refresh portfolio and history
      await loadPortfolio();
      await loadTradeHistory();
      await loadSimulation(currentSim.simulation_id);

      alert(`✓ ${action} ${quantity} ${ticker} @ $${price.toFixed(2)}`);
    } catch (err) {
      setError(`Fehler beim Trade: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleManualTrade = async (e) => {
    e.preventDefault();
    await executeTrade(
      tradeForm.ticker.toUpperCase(),
      tradeForm.action,
      tradeForm.quantity,
      tradeForm.price,
      'Manual trade'
    );

    // Reset form
    setTradeForm({ ticker: '', action: 'BUY', quantity: 10, price: 0 });
  };

  const executeRecommendation = async (rec) => {
    if (!confirm(`${rec.action} ${rec.ticker}?\nConfidence: ${(rec.confidence * 100).toFixed(1)}%\nReason: ${rec.reason}`)) {
      return;
    }

    // Get current price (simplified - in production, fetch real-time price)
    const quantity = 10; // Default quantity
    const price = 100; // TODO: Fetch real price

    await executeTrade(
      rec.ticker,
      rec.action,
      quantity,
      price,
      rec.reason,
      rec.confidence
    );
  };

  const resetSimulation = async () => {
    if (!currentSim) return;
    if (!confirm('Simulation zurücksetzen? Alle Trades werden gelöscht.')) return;

    setLoading(true);
    try {
      await apiClient.post(`/api/simulations/${currentSim.simulation_id}/reset`);
      await loadSimulation(currentSim.simulation_id);
      await loadPortfolio();
      await loadTradeHistory();
      alert('✓ Simulation zurückgesetzt');
    } catch (err) {
      setError('Fehler beim Zurücksetzen: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Helper functions
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

  return (
    <div className="simulation-dashboard">
      <div className="dashboard-header">
        <h2>📊 Trading Simulation</h2>
        <p className="subtitle">Test ML predictions with virtual capital</p>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {!currentSim ? (
        // No simulation - show creation form
        <div className="create-simulation">
          <div className="card">
            <h3>Neue Simulation erstellen</h3>
            <p>Starte eine virtuelle Trading-Simulation mit ML-basierten Empfehlungen</p>

            <div className="form-group">
              <label>Startkapital</label>
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
              className="btn btn-primary"
            >
              {loading ? 'Erstelle...' : 'Simulation starten'}
            </button>
          </div>

          <div className="info-card">
            <h4>Features</h4>
            <ul>
              <li>✓ KI-basierte Kauf/Verkauf Empfehlungen</li>
              <li>✓ Automatisches Portfolio-Management</li>
              <li>✓ Stop-Loss & Take-Profit Strategien</li>
              <li>✓ Performance Tracking & Metriken</li>
              <li>✓ Trade History & Begründungen</li>
            </ul>
          </div>
        </div>
      ) : (
        // Simulation loaded - show dashboard
        <div className="simulation-content">
          {/* Summary Cards */}
          <div className="summary-cards">
            <div className="card metric-card">
              <div className="metric-label">Portfolio Wert</div>
              <div className="metric-value">
                {portfolio ? formatCurrency(portfolio.total_value) : '...'}
              </div>
              {portfolio && (
                <div className={`metric-change ${portfolio.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                  {formatPercent(portfolio.total_pnl_percent)}
                </div>
              )}
            </div>

            <div className="card metric-card">
              <div className="metric-label">Cash</div>
              <div className="metric-value">
                {portfolio ? formatCurrency(portfolio.cash) : '...'}
              </div>
            </div>

            <div className="card metric-card">
              <div className="metric-label">Positionen</div>
              <div className="metric-value">
                {portfolio ? portfolio.positions.length : 0}
              </div>
            </div>

            <div className="card metric-card">
              <div className="metric-label">Win Rate</div>
              <div className="metric-value">
                {currentSim?.metrics?.win_rate_percent
                  ? `${currentSim.metrics.win_rate_percent.toFixed(1)}%`
                  : 'N/A'}
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="tabs">
            <button
              className={activeTab === 'overview' ? 'active' : ''}
              onClick={() => setActiveTab('overview')}
            >
              Übersicht
            </button>
            <button
              className={activeTab === 'recommendations' ? 'active' : ''}
              onClick={() => setActiveTab('recommendations')}
            >
              AI Empfehlungen
            </button>
            <button
              className={activeTab === 'trade' ? 'active' : ''}
              onClick={() => setActiveTab('trade')}
            >
              Trade
            </button>
            <button
              className={activeTab === 'history' ? 'active' : ''}
              onClick={() => setActiveTab('history')}
            >
              History
            </button>
          </div>

          {/* Tab Content */}
          <div className="tab-content">
            {activeTab === 'overview' && (
              <div className="overview-tab">
                <div className="card">
                  <h3>Portfolio Holdings</h3>
                  {portfolio && portfolio.positions.length > 0 ? (
                    <table className="holdings-table">
                      <thead>
                        <tr>
                          <th>Ticker</th>
                          <th>Quantity</th>
                          <th>Avg Cost</th>
                          <th>Current Price</th>
                          <th>Value</th>
                          <th>P&L</th>
                          <th>P&L %</th>
                        </tr>
                      </thead>
                      <tbody>
                        {portfolio.positions.map((pos) => (
                          <tr key={pos.ticker}>
                            <td className="ticker">{pos.ticker}</td>
                            <td>{pos.quantity}</td>
                            <td>{formatCurrency(pos.avg_cost)}</td>
                            <td>{formatCurrency(pos.current_price)}</td>
                            <td>{formatCurrency(pos.value)}</td>
                            <td className={pos.pnl >= 0 ? 'positive' : 'negative'}>
                              {formatCurrency(pos.pnl)}
                            </td>
                            <td className={pos.pnl_percent >= 0 ? 'positive' : 'negative'}>
                              {formatPercent(pos.pnl_percent)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="empty-state">
                      <p>Keine Positionen vorhanden</p>
                      <small>Erstelle Trades über AI Empfehlungen oder manuell</small>
                    </div>
                  )}
                </div>

                <div className="actions">
                  <button onClick={loadPortfolio} className="btn btn-secondary">
                    🔄 Aktualisieren
                  </button>
                  <button onClick={resetSimulation} className="btn btn-danger">
                    Reset Simulation
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'recommendations' && (
              <div className="recommendations-tab">
                <div className="card">
                  <div className="card-header">
                    <h3>AI Trading Empfehlungen</h3>
                    <button
                      onClick={loadRecommendations}
                      disabled={loading}
                      className="btn btn-secondary"
                    >
                      {loading ? 'Lade...' : '🤖 Empfehlungen laden'}
                    </button>
                  </div>

                  {recommendations.length > 0 ? (
                    <div className="recommendations-list">
                      {recommendations.map((rec, idx) => (
                        <div
                          key={idx}
                          className={`recommendation-card ${rec.action.toLowerCase()}`}
                        >
                          <div className="rec-header">
                            <span className="rec-action">{rec.action}</span>
                            <span className="rec-ticker">{rec.ticker}</span>
                            <span className="rec-confidence">
                              {(rec.confidence * 100).toFixed(1)}% confidence
                            </span>
                          </div>
                          <div className="rec-reason">{rec.reason}</div>
                          <button
                            onClick={() => executeRecommendation(rec)}
                            className="btn btn-sm"
                            disabled={loading}
                          >
                            Execute
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state">
                      <p>Keine Empfehlungen verfügbar</p>
                      <small>Klicke auf "Empfehlungen laden" um AI-Signale zu erhalten</small>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'trade' && (
              <div className="trade-tab">
                <div className="card">
                  <h3>Manueller Trade</h3>
                  <form onSubmit={handleManualTrade}>
                    <div className="form-row">
                      <div className="form-group">
                        <label>Ticker</label>
                        <input
                          type="text"
                          value={tradeForm.ticker}
                          onChange={(e) => setTradeForm({...tradeForm, ticker: e.target.value})}
                          placeholder="AAPL"
                          required
                        />
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

                    <button
                      type="submit"
                      disabled={loading}
                      className="btn btn-primary"
                    >
                      {loading ? 'Executing...' : 'Execute Trade'}
                    </button>
                  </form>
                </div>
              </div>
            )}

            {activeTab === 'history' && (
              <div className="history-tab">
                <div className="card">
                  <h3>Trade History</h3>
                  {tradeHistory.length > 0 ? (
                    <table className="history-table">
                      <thead>
                        <tr>
                          <th>Zeit</th>
                          <th>Action</th>
                          <th>Ticker</th>
                          <th>Quantity</th>
                          <th>Price</th>
                          <th>Confidence</th>
                          <th>Reason</th>
                        </tr>
                      </thead>
                      <tbody>
                        {tradeHistory.map((trade, idx) => (
                          <tr key={idx}>
                            <td>{new Date(trade.timestamp).toLocaleString()}</td>
                            <td className={trade.action === 'BUY' ? 'buy' : 'sell'}>
                              {trade.action}
                            </td>
                            <td className="ticker">{trade.ticker}</td>
                            <td>{trade.quantity}</td>
                            <td>{formatCurrency(trade.price)}</td>
                            <td>
                              {trade.ml_confidence
                                ? `${(trade.ml_confidence * 100).toFixed(1)}%`
                                : '-'}
                            </td>
                            <td className="reason">{trade.reason}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="empty-state">
                      <p>Keine Trades vorhanden</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default SimulationDashboard;
