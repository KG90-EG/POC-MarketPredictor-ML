/**
 * Frontend Logger Utility
 * 
 * Provides structured logging with levels and optional backend integration.
 */

const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

class Logger {
  constructor() {
    this.level = process.env.NODE_ENV === 'production' ? LOG_LEVELS.WARN : LOG_LEVELS.DEBUG;
    this.enableBackendLogging = false; // Set to true to send errors to backend
  }

  setLevel(level) {
    this.level = LOG_LEVELS[level] || LOG_LEVELS.INFO;
  }

  enableBackend(enabled = true) {
    this.enableBackendLogging = enabled;
  }

  formatMessage(level, message, context = {}) {
    const timestamp = new Date().toISOString();
    return {
      timestamp,
      level,
      message,
      context,
      userAgent: navigator.userAgent,
      url: window.location.href
    };
  }

  async sendToBackend(logEntry) {
    if (!this.enableBackendLogging) return;

    try {
      await fetch('/api/frontend-logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logEntry)
      });
    } catch (err) {
      // Silent fail - don't break the app if logging fails
      console.warn('Failed to send log to backend:', err);
    }
  }

  debug(message, context) {
    if (this.level <= LOG_LEVELS.DEBUG) {
      const entry = this.formatMessage('DEBUG', message, context);
      console.debug(`[DEBUG] ${message}`, context);
    }
  }

  info(message, context) {
    if (this.level <= LOG_LEVELS.INFO) {
      const entry = this.formatMessage('INFO', message, context);
      console.info(`[INFO] ${message}`, context);
    }
  }

  warn(message, context) {
    if (this.level <= LOG_LEVELS.WARN) {
      const entry = this.formatMessage('WARN', message, context);
      console.warn(`[WARN] ${message}`, context);
    }
  }

  error(message, context) {
    if (this.level <= LOG_LEVELS.ERROR) {
      const entry = this.formatMessage('ERROR', message, context);
      console.error(`[ERROR] ${message}`, context);
      this.sendToBackend(entry);
    }
  }

  // Convenience method for API errors
  apiError(endpoint, error, context = {}) {
    this.error(`API Error: ${endpoint}`, {
      ...context,
      endpoint,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    });
  }

  // Track user interactions
  track(action, data = {}) {
    this.info(`User Action: ${action}`, data);
  }
}

// Export singleton instance
const logger = new Logger();

export default logger;
export { LOG_LEVELS };
