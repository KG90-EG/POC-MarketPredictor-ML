import React, { useState } from "react";
import { apiClient } from "../api";
import "./MarketContextModal.css";

/**
 * Market Context Modal
 *
 * Displays LLM-generated market insights without trading recommendations.
 * Complies with "No Automated Trading" Non-Goal.
 */
function MarketContextModal({ isOpen, onClose }) {
  const [marketContext, setMarketContext] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch market context when modal opens
  React.useEffect(() => {
    if (isOpen && !marketContext) {
      fetchMarketContext();
    }
  }, [isOpen]);

  const fetchMarketContext = async () => {
    setLoading(true);
    setError(null);

    try {
      // First, fetch current stock rankings (required by backend)
      const rankingsResponse = await apiClient.get("/ranking?country=Global");
      const rankings = rankingsResponse.data.results || [];
      
      // Convert to format expected by backend
      const rankingData = rankings.slice(0, 20).map(stock => ({
        ticker: stock.ticker,
        prob: stock.prob,
        signal: stock.signal
      }));

      // Then fetch market context with rankings
      const response = await apiClient.post("/api/context/market", {
        ranking: rankingData,
        user_context: "General market overview"
      });

      setMarketContext(response.data);
    } catch (err) {
      console.error("Failed to fetch market context:", err);
      
      // Handle error detail properly (could be string, object, or array)
      let errorMessage = "Failed to load market context. Please try again.";
      
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === "string") {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          // Validation errors from FastAPI
          errorMessage = detail.map(e => e.msg || JSON.stringify(e)).join(", ");
        } else if (typeof detail === "object") {
          errorMessage = detail.msg || JSON.stringify(detail);
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="market-context-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <h2>📊 Market Context</h2>
          <button className="close-btn" onClick={onClose} aria-label="Close modal">
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="modal-content">
          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Analyzing market conditions...</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
              <button className="retry-btn" onClick={fetchMarketContext}>
                Try Again
              </button>
            </div>
          )}

          {marketContext && !loading && (
            <>
              {/* Market Regime */}
              {marketContext.regime && (
                <div className="context-section">
                  <h3>Market Regime</h3>
                  <div
                    className={`regime-badge regime-${marketContext.regime.status.toLowerCase().replace(/\s+/g, "-")}`}
                  >
                    {marketContext.regime.status}
                  </div>
                  <div className="regime-details">
                    <div className="regime-item">
                      <span className="label">VIX:</span>
                      <span className="value">{marketContext.regime.vix.toFixed(2)}</span>
                    </div>
                    <div className="regime-item">
                      <span className="label">S&P 500 Trend:</span>
                      <span className="value">{marketContext.regime.sp500_trend}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* LLM Insights */}
              {marketContext.context && (
                <div className="context-section">
                  <h3>Market Insights</h3>
                  <div className="insights-content">{marketContext.context}</div>
                </div>
              )}

              {/* Top Stocks Preview (if included) */}
              {marketContext.top_stocks && marketContext.top_stocks.length > 0 && (
                <div className="context-section">
                  <h3>Top Ranked Stocks</h3>
                  <div className="top-stocks-grid">
                    {marketContext.top_stocks.slice(0, 5).map((stock) => (
                      <div key={stock.ticker} className="top-stock-item">
                        <div className="stock-ticker">{stock.ticker}</div>
                        <div className="stock-score">{stock.composite_score.toFixed(1)}</div>
                        <div className="stock-signal">{stock.signal}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Disclaimer */}
              <div className="context-disclaimer">
                <h4>⚠️ Important Disclaimer</h4>
                <p>
                  This analysis is for <strong>informational purposes only</strong> and does not
                  constitute investment advice. The system provides decision support, not trading
                  recommendations. Always conduct your own research and consult with a financial
                  advisor before making investment decisions.
                </p>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button className="close-footer-btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default MarketContextModal;
