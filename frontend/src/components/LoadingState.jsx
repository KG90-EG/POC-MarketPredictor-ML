import React from "react";
import PropTypes from "prop-types";
import "./LoadingState.css";

/**
 * LoadingState Component
 *
 * Displays loading indicators with optional progress tracking and messages.
 * Used across the app for async operations like data fetching and analysis.
 *
 * Features:
 * - Animated spinner
 * - Progress bar (optional)
 * - Customizable messages
 * - Item count display
 */
const LoadingState = ({
  message = "Loading...",
  progress = null,
  itemCount = null,
  itemLabel = "items",
  size = "medium",
}) => {
  const sizeClass = `loading-${size}`;

  return (
    <div className={`loading-container ${sizeClass}`}>
      <div className="loading-spinner">
        <div className="spinner"></div>
      </div>

      <div className="loading-content">
        <p className="loading-message">{message}</p>

        {itemCount !== null && (
          <p className="loading-items">
            Analyzing {itemCount} {itemLabel}...
          </p>
        )}

        {progress !== null && (
          <div className="progress-container">
            <div className="progress-bar-wrapper">
              <div
                className="progress-bar-fill"
                style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
              />
            </div>
            <span className="progress-text">{Math.round(progress)}%</span>
          </div>
        )}
      </div>
    </div>
  );
};

LoadingState.propTypes = {
  message: PropTypes.string,
  progress: PropTypes.number,
  itemCount: PropTypes.number,
  itemLabel: PropTypes.string,
  size: PropTypes.oneOf(["small", "medium", "large"]),
};

export default LoadingState;
