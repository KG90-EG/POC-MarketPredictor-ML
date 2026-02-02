import React, { useState, useEffect } from 'react';
import './ExposureChart.css';

/**
 * ExposureChart Component
 * 
 * Visualizes portfolio exposure with limit warnings.
 * Shows allocation breakdown: Equity, Crypto, Cash
 * 
 * @param {Object} exposure - Current exposure percentages
 * @param {Object} limits - Position limits from regime
 * @param {boolean} defensiveMode - Whether defensive mode is active
 */
const ExposureChart = ({ exposure, limits, defensiveMode }) => {
  // Default values if not provided
  const equity = exposure?.equity_total || 0;
  const crypto = exposure?.crypto_total || 0;
  const cash = 100 - equity - crypto;
  
  // Check limit compliance
  const equityLimit = limits?.total_equity_max || 70;
  const cryptoLimit = limits?.total_crypto_max || 20;
  const minCash = limits?.min_cash || 10;
  
  const equityWarning = equity > equityLimit;
  const cryptoWarning = crypto > cryptoLimit;
  const cashWarning = cash < minCash;
  
  const hasWarning = equityWarning || cryptoWarning || cashWarning;
  
  return (
    <div className={`exposure-chart ${hasWarning ? 'has-warning' : ''}`}>
      <div className="exposure-header">
        <h3>Portfolio Exposure</h3>
        {defensiveMode && (
          <span className="defensive-tag">🔴 DEFENSIVE</span>
        )}
      </div>
      
      {/* Horizontal Bar */}
      <div className="exposure-bar">
        <div 
          className={`exposure-segment equity ${equityWarning ? 'over-limit' : ''}`}
          style={{ width: `${Math.min(equity, 100)}%` }}
          title={`Equities: ${equity.toFixed(1)}%`}
        />
        <div 
          className={`exposure-segment crypto ${cryptoWarning ? 'over-limit' : ''}`}
          style={{ width: `${Math.min(crypto, 100 - equity)}%` }}
          title={`Crypto: ${crypto.toFixed(1)}%`}
        />
        <div 
          className={`exposure-segment cash ${cashWarning ? 'under-limit' : ''}`}
          style={{ width: `${Math.max(cash, 0)}%` }}
          title={`Cash: ${cash.toFixed(1)}%`}
        />
      </div>
      
      {/* Limit Markers */}
      <div className="exposure-limits">
        <div 
          className="limit-marker equity-limit"
          style={{ left: `${equityLimit}%` }}
          title={`Equity Limit: ${equityLimit}%`}
        />
      </div>
      
      {/* Legend */}
      <div className="exposure-legend">
        <div className={`legend-item ${equityWarning ? 'warning' : ''}`}>
          <span className="legend-dot equity" />
          <span className="legend-label">Equities</span>
          <span className="legend-value">{equity.toFixed(1)}%</span>
          <span className="legend-limit">/ {equityLimit}%</span>
        </div>
        <div className={`legend-item ${cryptoWarning ? 'warning' : ''}`}>
          <span className="legend-dot crypto" />
          <span className="legend-label">Crypto</span>
          <span className="legend-value">{crypto.toFixed(1)}%</span>
          <span className="legend-limit">/ {cryptoLimit}%</span>
        </div>
        <div className={`legend-item ${cashWarning ? 'warning' : ''}`}>
          <span className="legend-dot cash" />
          <span className="legend-label">Cash</span>
          <span className="legend-value">{cash.toFixed(1)}%</span>
          <span className="legend-limit">min {minCash}%</span>
        </div>
      </div>
      
      {/* Warnings */}
      {hasWarning && (
        <div className="exposure-warnings">
          {equityWarning && (
            <div className="warning-item">
              ⚠️ Equity allocation exceeds limit ({equity.toFixed(1)}% > {equityLimit}%)
            </div>
          )}
          {cryptoWarning && (
            <div className="warning-item">
              ⚠️ Crypto allocation exceeds limit ({crypto.toFixed(1)}% > {cryptoLimit}%)
            </div>
          )}
          {cashWarning && (
            <div className="warning-item">
              ⚠️ Cash reserve below minimum ({cash.toFixed(1)}% < {minCash}%)
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ExposureChart;
