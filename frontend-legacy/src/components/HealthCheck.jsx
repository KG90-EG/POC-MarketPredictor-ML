import { useState, useEffect } from "react";
import { api } from "../api";
import "./HealthCheck.css";

function HealthCheck({ isOpen, onClose }) {
  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);

  const checkHealth = async () => {
    try {
      setLoading(true);
      setError(null);

      const [healthData, metricsData] = await Promise.all([api.health(), api.metrics()]);

      setHealth(healthData);
      setMetrics(metricsData);
      setLastChecked(new Date());
    } catch (err) {
      const errorMessage =
        err.response?.data?.detail ||
        err.message ||
        "Unable to connect to server. Please ensure backend is running.";
      setError(errorMessage);
      console.error("Health check error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isOpen) return;
    checkHealth();
    // Auto-refresh every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [isOpen]);

  if (!isOpen) return null;

  const getStatusColor = (status) => {
    if (status === "ok" || status === "connected" || status === true) return "#10b981";
    if (status === "disconnected" || status === false) return "#ef4444";
    return "#f59e0b";
  };

  const getStatusIcon = (status) => {
    if (status === "ok" || status === "connected" || status === true) return "✓";
    if (status === "disconnected" || status === false) return "✗";
    return "⚠";
  };

  if (loading && !health) {
    return (
      <div className="health-overlay" onClick={onClose}>
        <div className="health-modal" onClick={(e) => e.stopPropagation()}>
          <button className="health-close" onClick={onClose}>
            ✕
          </button>
          <div className="health-loading">
            <div className="spinner"></div>
            <span>Checking system health...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="health-overlay" onClick={onClose}>
        <div className="health-modal" onClick={(e) => e.stopPropagation()}>
          <button className="health-close" onClick={onClose}>
            ✕
          </button>
          <div className="health-error">
            <span className="error-icon">✗</span>
            <div>
              <strong>Health Check Failed</strong>
              <p>{error}</p>
              <button onClick={checkHealth} className="retry-btn">
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="health-overlay" onClick={onClose}>
      <div className="health-modal" onClick={(e) => e.stopPropagation()}>
        <button className="health-close" onClick={onClose}>
          ✕
        </button>
        <div className="health-check">
          <div className="health-header">
            <h3>
              <span
                className="pulse-dot"
                style={{ backgroundColor: getStatusColor(health?.status) }}
              ></span>
              System Health
            </h3>
          </div>

          <div className="health-grid">
            {/* Backend Status */}
            <div className="health-item">
              <div className="health-item-header">
                <span className="health-icon" style={{ color: getStatusColor(health?.status) }}>
                  {getStatusIcon(health?.status)}
                </span>
                <span className="health-label">Backend API</span>
              </div>
              <span className="health-value">{health?.status || "unknown"}</span>
            </div>

            {/* Model Status */}
            <div className="health-item">
              <div className="health-item-header">
                <span
                  className="health-icon"
                  style={{ color: getStatusColor(health?.model_loaded) }}
                >
                  {getStatusIcon(health?.model_loaded)}
                </span>
                <span className="health-label">ML Model</span>
              </div>
              <span className="health-value">{health?.model_loaded ? "Loaded" : "Not loaded"}</span>
              {health?.model_path && (
                <span className="health-detail">{health.model_path.split("/").pop()}</span>
              )}
            </div>

            {/* OpenAI Status */}
            <div className="health-item">
              <div className="health-item-header">
                <span
                  className="health-icon"
                  style={{ color: getStatusColor(health?.openai_available) }}
                >
                  {getStatusIcon(health?.openai_available)}
                </span>
                <span className="health-label">AI Analysis</span>
              </div>
              <span className="health-value">
                {health?.openai_available ? "Available" : "Unavailable"}
              </span>
            </div>

            {/* Cache Backend */}
            <div className="health-item">
              <div className="health-item-header">
                <span
                  className="health-icon"
                  style={{ color: getStatusColor(health?.redis_status || health?.cache_backend) }}
                >
                  {getStatusIcon(
                    health?.redis_status === "connected" || health?.cache_backend === "redis"
                  )}
                </span>
                <span className="health-label">Cache</span>
              </div>
              <span className="health-value">{health?.cache_backend || "unknown"}</span>
              {health?.redis_status && (
                <span className="health-detail">Redis: {health.redis_status}</span>
              )}
            </div>
          </div>

          {/* Metrics Section */}
          {metrics && (
            <div className="metrics-section">
              <h4>Performance Metrics</h4>
              <div className="metrics-grid">
                {/* Cache Stats */}
                {metrics.cache_stats && (
                  <div className="metric-card">
                    <div className="metric-header">
                      <span>📦 Cache</span>
                    </div>
                    <div className="metric-stats">
                      <div className="metric-row">
                        <span>Backend:</span>
                        <strong>{metrics.cache_stats.backend}</strong>
                      </div>
                      {metrics.cache_stats.redis_keys !== undefined && (
                        <div className="metric-row">
                          <span>Keys:</span>
                          <strong>{metrics.cache_stats.redis_keys}</strong>
                        </div>
                      )}
                      {metrics.cache_stats.redis_hits !== undefined && (
                        <div className="metric-row">
                          <span>Hit Rate:</span>
                          <strong>
                            {Math.round(
                              (metrics.cache_stats.redis_hits /
                                (metrics.cache_stats.redis_hits +
                                  metrics.cache_stats.redis_misses) || 0) * 100
                            )}
                            %
                          </strong>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Rate Limiter Stats */}
                {metrics.rate_limiter_stats && (
                  <div className="metric-card">
                    <div className="metric-header">
                      <span>🔒 Rate Limiter</span>
                    </div>
                    <div className="metric-stats">
                      <div className="metric-row">
                        <span>Tracked IPs:</span>
                        <strong>{metrics.rate_limiter_stats.tracked_ips}</strong>
                      </div>
                      <div className="metric-row">
                        <span>Limit:</span>
                        <strong>{metrics.rate_limiter_stats.requests_per_minute} RPM</strong>
                      </div>
                    </div>
                  </div>
                )}

                {/* WebSocket Stats */}
                {metrics.websocket_stats && (
                  <div className="metric-card">
                    <div className="metric-header">
                      <span>🔴 WebSocket</span>
                    </div>
                    <div className="metric-stats">
                      <div className="metric-row">
                        <span>Connections:</span>
                        <strong>{metrics.websocket_stats.active_connections}</strong>
                      </div>
                      <div className="metric-row">
                        <span>Subscriptions:</span>
                        <strong>{metrics.websocket_stats.total_subscriptions}</strong>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {lastChecked && (
                <div className="health-footer">
                  <span className="last-checked">Last Updated: {lastChecked.toLocaleString()}</span>
                  <button onClick={checkHealth} disabled={loading} className="refresh-btn-small">
                    {loading ? "⟳" : "↻"}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default HealthCheck;
