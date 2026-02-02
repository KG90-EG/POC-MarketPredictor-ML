import React, { useState } from "react";
import PropTypes from "prop-types";
import "./PriceAlert.css";

/**
 * PriceAlert Component
 * Allows setting price alerts for watchlist items
 */
function PriceAlert({ ticker, currentPrice, existingAlert, onSave, onDelete }) {
  const [showForm, setShowForm] = useState(false);
  const [alertType, setAlertType] = useState(existingAlert?.type || "above");
  const [targetPrice, setTargetPrice] = useState(existingAlert?.target_price || "");
  const [notification, setNotification] = useState(existingAlert?.notification || "browser");

  const handleSave = () => {
    if (!targetPrice || parseFloat(targetPrice) <= 0) {
      alert("Please enter a valid target price");
      return;
    }

    onSave({
      ticker,
      type: alertType,
      target_price: parseFloat(targetPrice),
      notification,
      current_price: currentPrice,
    });

    setShowForm(false);
  };

  const handleDelete = () => {
    if (confirm("Delete this price alert?")) {
      onDelete(ticker);
      setShowForm(false);
    }
  };

  const getAlertStatus = () => {
    if (!existingAlert || !currentPrice) return null;

    const target = existingAlert.target_price;
    const current = currentPrice;

    if (existingAlert.type === "above" && current >= target) {
      return {
        triggered: true,
        message: `🚀 Target reached! Price is $${current.toFixed(2)} (target was $${target.toFixed(2)})`,
      };
    }
    if (existingAlert.type === "below" && current <= target) {
      return {
        triggered: true,
        message: `⚠️ Price dropped! Currently $${current.toFixed(2)} (target was $${target.toFixed(2)})`,
      };
    }

    const diff = alertType === "above" ? target - current : current - target;
    const percentAway = ((Math.abs(target - current) / current) * 100).toFixed(1);

    return {
      triggered: false,
      message: `Watching... ${percentAway}% away from target ($${target.toFixed(2)})`,
    };
  };

  const status = getAlertStatus();

  return (
    <div className="price-alert-container">
      {existingAlert && !showForm ? (
        <div className={`alert-badge ${status?.triggered ? "triggered" : "active"}`}>
          <div className="alert-info">
            <span className="alert-icon">
              {status?.triggered ? "🔔" : alertType === "above" ? "📈" : "📉"}
            </span>
            <div className="alert-details">
              <div className="alert-type">
                Alert: {alertType === "above" ? "Above" : "Below"} $
                {existingAlert.target_price.toFixed(2)}
              </div>
              {status && (
                <div className={`alert-status ${status.triggered ? "triggered" : ""}`}>
                  {status.message}
                </div>
              )}
            </div>
          </div>
          <div className="alert-actions">
            <button onClick={() => setShowForm(true)} className="edit-alert-btn" title="Edit alert">
              ✏️
            </button>
            <button onClick={handleDelete} className="delete-alert-btn" title="Delete alert">
              ✕
            </button>
          </div>
        </div>
      ) : showForm ? (
        <div className="alert-form">
          <h4>Set Price Alert for {ticker}</h4>
          <p className="current-price">Current: ${currentPrice?.toFixed(2) || "N/A"}</p>

          <div className="form-group">
            <label htmlFor={`alert-type-${ticker}`}>Alert Type</label>
            <select
              id={`alert-type-${ticker}`}
              value={alertType}
              onChange={(e) => setAlertType(e.target.value)}
              className="alert-select"
            >
              <option value="above">Price goes above</option>
              <option value="below">Price goes below</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor={`target-price-${ticker}`}>Target Price ($)</label>
            <input
              id={`target-price-${ticker}`}
              type="number"
              step="0.01"
              min="0"
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              placeholder="e.g., 150.00"
              className="alert-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor={`notification-${ticker}`}>Notification</label>
            <select
              id={`notification-${ticker}`}
              value={notification}
              onChange={(e) => setNotification(e.target.value)}
              className="alert-select"
            >
              <option value="browser">Browser notification</option>
              <option value="visual">Visual only (in app)</option>
              <option value="both">Both</option>
            </select>
          </div>

          <div className="form-actions">
            <button onClick={handleSave} className="save-alert-btn">
              💾 Save Alert
            </button>
            <button onClick={() => setShowForm(false)} className="cancel-alert-btn">
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <button onClick={() => setShowForm(true)} className="add-alert-btn" title="Set price alert">
          🔔 Set Alert
        </button>
      )}
    </div>
  );
}

PriceAlert.propTypes = {
  ticker: PropTypes.string.isRequired,
  currentPrice: PropTypes.number,
  existingAlert: PropTypes.shape({
    type: PropTypes.oneOf(["above", "below"]).isRequired,
    target_price: PropTypes.number.isRequired,
    notification: PropTypes.string,
    triggered: PropTypes.bool,
  }),
  onSave: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
};

export default PriceAlert;
