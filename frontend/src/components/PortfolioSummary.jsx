import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const PortfolioSummary = ({ portfolioData }) => {
  if (!portfolioData) {
    return (
      <div className="portfolio-summary">
        <h2>Portfolio Summary</h2>
        <p className="no-data">No portfolio data available. Add positions to see your portfolio analysis.</p>
      </div>
    );
  }

  const { analysis, positions } = portfolioData;

  // Calculate asset class allocation
  const assetAllocation = positions.reduce((acc, pos) => {
    const type = pos.asset_type === 'stock' ? 'Equity' : pos.asset_type === 'crypto' ? 'Crypto' : 'Cash';
    acc[type] = (acc[type] || 0) + pos.allocation;
    return acc;
  }, {});

  // Add cash if not 100% allocated
  const totalAllocation = Object.values(assetAllocation).reduce((sum, val) => sum + val, 0);
  if (totalAllocation < 100) {
    assetAllocation['Cash'] = 100 - totalAllocation;
  }

  const pieData = Object.entries(assetAllocation).map(([name, value]) => ({
    name,
    value: parseFloat(value.toFixed(2))
  }));

  const COLORS = {
    'Equity': '#2563eb',
    'Crypto': '#f59e0b',
    'Cash': '#10b981'
  };

  // Diversification score color
  const getDiversificationColor = (score) => {
    if (score >= 75) return '#10b981'; // green
    if (score >= 50) return '#f59e0b'; // orange
    return '#ef4444'; // red
  };

  const diversificationScore = analysis?.diversification_score || 0;

  return (
    <div className="portfolio-summary">
      <h2>Portfolio Summary</h2>

      <div className="portfolio-grid">
        {/* Allocation Pie Chart */}
        <div className="allocation-chart">
          <h3>Asset Allocation</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#6b7280'} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `${value}%`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>

          <div className="allocation-total">
            <strong>Total Allocation:</strong> {totalAllocation.toFixed(1)}%
          </div>
        </div>

        {/* Diversification Score */}
        <div className="diversification-score">
          <h3>Diversification</h3>
          <div
            className="score-circle"
            style={{
              borderColor: getDiversificationColor(diversificationScore),
              color: getDiversificationColor(diversificationScore)
            }}
          >
            <div className="score-value">{diversificationScore.toFixed(0)}</div>
            <div className="score-label">/ 100</div>
          </div>
          <div className="score-description">
            {diversificationScore >= 75 && '✓ Well diversified portfolio'}
            {diversificationScore >= 50 && diversificationScore < 75 && '⚠ Moderate diversification'}
            {diversificationScore < 50 && '⚠ Low diversification - consider rebalancing'}
          </div>
        </div>

        {/* Violations & Warnings */}
        <div className="portfolio-alerts">
          <h3>Alerts</h3>

          {analysis?.violations && analysis.violations.length > 0 && (
            <div className="violations-section">
              <h4 className="violations-header">⛔ Violations</h4>
              <ul className="violations-list">
                {analysis.violations.map((violation, idx) => (
                  <li key={idx} className="violation-item">{violation}</li>
                ))}
              </ul>
            </div>
          )}

          {analysis?.warnings && analysis.warnings.length > 0 && (
            <div className="warnings-section">
              <h4 className="warnings-header">⚠ Warnings</h4>
              <ul className="warnings-list">
                {analysis.warnings.map((warning, idx) => (
                  <li key={idx} className="warning-item">{warning}</li>
                ))}
              </ul>
            </div>
          )}

          {(!analysis?.violations || analysis.violations.length === 0) &&
           (!analysis?.warnings || analysis.warnings.length === 0) && (
            <div className="no-alerts">
              ✓ No violations or warnings. Portfolio is within limits.
            </div>
          )}
        </div>

        {/* Rebalancing Suggestions */}
        {analysis?.rebalancing_suggestions && analysis.rebalancing_suggestions.length > 0 && (
          <div className="rebalancing-suggestions">
            <h3>Rebalancing Suggestions</h3>
            <ul className="suggestions-list">
              {analysis.rebalancing_suggestions.map((suggestion, idx) => (
                <li key={idx} className="suggestion-item">
                  <strong>{suggestion.ticker}:</strong> {suggestion.action}
                  ({suggestion.current.toFixed(1)}% → {suggestion.suggested.toFixed(1)}%)
                  <span className="suggestion-reason"> - {suggestion.reason}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default PortfolioSummary;
