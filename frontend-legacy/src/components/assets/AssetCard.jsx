import React from "react";
import PropTypes from "prop-types";
import "./AssetCard.css";

/**
 * AssetCard - Display an individual asset in a ranking list
 *
 * Features:
 * - Shows: rank, ticker, name, price, change%, score, signal
 * - Color-coded signal badges (BUY/SELL/HOLD)
 * - Risk indicator
 * - Sparkline chart placeholder
 * - Click to expand/select
 * - Hover state
 *
 * @param {object} props - Component props
 * @param {number} props.rank - Position in ranking
 * @param {string} props.ticker - Asset ticker symbol
 * @param {string} props.name - Asset name
 * @param {number} props.price - Current price
 * @param {number} props.change - Price change percentage (24h)
 * @param {number} props.score - AI score (0-100)
 * @param {string} props.signal - Trading signal (BUY/SELL/HOLD)
 * @param {string} props.riskLevel - Risk level (low/medium/high)
 * @param {string} props.assetType - Asset type (shares/digital_assets/commodities)
 * @param {Array} props.sparklineData - Array of price points for sparkline
 * @param {boolean} props.isSelected - Whether card is selected
 * @param {function} props.onClick - Click handler
 * @param {string} props.currency - Currency symbol
 */
export function AssetCard({
  rank,
  ticker,
  name,
  price,
  change,
  score,
  signal,
  riskLevel = "medium",
  assetType = "shares",
  sparklineData,
  isSelected = false,
  onClick,
  currency = "$",
}) {
  const formatPrice = (val) => {
    if (val === undefined || val === null) return "--";
    if (val >= 1000)
      return `${currency}${val.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
    if (val >= 1) return `${currency}${val.toFixed(2)}`;
    return `${currency}${val.toFixed(4)}`;
  };

  const formatChange = (val) => {
    if (val === undefined || val === null) return "--";
    const sign = val >= 0 ? "+" : "";
    return `${sign}${val.toFixed(2)}%`;
  };

  const getSignalClass = (sig) => {
    switch (sig?.toUpperCase()) {
      case "BUY":
      case "STRONG_BUY":
        return "asset-card__signal--buy";
      case "SELL":
      case "STRONG_SELL":
        return "asset-card__signal--sell";
      default:
        return "asset-card__signal--hold";
    }
  };

  const getScoreClass = (sc) => {
    if (sc >= 70) return "asset-card__score--high";
    if (sc >= 40) return "asset-card__score--medium";
    return "asset-card__score--low";
  };

  const getRiskIcon = (risk) => {
    switch (risk?.toLowerCase()) {
      case "low":
        return "🟢";
      case "high":
        return "🔴";
      default:
        return "🟡";
    }
  };

  const getAssetIcon = (type) => {
    switch (type) {
      case "digital_assets":
        return "🪙";
      case "commodities":
        return "🛢️";
      default:
        return "📈";
    }
  };

  return (
    <div
      className={`asset-card ${isSelected ? "asset-card--selected" : ""}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick?.();
        }
      }}
      aria-pressed={isSelected}
    >
      {/* Rank */}
      <div className="asset-card__rank">#{rank}</div>

      {/* Asset Info */}
      <div className="asset-card__info">
        <div className="asset-card__header">
          <span className="asset-card__icon" aria-hidden="true">
            {getAssetIcon(assetType)}
          </span>
          <span className="asset-card__ticker">{ticker}</span>
          <span className="asset-card__risk" title={`Risk: ${riskLevel}`}>
            {getRiskIcon(riskLevel)}
          </span>
        </div>
        <div className="asset-card__name">{name}</div>
      </div>

      {/* Price & Change */}
      <div className="asset-card__price-section">
        <div className="asset-card__price">{formatPrice(price)}</div>
        <div
          className={`asset-card__change ${change >= 0 ? "asset-card__change--positive" : "asset-card__change--negative"}`}
        >
          {formatChange(change)}
        </div>
      </div>

      {/* Sparkline Placeholder */}
      {sparklineData && sparklineData.length > 0 && (
        <div className="asset-card__sparkline">
          <Sparkline data={sparklineData} positive={change >= 0} />
        </div>
      )}

      {/* Score */}
      <div className={`asset-card__score ${getScoreClass(score)}`}>
        <span className="asset-card__score-value">{score?.toFixed(0) ?? "--"}</span>
        <span className="asset-card__score-label">Score</span>
      </div>

      {/* Signal */}
      <div className={`asset-card__signal ${getSignalClass(signal)}`}>{signal || "HOLD"}</div>
    </div>
  );
}

/**
 * Simple Sparkline component
 */
function Sparkline({ data, positive, width = 60, height = 24 }) {
  if (!data || data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data
    .map((val, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((val - min) / range) * height;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className="sparkline"
      aria-hidden="true"
    >
      <polyline
        points={points}
        fill="none"
        stroke={positive ? "#10b981" : "#ef4444"}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

AssetCard.propTypes = {
  rank: PropTypes.number.isRequired,
  ticker: PropTypes.string.isRequired,
  name: PropTypes.string,
  price: PropTypes.number,
  change: PropTypes.number,
  score: PropTypes.number,
  signal: PropTypes.string,
  riskLevel: PropTypes.oneOf(["low", "medium", "high"]),
  assetType: PropTypes.oneOf(["shares", "digital_assets", "commodities"]),
  sparklineData: PropTypes.arrayOf(PropTypes.number),
  isSelected: PropTypes.bool,
  onClick: PropTypes.func,
  currency: PropTypes.string,
};

export default AssetCard;
