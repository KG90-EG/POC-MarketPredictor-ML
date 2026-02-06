import React from "react";
import "./RiskBadge.css";

/**
 * RiskBadge Component
 *
 * Displays a color-coded risk score badge for an asset.
 *
 * Risk Levels:
 * - LOW (0-40): Green - Safe for larger positions
 * - MEDIUM (41-70): Yellow - Standard limits apply
 * - HIGH (71-100): Red - Position size reduced 50%
 *
 * @param {number} score - Risk score 0-100
 * @param {string} level - Risk level (LOW, MEDIUM, HIGH)
 * @param {Object} breakdown - Optional breakdown for tooltip
 * @param {boolean} compact - Show compact version
 */
const RiskBadge = ({ score, level, breakdown, compact = false }) => {
  // Determine color class based on level or score
  const getColorClass = () => {
    if (level === "LOW" || score <= 40) return "risk-low";
    if (level === "HIGH" || score > 70) return "risk-high";
    return "risk-medium";
  };

  // Format the breakdown tooltip
  const getTooltipContent = () => {
    if (!breakdown) return `Risk Score: ${score}/100`;
    return `Volatility: ${breakdown.volatility}\nDrawdown: ${breakdown.drawdown}\nCorrelation: ${breakdown.correlation}`;
  };

  if (compact) {
    return (
      <span className={`risk-badge-compact ${getColorClass()}`} title={getTooltipContent()}>
        {score}
      </span>
    );
  }

  return (
    <div className={`risk-badge ${getColorClass()}`} title={getTooltipContent()}>
      <span className="risk-badge-score">{score}</span>
      <span className="risk-badge-label">{level || "RISK"}</span>
      {breakdown && (
        <div className="risk-badge-tooltip">
          <div className="tooltip-row">
            <span>Volatility</span>
            <span>{breakdown.volatility}</span>
          </div>
          <div className="tooltip-row">
            <span>Drawdown</span>
            <span>{breakdown.drawdown}</span>
          </div>
          <div className="tooltip-row">
            <span>Correlation</span>
            <span>{breakdown.correlation}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskBadge;
