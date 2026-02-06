import React, { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";
import "./Panel.css";

/**
 * Panel - Collapsible panel wrapper component
 *
 * Features:
 * - Collapsible on mobile with animated expand/collapse
 * - Persists collapsed state in localStorage
 * - Accessible with ARIA attributes
 * - Optional loading state
 *
 * @param {object} props - Component props
 * @param {string} props.id - Unique identifier for the panel (used for localStorage)
 * @param {string} props.title - Panel header title
 * @param {React.ReactNode} props.icon - Optional icon for the header
 * @param {boolean} props.defaultCollapsed - Initial collapsed state
 * @param {boolean} props.collapsible - Whether panel can be collapsed
 * @param {boolean} props.loading - Show loading state
 * @param {React.ReactNode} props.headerActions - Optional actions for header (buttons, etc.)
 * @param {React.ReactNode} props.children - Panel content
 * @param {string} props.className - Additional CSS classes
 */
export function Panel({
  id,
  title,
  icon,
  defaultCollapsed = false,
  collapsible = true,
  loading = false,
  headerActions,
  children,
  className = "",
}) {
  // Load initial state from localStorage or use default
  const [isCollapsed, setIsCollapsed] = useState(() => {
    if (typeof window === "undefined") return defaultCollapsed;
    try {
      const stored = localStorage.getItem(`panel-${id}-collapsed`);
      if (stored !== null && stored !== "undefined") {
        return JSON.parse(stored);
      }
    } catch {
      // Ignore localStorage errors
    }
    return defaultCollapsed;
  });

  const contentRef = useRef(null);
  const [contentHeight, setContentHeight] = useState("auto");

  // Update localStorage when collapsed state changes
  useEffect(() => {
    if (typeof window !== "undefined" && id) {
      localStorage.setItem(`panel-${id}-collapsed`, JSON.stringify(isCollapsed));
    }
  }, [isCollapsed, id]);

  // Calculate content height for animation
  useEffect(() => {
    if (contentRef.current) {
      setContentHeight(isCollapsed ? "0px" : `${contentRef.current.scrollHeight}px`);
    }
  }, [isCollapsed, children]);

  const handleToggle = () => {
    if (collapsible) {
      setIsCollapsed(!isCollapsed);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleToggle();
    }
  };

  return (
    <div
      className={`panel ${isCollapsed ? "panel--collapsed" : ""} ${loading ? "panel--loading" : ""} ${className}`.trim()}
      data-panel-id={id}
    >
      <div
        className="panel__header"
        onClick={collapsible ? handleToggle : undefined}
        onKeyDown={collapsible ? handleKeyDown : undefined}
        role={collapsible ? "button" : undefined}
        tabIndex={collapsible ? 0 : undefined}
        aria-expanded={collapsible ? !isCollapsed : undefined}
        aria-controls={collapsible ? `panel-content-${id}` : undefined}
      >
        <div className="panel__header-left">
          {icon && <span className="panel__icon">{icon}</span>}
          <h2 className="panel__title">{title}</h2>
        </div>

        <div className="panel__header-right">
          {headerActions && (
            <div className="panel__actions" onClick={(e) => e.stopPropagation()}>
              {headerActions}
            </div>
          )}

          {collapsible && (
            <span
              className={`panel__toggle ${isCollapsed ? "panel__toggle--collapsed" : ""}`}
              aria-hidden="true"
            >
              ▼
            </span>
          )}
        </div>
      </div>

      <div
        id={`panel-content-${id}`}
        ref={contentRef}
        className="panel__content"
        style={{ maxHeight: contentHeight }}
        aria-hidden={isCollapsed}
      >
        <div className="panel__content-inner">
          {loading ? (
            <div className="panel__loading">
              <div className="panel__loading-spinner" />
              <span>Loading...</span>
            </div>
          ) : (
            children
          )}
        </div>
      </div>
    </div>
  );
}

Panel.propTypes = {
  id: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  icon: PropTypes.node,
  defaultCollapsed: PropTypes.bool,
  collapsible: PropTypes.bool,
  loading: PropTypes.bool,
  headerActions: PropTypes.node,
  children: PropTypes.node,
  className: PropTypes.string,
};

export default Panel;
