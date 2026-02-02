import React from "react";
import PropTypes from "prop-types";

/**
 * Search bar component for ticker lookup
 */
export function SearchBar({
  value,
  onChange,
  onSearch,
  onClear,
  placeholder = "Enter stock symbol (e.g., AAPL, TSLA)",
  disabled = false,
  loading = false,
}) {
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !disabled && !loading) {
      onSearch();
    }
  };

  const handleClear = () => {
    onChange("");
    if (onClear) {
      onClear();
    }
  };

  return (
    <div className="search-bar">
      <div className="search-input-group">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled || loading}
          className="search-input"
          aria-label="Stock search"
        />

        {value && (
          <button
            onClick={handleClear}
            className="search-clear-btn"
            aria-label="Clear search"
            type="button"
          >
            ✕
          </button>
        )}

        <button
          onClick={onSearch}
          disabled={disabled || loading || !value.trim()}
          className="search-btn"
          aria-label="Search"
        >
          {loading ? <span className="spinner-small">⌛</span> : "🔍 Search"}
        </button>
      </div>

      <div className="search-hint">Press Enter or click Search to look up a stock</div>
    </div>
  );
}

SearchBar.propTypes = {
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  onSearch: PropTypes.func.isRequired,
  onClear: PropTypes.func,
  placeholder: PropTypes.string,
  disabled: PropTypes.bool,
  loading: PropTypes.bool,
};

export default SearchBar;
