import React from "react";
import "./DefensiveModeBar.css";

/**
 * DefensiveModeBar Component
 *
 * Shows a prominent warning banner when market is in RISK_OFF regime.
 * Sticky at top of screen to ensure visibility.
 *
 * @param {boolean} active - Whether defensive mode is active
 * @param {Object} limits - Current position limits
 */
const DefensiveModeBar = ({ active, limits }) => {
  if (!active) return null;

  return (
    <div className="defensive-mode-bar" role="alert" aria-live="assertive">
      <div className="defensive-mode-content">
        <span className="defensive-mode-icon">🔴</span>
        <span className="defensive-mode-text">
          <strong>DEFENSIVE MODE ACTIVE</strong> — Position limits reduced by 50%
        </span>
        <span className="defensive-mode-details">
          Stock max: {limits?.single_stock_max || 5}% | Crypto max:{" "}
          {limits?.single_crypto_max || 2.5}% | Min cash: {limits?.min_cash || 30}%
        </span>
      </div>
    </div>
  );
};

export default DefensiveModeBar;
