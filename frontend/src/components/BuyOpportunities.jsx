import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { apiClient } from '../api';
import './BuyOpportunities.css';

function BuyOpportunities() {
  const [stockOpportunities, setStockOpportunities] = useState([]);
  const [cryptoOpportunities, setCryptoOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('stocks'); // 'stocks' or 'crypto'

  useEffect(() => {
    loadOpportunities();
    // Refresh every 5 minutes
    const interval = setInterval(loadOpportunities, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadOpportunities = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch stock rankings (top stocks by ML prediction)
      const stockResponse = await apiClient.get('/ranking?country=Global');
      const stocks = stockResponse.data.ranking || [];

      // Get predictions for top stocks
      const stockPredictions = await Promise.all(
        stocks.slice(0, 20).map(async (stock) => {
          try {
            const predRes = await apiClient.get(`/watchlist/prediction/${stock.ticker}?asset_type=stock`);
            return {
              ...stock,
              prediction: predRes.data
            };
          } catch (err) {
            console.error(`Failed to get prediction for ${stock.ticker}:`, err);
            return {
              ...stock,
              prediction: { signal: 'HOLD', confidence: 50, reasoning: 'No prediction available' }
            };
          }
        })
      );

      // Filter for BUY signals only
      const buyStocks = stockPredictions
        .filter(s => s.prediction.signal === 'BUY')
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
        .slice(0, 10);

      setStockOpportunities(buyStocks);

      // Fetch crypto rankings
      const cryptoResponse = await apiClient.get('/crypto/ranking?limit=50');
      const cryptos = cryptoResponse.data.ranking || [];

      // Get predictions for top cryptos
      const cryptoPredictions = await Promise.all(
        cryptos.slice(0, 20).map(async (crypto) => {
          try {
            const predRes = await apiClient.get(`/watchlist/prediction/${crypto.crypto_id}?asset_type=crypto`);
            return {
              ...crypto,
              prediction: predRes.data
            };
          } catch (err) {
            console.error(`Failed to get prediction for ${crypto.crypto_id}:`, err);
            return {
              ...crypto,
              prediction: { signal: 'HOLD', confidence: 50, reasoning: 'No prediction available' }
            };
          }
        })
      );

      // Filter for BUY signals only
      const buyCryptos = cryptoPredictions
        .filter(c => c.prediction.signal === 'BUY')
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
        .slice(0, 10);

      setCryptoOpportunities(buyCryptos);

    } catch (err) {
      console.error('Failed to load opportunities:', err);
      setError('Failed to load buy opportunities');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadOpportunities();
  };

  if (loading && stockOpportunities.length === 0 && cryptoOpportunities.length === 0) {
    return (
      <div className="buy-opportunities">
        <div className="opportunities-header">
          <h2>🎯 Top Buy Opportunities</h2>
        </div>
        <div className="loading-opportunities">
          <div className="spinner"></div>
          <p>Analyzing market for buy opportunities...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="buy-opportunities">
      <div className="opportunities-header">
        <h2>🎯 Top Buy Opportunities</h2>
        <button 
          className="refresh-btn" 
          onClick={handleRefresh} 
          disabled={loading}
          title="Refresh opportunities"
        >
          {loading ? '⟳' : '🔄'} Refresh
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="opportunities-tabs">
        <button
          className={`tab-btn ${activeTab === 'stocks' ? 'active' : ''}`}
          onClick={() => setActiveTab('stocks')}
        >
          📈 Stocks ({stockOpportunities.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'crypto' ? 'active' : ''}`}
          onClick={() => setActiveTab('crypto')}
        >
          ₿ Crypto ({cryptoOpportunities.length})
        </button>
      </div>

      <div className="opportunities-content">
        {activeTab === 'stocks' && (
          <div className="opportunities-list">
            {stockOpportunities.length === 0 ? (
              <div className="empty-opportunities">
                <p>😔 No strong BUY signals for stocks right now.</p>
                <p className="hint">The market may be in a bearish phase. Check back later or adjust your risk tolerance.</p>
              </div>
            ) : (
              <div className="opportunity-grid">
                {stockOpportunities.map((stock, index) => (
                  <div key={stock.ticker} className="opportunity-card">
                    <div className="opportunity-rank">#{index + 1}</div>
                    <div className="opportunity-main">
                      <div className="opportunity-header">
                        <span className="opportunity-ticker">{stock.ticker}</span>
                        <span className="opportunity-name">{stock.name || stock.ticker}</span>
                      </div>
                      
                      <div className="opportunity-signal">
                        <div className="signal-badge buy">
                          🟢 BUY
                        </div>
                        <div className="confidence-score">
                          {stock.prediction.confidence.toFixed(0)}% confidence
                        </div>
                      </div>

                      <div className="opportunity-details">
                        <div className="detail-item">
                          <span className="label">ML Probability:</span>
                          <span className="value">{(stock.probability * 100).toFixed(1)}%</span>
                        </div>
                        {stock.current_price && (
                          <div className="detail-item">
                            <span className="label">Price:</span>
                            <span className="value">${stock.current_price.toFixed(2)}</span>
                          </div>
                        )}
                      </div>

                      <div className="opportunity-reasoning">
                        {stock.prediction.reasoning}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'crypto' && (
          <div className="opportunities-list">
            {cryptoOpportunities.length === 0 ? (
              <div className="empty-opportunities">
                <p>😔 No strong BUY signals for crypto right now.</p>
                <p className="hint">Crypto market may be consolidating. Check back later for momentum signals.</p>
              </div>
            ) : (
              <div className="opportunity-grid">
                {cryptoOpportunities.map((crypto, index) => (
                  <div key={crypto.crypto_id} className="opportunity-card">
                    <div className="opportunity-rank">#{index + 1}</div>
                    <div className="opportunity-main">
                      <div className="opportunity-header">
                        <img 
                          src={crypto.image} 
                          alt={crypto.name}
                          className="crypto-icon"
                        />
                        <span className="opportunity-ticker">{crypto.symbol.toUpperCase()}</span>
                        <span className="opportunity-name">{crypto.name}</span>
                      </div>
                      
                      <div className="opportunity-signal">
                        <div className="signal-badge buy">
                          🟢 BUY
                        </div>
                        <div className="confidence-score">
                          {crypto.prediction.confidence.toFixed(0)}% confidence
                        </div>
                      </div>

                      <div className="opportunity-details">
                        <div className="detail-item">
                          <span className="label">Price:</span>
                          <span className="value">${crypto.price.toLocaleString()}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">24h Change:</span>
                          <span className={`value ${crypto.change_24h >= 0 ? 'positive' : 'negative'}`}>
                            {crypto.change_24h >= 0 ? '▲' : '▼'} {Math.abs(crypto.change_24h).toFixed(2)}%
                          </span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Momentum:</span>
                          <span className="value">{crypto.momentum_score.toFixed(2)}</span>
                        </div>
                      </div>

                      <div className="opportunity-reasoning">
                        {crypto.prediction.reasoning}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

BuyOpportunities.propTypes = {
  // No props needed currently
};

export default BuyOpportunities;
