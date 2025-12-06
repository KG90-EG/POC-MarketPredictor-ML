import { useState, useEffect } from 'react';
import { apiClient } from '../api';
import { translations, getTranslation } from '../translations';
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
  const [language, setLanguage] = useState(localStorage.getItem('app_language') || 'de');

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
      alert(`${t('simulationCreated')} #${newSim.simulation_id}: $${newSim.initial_capital.toLocaleString()}`);
    } catch (err) {
      setError(t('errorCreating') + ': ' + err.message);
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
      setError(t('errorLoading') + ': ' + err.message);
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
      setError(t('errorPortfolio'));
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
      setError(t('errorRecommendations') + ': ' + err.message);
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

      alert(`✓ ${t('tradeSuccess')}: ${action} ${quantity} ${ticker} @ $${price.toFixed(2)}`);
    } catch (err) {
      setError(`${t('errorTrade')}: ${err.response?.data?.detail || err.message}`);
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

  const executeAutoTrade = async () => {
    if (!currentSim) return;

    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post(
        `/api/simulations/${currentSim.simulation_id}/auto-trade`,
        { max_trades: 3 }
      );

      // Refresh all data
      await loadPortfolio();
      await loadTradeHistory();
      await loadSimulation(currentSim.simulation_id);

      const { trades_executed, trades } = response.data;
      if (trades_executed > 0) {
        const summary = trades.map(trade => `${trade.action} ${trade.quantity} ${trade.ticker}`).join(', ');
        alert(`✓ ${trades_executed} ${t('tradesExecuted')}:\n${summary}`);
      } else {
        alert(t('noTradesRecommended'));
      }
    } catch (err) {
      setError(`${t('errorAutoTrade')}: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
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
  const t = (key) => getTranslation(language, key);
  
  const changeLanguage = (lang) => {
    setLanguage(lang);
    localStorage.setItem('app_language', lang);
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

  return (
    <div className="simulation-dashboard">
      <div className="dashboard-header">
        <h2>📊 Trading Simulation</h2>
        <div className="header-controls">
          <div className="language-selector">
            <label>{t('language')}: </label>
            <select value={language} onChange={(e) => changeLanguage(e.target.value)}>
              <option value="de">🇩🇪 DE</option>
              <option value="en">🇬🇧 EN</option>
              <option value="it">🇮🇹 IT</option>
              <option value="es">🇪🇸 ES</option>
            </select>
          </div>
        </div>
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
            <p>Start a virtual trading simulation with ML-based recommendations</p>

            <div className="form-group">
              <label>{t('initialCapital')}</label>
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
              {loading ? t('creating') : t('startSimulation')}
            </button>
          </div>

          <div className="info-card">
            <h4>{t('features')}</h4>
            <ul>
              <li>✓ {t('feature1')}</li>
              <li>✓ {t('feature2')}</li>
              <li>✓ {t('feature3')}</li>
              <li>✓ {t('feature4')}</li>
              <li>✓ {t('feature5')}</li>
            </ul>
          </div>
        </div>
      ) : (
        // Simulation loaded - show dashboard
        <div className="simulation-content">
          {/* Summary Cards */}
          <div className="summary-cards">
            <div className="card metric-card">
              <div className="metric-label">{t('portfolioValue')}</div>
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
              <div className="metric-label">{t('cash')}</div>
              <div className="metric-value">
                {portfolio ? formatCurrency(portfolio.cash) : '...'}
              </div>
            </div>

            <div className="card metric-card">
              <div className="metric-label">{t('positions')}</div>
              <div className="metric-value">
                {portfolio ? portfolio.positions.length : 0}
              </div>
            </div>

            <div className="card metric-card">
              <div className="metric-label">{t('winRate')}</div>
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
              {t('overview')}
            </button>
            <button
              className={activeTab === 'recommendations' ? 'active' : ''}
              onClick={() => setActiveTab('recommendations')}
            >
              {t('recommendations')}
            </button>
            <button
              className={activeTab === 'trade' ? 'active' : ''}
              onClick={() => setActiveTab('trade')}
            >
              {t('trade')}
            </button>
            <button
              className={activeTab === 'history' ? 'active' : ''}
              onClick={() => setActiveTab('history')}
            >
              {t('history')}
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
                          <th>{t('ticker')}</th>
                          <th>{t('quantity')}</th>
                          <th>{t('avgCost')}</th>
                          <th>{t('currentPrice')}</th>
                          <th>{t('value')}</th>
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
                      <p>{t('noPositions')}</p>
                      <small>{t('noPositionsHint')}</small>
                    </div>
                  )}
                </div>

                <div className="actions">
                  <button onClick={loadPortfolio} className="btn btn-secondary">
                    🔄 {t('refresh')}
                  </button>
                  <button onClick={resetSimulation} className="btn btn-danger">
                    {t('reset')}
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'recommendations' && (
              <div className="recommendations-tab">
                <div className="card">
                  <div className="card-header">
                    <h3>{t('aiRecommendations')}</h3>
                    <div>
                      <button
                        onClick={loadRecommendations}
                        disabled={loading}
                        className="btn btn-secondary"
                        style={{marginRight: '10px'}}
                      >
                        {loading ? t('loading') : '🤖 ' + t('loadRecommendations')}
                      </button>
                      <button
                        onClick={executeAutoTrade}
                        disabled={loading}
                        className="btn btn-primary"
                      >
                        {loading ? t('executing') : '⚡ ' + t('autoTrade')}
                      </button>
                    </div>
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
                  <h3>{t('manualTrade')}</h3>
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
                        <label>{t('action')}</label>
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
                        <label>{t('quantity')}</label>
                        <input
                          type="number"
                          value={tradeForm.quantity}
                          onChange={(e) => setTradeForm({...tradeForm, quantity: Number(e.target.value)})}
                          min="1"
                          required
                        />
                      </div>

                      <div className="form-group">
                        <label>{t('price')}</label>
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
                      {loading ? t('executing') : t('executeTrade')}
                    </button>
                  </form>
                </div>
              </div>
            )}

            {activeTab === 'history' && (
              <div className="history-tab">
                <div className="card">
                  <div className="card-header">
                    <h3>{t('tradeHistory')}</h3>
                    <button
                      onClick={loadTradeHistory}
                      className="btn btn-secondary"
                    >
                      🔄 {t('refresh')}
                    </button>
                  </div>
                  {tradeHistory.length > 0 ? (
                    <table className="history-table">
                      <thead>
                        <tr>
                          <th>{t('time')}</th>
                          <th>{t('action')}</th>
                          <th>{t('ticker')}</th>
                          <th>{t('quantity')}</th>
                          <th>{t('price')}</th>
                          <th>{t('total')}</th>
                          <th>{t('confidence')}</th>
                          <th>{t('reason')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {tradeHistory.map((trade, idx) => (
                          <tr key={idx}>
                            <td>{new Date(trade.timestamp).toLocaleString('de-DE')}</td>
                            <td className={trade.action === 'BUY' ? 'buy' : 'sell'}>
                              {trade.action}
                            </td>
                            <td className="ticker">{trade.ticker}</td>
                            <td>{trade.quantity}</td>
                            <td>{formatCurrency(trade.price)}</td>
                            <td>{formatCurrency(trade.price * trade.quantity)}</td>
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
                      <p>{t('noTrades')}</p>
                      <small>{t('noTradesHint')}</small>
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
