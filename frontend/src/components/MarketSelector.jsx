import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { api } from '../api'
import './MarketSelector.css'

/**
 * Market view selector component
 * Single-selection mode: only one market can be selected at a time
 */
export function MarketSelector({ selectedMarket, onSelectionChange, disabled = false }) {
  const [markets, setMarkets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch available markets from backend
    const fetchMarkets = async () => {
      try {
        setLoading(true)
        const response = await api.get('/countries')
        setMarkets(response.data.countries || [])
      } catch (error) {
        console.error('Failed to fetch markets:', error)
        // Fallback to default markets on error
        setMarkets([
          { id: 'Global', label: '🌐 Global', description: 'Top global stocks' },
          { id: 'United States', label: '🇺🇸 United States', description: 'US market leaders' },
          { id: 'Switzerland', label: '🇨🇭 Switzerland', description: 'Swiss companies' },
          { id: 'Germany', label: '🇩🇪 Germany', description: 'German companies' },
          { id: 'United Kingdom', label: '🇬🇧 United Kingdom', description: 'UK companies' },
          { id: 'France', label: '🇫🇷 France', description: 'French companies' },
          { id: 'Japan', label: '🇯🇵 Japan', description: 'Japanese companies' },
          { id: 'Canada', label: '🇨🇦 Canada', description: 'Canadian companies' }
        ])
      } finally {
        setLoading(false)
      }
    }

    fetchMarkets()
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
