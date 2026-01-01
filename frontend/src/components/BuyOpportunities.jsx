import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { apiClient } from '../api';
import './BuyOpportunities.css';

function BuyOpportunities() {
  const [stockBuyOpportunities, setStockBuyOpportunities] = useState([]);
  const [stockSellOpportunities, setStockSellOpportunities] = useState([]);
  const [cryptoBuyOpportunities, setCryptoBuyOpportunities] = useState([]);
  const [cryptoSellOpportunities, setCryptoSellOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('stocks'); // 'stocks' or 'crypto'
  const [userContext, setUserContext] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);

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
        stocks.slice(0, 30).map(async (stock) => {
          try {
            const predRes = await apiClient.get(`/predict_ticker/${stock.ticker}`);
            // Transform predict_ticker response to prediction format
            const prediction = {
              signal: predRes.data.prediction > 0.5 ? 'BUY' : 'SELL',
              confidence: Math.round((predRes.data.probability || 0) * 100),
              reasoning: `Prediction probability: ${(predRes.data.probability || 0).toFixed(2)}`
            };
            return {
              ...stock,
              prediction
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

      // Filter for BUY and SELL signals
      const buyStocks = stockPredictions
        .filter(s => s.prediction.signal === 'BUY')
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
        .slice(0, 6);

      const sellStocks = stockPredictions
        .filter(s => s.prediction.signal === 'SELL')
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
        .slice(0, 6);

      setStockBuyOpportunities(buyStocks);
      setStockSellOpportunities(sellStocks);

      // Fetch crypto rankings
      const cryptoResponse = await apiClient.get('/crypto/ranking?limit=50');
      const cryptos = cryptoResponse.data.ranking || [];

      // Get predictions for top cryptos
      const cryptoPredictions = await Promise.all(
        cryptos.slice(0, 30).map(async (crypto) => {
          try {
            // Use momentum score from crypto ranking as prediction
            const score = crypto.momentum_score || crypto.probability || 0.5;
            const prediction = {
              signal: score > 0.6 ? 'BUY' : score < 0.4 ? 'SELL' : 'HOLD',
              confidence: Math.round(score * 100),
              reasoning: `Momentum score: ${score.toFixed(2)}`
            };
            return {
              ...crypto,
              prediction
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

      // Filter for BUY and SELL signals
      const buyCryptos = cryptoPredictions
        .filter(c => c.prediction.signal === 'BUY')
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
        .slice(0, 6);

      const sellCryptos = cryptoPredictions
        .filter(c => c.prediction.signal === 'SELL')
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
        .slice(0, 6);

      setCryptoBuyOpportunities(buyCryptos);
      setCryptoSellOpportunities(sellCryptos);

    } catch (err) {
      console.error('Failed to load opportunities:', err);
      setError('Failed to load opportunities');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadOpportunities();
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setAnalysis(null);

    try {
      const currentOpportunities = activeTab === 'stocks'
        ? [...stockBuyOpportunities, ...stockSellOpportunities]
        : [...cryptoBuyOpportunities, ...cryptoSellOpportunities];

      const opportunitiesData = currentOpportunities.map(opp => ({
        ticker: opp.ticker || opp.symbol || opp.crypto_id,
        name: opp.name,
        signal: opp.prediction.signal,
        confidence: opp.prediction.confidence,
        reasoning: opp.prediction.reasoning,
        price: opp.current_price || opp.price
      }));

      const response = await apiClient.post('/ai/analyze', {
        context: userContext || `Analyze these ${activeTab} opportunities and provide investment insights.`,
        opportunities: opportunitiesData,
        asset_type: activeTab
      });

      setAnalysis(response.data.analysis);
    } catch (err) {
      console.error('Failed to get AI analysis:', err);
      setAnalysis('Failed to get AI analysis. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading && stockBuyOpportunities.length === 0 && cryptoBuyOpportunities.length === 0) {
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
        <h2>🎯 Trading Opportunities</h2>
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
          📈 Stocks
        </button>
        <button
          className={`tab-btn ${activeTab === 'crypto' ? 'active' : ''}`}
          onClick={() => setActiveTab('crypto')}
        >
          ₿ Crypto
        </button>
      </div>

      {/* AI Analysis Section */}
      <section className="analysis-section" role="region" aria-label="AI analysis context input">
        <label>
          <strong>🤖 Optional context for AI analysis</strong>
          <textarea
            value={userContext}
            onChange={(e) => setUserContext(e.target.value)}
            placeholder={`e.g., I'm interested in ${activeTab === 'stocks' ? 'tech stocks with growth potential' : 'high momentum crypto'}, looking for short-term trades...`}
            rows={3}
            aria-label="Enter context for AI analysis"
          />
        </label>
        <button
          onClick={handleAnalyze}
          disabled={analyzing}
          className="analyze-btn"
          aria-label="Request AI analysis and recommendations"
        >
          {analyzing ? (
            <>
              <span className="spinner"></span>
              Analyzing...
            </>
          ) : (
            '✨ Get AI Recommendations'
          )}
        </button>
      </section>

      {/* AI Analysis Result */}
      {analysis && (
        <section className="analysis-result" role="region" aria-label="AI analysis results">
          <h3>💡 AI Analysis & Recommendations</h3>
          <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{analysis}</p>
        </section>
      )}

      <div className="opportunities-content">
        {activeTab === 'stocks' && (
          <>
            {/* Buy Opportunities */}
            <div className="opportunity-section">
              <h3 className="section-title">🟢 Top Buy Opportunities (Max 10)</h3>
              {stockBuyOpportunities.length === 0 ? (
                <div className="empty-opportunities">
                  <p>😔 No strong BUY signals for stocks right now.</p>
                  <p className="hint">The market may be in a bearish phase. Check back later.</p>
                </div>
              ) : (
                <div className="opportunity-grid">
                  {stockBuyOpportunities.map((stock, index) => (
                    <div key={stock.ticker} className="opportunity-card buy-card">
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
                          {stock.prediction?.metrics?.probability != null && (
                            <div className="detail-item">
                              <span className="label">ML Probability:</span>
                              <span className="value">{(stock.prediction.metrics.probability * 100).toFixed(1)}%</span>
                            </div>
                          )}
                          <div className="detail-item">
                            <span className="label">Price:</span>
                            <span className="value">{stock.current_price != null ? `$${stock.current_price.toFixed(2)}` : 'N/A'}</span>
                          </div>
                        </div>

                        <div className="opportunity-reasoning">
                          {stock.prediction.reasoning}
                        </div>

                        <div className="opportunity-actions">
                          <a
                            href={`https://finance.yahoo.com/quote/${stock.ticker}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="chart-link"
                          >
                            📊 View Chart
                          </a>
                          <a
                            href={`https://www.google.com/finance/quote/${stock.ticker}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="market-link"
                          >
                            🔗 Market Info
                          </a>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Sell Opportunities */}
            <div className="opportunity-section">
              <h3 className="section-title">🔴 Top Sell Opportunities (Max 10)</h3>
              {stockSellOpportunities.length === 0 ? (
                <div className="empty-opportunities">
                  <p>😔 No strong SELL signals for stocks right now.</p>
                  <p className="hint">The market may be in a bullish phase. Check back later.</p>
                </div>
              ) : (
                <div className="opportunity-grid">
                  {stockSellOpportunities.map((stock, index) => (
                    <div key={stock.ticker} className="opportunity-card sell-card">
                      <div className="opportunity-rank">#{index + 1}</div>
                      <div className="opportunity-main">
                        <div className="opportunity-header">
                          <span className="opportunity-ticker">{stock.ticker}</span>
                          <span className="opportunity-name">{stock.name || stock.ticker}</span>
                        </div>

                        <div className="opportunity-signal">
                          <div className="signal-badge sell">
                            🔴 SELL
                          </div>
                          <div className="confidence-score">
                            {stock.prediction.confidence.toFixed(0)}% confidence
                          </div>
                        </div>

                        <div className="opportunity-details">
                          {stock.prediction?.metrics?.probability != null && (
                            <div className="detail-item">
                              <span className="label">ML Probability:</span>
                              <span className="value">{(stock.prediction.metrics.probability * 100).toFixed(1)}%</span>
                            </div>
                          )}
                          <div className="detail-item">
                            <span className="label">Price:</span>
                            <span className="value">{stock.current_price != null ? `$${stock.current_price.toFixed(2)}` : 'N/A'}</span>
                          </div>
                        </div>

                        <div className="opportunity-reasoning">
                          {stock.prediction.reasoning}
                        </div>

                        <div className="opportunity-actions">
                          <a
                            href={`https://finance.yahoo.com/quote/${stock.ticker}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="chart-link"
                          >
                            📊 View Chart
                          </a>
                          <a
                            href={`https://www.google.com/finance/quote/${stock.ticker}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="market-link"
                          >
                            🔗 Market Info
                          </a>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {activeTab === 'crypto' && (
          <>
            {/* Buy Opportunities */}
            <div className="opportunity-section">
              <h3 className="section-title">🟢 Top Buy Opportunities (Max 10)</h3>
              {cryptoBuyOpportunities.length === 0 ? (
                <div className="empty-opportunities">
                  <p>😔 No strong BUY signals for crypto right now.</p>
                  <p className="hint">Crypto market may be consolidating. Check back later.</p>
                </div>
              ) : (
                <div className="opportunity-grid">
                  {cryptoBuyOpportunities.map((crypto, index) => (
                    <div key={crypto.crypto_id} className="opportunity-card buy-card">
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

                        <div className="opportunity-actions">
                          <a
                            href={`https://www.coingecko.com/en/coins/${crypto.crypto_id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="chart-link"
                          >
                            📊 View Chart
                          </a>
                          <a
                            href={`https://coinmarketcap.com/currencies/${crypto.crypto_id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="market-link"
                          >
                            🔗 Market Info
                          </a>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Sell Opportunities */}
            <div className="opportunity-section">
              <h3 className="section-title">🔴 Top Sell Opportunities (Max 10)</h3>
              {cryptoSellOpportunities.length === 0 ? (
                <div className="empty-opportunities">
                  <p>😔 No strong SELL signals for crypto right now.</p>
                  <p className="hint">Crypto market may be in uptrend. Check back later.</p>
                </div>
              ) : (
                <div className="opportunity-grid">
                  {cryptoSellOpportunities.map((crypto, index) => (
                    <div key={crypto.crypto_id} className="opportunity-card sell-card">
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
                          <div className="signal-badge sell">
                            🔴 SELL
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

                        <div className="opportunity-actions">
                          <a
                            href={`https://www.coingecko.com/en/coins/${crypto.crypto_id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="chart-link"
                          >
                            📊 View Chart
                          </a>
                          <a
                            href={`https://coinmarketcap.com/currencies/${crypto.crypto_id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="market-link"
                          >
                            🔗 Market Info
                          </a>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

BuyOpportunities.propTypes = {
  // No props needed currently
};

export default BuyOpportunities;
