import React, { useRef, useState } from "react";
import PropTypes from "prop-types";
import "./Tabs.css";

/**
 * Tabs - Reusable tab component with keyboard navigation and ARIA support
 *
 * Features:
 * - Keyboard navigation (← → arrows, Enter, Home, End)
 * - ARIA roles (tablist, tab, tabpanel)
 * - Optional badge/counter per tab
 * - Mobile swipe support
 * - Controlled or uncontrolled mode
 *
 * @param {object} props - Component props
 * @param {Array} props.tabs - Array of tab definitions {id, label, icon?, count?, disabled?}
 * @param {string} props.activeTab - Currently active tab id (controlled)
 * @param {string} props.defaultTab - Default active tab (uncontrolled)
 * @param {function} props.onTabChange - Callback when tab changes
 * @param {string} props.size - Tab size: 'sm', 'md', 'lg'
 * @param {boolean} props.fullWidth - Whether tabs should fill container width
 * @param {string} props.className - Additional CSS classes
 */
export function Tabs({
  tabs,
  activeTab: controlledActiveTab,
  defaultTab,
  onTabChange,
  size = "md",
  fullWidth = false,
  className = "",
}) {
  // Support both controlled and uncontrolled modes
  const [internalActiveTab, setInternalActiveTab] = useState(defaultTab || tabs[0]?.id);
  const activeTab = controlledActiveTab ?? internalActiveTab;

  const tabListRef = useRef(null);
  const tabRefs = useRef({});

  // Swipe state for mobile
  const [touchStart, setTouchStart] = useState(null);
  const [touchEnd, setTouchEnd] = useState(null);
  const minSwipeDistance = 50;

  const handleTabChange = (tabId) => {
    if (controlledActiveTab === undefined) {
      setInternalActiveTab(tabId);
    }
    onTabChange?.(tabId);
  };

  const handleKeyDown = (e, tabId) => {
    const enabledTabs = tabs.filter((t) => !t.disabled);
    const currentIndex = enabledTabs.findIndex((t) => t.id === tabId);

    let nextIndex = currentIndex;

    switch (e.key) {
      case "ArrowLeft":
        e.preventDefault();
        nextIndex = currentIndex > 0 ? currentIndex - 1 : enabledTabs.length - 1;
        break;
      case "ArrowRight":
        e.preventDefault();
        nextIndex = currentIndex < enabledTabs.length - 1 ? currentIndex + 1 : 0;
        break;
      case "Home":
        e.preventDefault();
        nextIndex = 0;
        break;
      case "End":
        e.preventDefault();
        nextIndex = enabledTabs.length - 1;
        break;
      case "Enter":
      case " ":
        e.preventDefault();
        handleTabChange(tabId);
        return;
      default:
        return;
    }

    const nextTab = enabledTabs[nextIndex];
    if (nextTab) {
      tabRefs.current[nextTab.id]?.focus();
    }
  };

  // Touch handlers for mobile swipe
  const onTouchStart = (e) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;

    const distance = touchStart - touchEnd;
    const isSwipe = Math.abs(distance) > minSwipeDistance;

    if (isSwipe) {
      const enabledTabs = tabs.filter((t) => !t.disabled);
      const currentIndex = enabledTabs.findIndex((t) => t.id === activeTab);

      if (distance > 0 && currentIndex < enabledTabs.length - 1) {
        // Swipe left - next tab
        handleTabChange(enabledTabs[currentIndex + 1].id);
      } else if (distance < 0 && currentIndex > 0) {
        // Swipe right - previous tab
        handleTabChange(enabledTabs[currentIndex - 1].id);
      }
    }
  };

  return (
    <div
      className={`tabs tabs--${size} ${fullWidth ? "tabs--full-width" : ""} ${className}`.trim()}
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
    >
      <div ref={tabListRef} className="tabs__list" role="tablist" aria-label="Asset types">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          const isDisabled = tab.disabled;

          return (
            <button
              key={tab.id}
              ref={(el) => (tabRefs.current[tab.id] = el)}
              role="tab"
              id={`tab-${tab.id}`}
              aria-selected={isActive}
              aria-controls={`tabpanel-${tab.id}`}
              aria-disabled={isDisabled}
              tabIndex={isActive ? 0 : -1}
              className={`tabs__tab ${isActive ? "tabs__tab--active" : ""} ${isDisabled ? "tabs__tab--disabled" : ""}`}
              onClick={() => !isDisabled && handleTabChange(tab.id)}
              onKeyDown={(e) => handleKeyDown(e, tab.id)}
              disabled={isDisabled}
            >
              {tab.icon && <span className="tabs__icon">{tab.icon}</span>}
              <span className="tabs__label">{tab.label}</span>
              {tab.count !== undefined && <span className="tabs__count">{tab.count}</span>}
            </button>
          );
        })}
        <div
          className="tabs__indicator"
          style={{
            width: `${100 / tabs.length}%`,
            transform: `translateX(${tabs.findIndex((t) => t.id === activeTab) * 100}%)`,
          }}
        />
      </div>
    </div>
  );
}

Tabs.propTypes = {
  tabs: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      icon: PropTypes.node,
      count: PropTypes.number,
      disabled: PropTypes.bool,
    })
  ).isRequired,
  activeTab: PropTypes.string,
  defaultTab: PropTypes.string,
  onTabChange: PropTypes.func,
  size: PropTypes.oneOf(["sm", "md", "lg"]),
  fullWidth: PropTypes.bool,
  className: PropTypes.string,
};

/**
 * TabPanel - Container for tab content
 */
export function TabPanel({ id, activeTab, children, className = "" }) {
  const isActive = id === activeTab;

  return (
    <div
      role="tabpanel"
      id={`tabpanel-${id}`}
      aria-labelledby={`tab-${id}`}
      hidden={!isActive}
      className={`tabs__panel ${isActive ? "tabs__panel--active" : ""} ${className}`.trim()}
    >
      {isActive && children}
    </div>
  );
}

TabPanel.propTypes = {
  id: PropTypes.string.isRequired,
  activeTab: PropTypes.string.isRequired,
  children: PropTypes.node,
  className: PropTypes.string,
};

export default Tabs;
