import { useState, useEffect } from 'react';
import { apiClient } from '../api';
import './AlertPanel.css';

function AlertPanel() {
  const [alerts, setAlerts] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState({
    unreadOnly: false,
    priority: '',
    assetType: ''
  });
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadAlerts();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadAlerts, 30000);
    return () => clearInterval(interval);
  }, [filter]);

  const loadAlerts = async () => {
    try {
      const params = new URLSearchParams();
      if (filter.unreadOnly) params.append('unread_only', 'true');
      if (filter.priority) params.append('priority', filter.priority);
      if (filter.assetType) params.append('asset_type', filter.assetType);
      params.append('limit', '50');

      const response = await apiClient.get(`/alerts?${params.toString()}`);
      setAlerts(response.data.alerts || []);
      setUnreadCount(response.data.unread_count || 0);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    }
  };

  const markAsRead = async (alertIds) => {
    try {
      await apiClient.post('/alerts/mark-read', alertIds);
      loadAlerts();
    } catch (error) {
      console.error('Failed to mark alerts as read:', error);
    }
  };

  const markAllAsRead = async () => {
    const unreadIds = alerts.filter(a => !a.read).map(a => a.alert_id);
    if (unreadIds.length > 0) {
      await markAsRead(unreadIds);
    }
  };

  const clearOldAlerts = async () => {
    if (confirm('Clear alerts older than 7 days?')) {
      try {
        await apiClient.delete('/alerts/clear?older_than_days=7');
        loadAlerts();
      } catch (error) {
        console.error('Failed to clear old alerts:', error);
      }
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'critical': return '🚨';
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '📌';
    }
  };

  const getAlertTypeLabel = (type) => {
    switch (type) {
      case 'signal_change': return 'Signal Changed';
      case 'high_confidence': return 'High Confidence';
      case 'price_spike': return 'Price Spike';
      case 'momentum_shift': return 'Momentum Shift';
      default: return type;
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <>
      {/* Alert Bell Icon */}
      <button
        className="alert-bell"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Notifications"
      >
        🔔
        {unreadCount > 0 && (
          <span className="alert-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
        )}
      </button>

      {/* Alert Panel */}
      {isOpen && (
        <div className="alert-panel">
          <div className="alert-header">
            <h3>Alerts</h3>
            <button className="close-btn" onClick={() => setIsOpen(false)}>✕</button>
          </div>

          <div className="alert-filters">
            <label>
              <input
                type="checkbox"
                checked={filter.unreadOnly}
                onChange={(e) => setFilter({ ...filter, unreadOnly: e.target.checked })}
              />
              Unread only
            </label>

            <select
              value={filter.priority}
              onChange={(e) => setFilter({ ...filter, priority: e.target.value })}
            >
              <option value="">All priorities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>

            <select
              value={filter.assetType}
              onChange={(e) => setFilter({ ...filter, assetType: e.target.value })}
            >
              <option value="">All types</option>
              <option value="stock">Stocks</option>
              <option value="crypto">Crypto</option>
            </select>
          </div>

          <div className="alert-actions">
            <button onClick={markAllAsRead} disabled={unreadCount === 0}>
              Mark all read
            </button>
            <button onClick={clearOldAlerts}>Clear old</button>
            <button onClick={loadAlerts}>🔄 Refresh</button>
          </div>

          <div className="alert-list">
            {alerts.length === 0 ? (
              <div className="alert-empty">
                <p>No alerts</p>
              </div>
            ) : (
              alerts.map((alert) => (
                <div
                  key={alert.alert_id}
                  className={`alert-item ${alert.read ? 'read' : 'unread'} priority-${alert.priority}`}
                  onClick={() => !alert.read && markAsRead([alert.alert_id])}
                >
                  <div className="alert-item-header">
                    <span className="alert-priority">{getPriorityIcon(alert.priority)}</span>
                    <span className="alert-type">{getAlertTypeLabel(alert.alert_type)}</span>
                    <span className="alert-time">{formatTime(alert.timestamp)}</span>
                  </div>

                  <div className="alert-item-body">
                    <div className="alert-symbol">
                      <strong>{alert.symbol}</strong> {alert.name && `(${alert.name})`}
                    </div>
                    <div className="alert-message">{alert.message}</div>

                    {alert.data && (
                      <div className="alert-details">
                        {alert.data.old_signal && (
                          <span className="detail-badge">
                            {alert.data.old_signal} → {alert.data.new_signal}
                          </span>
                        )}
                        {alert.data.confidence && (
                          <span className="detail-badge">
                            {alert.data.confidence.toFixed(0)}% confidence
                          </span>
                        )}
                        {alert.data.change_pct && (
                          <span className={`detail-badge ${alert.data.change_pct > 0 ? 'positive' : 'negative'}`}>
                            {alert.data.change_pct > 0 ? '+' : ''}{alert.data.change_pct.toFixed(1)}%
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Overlay */}
      {isOpen && <div className="alert-overlay" onClick={() => setIsOpen(false)} />}
    </>
  );
}

export default AlertPanel;
