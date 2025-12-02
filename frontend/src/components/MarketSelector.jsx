import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { api } from '../api'

/**
 * Market view selector component
 * Single-selection mode: only one market can be selected at a time
 */
export function MarketSelector({ selectedMarket, onSelectionChange, disabled = false }) {
  const [markets, setMarkets] = useState([
    { id: 'Global', label: '🌐 Global', description: 'Top global stocks' },
    { id: 'United States', label: '🇺🇸 United States', description: 'US market leaders' },
    { id: 'Switzerland', label: '🇨🇭 Switzerland', description: 'Swiss companies' },
    { id: 'Germany', label: '🇩🇪 Germany', description: 'German companies' },
    { id: 'United Kingdom', label: '🇬🇧 United Kingdom', description: 'UK companies' },
    { id: 'France', label: '🇫🇷 France', description: 'French companies' },
    { id: 'Japan', label: '🇯🇵 Japan', description: 'Japanese companies' },
    { id: 'Canada', label: '🇨🇦 Canada', description: 'Canadian companies' }
  ])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Future: fetch available markets from backend
    // This allows dynamic market addition without frontend changes
    const fetchMarkets = async () => {
      try {
        setLoading(true)
        // When backend provides /api/markets endpoint, uncomment:
        // const response = await api.get('/markets')
        // setMarkets(response.data)
      } catch (error) {
        console.error('Failed to fetch markets:', error)
        // Keep default markets on error
      } finally {
        setLoading(false)
      }
    }

    // fetchMarkets() // Uncomment when backend supports it
  }, [])

  const selectMarket = (marketId) => {
    if (disabled) return
    // Single-selection: always replace with new selection
    onSelectionChange(marketId)
  }

  return (
    <div className="market-selector">
      <h3 className="market-selector-title">
        Select Market
        <span className="market-selector-count">
          (Single selection)
        </span>
      </h3>
      {loading ? (
        <div className="market-loading">Loading markets...</div>
      ) : (
        <div className="market-buttons">
          {markets.map(market => (
            <button
              key={market.id}
              className={`market-button ${selectedMarket === market.id ? 'selected' : ''}`}
              onClick={() => selectMarket(market.id)}
              disabled={disabled}
              title={market.description}
              aria-pressed={selectedMarket === market.id}
              aria-label={`Select ${market.label} market`}
            >
              {market.label}
              {selectedMarket === market.id && <span className="checkmark"> ✓</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

MarketSelector.propTypes = {
  selectedMarket: PropTypes.string.isRequired,
  onSelectionChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool
}

export default MarketSelector
