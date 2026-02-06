import React from "react";
import PropTypes from "prop-types";
import "./Dashboard.css";

/**
 * Dashboard - Main multi-asset trading dashboard layout
 *
 * Uses CSS Grid for responsive 3-column layout:
 * - Desktop: 3 columns (signals | assets | backtest)
 * - Tablet: 2 columns
 * - Mobile: Single column, stacked
 *
 * @param {object} props - Component props
 * @param {React.ReactNode} props.header - Header component
 * @param {React.ReactNode} props.signalsPanel - Left panel for signals/opportunities
 * @param {React.ReactNode} props.assetsPanel - Main panel for asset rankings
 * @param {React.ReactNode} props.backtestPanel - Right panel for backtest/analysis
 * @param {React.ReactNode} props.footer - Footer component
 * @param {string} props.className - Additional CSS classes
 */
export function Dashboard({
  header,
  signalsPanel,
  assetsPanel,
  backtestPanel,
  footer,
  className = "",
}) {
  return (
    <div className={`dashboard ${className}`.trim()}>
      {header && <header className="dashboard__header">{header}</header>}

      <div className="dashboard__content">
        {signalsPanel && (
          <aside className="dashboard__signals" role="complementary" aria-label="Trading Signals">
            {signalsPanel}
          </aside>
        )}

        <main className="dashboard__assets" role="main" aria-label="Asset Rankings">
          {assetsPanel}
        </main>

        {backtestPanel && (
          <aside
            className="dashboard__backtest"
            role="complementary"
            aria-label="Backtest Analysis"
          >
            {backtestPanel}
          </aside>
        )}
      </div>

      {footer && <footer className="dashboard__footer">{footer}</footer>}
    </div>
  );
}

Dashboard.propTypes = {
  header: PropTypes.node,
  signalsPanel: PropTypes.node,
  assetsPanel: PropTypes.node.isRequired,
  backtestPanel: PropTypes.node,
  footer: PropTypes.node,
  className: PropTypes.string,
};

export default Dashboard;
