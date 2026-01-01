import React, { useState, useRef, useEffect } from 'react'
import PropTypes from 'prop-types'
import './AutocompleteSearch.css'

/**
 * AutocompleteSearch Component
 * Search input with dropdown suggestions
 */
function AutocompleteSearch({ 
  suggestions = [], 
  onSearch, 
  placeholder = "Search...",
  loading = false,
  disabled = false 
}) {
  const [query, setQuery] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const wrapperRef = useRef(null)
  const inputRef = useRef(null)

  // Filter suggestions based on query
  const filteredSuggestions = React.useMemo(() => {
    if (!query.trim()) return []
    
    const lowerQuery = query.toLowerCase()
    return suggestions.filter(item => 
      (item.ticker || '').toLowerCase().includes(lowerQuery) ||
      (item.name || '').toLowerCase().includes(lowerQuery) ||
      (item.symbol || '').toLowerCase().includes(lowerQuery)
    ).slice(0, 10) // Limit to 10 results
  }, [query, suggestions])

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleInputChange = (e) => {
    const value = e.target.value
    setQuery(value)
    setShowSuggestions(value.trim().length > 0)
    setSelectedIndex(-1)
  }

  const handleSuggestionClick = (suggestion) => {
    const ticker = suggestion.ticker || suggestion.symbol
    setQuery(ticker)
    setShowSuggestions(false)
    onSearch(ticker)
  }

  const handleKeyDown = (e) => {
    if (!showSuggestions) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(prev => 
          prev < filteredSuggestions.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1)
        break
      case 'Enter':
        e.preventDefault()
        if (selectedIndex >= 0 && filteredSuggestions[selectedIndex]) {
          handleSuggestionClick(filteredSuggestions[selectedIndex])
        } else if (query.trim()) {
          setShowSuggestions(false)
          onSearch(query.trim().toUpperCase())
        }
        break
      case 'Escape':
        setShowSuggestions(false)
        setSelectedIndex(-1)
        break
      default:
        break
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      setShowSuggestions(false)
      onSearch(query.trim().toUpperCase())
    }
  }

  return (
    <div className="autocomplete-wrapper" ref={wrapperRef}>
      <form onSubmit={handleSubmit} className="autocomplete-form">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => query.trim() && setShowSuggestions(true)}
          placeholder={placeholder}
          disabled={disabled || loading}
          className="autocomplete-input"
          aria-label="Search stocks"
          aria-autocomplete="list"
          aria-controls="autocomplete-suggestions"
          aria-expanded={showSuggestions}
          autoComplete="off"
        />
        <button
          type="submit"
          disabled={disabled || loading || !query.trim()}
          className="autocomplete-submit"
          aria-label="Search"
        >
          {loading ? '⏳' : '🔍'}
        </button>
      </form>

      {/* Suggestions Dropdown */}
      {showSuggestions && filteredSuggestions.length > 0 && (
        <ul 
          id="autocomplete-suggestions"
          className="autocomplete-suggestions"
          role="listbox"
        >
          {filteredSuggestions.map((suggestion, index) => {
            const ticker = suggestion.ticker || suggestion.symbol
            const isSelected = index === selectedIndex

            return (
              <li
                key={ticker}
                onClick={() => handleSuggestionClick(suggestion)}
                className={`autocomplete-suggestion ${isSelected ? 'selected' : ''}`}
                role="option"
                aria-selected={isSelected}
              >
                <div className="suggestion-ticker">
                  <span className="ticker-symbol">{ticker}</span>
                  {suggestion.country && (
                    <span className="country-badge">{suggestion.country}</span>
                  )}
                </div>
                <div className="suggestion-name">{suggestion.name || 'N/A'}</div>
                {suggestion.sector && (
                  <div className="suggestion-sector">{suggestion.sector}</div>
                )}
                {suggestion.price && (
                  <div className="suggestion-price">
                    ${suggestion.price.toFixed(2)}
                    {suggestion.change && (
                      <span className={`change ${suggestion.change > 0 ? 'positive' : 'negative'}`}>
                        {suggestion.change > 0 ? '+' : ''}{suggestion.change.toFixed(2)}%
                      </span>
                    )}
                  </div>
                )}
              </li>
            )
          })}
        </ul>
      )}

      {/* No Results Message */}
      {showSuggestions && query.trim() && filteredSuggestions.length === 0 && (
        <div className="autocomplete-no-results">
          <span className="no-results-icon">🔍</span>
          <span>No matches found for &quot;{query}&quot;</span>
        </div>
      )}
    </div>
  )
}

AutocompleteSearch.propTypes = {
  suggestions: PropTypes.arrayOf(PropTypes.shape({
    ticker: PropTypes.string,
    symbol: PropTypes.string,
    name: PropTypes.string,
    country: PropTypes.string,
    sector: PropTypes.string,
    price: PropTypes.number,
    change: PropTypes.number
  })),
  onSearch: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  loading: PropTypes.bool,
  disabled: PropTypes.bool
}

export default AutocompleteSearch
