import { useState, useEffect } from "react";
import { apiClient } from "../api";
import "./StockExplorer.css";

/**
 * Modern Stock Explorer - Simplified and user-friendly
 *
 * Features:
 * - Card-based design (similar to WatchlistManagerV2)
 * - Clean stock search with autocomplete
 * - Beautiful stock cards with essential info
 * - Market selector (Global, US, EU)
 * - Loading states with proper error handling
 */
function StockExplorer() {
  const [market, setMarket] = useState("global");
  const [stocks, setStocks] = useState([]);
  const [filteredStocks, setFilteredStocks] = useState([]);
  const [searchTicker, setSearchTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);

  // Load stocks when market changes
  useEffect(() => {
    loadStocks();
  }, [market]);

  // Filter stocks when search changes
  useEffect(() => {
    if (searchTicker.trim() === "") {
      setFilteredStocks(stocks);
    } else {
      const search = searchTicker.toLowerCase();
      const filtered = stocks.filter(
        (stock) =>
          stock.ticker.toLowerCase().includes(search) ||
          (stock.name && stock.name.toLowerCase().includes(search))
      );
      setFilteredStocks(filtered);
    }
  }, [searchTicker, stocks]);

  const loadStocks = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get rankings
      const rankResponse = await apiClient.post("/api/rank", {
        market,
        limit: 50,
      });

      const rankings = rankResponse.data.rankings || [];

      // Get details for all tickers
      const tickers = rankings.map((r) => r.ticker);
      const detailsPromises = tickers.map(async (ticker) => {
        try {
          const res = await apiClient.get(`/api/ticker/${ticker}`);
          return { ticker, ...res.data };
        } catch (err) {
          console.error(`Failed to load details for ${ticker}:`, err);
          return { ticker };
        }
      });

      const details = await Promise.all(detailsPromises);

      // Combine rankings with details
      const enrichedStocks = rankings.map((r, index) => {
        const detail = details.find((d) => d.ticker === r.ticker) || {};
        return {
          ...r,
          ...detail,
          rank: index + 1,
        };
      });

      setStocks(enrichedStocks);
      setFilteredStocks(enrichedStocks);
    } catch (err) {
      console.error("Error loading stocks:", err);
      setError(err.response?.data?.detail || "Failed to load stocks");
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    if (!price) return "N/A";
    return `$${price.toFixed(2)}`;
  };

  const formatChange = (change) => {
    if (change === undefined || change === null) return "N/A";
    const sign = change >= 0 ? "+" : "";
    return `${sign}${change.toFixed(2)}%`;
  };

  const formatMarketCap = (cap) => {
    if (!cap) return "N/A";
    if (cap >= 1e12) return `$${(cap / 1e12).toFixed(2)}T`;
    if (cap >= 1e9) return `$${(cap / 1e9).toFixed(2)}B`;
    if (cap >= 1e6) return `$${(cap / 1e6).toFixed(2)}M`;
    return `$${cap.toFixed(2)}`;
  };

  const getConfidenceBadge = (prob) => {
    if (prob >= 0.65) return { text: "Strong Buy", class: "strong-buy" };
    if (prob >= 0.55) return { text: "Buy", class: "buy" };
    if (prob >= 0.45) return { text: "Hold", class: "hold" };
    if (prob >= 0.35) return { text: "Consider Selling", class: "sell" };
    return { text: "Sell", class: "strong-sell" };
  };

  const getRankIcon = (rank) => {
    if (rank === 1) return "🥇";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    return `#${rank}`;
  };

  return (
    <div className="stock-explorer">
      {/* Header */}
      <div className="explorer-header">
        <h2>📈 Stock Explorer</h2>
        <p>AI-ranked stocks with real-time data</p>
      </div>

      {error && (
        <div className="error-banner">
          <span>❌ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Market Selector */}
      <div className="market-selector-card card">
        <h3>🌍 Select Market</h3>
        <div className="market-buttons">
          <button
            className={`market-btn ${market === "global" ? "active" : ""}`}
            onClick={() => setMarket("global")}
            disabled={loading}
          >
            🌎 Global
          </button>
          <button
            className={`market-btn ${market === "us" ? "active" : ""}`}
            onClick={() => setMarket("us")}
            disabled={loading}
          >
            🇺🇸 US
          </button>
          <button
            className={`market-btn ${market === "eu" ? "active" : ""}`}
            onClick={() => setMarket("eu")}
            disabled={loading}
          >
            🇪🇺 EU
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="search-card card">
        <h3>🔍 Search Stocks</h3>
        <input
          type="text"
          value={searchTicker}
          onChange={(e) => setSearchTicker(e.target.value)}
          placeholder="Search by ticker or name (e.g., AAPL, Tesla)..."
          className="search-input"
        />
        {searchTicker && (
          <div className="search-results-count">
            Found {filteredStocks.length} {filteredStocks.length === 1 ? "stock" : "stocks"}
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading {market.toUpperCase()} stocks...</p>
        </div>
      )}

      {/* Stock Cards Grid */}
      {!loading && filteredStocks.length > 0 && (
        <div className="stocks-grid">
          {filteredStocks.slice(0, 20).map((stock) => {
            const badge = getConfidenceBadge(stock.prob);
            const changeClass = stock.change >= 0 ? "positive" : "negative";

            return (
              <div
                key={stock.ticker}
                className="stock-card card"
                onClick={() => setSelectedStock(stock)}
              >
                {/* Rank Badge */}
                <div className="rank-badge">{getRankIcon(stock.rank)}</div>

                {/* Stock Header */}
                <div className="stock-header">
                  <div className="ticker-name">
                    <h4>{stock.ticker}</h4>
                    <p>{stock.name || "N/A"}</p>
                  </div>
                  <div className={`confidence-badge ${badge.class}`}>{badge.text}</div>
                </div>

                {/* Stock Metrics */}
                <div className="stock-metrics">
                  <div className="metric-row">
                    <span className="metric-label">Price</span>
                    <span className="metric-value">{formatPrice(stock.price)}</span>
                  </div>
                  <div className="metric-row">
                    <span className="metric-label">Change</span>
                    <span className={`metric-value ${changeClass}`}>
                      {formatChange(stock.change)}
                    </span>
                  </div>
                  <div className="metric-row">
                    <span className="metric-label">Confidence</span>
                    <span className="metric-value">{(stock.prob * 100).toFixed(1)}%</span>
                  </div>
                  <div className="metric-row">
                    <span className="metric-label">Market Cap</span>
                    <span className="metric-value">{formatMarketCap(stock.market_cap)}</span>
                  </div>
                </div>

                {/* Footer */}
                <div className="stock-footer">
                  {stock.country && <span className="country-tag">{stock.country}</span>}
                  {stock.sector && <span className="sector-tag">{stock.sector}</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {!loading && filteredStocks.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h3>No stocks found</h3>
          <p>Try adjusting your search or selecting a different market</p>
        </div>
      )}

      {/* Selected Stock Detail Modal */}
      {selectedStock && (
        <div className="modal-overlay" onClick={() => setSelectedStock(null)}>
          <div className="modal-content card" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedStock(null)}>
              ✕
            </button>

            <div className="modal-header">
              <h2>{selectedStock.ticker}</h2>
              <div className={`confidence-badge ${getConfidenceBadge(selectedStock.prob).class}`}>
                {getConfidenceBadge(selectedStock.prob).text}
              </div>
            </div>

            <h3>{selectedStock.name || "N/A"}</h3>

            <div className="modal-metrics">
              <div className="modal-metric-card">
                <span className="label">Current Price</span>
                <span className="value">{formatPrice(selectedStock.price)}</span>
              </div>
              <div className="modal-metric-card">
                <span className="label">Daily Change</span>
                <span className={`value ${selectedStock.change >= 0 ? "positive" : "negative"}`}>
                  {formatChange(selectedStock.change)}
                </span>
              </div>
              <div className="modal-metric-card">
                <span className="label">AI Confidence</span>
                <span className="value">{(selectedStock.prob * 100).toFixed(2)}%</span>
              </div>
              <div className="modal-metric-card">
                <span className="label">Market Cap</span>
                <span className="value">{formatMarketCap(selectedStock.market_cap)}</span>
              </div>
              {selectedStock.volume && (
                <div className="modal-metric-card">
                  <span className="label">Volume</span>
                  <span className="value">{selectedStock.volume.toLocaleString()}</span>
                </div>
              )}
            </div>

            {(selectedStock.country || selectedStock.sector) && (
              <div className="modal-tags">
                {selectedStock.country && <span className="tag">🌍 {selectedStock.country}</span>}
                {selectedStock.sector && <span className="tag">🏢 {selectedStock.sector}</span>}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default StockExplorer;
