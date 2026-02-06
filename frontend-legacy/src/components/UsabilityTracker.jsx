import { useState, useEffect, useCallback } from "react";

/**
 * UsabilityTracker Component
 *
 * Tracks user interactions and behavior patterns for usability testing.
 * Captures metrics like:
 * - Click patterns and heatmap data
 * - Time spent on different sections
 * - Navigation paths
 * - Error encounters
 * - Task completion rates
 */

const UsabilityTracker = ({ enabled = false, sessionId = null }) => {
  const [session, setSession] = useState(null);
  const [events, setEvents] = useState([]);

  // Initialize tracking session
  useEffect(() => {
    if (!enabled) return;

    const newSession = {
      id: sessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      startTime: Date.now(),
      userAgent: navigator.userAgent,
      screenSize: `${window.innerWidth}x${window.innerHeight}`,
      viewport: `${window.visualViewport?.width || window.innerWidth}x${window.visualViewport?.height || window.innerHeight}`,
      language: navigator.language,
      events: [],
    };

    setSession(newSession);
    console.log("[UsabilityTracker] Session started:", newSession.id);

    return () => {
      if (events.length > 0) {
        exportSession();
      }
    };
  }, [enabled, sessionId]);

  // Track click events
  const trackClick = useCallback(
    (event) => {
      if (!enabled || !session) return;

      const clickData = {
        type: "click",
        timestamp: Date.now(),
        x: event.clientX,
        y: event.clientY,
        pageX: event.pageX,
        pageY: event.pageY,
        target: {
          tag: event.target.tagName,
          id: event.target.id,
          className: event.target.className,
          text: event.target.innerText?.substring(0, 50) || "",
        },
        path: event
          .composedPath()
          .slice(0, 5)
          .map((el) => ({
            tag: el.tagName,
            id: el.id,
            className: el.className,
          })),
      };

      setEvents((prev) => [...prev, clickData]);
    },
    [enabled, session]
  );

  // Track scroll events
  const trackScroll = useCallback(() => {
    if (!enabled || !session) return;

    const scrollData = {
      type: "scroll",
      timestamp: Date.now(),
      scrollX: window.scrollX,
      scrollY: window.scrollY,
      scrollHeight: document.documentElement.scrollHeight,
      clientHeight: document.documentElement.clientHeight,
    };

    setEvents((prev) => [...prev, scrollData]);
  }, [enabled, session]);

  // Track page visibility changes
  const trackVisibility = useCallback(() => {
    if (!enabled || !session) return;

    const visibilityData = {
      type: "visibility",
      timestamp: Date.now(),
      visible: !document.hidden,
    };

    setEvents((prev) => [...prev, visibilityData]);
  }, [enabled, session]);

  // Track navigation
  const trackNavigation = useCallback(
    (from, to) => {
      if (!enabled || !session) return;

      const navigationData = {
        type: "navigation",
        timestamp: Date.now(),
        from,
        to,
        method: "click", // could be 'back', 'forward', 'direct'
      };

      setEvents((prev) => [...prev, navigationData]);
    },
    [enabled, session]
  );

  // Track errors
  const trackError = useCallback(
    (error, errorInfo) => {
      if (!enabled || !session) return;

      const errorData = {
        type: "error",
        timestamp: Date.now(),
        message: error.message,
        stack: error.stack?.substring(0, 500),
        componentStack: errorInfo?.componentStack?.substring(0, 500),
      };

      setEvents((prev) => [...prev, errorData]);
    },
    [enabled, session]
  );

  // Track custom events
  const trackCustomEvent = useCallback(
    (eventName, data = {}) => {
      if (!enabled || !session) return;

      const customData = {
        type: "custom",
        name: eventName,
        timestamp: Date.now(),
        data,
      };

      setEvents((prev) => [...prev, customData]);
    },
    [enabled, session]
  );

  // Export session data
  const exportSession = useCallback(() => {
    if (!session || events.length === 0) return;

    const sessionData = {
      ...session,
      endTime: Date.now(),
      duration: Date.now() - session.startTime,
      events,
      statistics: {
        totalEvents: events.length,
        clickCount: events.filter((e) => e.type === "click").length,
        scrollCount: events.filter((e) => e.type === "scroll").length,
        errorCount: events.filter((e) => e.type === "error").length,
        navigationCount: events.filter((e) => e.type === "navigation").length,
      },
    };

    // Store in localStorage
    const existingSessions = JSON.parse(localStorage.getItem("usability_sessions") || "[]");
    existingSessions.push(sessionData);

    // Keep only last 50 sessions
    if (existingSessions.length > 50) {
      existingSessions.shift();
    }

    localStorage.setItem("usability_sessions", JSON.stringify(existingSessions));

    // Also log to console for debugging
    console.log("[UsabilityTracker] Session exported:", sessionData);

    // Send to backend if API is available
    sendToBackend(sessionData);
  }, [session, events]);

  // Send session data to backend
  const sendToBackend = async (sessionData) => {
    try {
      const response = await fetch("/api/usability/sessions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(sessionData),
      });

      if (response.ok) {
        console.log("[UsabilityTracker] Session data sent to backend");
      }
    } catch (error) {
      console.warn("[UsabilityTracker] Failed to send session data:", error);
    }
  };

  // Attach event listeners
  useEffect(() => {
    if (!enabled) return;

    document.addEventListener("click", trackClick);
    window.addEventListener("scroll", trackScroll, { passive: true });
    document.addEventListener("visibilitychange", trackVisibility);
    window.addEventListener("error", (e) => trackError(e.error, { componentStack: e.filename }));

    // Track scroll every 2 seconds max (throttled)
    let scrollTimeout;
    const throttledScroll = () => {
      if (scrollTimeout) return;
      scrollTimeout = setTimeout(() => {
        trackScroll();
        scrollTimeout = null;
      }, 2000);
    };
    window.addEventListener("scroll", throttledScroll, { passive: true });

    return () => {
      document.removeEventListener("click", trackClick);
      window.removeEventListener("scroll", trackScroll);
      document.removeEventListener("visibilitychange", trackVisibility);
      window.removeEventListener("scroll", throttledScroll);
    };
  }, [enabled, trackClick, trackScroll, trackVisibility, trackError]);

  // Export session on unmount or before page unload
  useEffect(() => {
    if (!enabled) return;

    const handleBeforeUnload = () => {
      exportSession();
    };

    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
      exportSession();
    };
  }, [enabled, exportSession]);

  // Expose tracking methods globally
  useEffect(() => {
    if (!enabled) return;

    window.usabilityTracker = {
      trackNavigation,
      trackError,
      trackCustomEvent,
      exportSession,
      getEvents: () => events,
      getSession: () => session,
    };

    return () => {
      delete window.usabilityTracker;
    };
  }, [enabled, trackNavigation, trackError, trackCustomEvent, exportSession, events, session]);

  // This component doesn't render anything
  return null;
};

