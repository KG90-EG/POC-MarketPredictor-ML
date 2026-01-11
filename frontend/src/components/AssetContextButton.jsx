import React, { useState } from "react";
import { apiClient } from "../api";
import "./AssetContextButton.css";

/**
 * Asset Context Button
 *
 * Shows LLM-generated context for a specific asset when clicked.
 * Used in StockRanking rows and detail sidebars.
 */
function AssetContextButton({ ticker, companyName }) {
  const [context, setContext] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isOpen, setIsOpen] = useState(false);

  const fetchAssetContext = async () => {
    setLoading(true);
    setError(null);
    setIsOpen(true);

    try {
      const response = await apiClient.get(`/api/context/asset/${ticker}`);
      setContext(response.data);
    } catch (err) {
      console.error(`Failed to fetch context for ${ticker}:`, err);
      
      // Handle error detail properly (could be string, object, or array)
      let errorMessage = "Failed to load asset context. Please try again.";
      
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

  const handleClose = () => {
    setIsOpen(false);
  };

  return (
    <>
      {/* Trigger Button */}
      <button
        className="asset-context-btn"
        onClick={fetchAssetContext}
        aria-label={`Get AI insights for ${ticker}`}
        title="Get AI insights"
      >
        <span className="btn-icon">💬</span>
        <span className="btn-text">Insights</span>
      </button>

      {/* Context Popover */}
      {isOpen && (
        <div className="asset-context-overlay" onClick={handleClose}>
          <div className="asset-context-popover" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="popover-header">
              <div className="popover-title">
                <h3>{ticker}</h3>
                {companyName && <span className="company-name">{companyName}</span>}
              </div>
              <button className="popover-close" onClick={handleClose} aria-label="Close">
                ✕
              </button>
            </div>

            {/* Content */}
            <div className="popover-content">
              {loading && (
                <div className="loading-state">
                  <div className="spinner"></div>
                  <p>Analyzing {ticker}...</p>
                </div>
              )}

              {error && (
                <div className="error-state">
                  <span className="error-icon">⚠️</span>
                  <p>{error}</p>
                  <button className="retry-btn" onClick={fetchAssetContext}>
                    Try Again
                  </button>
                </div>
              )}

              {context && !loading && (
                <>
                  {/* Asset Context */}
                  <div className="context-text">{context.context}</div>

                  {/* Key Metrics (if available) */}
                  {context.metrics && (
                    <div className="metrics-section">
                      <h4>Key Metrics</h4>
                      <div className="metrics-grid">
                        {context.metrics.composite_score && (
                          <div className="metric-item">
                            <span className="metric-label">Composite Score:</span>
                            <span className="metric-value">
                              {context.metrics.composite_score.toFixed(1)}
                            </span>
                          </div>
                        )}
                        {context.metrics.signal && (
                          <div className="metric-item">
                            <span className="metric-label">Signal:</span>
                            <span
                              className={`signal-badge signal-${context.metrics.signal.toLowerCase()}`}
                            >
                              {context.metrics.signal}
                            </span>
                          </div>
                        )}
                        {context.metrics.price && (
                          <div className="metric-item">
                            <span className="metric-label">Price:</span>
                            <span className="metric-value">
                              ${context.metrics.price.toFixed(2)}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Disclaimer */}
                  <div className="asset-disclaimer">
                    <p>
                      <strong>⚠️ Informational Only:</strong> This analysis is for educational
                      purposes and does not constitute investment advice. Always conduct your own
                      research.
                    </p>
                  </div>
                </>
              )}
            </div>

            {/* Footer */}
            <div className="popover-footer">
              <button className="close-btn" onClick={handleClose}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default AssetContextButton;
