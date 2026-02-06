import React from "react";

const MarketRegimeStatus = ({ regime, loading }) => {
  if (loading || !regime) {
    return (
      <div className="regime-status-container loading">
        <span className="regime-loading">⏳ Loading market regime...</span>
      </div>
    );
  }

  // Map backend response fields to component variables
  const regimeType = regime.status || regime.regime; // 'status' from /api/regime, 'regime' from legacy
  const regime_score = regime.score ?? regime.regime_score ?? 50; // Default to 50 if missing
  const vix_level = regime.volatility?.regime || regime.vix_level;
  const sp500_trend = regime.trend?.regime || regime.sp500_trend;
  const summary = regime.summary;

  // Determine regime color and icon
  const getRegimeStyle = (type) => {
    switch (type) {
      case "RISK_ON":
        return {
          icon: "🟢",
          color: "#10b981",
          bgColor: "#d1fae5",
          darkBg: "#064e3b",
          label: "Risk-On",
          description: "Favorable market conditions - Growth opportunities",
        };
      case "NEUTRAL":
        return {
          icon: "🟡",
          color: "#f59e0b",
          bgColor: "#fef3c7",
          darkBg: "#78350f",
          label: "Neutral",
          description: "Mixed signals - Exercise caution",
        };
      case "RISK_OFF":
        return {
          icon: "🔴",
          color: "#ef4444",
          bgColor: "#fee2e2",
          darkBg: "#7f1d1d",
          label: "Risk-Off",
          description: "Defensive mode - Capital preservation priority",
        };
      default:
        return {
          icon: "⚪",
          color: "#6b7280",
          bgColor: "#f3f4f6",
          darkBg: "#374151",
          label: "Unknown",
          description: "Unable to determine market regime",
        };
    }
  };

  const style = getRegimeStyle(regimeType);

  return (
    <div className="regime-status-container">
      {/* Main Status Badge */}
      <div
        className="regime-badge"
        style={{
          backgroundColor: style.bgColor,
          borderLeft: `4px solid ${style.color}`,
        }}
      >
        <div className="regime-header">
          <span className="regime-icon">{style.icon}</span>
          <div className="regime-info">
            <div className="regime-label">
              <strong>Market Regime:</strong> {style.label}
            </div>
            <div className="regime-description">{style.description}</div>
          </div>
        </div>

        {/* Regime Score */}
        <div className="regime-score">
          <div className="score-bar-container">
            <div className="score-label-row">
              <span>Risk-Off</span>
              <span>Neutral</span>
              <span>Risk-On</span>
            </div>
            <div className="score-bar">
              <div
                className="score-fill"
                style={{
                  width: `${regime_score}%`,
                  backgroundColor: style.color,
                }}
              />
              <div className="score-marker" style={{ left: `${regime_score}%` }}>
                {regime_score.toFixed(0)}
              </div>
            </div>
          </div>
        </div>

        {/* Regime Details */}
        <div className="regime-details">
          <div className="regime-detail-item">
            <span className="detail-label">VIX Level:</span>
            <span className={`detail-value vix-${vix_level?.toLowerCase()}`}>
              {vix_level || "Unknown"}
            </span>
          </div>
          <div className="regime-detail-item">
            <span className="detail-label">S&P 500 Trend:</span>
            <span className={`detail-value trend-${sp500_trend?.toLowerCase()}`}>
              {sp500_trend || "Unknown"}
            </span>
          </div>
        </div>

        {/* Summary */}
        {summary && (
          <div className="regime-summary">
            <strong>Analysis:</strong> {summary}
          </div>
        )}
      </div>

      {/* Risk-Off Warning Banner */}
      {regimeType === "RISK_OFF" && (
        <div className="regime-warning-banner risk-off">
          <div className="warning-icon">⚠️</div>
          <div className="warning-content">
            <div className="warning-title">DEFENSIVE MODE ACTIVE</div>
            <div className="warning-message">
              Market conditions are unfavorable. BUY signals are suppressed. Consider reducing
              position sizes and increasing cash reserves.
            </div>
            <div className="warning-actions">
              <span className="warning-recommendation">
                Recommended: Max 5% per position, 30% minimum cash
              </span>
            </div>
          </div>
        </div>
      )}

      {/* High Volatility Warning */}
      {vix_level === "HIGH" && regimeType !== "RISK_OFF" && (
        <div className="regime-warning-banner high-volatility">
          <div className="warning-icon">⚡</div>
          <div className="warning-content">
            <div className="warning-title">HIGH VOLATILITY DETECTED</div>
            <div className="warning-message">
              Market volatility is elevated. Consider 50% of normal allocation sizes. Use wider
              stop-losses and avoid concentration.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketRegimeStatus;
