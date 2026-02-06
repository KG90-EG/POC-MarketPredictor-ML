import { useState, useEffect, useCallback } from 'react'

const API_BASE = ''

// Asset type tabs
const ASSET_TYPES = [
  { id: 'shares', label: 'Stocks', icon: '📈' },
  { id: 'digital_assets', label: 'Crypto', icon: '🪙' },
  { id: 'commodities', label: 'Commodities', icon: '🛢️' }
]

// Signal color helper
function getSignalColor(score) {
  if (score >= 65) return '#22c55e' // green
  if (score >= 45) return '#eab308' // yellow
  return '#ef4444' // red
}

function getSignalLabel(score) {
  if (score >= 70) return 'STRONG BUY'
  if (score >= 55) return 'BUY'
  if (score >= 45) return 'HOLD'
  if (score >= 35) return 'SELL'
  return 'STRONG SELL'
}

export default function App() {
  const [assetType, setAssetType] = useState('shares')
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [regime, setRegime] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedAsset, setSelectedAsset] = useState(null)
  const [darkMode, setDarkMode] = useState(() => 
    window.matchMedia('(prefers-color-scheme: dark)').matches
  )

  // Fetch market regime
  useEffect(() => {
    fetch(`${API_BASE}/regime`)
      .then(r => r.json())
      .then(setRegime)
      .catch(console.error)
  }, [])

  // Fetch assets when type changes
  const fetchAssets = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/ranking/${assetType}?limit=20`)
      if (!res.ok) throw new Error('Failed to fetch')
      const data = await res.json()
      // Normalize response
      const items = data.rankings || data.assets || data || []
      setAssets(items)
    } catch (e) {
      setError(e.message)
      setAssets([])
    } finally {
      setLoading(false)
    }
  }, [assetType])

  useEffect(() => {
    fetchAssets()
  }, [fetchAssets])

  // Filter by search
  const filteredAssets = assets.filter(a => {
    const ticker = a.ticker || a.symbol || ''
    const name = a.name || a.company_name || ''
    const q = searchQuery.toLowerCase()
    return ticker.toLowerCase().includes(q) || name.toLowerCase().includes(q)
  })

  // Toggle dark mode
  useEffect(() => {
    document.body.classList.toggle('dark', darkMode)
  }, [darkMode])

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <h1>🎯 Market Predictor</h1>
        </div>
        <div className="header-right">
          {regime && (
            <div className={`regime-badge ${regime.market?.regime || 'neutral'}`}>
              {regime.market?.regime === 'risk_on' ? '🟢' : '🔴'} 
              {regime.market?.regime?.replace('_', ' ').toUpperCase() || 'NEUTRAL'}
            </div>
          )}
          <button 
            className="icon-btn" 
            onClick={() => setDarkMode(!darkMode)}
            title="Toggle theme"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {/* Search */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search ticker or name..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
        {searchQuery && (
          <button className="clear-btn" onClick={() => setSearchQuery('')}>✕</button>
        )}
      </div>

      {/* Asset Type Tabs */}
      <div className="tabs">
        {ASSET_TYPES.map(type => (
          <button
            key={type.id}
            className={`tab ${assetType === type.id ? 'active' : ''}`}
            onClick={() => setAssetType(type.id)}
          >
            <span className="tab-icon">{type.icon}</span>
            <span className="tab-label">{type.label}</span>
          </button>
        ))}
      </div>

      {/* Main Content */}
      <main className="main">
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading predictions...</p>
          </div>
        )}

        {error && (
          <div className="error">
            <p>⚠️ {error}</p>
            <button onClick={fetchAssets}>Retry</button>
          </div>
        )}

        {!loading && !error && filteredAssets.length === 0 && (
          <div className="empty">
            <p>No assets found</p>
          </div>
        )}

        {!loading && !error && filteredAssets.length > 0 && (
          <div className="asset-list">
            {filteredAssets.map((asset, i) => {
              const ticker = asset.ticker || asset.symbol || 'N/A'
              const name = asset.name || asset.company_name || ticker
              const score = Math.round((asset.score || asset.prob || 0.5) * 100) / 100
              const displayScore = score > 1 ? score : Math.round(score * 100)
              const change = asset.change_percent || asset.price_change_24h || 0
              
              return (
                <div 
                  key={ticker + i} 
                  className="asset-card"
                  onClick={() => setSelectedAsset(asset)}
                >
                  <div className="asset-rank">#{i + 1}</div>
                  <div className="asset-info">
                    <div className="asset-ticker">{ticker}</div>
                    <div className="asset-name">{name}</div>
                  </div>
                  <div className="asset-score" style={{ color: getSignalColor(displayScore) }}>
                    <div className="score-value">{displayScore}</div>
                    <div className="score-label">{getSignalLabel(displayScore)}</div>
                  </div>
                  <div className={`asset-change ${change >= 0 ? 'positive' : 'negative'}`}>
                    {change >= 0 ? '+' : ''}{change.toFixed(2)}%
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </main>

      {/* Detail Sidebar */}
      {selectedAsset && (
        <div className="sidebar-overlay" onClick={() => setSelectedAsset(null)}>
          <div className="sidebar" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedAsset(null)}>✕</button>
            <h2>{selectedAsset.ticker || selectedAsset.symbol}</h2>
            <p className="sidebar-name">{selectedAsset.name || selectedAsset.company_name}</p>
            
            <div className="sidebar-stats">
              <div className="stat">
                <span className="stat-label">Score</span>
                <span className="stat-value" style={{ color: getSignalColor(
                  (selectedAsset.score || selectedAsset.prob || 0.5) > 1 
                    ? (selectedAsset.score || selectedAsset.prob)
                    : Math.round((selectedAsset.score || selectedAsset.prob || 0.5) * 100)
                )}}>
                  {(selectedAsset.score || selectedAsset.prob || 0.5) > 1 
                    ? Math.round(selectedAsset.score || selectedAsset.prob)
                    : Math.round((selectedAsset.score || selectedAsset.prob || 0.5) * 100)}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Signal</span>
                <span className="stat-value">
                  {getSignalLabel(
                    (selectedAsset.score || selectedAsset.prob || 0.5) > 1 
                      ? (selectedAsset.score || selectedAsset.prob)
                      : Math.round((selectedAsset.score || selectedAsset.prob || 0.5) * 100)
                  )}
                </span>
              </div>
              {selectedAsset.price && (
                <div className="stat">
                  <span className="stat-label">Price</span>
                  <span className="stat-value">${selectedAsset.price.toFixed(2)}</span>
                </div>
              )}
              {(selectedAsset.change_percent || selectedAsset.price_change_24h) && (
                <div className="stat">
                  <span className="stat-label">Change</span>
                  <span className={`stat-value ${(selectedAsset.change_percent || selectedAsset.price_change_24h) >= 0 ? 'positive' : 'negative'}`}>
                    {(selectedAsset.change_percent || selectedAsset.price_change_24h) >= 0 ? '+' : ''}
                    {(selectedAsset.change_percent || selectedAsset.price_change_24h).toFixed(2)}%
                  </span>
                </div>
              )}
              {selectedAsset.market_cap && (
                <div className="stat">
                  <span className="stat-label">Market Cap</span>
                  <span className="stat-value">
                    ${(selectedAsset.market_cap / 1e9).toFixed(2)}B
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="footer">
        <span>Market Predictor ML v2.0</span>
        <span>•</span>
        <span>{new Date().toLocaleTimeString()}</span>
      </footer>
    </div>
  )
}
