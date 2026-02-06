import React, { useState, useRef, useEffect } from "react";
import PropTypes from "prop-types";
import "./Header.css";

/**
 * Header - Dashboard header component
 *
 * Features:
 * - Logo with link to home
 * - Optional search input
 * - Settings button
 * - Theme toggle (dark/light mode)
 * - Help button
 * - Mobile hamburger menu
 *
 * @param {object} props - Component props
 * @param {string} props.title - Application title
 * @param {boolean} props.darkMode - Current dark mode state
 * @param {function} props.onToggleDarkMode - Dark mode toggle handler
 * @param {function} props.onOpenSettings - Settings button handler
 * @param {function} props.onOpenHelp - Help button handler
 * @param {React.ReactNode} props.searchComponent - Optional search component slot
 * @param {React.ReactNode} props.statusIndicator - Optional status indicator (health, connection)
 * @param {React.ReactNode} props.children - Additional header content
 * @param {string} props.className - Additional CSS classes
 */
export function Header({
  title = "Market Predictor",
  darkMode = false,
  onToggleDarkMode,
  onOpenSettings,
  onOpenHelp,
  searchComponent,
  statusIndicator,
  children,
  className = "",
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const mobileMenuRef = useRef(null);

  // Close mobile menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (mobileMenuRef.current && !mobileMenuRef.current.contains(event.target)) {
        setMobileMenuOpen(false);
      }
    }

    if (mobileMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [mobileMenuOpen]);

  // Close mobile menu on escape key
  useEffect(() => {
    function handleEscape(e) {
      if (e.key === "Escape" && mobileMenuOpen) {
        setMobileMenuOpen(false);
      }
    }

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [mobileMenuOpen]);

  return (
    <header className={`header-component ${className}`.trim()}>
      <div className="header__container">
        {/* Logo / Brand */}
        <div className="header__brand">
          <a href="/" className="header__logo-link" aria-label="Go to homepage">
            <span className="header__logo" aria-hidden="true">
              📈
            </span>
            <span className="header__title">{title}</span>
          </a>
        </div>

        {/* Search (Optional) */}
        {searchComponent && <div className="header__search">{searchComponent}</div>}

        {/* Desktop Actions */}
        <nav className="header__nav" aria-label="Main navigation">
          {/* Status Indicator */}
          {statusIndicator && <div className="header__status">{statusIndicator}</div>}

          {/* Additional Content */}
          {children && <div className="header__custom">{children}</div>}

          {/* Theme Toggle */}
          <button
            className="header__action header__action--theme"
            onClick={onToggleDarkMode}
            aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            title={darkMode ? "Light mode" : "Dark mode"}
          >
            <span aria-hidden="true">{darkMode ? "☀️" : "🌙"}</span>
          </button>

          {/* Settings */}
          {onOpenSettings && (
            <button
              className="header__action header__action--settings"
              onClick={onOpenSettings}
              aria-label="Open settings"
              title="Settings"
            >
              <span aria-hidden="true">⚙️</span>
            </button>
          )}

          {/* Help */}
          {onOpenHelp && (
            <button
              className="header__action header__action--help"
              onClick={onOpenHelp}
              aria-label="Open help"
              title="Help"
            >
              <span aria-hidden="true">❓</span>
            </button>
          )}
        </nav>

        {/* Mobile Hamburger */}
        <button
          className={`header__hamburger ${mobileMenuOpen ? "header__hamburger--open" : ""}`}
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileMenuOpen}
          aria-controls="mobile-menu"
        >
          <span className="header__hamburger-line" />
          <span className="header__hamburger-line" />
          <span className="header__hamburger-line" />
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div
          id="mobile-menu"
          ref={mobileMenuRef}
          className="header__mobile-menu"
          role="navigation"
          aria-label="Mobile navigation"
        >
          {searchComponent && <div className="header__mobile-search">{searchComponent}</div>}

          <div className="header__mobile-actions">
            <button className="header__mobile-action" onClick={onToggleDarkMode}>
              <span aria-hidden="true">{darkMode ? "☀️" : "🌙"}</span>
              <span>{darkMode ? "Light Mode" : "Dark Mode"}</span>
            </button>

            {onOpenSettings && (
              <button
                className="header__mobile-action"
                onClick={() => {
                  onOpenSettings();
                  setMobileMenuOpen(false);
                }}
              >
                <span aria-hidden="true">⚙️</span>
                <span>Settings</span>
              </button>
            )}

            {onOpenHelp && (
              <button
                className="header__mobile-action"
                onClick={() => {
                  onOpenHelp();
                  setMobileMenuOpen(false);
                }}
              >
                <span aria-hidden="true">❓</span>
                <span>Help</span>
              </button>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

Header.propTypes = {
  title: PropTypes.string,
  darkMode: PropTypes.bool,
  onToggleDarkMode: PropTypes.func,
  onOpenSettings: PropTypes.func,
  onOpenHelp: PropTypes.func,
  searchComponent: PropTypes.node,
  statusIndicator: PropTypes.node,
  children: PropTypes.node,
  className: PropTypes.string,
};

export default Header;
