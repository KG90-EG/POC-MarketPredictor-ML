import { useEffect, useCallback } from "react";

/**
 * Analytics Integration Component
 *
 * Provides comprehensive analytics tracking including:
 * - Page views
 * - User interactions
 * - Custom events
 * - Performance metrics
 * - Error tracking
 * - User journey tracking
 */

class Analytics {
  constructor() {
    this.queue = [];
    this.sessionId = null;
    this.userId = null;
    this.isInitialized = false;
    this.config = {
      endpoint: "/api/analytics/events",
      batchSize: 10,
      flushInterval: 5000, // 5 seconds
      debug: false,
    };
  }

  // Initialize analytics
  init(config = {}) {
    if (this.isInitialized) {
      console.warn("[Analytics] Already initialized");
      return;
    }

    this.config = { ...this.config, ...config };

    // Get or create session ID
    this.sessionId = sessionStorage.getItem("analytics_session_id");
    if (!this.sessionId) {
      this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem("analytics_session_id", this.sessionId);
    }

    // Get or create user ID
    this.userId = localStorage.getItem("analytics_user_id");
    if (!this.userId) {
      this.userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem("analytics_user_id", this.userId);
    }

    // Start flush interval
    this.flushInterval = setInterval(() => {
      this.flush();
    }, this.config.flushInterval);

    // Flush on page unload
    window.addEventListener("beforeunload", () => {
      this.flush(true);
    });

    this.isInitialized = true;
    this.log("Analytics initialized", { sessionId: this.sessionId, userId: this.userId });

    // Track initial page view
    this.trackPageView();
  }

  // Log debug messages
  log(...args) {
    if (this.config.debug) {
      console.log("[Analytics]", ...args);
    }
  }

  // Add event to queue
  track(eventName, properties = {}) {
    if (!this.isInitialized) {
      console.warn("[Analytics] Not initialized. Call init() first.");
      return;
    }

    const event = {
      eventName,
      properties,
      sessionId: this.sessionId,
      userId: this.userId,
      timestamp: Date.now(),
      url: window.location.href,
      pathname: window.location.pathname,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
      screenSize: `${window.innerWidth}x${window.innerHeight}`,
      language: navigator.language,
    };

    this.queue.push(event);
    this.log("Event tracked:", event);

    // Auto-flush if batch size reached
    if (this.queue.length >= this.config.batchSize) {
      this.flush();
    }
  }

  // Track page view
  trackPageView(pageName = null) {
    this.track("page_view", {
      page: pageName || document.title,
      pathname: window.location.pathname,
      hash: window.location.hash,
    });
  }

  // Track click events
  trackClick(element, label = null) {
    this.track("click", {
      element: element.tagName,
      elementId: element.id,
      elementClass: element.className,
      label: label || element.innerText?.substring(0, 50) || element.getAttribute("aria-label"),
      x: event?.clientX,
      y: event?.clientY,
    });
  }

  // Track form submission
  trackFormSubmit(formName, success = true, data = {}) {
    this.track("form_submit", {
      formName,
      success,
      ...data,
    });
  }

  // Track search
  trackSearch(query, resultsCount = null) {
    this.track("search", {
      query,
      resultsCount,
    });
  }

  // Track feature usage
  trackFeature(featureName, action = "use", data = {}) {
    this.track("feature_usage", {
      feature: featureName,
      action,
      ...data,
    });
  }

  // Track errors
  trackError(error, errorInfo = {}) {
    this.track("error", {
      message: error.message,
      stack: error.stack?.substring(0, 500),
      ...errorInfo,
    });
  }

  // Track performance metrics
  trackPerformance(metricName, value, unit = "ms") {
    this.track("performance", {
      metric: metricName,
      value,
      unit,
    });
  }

  // Track user timing
  trackTiming(category, variable, time, label = null) {
    this.track("timing", {
      category,
      variable,
      time,
      label,
    });
  }

  // Track conversion
  trackConversion(conversionName, value = null, currency = "USD") {
    this.track("conversion", {
      conversion: conversionName,
      value,
      currency,
    });
  }

  // Track engagement
  trackEngagement(action, target, value = null) {
    this.track("engagement", {
      action,
      target,
      value,
    });
  }

  // Set user properties
  setUserProperties(properties) {
    this.track("user_properties", properties);
  }

