import React from "react";
import PropTypes from "prop-types";

function HelpModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="help-modal-title"
    >
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Close help modal">
          ×
        </button>
        <h2 id="help-modal-title">📚 How to Use Trading Fun</h2>

        <div className="help-section">
          <h3>🚀 Getting Started</h3>
          <p>
            Rankings load automatically when you open the app. The system analyzes 50 popular stocks
            using machine learning and provides buy/sell recommendations.
          </p>
        </div>

        <div className="help-section">
          <h3>📊 Understanding the Rankings</h3>
          <ul>
            <li>
              <strong>Probability:</strong> ML model&apos;s confidence in stock outperformance
              (higher = better)
            </li>
            <li>
              <strong>Rank Badges:</strong> Top 3 stocks get gold, silver, and bronze badges
            </li>
            <li>
              <strong>Color Indicators:</strong> Green = price up, Red = price down
            </li>
          </ul>
        </div>

        <div className="help-section">
          <h3>🎯 Buy/Sell Signals</h3>
          <ul>
            <li>
              <strong>STRONG BUY</strong> (≥65%): High confidence opportunity
            </li>
            <li>
              <strong>BUY</strong> (≥55%): Good buying opportunity
            </li>
            <li>
              <strong>HOLD</strong> (45-54%): Maintain position
            </li>
            <li>
              <strong>CONSIDER SELLING</strong> (35-44%): Weak position
            </li>
            <li>
              <strong>SELL</strong> (&lt;35%): Exit recommended
            </li>
          </ul>
        </div>

        <div className="help-section">
          <h3>🔍 Navigation</h3>
          <ul>
            <li>
              <strong>Pagination:</strong> Use dropdown to jump to any page, or Previous/Next
              buttons
            </li>
            <li>
              <strong>Click a row:</strong> Opens detailed company information sidebar
            </li>
            <li>
              <strong>Search:</strong> Look up specific stocks not in the main ranking
            </li>
            <li>
              <strong>Refresh:</strong> Reload latest market data and rankings
            </li>
          </ul>
        </div>

        <div className="help-section">
          <h3>🤖 AI Analysis (Optional)</h3>
          <p>
            Add context like &quot;focus on tech stocks&quot; or &quot;conservative portfolio&quot;
            to get personalized AI-powered recommendations. The system provides specific buy/sell
            advice, risk assessment, and action plans.
          </p>
        </div>

        <div className="help-section">
          <h3>🌓 Theme Toggle</h3>
          <p>
            Click the sun/moon icon to switch between light and dark modes. Your preference is saved
            automatically.
          </p>
        </div>
      </div>
    </div>
  );
}

HelpModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default HelpModal;
