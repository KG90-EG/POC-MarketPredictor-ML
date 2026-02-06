import React from "react";
import PropTypes from "prop-types";
import "./Footer.css";

/**
 * Footer - Dashboard footer component
 *
 * Features:
 * - Market regime indicator
 * - Last update timestamp
 * - Connection status
 * - Responsive layout
 *
 * @param {object} props - Component props
 * @param {string} props.marketRegime - Current market regime (bull/bear/neutral/volatile)
 * @param {Date|string} props.lastUpdate - Last data update timestamp
 * @param {string} props.connectionStatus - Connection status (connected/disconnected/reconnecting)
 * @param {string} props.version - Application version
 * @param {React.ReactNode} props.children - Additional footer content
 * @param {string} props.className - Additional CSS classes
 */
export function Footer({
  marketRegime = "neutral",
  lastUpdate,
  connectionStatus = "connected",
  version,
  children,
  className = "",
}) {
  // Format timestamp
  const formatTime = (date) => {
    if (!date) return "--:--";
    const d = date instanceof Date ? date : new Date(date);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  // Market regime config
  const regimeConfig = {
    bull: { icon: "🐂", label: "Bull Market", color: "#10b981" },
    bear: { icon: "🐻", label: "Bear Market", color: "#ef4444" },
    neutral: { icon: "➡️", label: "Neutral", color: "#6b7280" },
    volatile: { icon: "⚡", label: "High Volatility", color: "#f59e0b" },
  };

  const regime = regimeConfig[marketRegime] || regimeConfig.neutral;

  // Connection status config
  const connectionConfig = {
    connected: { icon: "🟢", label: "Connected", color: "#10b981" },
    disconnected: { icon: "🔴", label: "Disconnected", color: "#ef4444" },
    reconnecting: { icon: "🟡", label: "Reconnecting...", color: "#f59e0b" },
  };

  const connection = connectionConfig[connectionStatus] || connectionConfig.disconnected;

  return (
    <footer className={`footer-component ${className}`.trim()}>
      <div className="footer__container">
        {/* Left Section - Market Status */}
        <div className="footer__section footer__section--left">
          {/* Market Regime */}
          <div className="footer__indicator footer__indicator--regime" title={regime.label}>
            <span className="footer__icon" aria-hidden="true">
              {regime.icon}
            </span>
            <span className="footer__label" style={{ color: regime.color }}>
              {regime.label}
            </span>
          </div>

          {/* Last Update */}
          <div className="footer__indicator footer__indicator--update" title="Last data update">
            <span className="footer__icon" aria-hidden="true">
              🕐
            </span>
            <span className="footer__label">Updated: {formatTime(lastUpdate)}</span>
          </div>
        </div>

        {/* Center Section - Custom Content */}
        {children && <div className="footer__section footer__section--center">{children}</div>}

        {/* Right Section - Status */}
        <div className="footer__section footer__section--right">
          {/* Connection Status */}
          <div
            className="footer__indicator footer__indicator--connection"
            title={connection.label}
            role="status"
            aria-live="polite"
          >
            <span className="footer__icon" aria-hidden="true">
              {connection.icon}
            </span>
            <span className="footer__label">{connection.label}</span>
          </div>

          {/* Version */}
          {version && (
            <div className="footer__indicator footer__indicator--version">
              <span className="footer__label footer__label--muted">v{version}</span>
            </div>
          )}
        </div>
      </div>
    </footer>
  );
}

Footer.propTypes = {
  marketRegime: PropTypes.oneOf(["bull", "bear", "neutral", "volatile"]),
  lastUpdate: PropTypes.oneOfType([PropTypes.instanceOf(Date), PropTypes.string]),
  connectionStatus: PropTypes.oneOf(["connected", "disconnected", "reconnecting"]),
  version: PropTypes.string,
  children: PropTypes.node,
  className: PropTypes.string,
};

export default Footer;