  // Flush events to backend
  async flush(synchronous = false) {
    if (this.queue.length === 0) return;

    const events = [...this.queue];
    this.queue = [];

    const payload = {
      events,
      meta: {
        flushTime: Date.now(),
        sessionId: this.sessionId,
        userId: this.userId,
      },
    };

    this.log("Flushing events:", events.length);

    try {
      if (synchronous && navigator.sendBeacon) {
        // Use sendBeacon for synchronous flushing (on page unload)
        const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
        navigator.sendBeacon(this.config.endpoint, blob);
      } else {
        // Use fetch for normal flushing
        const response = await fetch(this.config.endpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        this.log("Events sent successfully");
      }

      // Also store in localStorage for backup
      this.storeLocally(events);
    } catch (error) {
      console.error("[Analytics] Failed to send events:", error);
      // Re-add events to queue on failure
      this.queue.unshift(...events);
    }
  }

  // Store events locally as backup
  storeLocally(events) {
    try {
      const stored = JSON.parse(localStorage.getItem("analytics_events") || "[]");
      stored.push(...events);

      // Keep only last 1000 events
      if (stored.length > 1000) {
        stored.splice(0, stored.length - 1000);
      }

      localStorage.setItem("analytics_events", JSON.stringify(stored));
    } catch (error) {
      console.warn("[Analytics] Failed to store events locally:", error);
    }
  }

  // Get stored events
  getStoredEvents() {
    try {
      return JSON.parse(localStorage.getItem("analytics_events") || "[]");
    } catch (error) {
      console.warn("[Analytics] Failed to retrieve stored events:", error);
      return [];
    }
  }

  // Clear stored events
  clearStoredEvents() {
    localStorage.removeItem("analytics_events");
  }

  // Destroy analytics instance
  destroy() {
    if (this.flushInterval) {
      clearInterval(this.flushInterval);
    }
    this.flush(true);
    this.isInitialized = false;
    this.log("Analytics destroyed");
  }
}

// Create singleton instance
const analytics = new Analytics();

// Export singleton
export default analytics;

/**
 * React Hook for Analytics
 */
export const useAnalytics = () => {
  const trackPageView = useCallback((pageName) => {
    analytics.trackPageView(pageName);
  }, []);

  const trackClick = useCallback((element, label) => {
    analytics.trackClick(element, label);
  }, []);

  const trackEvent = useCallback((eventName, properties) => {
    analytics.track(eventName, properties);
  }, []);

  const trackFeature = useCallback((featureName, action, data) => {
    analytics.trackFeature(featureName, action, data);
  }, []);

  const trackSearch = useCallback((query, resultsCount) => {
    analytics.trackSearch(query, resultsCount);
  }, []);

  const trackError = useCallback((error, errorInfo) => {
    analytics.trackError(error, errorInfo);
  }, []);

  const trackConversion = useCallback((conversionName, value, currency) => {
    analytics.trackConversion(conversionName, value, currency);
  }, []);

  useEffect(() => {
    // Track page view on mount
    trackPageView();
  }, [trackPageView]);

  return {
    trackPageView,
    trackClick,
    trackEvent,
    trackFeature,
    trackSearch,
    trackError,
    trackConversion,
    setUserProperties: analytics.setUserProperties.bind(analytics),
  };
};

/**
 * AnalyticsProvider Component
 * Initializes analytics and provides tracking throughout app
 */
export const AnalyticsProvider = ({ children, config = {} }) => {
  useEffect(() => {
    analytics.init({
      debug: import.meta.env.DEV,
      ...config,
    });

    return () => {
      analytics.destroy();
    };
  }, [config]);

  return <>{children}</>;
};

/**
 * Helper function to track Web Vitals
 */
export const trackWebVitals = () => {
  // Track FCP (First Contentful Paint)
  if ("PerformanceObserver" in window) {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === "first-contentful-paint") {
          analytics.trackPerformance("FCP", Math.round(entry.startTime));
        }
      }
    });
    observer.observe({ type: "paint", buffered: true });

    // Track LCP (Largest Contentful Paint)
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1];
      analytics.trackPerformance("LCP", Math.round(lastEntry.startTime));
    });
    lcpObserver.observe({ type: "largest-contentful-paint", buffered: true });

    // Track FID (First Input Delay)
    const fidObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        analytics.trackPerformance("FID", Math.round(entry.processingStart - entry.startTime));
      }
    });
    fidObserver.observe({ type: "first-input", buffered: true });

    // Track CLS (Cumulative Layout Shift)
    let clsValue = 0;
    const clsObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
          analytics.trackPerformance("CLS", Math.round(clsValue * 1000) / 1000, "score");
        }
      }
    });
    clsObserver.observe({ type: "layout-shift", buffered: true });
  }

  // Track page load time
  window.addEventListener("load", () => {
    const perfData = window.performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
    analytics.trackPerformance("PageLoad", pageLoadTime);
  });
};