export default UsabilityTracker;

// Helper function to analyze session data
export const analyzeUsabilityData = (sessions) => {
  if (!sessions || sessions.length === 0) {
    return {
      totalSessions: 0,
      averageDuration: 0,
      totalClicks: 0,
      totalErrors: 0,
      clickHeatmap: [],
      commonPaths: [],
      errorPatterns: [],
    };
  }

  const totalSessions = sessions.length;
  const totalDuration = sessions.reduce((sum, s) => sum + s.duration, 0);
  const averageDuration = totalDuration / totalSessions;

  const allEvents = sessions.flatMap((s) => s.events);
  const totalClicks = allEvents.filter((e) => e.type === "click").length;
  const totalErrors = allEvents.filter((e) => e.type === "error").length;

  // Generate click heatmap data
  const clickHeatmap = allEvents
    .filter((e) => e.type === "click")
    .map((e) => ({
      x: e.x,
      y: e.y,
      pageX: e.pageX,
      pageY: e.pageY,
      target: e.target,
    }));

  // Analyze common navigation paths
  const navigationEvents = allEvents.filter((e) => e.type === "navigation");
  const pathCounts = {};

  navigationEvents.forEach((nav) => {
    const path = `${nav.from} → ${nav.to}`;
    pathCounts[path] = (pathCounts[path] || 0) + 1;
  });

  const commonPaths = Object.entries(pathCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([path, count]) => ({ path, count }));

  // Analyze error patterns
  const errorEvents = allEvents.filter((e) => e.type === "error");
  const errorCounts = {};

  errorEvents.forEach((err) => {
    const key = err.message;
    errorCounts[key] = (errorCounts[key] || 0) + 1;
  });

  const errorPatterns = Object.entries(errorCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([error, count]) => ({ error, count }));

  return {
    totalSessions,
    averageDuration: Math.round(averageDuration / 1000), // in seconds
    totalClicks,
    totalErrors,
    clickHeatmap,
    commonPaths,
    errorPatterns,
    sessionsAnalyzed: sessions.length,
  };
};
