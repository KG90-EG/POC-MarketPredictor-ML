/**
 * ExplanationCard Component
 *
 * Displays AI-generated explanations for trading signals.
 * Shows explanation text, factor chips, and sentiment indicator.
 */

import React from "react";
import PropTypes from "prop-types";
import "./ExplanationCard.css";

const SENTIMENT_COLORS = {
  bullish: "#22c55e",
  bearish: "#ef4444",
  neutral: "#6b7280",
};

const SENTIMENT_ICONS = {
  bullish: "📈",
  bearish: "📉",
  neutral: "➡️",
};

export function ExplanationCard({
  ticker,
  signal,
  explanation,
  factors = [],
  sentiment = "neutral",
  confidence,
  cached = false,
  fallback = false,
  loading = false,
  onRefresh,
}) {
  if (loading) {
    return (
      <div className="explanation-card explanation-card--loading">
        <div className="explanation-skeleton">
          <div className="skeleton-line skeleton-line--title" />
          <div className="skeleton-line skeleton-line--text" />
          <div className="skeleton-line skeleton-line--text skeleton-line--short" />
          <div className="skeleton-factors">
            <div className="skeleton-chip" />
            <div className="skeleton-chip" />
            <div className="skeleton-chip" />
          </div>
        </div>
      </div>
    );
  }

  const sentimentColor = SENTIMENT_COLORS[sentiment] || SENTIMENT_COLORS.neutral;
  const sentimentIcon = SENTIMENT_ICONS[sentiment] || SENTIMENT_ICONS.neutral;

  return (
    <div className="explanation-card">
      {/* Header */}
      <div className="explanation-header">
        <div className="explanation-title">
          <span className="explanation-icon">🤖</span>
          <span>AI Analysis</span>
          {ticker && <span className="explanation-ticker">{ticker}</span>}
        </div>
        <div className="explanation-badges">
          {cached && (
            <span className="explanation-badge explanation-badge--cached" title="Cached response">
              ⚡ Cached
            </span>
          )}
          {fallback && (
            <span
              className="explanation-badge explanation-badge--fallback"
              title="Fallback response"
            >
              ⚠️ Basic
            </span>
          )}
          {onRefresh && (
            <button className="explanation-refresh" onClick={onRefresh} title="Refresh explanation">
              🔄
            </button>
          )}
        </div>
      </div>

      {/* Signal and Confidence */}
      {signal && (
        <div className="explanation-signal">
          <span className={`signal-badge signal-badge--${signal.toLowerCase()}`}>{signal}</span>
          {confidence !== undefined && (
            <span className="signal-confidence">{Math.round(confidence)}% confidence</span>
          )}
        </div>
      )}

      {/* Explanation Text */}
      <div className="explanation-text">{explanation || "No explanation available."}</div>

      {/* Factors */}
      {factors.length > 0 && (
        <div className="explanation-factors">
          <span className="factors-label">Key Factors:</span>
          <div className="factors-list">
            {factors.map((factor, index) => (
              <span key={index} className="factor-chip">
                {factor}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Sentiment */}
      <div className="explanation-sentiment" style={{ borderColor: sentimentColor }}>
        <span className="sentiment-icon">{sentimentIcon}</span>
        <span className="sentiment-label" style={{ color: sentimentColor }}>
          {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)} Sentiment
        </span>
      </div>

      {/* Disclaimer */}
      <div className="explanation-disclaimer">
        <span className="disclaimer-icon">ℹ️</span>
        AI-generated analysis. Not financial advice. Do your own research.
      </div>
    </div>
  );
}

ExplanationCard.propTypes = {
  ticker: PropTypes.string,
  signal: PropTypes.oneOf(["BUY", "SELL", "HOLD"]),
  explanation: PropTypes.string,
  factors: PropTypes.arrayOf(PropTypes.string),
  sentiment: PropTypes.oneOf(["bullish", "bearish", "neutral"]),
  confidence: PropTypes.number,
  cached: PropTypes.bool,
  fallback: PropTypes.bool,
  loading: PropTypes.bool,
  onRefresh: PropTypes.func,
};

export default ExplanationCard;
