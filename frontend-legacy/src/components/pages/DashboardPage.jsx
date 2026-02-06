import React, { useState, useCallback } from "react";
import PropTypes from "prop-types";
import { Dashboard, Panel, Header, Footer } from "../layout";
import TopAssetsPanel from "../assets/TopAssetsPanel";
import "./DashboardPage.css";

/**
 * DashboardPage - Main multi-asset trading dashboard page
 *
 * Uses the new Dashboard layout with:
 * - Header with theme toggle, settings, help
 * - Left panel: Trading signals
 * - Center panel: Top Assets with tabs
 * - Right panel: Backtest/Analysis
 * - Footer with market regime and status
 */
export function DashboardPage({
  darkMode = false,
  onToggleDarkMode,
  onOpenSettings,
  onOpenHelp,
  onAssetClick,
  marketRegime = "neutral",
  connectionStatus = "connected",
}) {
  const [lastUpdate] = useState(new Date());

  // Handle asset selection
  const handleAssetClick = useCallback(
    (asset) => {
      if (onAssetClick) {
        onAssetClick(asset);
      }
    },
    [onAssetClick]
  );

  return (
    <Dashboard
      className={darkMode ? "dark-mode" : ""}
      header={
        <Header
          title="Market Predictor"
          darkMode={darkMode}
          onToggleDarkMode={onToggleDarkMode}
          onOpenSettings={onOpenSettings}
          onOpenHelp={onOpenHelp}
        />
      }
      signalsPanel={
        <Panel id="signals" title="Trading Signals" icon="🎯" defaultCollapsed={false}>
          <SignalsPlaceholder />
        </Panel>
      }
      assetsPanel={
        <Panel id="assets" title="Top Assets" icon="📊" collapsible={false}>
          <TopAssetsPanel onAssetClick={handleAssetClick} limit={10} />
        </Panel>
      }
      backtestPanel={
        <Panel id="backtest" title="Backtest" icon="📈" defaultCollapsed={false}>
          <BacktestPlaceholder />
        </Panel>
      }
      footer={
        <Footer
          marketRegime={marketRegime}
          lastUpdate={lastUpdate}
          connectionStatus={connectionStatus}
          version="2.0.0"
        />
      }
    />
  );
}

// Placeholder components - will be replaced with real components
function SignalsPlaceholder() {
  return (
    <div className="placeholder-content">
      <p className="placeholder-text">🎯 Trading Signals</p>
      <p className="placeholder-subtext">Buy/Sell opportunities will appear here</p>
      <div className="placeholder-items">
        <div className="placeholder-item placeholder-item--buy">
          <span>AAPL</span>
          <span className="badge badge--buy">BUY</span>
        </div>
        <div className="placeholder-item placeholder-item--sell">
          <span>TSLA</span>
          <span className="badge badge--sell">SELL</span>
        </div>
        <div className="placeholder-item placeholder-item--hold">
          <span>GOOGL</span>
          <span className="badge badge--hold">HOLD</span>
        </div>
      </div>
    </div>
  );
}

function BacktestPlaceholder() {
  return (
    <div className="placeholder-content">
      <p className="placeholder-text">📈 Backtest Analysis</p>
      <p className="placeholder-subtext">Historical performance data</p>
      <div className="placeholder-stats">
        <div className="stat">
          <span className="stat-value">+23.5%</span>
          <span className="stat-label">YTD Return</span>
        </div>
        <div className="stat">
          <span className="stat-value">1.45</span>
          <span className="stat-label">Sharpe Ratio</span>
        </div>
        <div className="stat">
          <span className="stat-value">-8.2%</span>
          <span className="stat-label">Max Drawdown</span>
        </div>
      </div>
    </div>
  );
}

DashboardPage.propTypes = {
  darkMode: PropTypes.bool,
  onToggleDarkMode: PropTypes.func,
  onOpenSettings: PropTypes.func,
  onOpenHelp: PropTypes.func,
  onAssetClick: PropTypes.func,
  marketRegime: PropTypes.oneOf(["bull", "bear", "neutral", "volatile"]),
  connectionStatus: PropTypes.oneOf(["connected", "disconnected", "reconnecting"]),
};

export default DashboardPage;
