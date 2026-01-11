import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { apiClient } from "../api";
import { convertAndFormat } from "../utils/currency";
import "./BuyOpportunities.css";

function BuyOpportunities({ currency = "USD", exchangeRate = null }) {
  const [stockBuyOpportunities, setStockBuyOpportunities] = useState([]);
  const [stockHoldOpportunities, setStockHoldOpportunities] = useState([]);
  const [stockSellOpportunities, setStockSellOpportunities] = useState([]);
  const [cryptoBuyOpportunities, setCryptoBuyOpportunities] = useState([]);
  const [cryptoHoldOpportunities, setCryptoHoldOpportunities] = useState([]);
  const [cryptoSellOpportunities, setCryptoSellOpportunities] = useState([]);
  const [commodityBuyOpportunities, setCommodityBuyOpportunities] = useState([]);
  const [commodityHoldOpportunities, setCommodityHoldOpportunities] = useState([]);
  const [commoditySellOpportunities, setCommoditySellOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("stocks"); // 'stocks', 'crypto', or 'commodities'
  const [userContext, setUserContext] = useState("");
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
      // Use /ranking endpoint instead of /popular_stocks for accurate data
      // Add cache buster to prevent stale data
      const cacheBuster = `?_t=${Date.now()}`;
      const rankingResponse = await apiClient.get(`/ranking${cacheBuster}`);
      const ranking = rankingResponse.data.ranking || [];

      console.log(`📊 Received ${ranking.length} stocks from /ranking endpoint`);
      console.log(
        "🔍 First 5 stocks:",
        ranking
          .slice(0, 5)
          .map((s) => `${s.ticker}=$${s.price.toFixed(2)}`)
          .join(", ")
      );

      // Get stock names from /popular_stocks (for display only)
      const popularResponse = await apiClient.get("/popular_stocks?limit=100");
      const popularStocks = popularResponse.data.stocks || [];
      const stockNames = {};
      popularStocks.forEach((s) => {
        stockNames[s.ticker] = s.name;
      });

      console.log(`📝 Loaded ${Object.keys(stockNames).length} stock names`);

      // Convert ranking data to predictions (no need for additional API calls)
      const stockPredictions = ranking.map((item) => {
        const prediction = {
          signal: item.action || (item.prob > 0.6 ? "BUY" : item.prob < 0.4 ? "SELL" : "HOLD"),
          confidence: item.confidence || Math.round(item.prob * 100),
          reasoning: `AI Confidence: ${(item.prob * 100).toFixed(1)}%`,
          metrics: {
            probability: item.prob,
            price: item.price,
          },
        };

        return {
          ticker: item.ticker,
          name: stockNames[item.ticker] || item.ticker,
          current_price: item.price, // Use price from ranking
          prediction,
        };
      });

      // Filter for BUY, HOLD, and SELL signals
      const buyStocks = stockPredictions
        .filter((s) => s.prediction.signal === "BUY")
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
        .slice(0, 6);

      const holdStocks = stockPredictions
        .filter((s) => s.prediction.signal === "HOLD")
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
        .slice(0, 6);

      const sellStocks = stockPredictions
        .filter((s) => s.prediction.signal === "SELL")
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
        .slice(0, 6);

      setStockBuyOpportunities(buyStocks);
      setStockHoldOpportunities(holdStocks);
      setStockSellOpportunities(sellStocks);

      console.log(
        `✅ Loaded ${buyStocks.length} BUY, ${holdStocks.length} HOLD, ${sellStocks.length} SELL stocks`
      );

      // Fetch crypto rankings
      const cryptoResponse = await apiClient.get("/crypto/ranking?limit=50");
      const cryptos = cryptoResponse.data.ranking || [];

      // Get predictions for top cryptos
      const cryptoPredictions = await Promise.all(
        cryptos.slice(0, 30).map(async (crypto) => {
          try {
            // Use momentum score from crypto ranking as prediction
            const score = crypto.momentum_score || crypto.probability || 0.5;
            const prediction = {
              signal: score > 0.6 ? "BUY" : score < 0.4 ? "SELL" : "HOLD",
              confidence: Math.round(score * 100),
              reasoning: `Momentum score: ${score.toFixed(2)}`,
            };
            return {
              ...crypto,
              prediction,
            };
          } catch (err) {
            console.error(`Failed to get prediction for ${crypto.crypto_id}:`, err);
            return {
              ...crypto,
              prediction: { signal: "HOLD", confidence: 50, reasoning: "No prediction available" },
            };
          }
        })
      );

      // Filter for BUY, HOLD, and SELL signals
      const buyCryptos = cryptoPredictions
        .filter((c) => c.prediction.signal === "BUY")
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
        .slice(0, 6);

      const holdCryptos = cryptoPredictions
        .filter((c) => c.prediction.signal === "HOLD")
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
        .slice(0, 6);

      const sellCryptos = cryptoPredictions
        .filter((c) => c.prediction.signal === "SELL")
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
        .slice(0, 6);

      setCryptoBuyOpportunities(buyCryptos);
      setCryptoHoldOpportunities(holdCryptos);
      setCryptoSellOpportunities(sellCryptos);

      console.log(
        `✅ Loaded ${buyCryptos.length} crypto BUY, ${holdCryptos.length} HOLD, ${sellCryptos.length} SELL`
      );

      // Load Commodities (Gold, Oil, Silver, etc.)
      try {
        await loadCommodities();
      } catch (commErr) {
        console.warn("Commodities loading failed (non-critical):", commErr);
        // Don't fail the whole page if commodities fail
      }
    } catch (err) {
      console.error("Failed to load opportunities:", err);
      console.error("Error details:", err.message, err.response?.data);
      setError(`Failed to load opportunities: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadCommodities = async () => {
    try {
      // Popular commodities
      const commodities = [
        { ticker: "GC=F", name: "Gold", type: "Precious Metal" },
        { ticker: "SI=F", name: "Silver", type: "Precious Metal" },
        { ticker: "CL=F", name: "Crude Oil", type: "Energy" },
        { ticker: "NG=F", name: "Natural Gas", type: "Energy" },
        { ticker: "HG=F", name: "Copper", type: "Industrial Metal" },
        { ticker: "PL=F", name: "Platinum", type: "Precious Metal" },
      ];

      const commodityPredictions = await Promise.all(
        commodities.map(async (commodity) => {
          try {
            const predRes = await apiClient.get(`/api/predict/${commodity.ticker}`);
            const probability = predRes.data.probability || 0.5;
            const prediction = {
              signal: probability > 0.6 ? "BUY" : probability < 0.4 ? "SELL" : "HOLD",
              confidence: Math.round(probability * 100),
              reasoning: `AI Confidence: ${(probability * 100).toFixed(1)}%`,
            };
            return {
              ...commodity,
              current_price: predRes.data.price || 0,
              prediction,
            };
          } catch (err) {
            console.error(`Failed to get prediction for ${commodity.ticker}:`, err);
            return {
              ...commodity,
              current_price: 0,
              prediction: { signal: "HOLD", confidence: 50, reasoning: "No prediction available" },
            };
          }
        })
      );

      const buyCommodities = commodityPredictions
        .filter((c) => c.prediction.signal === "BUY")
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence);

      const holdCommodities = commodityPredictions
        .filter((c) => c.prediction.signal === "HOLD")
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence);

      const sellCommodities = commodityPredictions
        .filter((c) => c.prediction.signal === "SELL")
        .sort((a, b) => b.prediction.confidence - a.prediction.confidence);

      setCommodityBuyOpportunities(buyCommodities);
      setCommodityHoldOpportunities(holdCommodities);
      setCommoditySellOpportunities(sellCommodities);
    } catch (err) {
      console.error("Failed to load commodities:", err);
    }
  };

  const handleRefresh = () => {
    loadOpportunities();
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setAnalysis(null);

    try {
      const currentOpportunities =
        activeTab === "stocks"
          ? [...stockBuyOpportunities, ...stockHoldOpportunities, ...stockSellOpportunities]
          : activeTab === "crypto"
            ? [...cryptoBuyOpportunities, ...cryptoHoldOpportunities, ...cryptoSellOpportunities]
            : [
                ...commodityBuyOpportunities,
                ...commodityHoldOpportunities,
                ...commoditySellOpportunities,
              ];

      const opportunitiesData = currentOpportunities.map((opp) => ({
        ticker: opp.ticker || opp.symbol || opp.crypto_id,
        name: opp.name,
        signal: opp.prediction.signal,
        confidence: opp.prediction.confidence,
        reasoning: opp.prediction.reasoning,
        price: opp.current_price || opp.price,
      }));

      const response = await apiClient.post("/ai/analyze", {
        context:
          userContext ||
          `Analyze these ${activeTab} opportunities and provide investment insights.`,
        opportunities: opportunitiesData,
        asset_type: activeTab,
      });

      setAnalysis(response.data.analysis);
    } catch (err) {
      console.error("Failed to get AI analysis:", err);
      setAnalysis("Failed to get AI analysis. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  if (
    loading &&
    stockBuyOpportunities.length === 0 &&
    cryptoBuyOpportunities.length === 0 &&
    commodityBuyOpportunities.length === 0
  ) {
    return (
      <div className="buy-opportunities">
        <div className="opportunities-header">
          <h2>🎯 Trading Opportunities</h2>
        </div>
        <div className="loading-opportunities">
          <div className="spinner"></div>
          <p>Analyzing markets for trading opportunities...</p>
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
          {loading ? "⟳" : "🔄"} Refresh
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="opportunities-tabs">
        <button
          className={`tab-btn ${activeTab === "stocks" ? "active" : ""}`}
          onClick={() => setActiveTab("stocks")}
        >
          📈 Stocks
        </button>
        <button
          className={`tab-btn ${activeTab === "crypto" ? "active" : ""}`}
          onClick={() => setActiveTab("crypto")}
        >
          ₿ Crypto
        </button>
        <button
          className={`tab-btn ${activeTab === "commodities" ? "active" : ""}`}
          onClick={() => setActiveTab("commodities")}
        >
          🥇 Rohstoffe
        </button>
      </div>

      {/* AI Analysis Section */}
      <section className="analysis-section" role="region" aria-label="AI analysis context input">
        <label>
          <strong>🤖 Optional context for AI analysis</strong>
          <textarea
            value={userContext}
            onChange={(e) => setUserContext(e.target.value)}
            placeholder={`e.g., I'm interested in ${activeTab === "stocks" ? "tech stocks with growth potential" : activeTab === "crypto" ? "high momentum crypto" : "commodities for inflation hedge"}, looking for short-term trades...`}
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
            "✨ Get AI Recommendations"
          )}
        </button>
      </section>

      {/* AI Analysis Result */}
      {analysis && (
        <section className="analysis-result" role="region" aria-label="AI analysis results">
          <h3>💡 AI Analysis & Recommendations</h3>
          <p style={{ whiteSpace: "pre-wrap", lineHeight: 1.7 }}>{analysis}</p>
        </section>
      )}

      <div className="opportunities-content">
        {activeTab === "stocks" && (
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
                          <div className="signal-badge buy">🟢 BUY</div>
                          <div className="confidence-score">
                            {stock.prediction.confidence.toFixed(0)}% confidence
                          </div>
                        </div>

                        <div className="opportunity-details">
                          {stock.prediction?.metrics?.probability != null && (
                            <div className="detail-item">
                              <span className="label">ML Probability:</span>
                              <span className="value">
                                {(stock.prediction.metrics.probability * 100).toFixed(1)}%
                              </span>
                            </div>
                          )}
                          <div className="detail-item">
                            <span className="label">Price:</span>
                            <span className="value">
                              {stock.current_price > 0
                                ? convertAndFormat(stock.current_price, currency, exchangeRate)
                                : "N/A"}
                            </span>
                          </div>
                        </div>

                        <div className="opportunity-reasoning">{stock.prediction.reasoning}</div>

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

            {/* Hold Opportunities */}
            <div className="opportunity-section">
              <h3 className="section-title">🟡 Hold Recommendations (Max 10)</h3>
              {stockHoldOpportunities.length === 0 ? (
                <div className="empty-opportunities">
                  <p>😔 No HOLD signals for stocks right now.</p>
                  <p className="hint">Most stocks show strong BUY or SELL signals.</p>
                </div>
              ) : (
                <div className="opportunity-grid">
                  {stockHoldOpportunities.map((stock, index) => (
                    <div key={stock.ticker} className="opportunity-card hold-card">
                      <div className="opportunity-rank">#{index + 1}</div>
                      <div className="opportunity-main">
                        <div className="opportunity-header">
                          <span className="opportunity-ticker">{stock.ticker}</span>
                          <span className="opportunity-name">{stock.name || stock.ticker}</span>
                        </div>

                        <div className="opportunity-signal">
                          <div className="signal-badge hold">🟡 HOLD</div>
                          <div className="confidence-score">
                            {stock.prediction.confidence.toFixed(0)}% confidence
                          </div>
                        </div>

                        <div className="opportunity-details">
                          {stock.prediction?.metrics?.probability != null && (
                            <div className="detail-item">
                              <span className="label">ML Probability:</span>
                              <span className="value">
                                {(stock.prediction.metrics.probability * 100).toFixed(1)}%
                              </span>
                            </div>
                          )}
                          <div className="detail-item">
                            <span className="label">Price:</span>
                            <span className="value">
                              {stock.current_price > 0
                                ? convertAndFormat(stock.current_price, currency, exchangeRate)
                                : "N/A"}
                            </span>
                          </div>
                        </div>

                        <div className="opportunity-reasoning">{stock.prediction.reasoning}</div>

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
                          <div className="signal-badge sell">🔴 SELL</div>
                          <div className="confidence-score">
                            {stock.prediction.confidence.toFixed(0)}% confidence
                          </div>
                        </div>

                        <div className="opportunity-details">
                          {stock.prediction?.metrics?.probability != null && (
                            <div className="detail-item">
                              <span className="label">ML Probability:</span>
                              <span className="value">
                                {(stock.prediction.metrics.probability * 100).toFixed(1)}%
                              </span>
                            </div>
                          )}
                          <div className="detail-item">
                            <span className="label">Price:</span>
                            <span className="value">
                              {stock.current_price > 0
                                ? convertAndFormat(stock.current_price, currency, exchangeRate)
                                : "N/A"}
                            </span>
                          </div>
                        </div>

                        <div className="opportunity-reasoning">{stock.prediction.reasoning}</div>

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

        {activeTab === "crypto" && (
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
                          <img src={crypto.image} alt={crypto.name} className="crypto-icon" />
                          <span className="opportunity-ticker">{crypto.symbol.toUpperCase()}</span>
                          <span className="opportunity-name">{crypto.name}</span>
                        </div>

                        <div className="opportunity-signal">
                          <div className="signal-badge buy">🟢 BUY</div>
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
                            <span
                              className={`value ${crypto.change_24h >= 0 ? "positive" : "negative"}`}
                            >
                              {crypto.change_24h >= 0 ? "▲" : "▼"}{" "}
                              {Math.abs(crypto.change_24h).toFixed(2)}%
                            </span>
                          </div>
                          <div className="detail-item">
                            <span className="label">Momentum:</span>
                            <span className="value">{crypto.momentum_score.toFixed(2)}</span>
                          </div>
                        </div>

                        <div className="opportunity-reasoning">{crypto.prediction.reasoning}</div>

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

            {/* Hold Opportunities */}
            <div className="opportunity-section">
              <h3 className="section-title">🟡 Hold Recommendations (Max 10)</h3>
              {cryptoHoldOpportunities.length === 0 ? (
                <div className="empty-opportunities">
                  <p>😔 No HOLD signals for crypto right now.</p>
                  <p className="hint">Most cryptos show strong BUY or SELL signals.</p>
                </div>
              ) : (
                <div className="opportunity-grid">
                  {cryptoHoldOpportunities.map((crypto, index) => (
                    <div key={crypto.crypto_id} className="opportunity-card hold-card">
                      <div className="opportunity-rank">#{index + 1}</div>
                      <div className="opportunity-main">
                        <div className="opportunity-header">
                          <img src={crypto.image} alt={crypto.name} className="crypto-icon" />
                          <span className="opportunity-ticker">{crypto.symbol.toUpperCase()}</span>
                          <span className="opportunity-name">{crypto.name}</span>
                        </div>

                        <div className="opportunity-signal">
                          <div className="signal-badge hold">🟡 HOLD</div>
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
                            <span
                              className={`value ${crypto.change_24h >= 0 ? "positive" : "negative"}`}
                            >
                              {crypto.change_24h >= 0 ? "▲" : "▼"}{" "}
                              {Math.abs(crypto.change_24h).toFixed(2)}%
                            </span>
                          </div>
                          <div className="detail-item">
                            <span className="label">Momentum:</span>
                            <span className="value">{crypto.momentum_score.toFixed(2)}</span>
                          </div>
                        </div>

                        <div className="opportunity-reasoning">{crypto.prediction.reasoning}</div>

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
                          <img src={crypto.image} alt={crypto.name} className="crypto-icon" />
                          <span className="opportunity-ticker">{crypto.symbol.toUpperCase()}</span>
                          <span className="opportunity-name">{crypto.name}</span>
                        </div>

                        <div className="opportunity-signal">
                          <div className="signal-badge sell">🔴 SELL</div>
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
                            <span
                              className={`value ${crypto.change_24h >= 0 ? "positive" : "negative"}`}
                            >
                              {crypto.change_24h >= 0 ? "▲" : "▼"}{" "}
                              {Math.abs(crypto.change_24h).toFixed(2)}%
                            </span>
                          </div>
                          <div className="detail-item">
                            <span className="label">Momentum:</span>
                            <span className="value">{crypto.momentum_score.toFixed(2)}</span>
                          </div>
                        </div>

                        <div className="opportunity-reasoning">{crypto.prediction.reasoning}</div>

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

        {activeTab === "commodities" && (
          <>
            {/* Buy Opportunities - Commodities */}
            <div className="opportunity-section">
              <h3 className="section-title">🟢 Top Buy Opportunities - Rohstoffe</h3>
              {commodityBuyOpportunities.length === 0 ? (
                <div className="empty-opportunities">
                  <p>😔 No strong BUY signals for commodities right now.</p>
                  <p className="hint">Commodities market may be consolidating. Check back later.</p>
                </div>
              ) : (
                <div className="opportunity-grid">
                  {commodityBuyOpportunities.map((commodity, index) => (
                    <div key={commodity.ticker} className="opportunity-card buy-card">
                      <div className="opportunity-rank">#{index + 1}</div>
                      <div className="opportunity-main">
                        <div className="opportunity-header">
                          <span className="opportunity-ticker">{commodity.ticker}</span>
                          <span className="opportunity-name">{commodity.name}</span>
                          <span
                            className="commodity-type"
                            style={{ fontSize: "0.8rem", color: "#666" }}
                          >
                            {commodity.type}
                          </span>
                        </div>

                        <div className="opportunity-signal">
                          <div className="signal-badge buy">🟢 BUY</div>
                          <div className="confidence-score">
                            {commodity.prediction.confidence.toFixed(0)}% confidence
                          </div>
                        </div>

                        <div className="opportunity-details">
                          <div className="detail-item">
                            <span className="label">Price:</span>
                            <span className="value">
                              {commodity.current_price > 0
                                ? convertAndFormat(commodity.current_price, currency, exchangeRate)
                                : "N/A"}
                            </span>
                          </div>
                          <div className="detail-item">
                            <span className="label">Type:</span>
                            <span className="value">{commodity.type}</span>
                          </div>
                        </div>

                        <div className="opportunity-reasoning">
                          {commodity.prediction.reasoning}
                        </div>

                        <div className="opportunity-actions">
                          <a
                            href={`https://finance.yahoo.com/quote/${commodity.ticker}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="chart-link"
                          >
                            📊 View Chart
                          </a>
                          <a
                            href={`https://www.investing.com/commodities/`}
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

            {/* Hold Opportunities - Commodities */}
            <div className="opportunity-section">
              <h3 className="section-title">🟡 Hold Recommendations - Rohstoffe</h3>
              {commodityHoldOpportunities.length === 0 ? (
                <div className="empty-opportunities">
                  <p>😔 No HOLD signals for commodities right now.</p>
                  <p className="hint">Most commodities show strong BUY or SELL signals.</p>
                </div>
              ) : (
                <div className="opportunity-grid">
                  {commodityHoldOpportunities.map((commodity, index) => (
                    <div key={commodity.ticker} className="opportunity-card hold-card">
                      <div className="opportunity-rank">#{index + 1}</div>
                      <div className="opportunity-main">
                        <div className="opportunity-header">
                          <span className="opportunity-ticker">{commodity.ticker}</span>
                          <span className="opportunity-name">{commodity.name}</span>
                          <span
                            className="commodity-type"
                            style={{ fontSize: "0.8rem", color: "#666" }}
                          >
                            {commodity.type}
                          </span>
                        </div>

                        <div className="opportunity-signal">
                          <div className="signal-badge hold">🟡 HOLD</div>
                          <div className="confidence-score">
                            {commodity.prediction.confidence.toFixed(0)}% confidence
                          </div>
                        </div>

                        <div className="opportunity-details">
                          <div className="detail-item">
                            <span className="label">Price:</span>
                            <span className="value">
                              {commodity.current_price > 0
                                ? convertAndFormat(commodity.current_price, currency, exchangeRate)
                                : "N/A"}
                            </span>
                          </div>
                          <div className="detail-item">
                            <span className="label">Type:</span>
                            <span className="value">{commodity.type}</span>
                          </div>
                        </div>

                        <div className="opportunity-reasoning">
                          {commodity.prediction.reasoning}
                        </div>

                        <div className="opportunity-actions">
                          <a
                            href={`https://finance.yahoo.com/quote/${commodity.ticker}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="chart-link"
                          >
                            📊 View Chart
                          </a>
                          <a
                            href={`https://www.investing.com/commodities/`}
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

            {/* Sell Opportunities - Commodities */}
            <div className="opportunity-section">
              <h3 className="section-title">🔴 Top Sell Opportunities - Rohstoffe</h3>
              {commoditySellOpportunities.length === 0 ? (
                <div className="empty-opportunities">
                  <p>😔 No strong SELL signals for commodities right now.</p>
                  <p className="hint">Commodities market may be in uptrend. Check back later.</p>
                </div>
              ) : (
                <div className="opportunity-grid">
                  {commoditySellOpportunities.map((commodity, index) => (
                    <div key={commodity.ticker} className="opportunity-card sell-card">
                      <div className="opportunity-rank">#{index + 1}</div>
                      <div className="opportunity-main">
                        <div className="opportunity-header">
                          <span className="opportunity-ticker">{commodity.ticker}</span>
                          <span className="opportunity-name">{commodity.name}</span>
                          <span
                            className="commodity-type"
                            style={{ fontSize: "0.8rem", color: "#666" }}
                          >
                            {commodity.type}
                          </span>
                        </div>

                        <div className="opportunity-signal">
                          <div className="signal-badge sell">🔴 SELL</div>
                          <div className="confidence-score">
                            {commodity.prediction.confidence.toFixed(0)}% confidence
                          </div>
                        </div>

                        <div className="opportunity-details">
                          <div className="detail-item">
                            <span className="label">Price:</span>
                            <span className="value">
                              {commodity.current_price > 0
                                ? convertAndFormat(commodity.current_price, currency, exchangeRate)
                                : "N/A"}
                            </span>
                          </div>
                          <div className="detail-item">
                            <span className="label">Type:</span>
                            <span className="value">{commodity.type}</span>
                          </div>
                        </div>

                        <div className="opportunity-reasoning">
                          {commodity.prediction.reasoning}
                        </div>

                        <div className="opportunity-actions">
                          <a
                            href={`https://finance.yahoo.com/quote/${commodity.ticker}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="chart-link"
                          >
                            📊 View Chart
                          </a>
                          <a
                            href={`https://www.investing.com/commodities/`}
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
  currency: PropTypes.string,
  exchangeRate: PropTypes.number,
};

export default BuyOpportunities;
