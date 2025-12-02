import React from 'react'
import PropTypes from 'prop-types'
import { MARKET_VIEWS } from '../constants'

/**
 * Market view selector component
 * Allows users to select one market to view at a time
 */
export function MarketSelector({ selectedView, onSelectionChange, disabled = false }) {
  const handleViewSelection = (viewId) => {
    if (disabled) return
    
    // Single selection mode - directly set the new view
    onSelectionChange(viewId)
  }

  return (
    <div className="market-selector">
      <h3 className="market-selector-title">
        Select Market
      </h3>
      <div className="market-buttons">
        {MARKET_VIEWS.map(view => {
          const isSelected = selectedView === view.id
          return (
            <button
              key={view.id}
              className={`market-button ${isSelected ? 'selected' : ''}`}
              onClick={() => handleViewSelection(view.id)}
              disabled={disabled}
              title={view.description}
              aria-pressed={isSelected}
            >
              {view.label}
              {isSelected && <span className="checkmark"> ✓</span>}
            </button>
          )
        })}
      </div>
    </div>
  )
}

MarketSelector.propTypes = {
  selectedView: PropTypes.string.isRequired,
  onSelectionChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool
}

export default MarketSelector
