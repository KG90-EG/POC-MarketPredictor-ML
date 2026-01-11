import React from "react";

const AllocationBreakdown = ({ positions, limits }) => {
  if (!positions || positions.length === 0) {
    return (
      <div className="allocation-breakdown">
        <h2>Position Breakdown</h2>
        <p className="no-data">No positions to display.</p>
      </div>
    );
  }

  // Get limits
  const stockLimit = limits?.position_limits?.max_stock_position || 10;
  const cryptoLimit = limits?.position_limits?.max_crypto_position || 5;

  const getProgressColor = (allocation, limit) => {
    const percentage = (allocation / limit) * 100;
    if (percentage >= 100) return "#ef4444"; // red - over limit
    if (percentage >= 80) return "#f59e0b"; // orange - warning
    return "#10b981"; // green - good
  };

  const getSignalBadgeClass = (signal) => {
    if (!signal) return "signal-badge signal-hold";
    const normalized = signal.toLowerCase().replace(/\s+/g, "_");
    return `signal-badge signal-${normalized}`;
  };

  return (
    <div className="allocation-breakdown">
      <h2>Position Breakdown</h2>

      <div className="limits-info">
        <span className="limit-badge">Stock Limit: {stockLimit}%</span>
        <span className="limit-badge">Crypto Limit: {cryptoLimit}%</span>
      </div>

      <div className="positions-table-container">
        <table className="positions-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Type</th>
              <th>Allocation</th>
              <th>Score</th>
              <th>Signal</th>
              <th>Status</th>
              <th>Max Allowed</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((position, idx) => {
              const limit = position.asset_type === "stock" ? stockLimit : cryptoLimit;
              const progressColor = getProgressColor(position.allocation, limit);
              const progressWidth = Math.min((position.allocation / limit) * 100, 100);
              const isOverLimit = position.allocation > limit;

              return (
                <tr key={idx} className={isOverLimit ? "over-limit" : ""}>
                  <td className="ticker-cell">
                    <strong>{position.ticker}</strong>
                  </td>
                  <td className="type-cell">
                    <span className={`type-badge type-${position.asset_type}`}>
                      {position.asset_type}
                    </span>
                  </td>
                  <td className="allocation-cell">
                    <div className="allocation-wrapper">
                      <div className="allocation-value">{position.allocation.toFixed(1)}%</div>
                      <div className="allocation-bar">
                        <div
                          className="allocation-fill"
                          style={{
                            width: `${progressWidth}%`,
                            backgroundColor: progressColor,
                          }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="score-cell">
                    {position.score ? position.score.toFixed(0) : "N/A"}
                  </td>
                  <td className="signal-cell">
                    {position.signal && (
                      <span className={getSignalBadgeClass(position.signal)}>
                        {position.signal}
                      </span>
                    )}
                  </td>
                  <td className="status-cell">
                    {isOverLimit && (
                      <span className="status-badge status-violation">⛔ Over Limit</span>
                    )}
                    {!isOverLimit && position.allocation >= limit * 0.8 && (
                      <span className="status-badge status-warning">⚠ Near Limit</span>
                    )}
                    {!isOverLimit && position.allocation < limit * 0.8 && (
                      <span className="status-badge status-ok">✓ OK</span>
                    )}
                  </td>
                  <td className="limit-cell">{limit}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Summary Statistics */}
      <div className="breakdown-summary">
        <div className="summary-stat">
          <span className="stat-label">Total Positions:</span>
          <span className="stat-value">{positions.length}</span>
        </div>
        <div className="summary-stat">
          <span className="stat-label">Total Allocation:</span>
          <span className="stat-value">
            {positions.reduce((sum, p) => sum + p.allocation, 0).toFixed(1)}%
          </span>
        </div>
        <div className="summary-stat">
          <span className="stat-label">Avg Position Size:</span>
          <span className="stat-value">
            {(positions.reduce((sum, p) => sum + p.allocation, 0) / positions.length).toFixed(1)}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default AllocationBreakdown;
