import React from 'react'
import PropTypes from 'prop-types'

/**
 * Market view selector component
 * Allows users to select one or multiple markets to view
 */
export function MarketSelector({ selectedViews, onSelectionChange, disabled = false }) {
  const marketViews = [
    { id: 'Global', label: '🌐 Global', description: 'Top US stocks' },
    { id: 'United States', label: '🇺🇸 United States', description: 'US market leaders' },
    { id: 'Switzerland', label: '🇨🇭 Switzerland', description: 'Swiss companies' },
    { id: 'Germany', label: '🇩🇪 Germany', description: 'German companies' },
    { id: 'United Kingdom', label: '🇬🇧 United Kingdom', description: 'UK companies' },
    { id: 'France', label: '🇫🇷 France', description: 'French companies' },
    { id: 'Japan', label: '🇯🇵 Japan', description: 'Japanese companies' },
    { id: 'Canada', label: '🇨🇦 Canada', description: 'Canadian companies' }
  ]

  const toggleView = (viewId) => {
    if (disabled) return
    
    const newSelection = selectedViews.includes(viewId)
      ? selectedViews.filter(v => v !== viewId)
      : [...selectedViews, viewId]
    
    // Ensure at least one view is selected
    if (newSelection.length > 0) {
      onSelectionChange(newSelection)
    }
  }

  return (
    <div className="market-selector">
      <h3 className="market-selector-title">
        Select Markets
        <span className="market-selector-count">
          ({selectedViews.length} selected)
        </span>
      </h3>
      <div className="market-buttons">
        {marketViews.map(view => (
          <button
            key={view.id}
            className={`market-button ${selectedViews.includes(view.id) ? 'selected' : ''}`}
            onClick={() => toggleView(view.id)}
            disabled={disabled}
            title={view.description}
            aria-pressed={selectedViews.includes(view.id)}
          >
            {view.label}
            {selectedViews.includes(view.id) && <span className="checkmark"> ✓</span>}
          </button>
        ))}
      </div>
    </div>
  )
}

MarketSelector.propTypes = {
  selectedViews: PropTypes.arrayOf(PropTypes.string).isRequired,
  onSelectionChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool
}

export default MarketSelector
