import React from "react";
import PropTypes from "prop-types";
import "./InfoCard.css";

/**
 * InfoCard Component
 * Displays helpful information, tips, or documentation inline
 */
function InfoCard({ title, children, type = "info", icon, dismissible = false, onDismiss }) {
  const getIcon = () => {
    if (icon) return icon;

    switch (type) {
      case "tip":
        return "💡";
      case "warning":
        return "⚠️";
      case "success":
        return "✅";
      case "info":
      default:
        return "ℹ️";
    }
  };

  const getColorScheme = () => {
    switch (type) {
      case "tip":
        return {
          border: "#f59e0b",
          background: "linear-gradient(135deg, #fef3c715 0%, #fbbf2415 100%)",
          iconColor: "#f59e0b",
        };
      case "warning":
        return {
          border: "#dc3545",
          background: "linear-gradient(135deg, #fee2e215 0%, #fecaca15 100%)",
          iconColor: "#dc3545",
        };
      case "success":
        return {
          border: "#28a745",
          background: "linear-gradient(135deg, #d1fae515 0%, #86efac15 100%)",
          iconColor: "#28a745",
        };
      case "info":
      default:
        return {
          border: "#667eea",
          background: "linear-gradient(135deg, #667eea15 0%, #764ba215 100%)",
          iconColor: "#667eea",
        };
    }
  };

  const colorScheme = getColorScheme();

  return (
    <div
      className="info-card"
      style={{
        border: `2px solid ${colorScheme.border}`,
        background: colorScheme.background,
      }}
    >
      <div className="info-card-header">
        <span className="info-icon" style={{ color: colorScheme.iconColor }}>
          {getIcon()}
        </span>
        {title && <h4 className="info-title">{title}</h4>}
        {dismissible && (
          <button onClick={onDismiss} className="dismiss-btn" aria-label="Dismiss">
            ×
          </button>
        )}
      </div>
      <div className="info-content">{children}</div>
    </div>
  );
}

InfoCard.propTypes = {
  title: PropTypes.string,
  children: PropTypes.node.isRequired,
  type: PropTypes.oneOf(["info", "tip", "warning", "success"]),
  icon: PropTypes.string,
  dismissible: PropTypes.bool,
  onDismiss: PropTypes.func,
};

export default InfoCard;
