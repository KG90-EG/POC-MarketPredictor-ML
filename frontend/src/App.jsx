import React, { useState, useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { api, handleApiError } from './api'
import ErrorBoundary from './components/ErrorBoundary'
import HealthCheck from './components/HealthCheck'
import Tooltip from './components/Tooltip'
import './styles.css'

// Create a React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function AppContent() {
  const [results, setResults] = useState([])
  const [tickerDetails, setTickerDetails] = useState({})
  const [analysis, setAnalysis] = useState(null)
  const [userContext, setUserContext] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingProgress, setLoadingProgress] = useState({ current: 0, total: 0 })
  const [analyzing, setAnalyzing] = useState(false)
  const [searchTicker, setSearchTicker] = useState('')
  const [searchLoading, setSearchLoading] = useState(false)
  const [searchResult, setSearchResult] = useState(null)
  const [searchResultDetails, setSearchResultDetails] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)
  const [showHelp, setShowHelp] = useState(false)
  const [selectedCompany, setSelectedCompany] = useState(null)
  const [selectedViews, setSelectedViews] = useState(['Global'])
  const [showHealthPanel, setShowHealthPanel] = useState(false)
  const [healthStatus, setHealthStatus] = useState('loading')
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : false
  })
  
  // Digital Assets / Crypto state
  const [portfolioView, setPortfolioView] = useState('stocks') // 'stocks' or 'crypto'
  const [cryptoResults, setCryptoResults] = useState([])
  const [cryptoLoading, setCryptoLoading] = useState(false)
  const [includeNFT, setIncludeNFT] = useState(true)
  const [cryptoLimit, setCryptoLimit] = useState(50)
  const [cryptoPage, setCryptoPage] = useState(1)
  const [cryptoPerPage] = useState(20) // Items per page

  useEffect(() => {
    document.body.classList.toggle('dark-mode', darkMode)
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  // Auto-load ranking on mount
  useEffect(() => {
    fetchRanking()
  }, [])

  // Check health status periodically
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthResp = await api.health()
        const allHealthy = healthResp.api_healthy && healthResp.model_loaded && healthResp.openai_configured
        setHealthStatus(allHealthy ? 'healthy' : 'warning')
      } catch (error) {
        setHealthStatus('error')
      }
    }
    
    checkHealth()
    const interval = setInterval(checkHealth, 30000) // Check every 30s
    return () => clearInterval(interval)
  }, [])

  function toggleDarkMode() {
    setDarkMode(!darkMode)
  }

  async function fetchRanking(views = selectedViews) {
    setLoading(true)
    setAnalysis(null)
    setCurrentPage(1)
    setLoadingProgress({ current: 0, total: 0 })
    
    try {
      // Fetch ranking for each selected view and merge
      let allRankings = []
      for (const view of views) {
        const resp = await api.getRanking(view)
        allRankings = [...allRankings, ...resp.data.ranking]
      }
      
      // Remove duplicates and re-sort by probability
      const uniqueRankings = Array.from(
        new Map(allRankings.map(item => [item.ticker, item])).values()
      ).sort((a, b) => b.prob - a.prob)
      
      setResults(uniqueRankings)
      
      // Batch fetch ticker details (much faster than sequential)
      const tickers = uniqueRankings.map(r => r.ticker)
      setLoadingProgress({ current: 0, total: tickers.length })
      
      try {
        const batchResp = await api.getTickerInfoBatch(tickers)
        const { results: batchResults, errors } = batchResp.data
        
        // Log any errors but don't fail the whole operation
        if (Object.keys(errors).length > 0) {
          console.warn('Some tickers failed to load:', errors)
          const failedCount = Object.keys(errors).length
          if (failedCount > tickers.length / 2) {
            console.warn(`High failure rate: ${failedCount}/${tickers.length} tickers failed`)
          }
        }
        
        setTickerDetails(batchResults || {})
        setLoadingProgress({ current: Object.keys(batchResults || {}).length, total: tickers.length })
      } catch (batchError) {
        console.error('Batch fetch failed, falling back to sequential', batchError)
        const error = handleApiError(batchError)
        if (error.isNetworkError) {
          alert('⚠️ Network error: Please check your connection and try again.')
        }
        // Fallback to sequential if batch fails
        await fetchDetailsSequential(uniqueRankings)
      }
    } catch (e) {
      const error = handleApiError(e, 'Error fetching ranking')
      let errorMessage = `Failed to load rankings: ${error.message}`
      if (error.isNetworkError) {
        errorMessage = '⚠️ Network error: Unable to connect to the backend. Please ensure the server is running.'
      } else if (error.isRateLimit) {
        errorMessage = '⏱️ Rate limit exceeded. Please wait a moment and try again.'
      }
      alert(errorMessage)
      console.error('Ranking fetch error:', error)
    } finally {
      setLoading(false)
      setLoadingProgress({ current: 0, total: 0 })
    }
  }
  
  // Fallback method for sequential fetching
  async function fetchDetailsSequential(ranking) {
    const details = {}
    for (let i = 0; i < ranking.length; i++) {
      const r = ranking[i]
      setLoadingProgress({ current: i + 1, total: ranking.length })
      try {
        const infoResp = await api.getTickerInfo(r.ticker)
        details[r.ticker] = infoResp.data
      } catch (e) {
        console.error(`Failed to fetch info for ${r.ticker}`, e)
      }
    }
    setTickerDetails(details)
  }

  async function fetchCryptoRanking() {
    setCryptoLoading(true)
    setCryptoPage(1) // Reset to first page
    try {
      const resp = await api.getCryptoRanking('', includeNFT, 0.0, cryptoLimit)
      const rankings = resp.data.ranking || []
      setCryptoResults(rankings)
    } catch (e) {
      const error = handleApiError(e, 'Error fetching crypto rankings')
      let errorMessage = `Failed to load crypto rankings: ${error.message}`
      if (error.isNetworkError) {
        errorMessage = '⚠️ Network error: Unable to connect to the backend.'
      } else if (error.isRateLimit) {
        errorMessage = '⏱️ Rate limit exceeded. Please wait a moment and try again.'
      }
      alert(errorMessage)
      console.error('Crypto ranking fetch error:', error)
    } finally {
      setCryptoLoading(false)
    }
  }

  async function requestAnalysis() {
    if (results.length === 0) return
    setAnalyzing(true)
    try {
      const resp = await api.analyze(results, userContext || null)
      const cachedNote = resp.data.cached ? ' (cached result)' : ''
      setAnalysis(resp.data.analysis + cachedNote)
    } catch (e) {
      const error = handleApiError(e, 'Analysis failed')
      if (error.isRateLimit) {
        alert('⏱️ Rate limit reached. Please wait 30-60 seconds and try again.\n\n' + error.message)
      } else {
        alert(`Error: ${error.message}\n\nMake sure OPENAI_API_KEY is set correctly.`)
      }
    } finally {
      setAnalyzing(false)
    }
  }

  async function performSearch() {
    const t = (searchTicker || '').trim().toUpperCase()
    if (!t) {
      alert('Please enter a stock symbol to search.')
      return
    }
    setSearchLoading(true)
    setSearchResult(null)
    setSearchResultDetails(null)
    try {
      const [infoResp, predResp] = await Promise.all([
        api.getTickerInfo(t),
        api.predictTicker(t)
      ])
      const info = infoResp.data || {}
      const prob = predResp.data?.prob || null
      setSearchResult({
        ticker: t,
        prob
      })
      setSearchResultDetails({
        [t]: {
          name: info.name || 'N/A',
          price: info.price || null,
          change: info.change || null,
          volume: info.volume || null,
          market_cap: info.market_cap || null,
          country: info.country || 'N/A'
        }
      })
    } catch (e) {
      const error = handleApiError(e, 'Search failed')
      let errorMessage = `Unable to find ticker ${t}`
      if (error.isNetworkError) {
        errorMessage = '⚠️ Network error: Please check your connection.'  
      } else if (error.status === 404) {
        errorMessage = `❌ Ticker "${t}" not found. Please check the symbol and try again.`
      } else if (error.isRateLimit) {
        errorMessage = '⏱️ Rate limit exceeded. Please wait a moment and try again.'
      } else {
        errorMessage = `Search failed: ${error.message}`
      }
      alert(errorMessage)
      console.error('Search error:', error)
    } finally {
      setSearchLoading(false)
    }
  }

  function formatNumber(num) {
    if (!num) return 'N/A'
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`
    return `$${num.toFixed(2)}`
  }

  function getRankBadgeClass(rank) {
    if (rank === 1) return 'rank-badge gold'
    if (rank === 2) return 'rank-badge silver'
    if (rank === 3) return 'rank-badge bronze'
    return 'rank-badge'
  }

  function handleKeyPress(e, action) {
    if (e.key === 'Enter') {
      action()
    }
  }

  async function openCompanyDetail(ticker) {
    setSelectedCompany({ ticker, loading: true })
    try {
      const [infoResp, predResp] = await Promise.all([
        api.getTickerInfo(ticker),
        api.predictTicker(ticker)
      ])
      const info = infoResp.data || {}
      const prob = predResp.data?.prob || null
      
      // Calculate signal
      let signal = 'HOLD'
      if (prob >= 0.65) signal = 'STRONG BUY'
      else if (prob >= 0.55) signal = 'BUY'
      else if (prob >= 0.45) signal = 'HOLD'
      else if (prob >= 0.35) signal = 'CONSIDER SELLING'
      else signal = 'SELL'
      
      setSelectedCompany({
        ticker,
        ...info,
        prob,
        signal,
        loading: false
      })
    } catch (e) {
      const error = handleApiError(e, 'Failed to load company details')
      let errorMessage = error.message
      if (error.isNetworkError) {
        errorMessage = '⚠️ Network error: Unable to load company details.'
      } else if (error.isRateLimit) {
        errorMessage = '⏱️ Rate limit exceeded. Please wait a moment.'
      }
      setSelectedCompany({ ticker, error: errorMessage, loading: false })
      console.error('Company detail error:', error)
    }
  }

  return (
    <div className="container">
      {/* Skip Navigation Link */}
      <a href="#main-content" className="skip-link">Skip to main content</a>
      
      <header className="header" role="banner">
        <button 
          className="theme-toggle" 
          onClick={toggleDarkMode} 
          aria-label={`Switch to ${darkMode ? 'light' : 'dark'} mode`}
          title={`Toggle ${darkMode ? 'light' : 'dark'} mode`}
        >
          {darkMode ? '☀️' : '🌙'}
        </button>
        <button 
          className={`health-indicator ${healthStatus}`} 
          onClick={() => setShowHealthPanel(!showHealthPanel)} 
          aria-label={`System health status: ${healthStatus}. Click to view details.`}
          aria-expanded={showHealthPanel}
          title="System Health"
        >
          {healthStatus === 'healthy' && '✅'}
          {healthStatus === 'warning' && '⚠️'}
          {healthStatus === 'error' && '❌'}
          {healthStatus === 'loading' && '⏳'}
        </button>
        <button 
          className="help-button" 
          onClick={() => setShowHelp(true)} 
          aria-label="Open help and usage guide"
          title="Help & Guide"
        >
          ❓
        </button>
        <h1><span className="emoji" aria-hidden="true">📈</span> POC Trading Overview</h1>
        <p>AI-Powered Stock Ranking & Analysis</p>
      </header>
      
      {/* Health Check Section - Toggle visibility */}
      <HealthCheck isOpen={showHealthPanel} onClose={() => setShowHealthPanel(false)} />
      
      <main id="main-content" role="main">
      {/* Portfolio View Toggle */}
      <section className="card" style={{marginBottom: '24px'}} role="region" aria-label="Portfolio view selector">
        <div className="card-title">📊 Portfolio View</div>
        <div style={{display: 'flex', gap: '16px', marginTop: '12px'}}>
          <button
            onClick={() => {
              setPortfolioView('stocks')
              if (results.length === 0) fetchRanking()
            }}
            aria-label="Switch to stocks and shares portfolio view"
            aria-pressed={portfolioView === 'stocks'}
            style={{
              flex: 1,
              padding: '16px 24px',
              background: portfolioView === 'stocks' 
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                : '#f0f0f0',
              color: portfolioView === 'stocks' ? 'white' : '#333',
              border: portfolioView === 'stocks' ? '3px solid #764ba2' : '2px solid #ddd',
              borderRadius: '12px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '1rem',
              transition: 'all 0.3s ease',
              boxShadow: portfolioView === 'stocks' 
                ? '0 6px 16px rgba(102, 126, 234, 0.5)' 
                : '0 2px 8px rgba(0, 0, 0, 0.1)',
              transform: portfolioView === 'stocks' ? 'scale(1.02)' : 'scale(1)'
            }}
          >
            <div style={{fontSize: '2rem', marginBottom: '8px'}}>📈</div>
            <div>Stocks & Shares</div>
            <div style={{fontSize: '0.75rem', marginTop: '4px', opacity: 0.9}}>
              Traditional equities, indices & ETFs
            </div>
          </button>
          
          <button
            onClick={() => {
              setPortfolioView('crypto')
              if (cryptoResults.length === 0) fetchCryptoRanking()
            }}
            aria-label="Switch to digital assets and cryptocurrency portfolio view"
            aria-pressed={portfolioView === 'crypto'}
            style={{
              flex: 1,
              padding: '16px 24px',
              background: portfolioView === 'crypto' 
                ? 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)' 
                : '#f0f0f0',
              color: portfolioView === 'crypto' ? 'white' : '#333',
              border: portfolioView === 'crypto' ? '3px solid #ea580c' : '2px solid #ddd',
              borderRadius: '12px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '1rem',
              transition: 'all 0.3s ease',
              boxShadow: portfolioView === 'crypto' 
                ? '0 6px 16px rgba(245, 158, 11, 0.5)' 
                : '0 2px 8px rgba(0, 0, 0, 0.1)',
              transform: portfolioView === 'crypto' ? 'scale(1.02)' : 'scale(1)'
            }}
          >
            <div style={{fontSize: '2rem', marginBottom: '8px'}}>₿</div>
            <div>Digital Assets</div>
            <div style={{fontSize: '0.75rem', marginTop: '4px', opacity: 0.9}}>
              Crypto, NFTs, Bitcoin, Ethereum & more
            </div>
          </button>
        </div>
      </section>
      
      {/* Market View Selector - Only for stocks */}
      {portfolioView === 'stocks' && (
      <section className="card" role="region" aria-label="Market view selector">
        <div className="card-title">
          🌍 Market View - {selectedViews.join(', ')}
          {!loading && results.length > 0 && (
            <span style={{marginLeft: '8px', color: '#667eea', fontWeight: 'bold'}}>({results.length})</span>
          )}
        </div>
        <div style={{marginBottom: '8px', fontSize: '0.9rem', color: '#666'}}>
          💡 Click to select multiple markets
        </div>
        <div style={{display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '16px'}}>
          {['Global', 'United States', 'Switzerland', 'Germany', 'United Kingdom', 'France', 'Japan', 'Canada'].map(view => {
            const isSelected = selectedViews.includes(view)
            return (
              <button
                key={view}
                onClick={() => {
                  let newViews
                  if (isSelected) {
                    // Deselect if already selected (but keep at least one)
                    newViews = selectedViews.length > 1 
                      ? selectedViews.filter(v => v !== view)
                      : selectedViews
                  } else {
                    // Add to selection
                    newViews = [...selectedViews, view]
                  }
                  setSelectedViews(newViews)
                  fetchRanking(newViews)
                }}
                aria-label={`${view} market view`}
                aria-pressed={isSelected}
                style={{
                  padding: '10px 20px',
                  background: isSelected ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#f0f0f0',
                  color: isSelected ? 'white' : '#333',
                  border: isSelected ? '2px solid #764ba2' : '2px solid transparent',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: isSelected ? '600' : '400',
                  transition: 'all 0.3s ease',
                  boxShadow: isSelected ? '0 4px 12px rgba(102, 126, 234, 0.4)' : 'none',
                  position: 'relative'
                }}
              >
                {isSelected && <span style={{position: 'absolute', top: '-4px', right: '-4px', fontSize: '12px'}}>✓</span>}
                {view === 'Global' ? '🌐' : 
                 view === 'United States' ? '🇺🇸' : 
                 view === 'Switzerland' ? '🇨🇭' : 
                 view === 'Germany' ? '🇩🇪' : 
                 view === 'United Kingdom' ? '🇬🇧' : 
                 view === 'France' ? '🇫🇷' : 
                 view === 'Japan' ? '🇯🇵' : 
                 view === 'Canada' ? '🇨🇦' : '🌎'} {view}
              </button>
            )
          })}
        </div>
        
        {loading ? (
          <div style={{textAlign: 'center', padding: '40px'}} role="status" aria-live="polite" aria-atomic="true">
            <span className="spinner"></span>
            <p>Loading {selectedViews.join(', ')} market rankings...</p>
            {loadingProgress.total > 0 && (
              <div style={{marginTop: '16px'}}>
                <div style={{
                  width: '100%',
                  maxWidth: '400px',
                  margin: '0 auto',
                  background: '#e0e0e0',
                  borderRadius: '8px',
                  height: '8px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${(loadingProgress.current / loadingProgress.total) * 100}%`,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    height: '100%',
                    transition: 'width 0.3s ease'
                  }}></div>
                </div>
                <p style={{fontSize: '0.9rem', color: '#666', marginTop: '8px'}}>
                  Loading details: {loadingProgress.current} / {loadingProgress.total}
                </p>
              </div>
            )}
          </div>
        ) : results.length > 0 ? (
          <div style={{marginBottom: '16px'}}>
          </div>
        ) : (
          <p style={{color: '#666', fontSize: '0.9rem', margin: '0'}}>
            Select a market view above to analyze top performers for a diversified portfolio
          </p>
        )}
      </section>
      )}

      {/* Digital Assets / Crypto View */}
      {portfolioView === 'crypto' && (
        <section className="card" role="region" aria-label="Digital assets and cryptocurrency rankings">
          <div className="card-title">
            ₿ Digital Assets Rankings
            {!cryptoLoading && cryptoResults.length > 0 && (
              <span style={{marginLeft: '8px', color: '#f59e0b', fontWeight: 'bold'}}>({cryptoResults.length})</span>
            )}
          </div>
          
          {/* NFT Toggle and Limit Selector */}
          <div style={{marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap'}}>
            <label style={{display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer'}}>
              <input 
                type="checkbox" 
                checked={includeNFT}
                onChange={(e) => {
                  setIncludeNFT(e.target.checked)
                  // Auto-refresh if crypto data is already loaded
                  if (cryptoResults.length > 0) {
                    fetchCryptoRanking()
                  }
                }}
                aria-label="Include NFT-related tokens in rankings"
                style={{width: '18px', height: '18px'}}
              />
              <span style={{fontSize: '0.95rem'}}>Include NFT tokens</span>
            </label>
            
            <label style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
              <span style={{fontSize: '0.95rem', fontWeight: '500'}}>Top:</span>
              <select 
                value={cryptoLimit}
                onChange={(e) => {
                  setCryptoLimit(Number(e.target.value))
                  // Auto-refresh if crypto data is already loaded
                  if (cryptoResults.length > 0) {
                    setTimeout(() => fetchCryptoRanking(), 100)
                  }
                }}
                aria-label="Select number of cryptocurrencies to display"
                style={{
                  padding: '6px 12px',
                  border: '2px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '0.9rem',
                  cursor: 'pointer'
                }}
              >
                <option value={20}>20 cryptos</option>
                <option value={50}>50 cryptos</option>
                <option value={100}>100 cryptos</option>
                <option value={200}>200 cryptos</option>
              </select>
            </label>
            
            <button 
              onClick={fetchCryptoRanking}
              disabled={cryptoLoading}
              aria-label="Refresh cryptocurrency rankings from CoinGecko"
              style={{
                padding: '8px 16px',
                background: 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: cryptoLoading ? 'not-allowed' : 'pointer',
                fontWeight: '600',
                fontSize: '0.9rem'
              }}
            >
              {cryptoLoading ? '⟳ Refreshing...' : '🔄 Refresh Rankings'}
            </button>
          </div>
          
          {cryptoLoading ? (
            <div style={{textAlign: 'center', padding: '40px'}} role="status" aria-live="polite" aria-atomic="true">
              <span className="spinner"></span>
              <p>Loading digital assets rankings...</p>
            </div>
          ) : cryptoResults.length > 0 ? (
            <div>
              <div style={{marginBottom: '16px', padding: '12px', background: '#fef3c7', borderRadius: '8px', fontSize: '0.9rem'}}>
                ℹ️ <strong>Digital Assets powered by CoinGecko API.</strong> Momentum scores consider market cap rank, price trends (24h/7d/30d), and liquidity.
              </div>
              
              <table aria-label="Digital assets and cryptocurrency rankings table">
                <thead>
                  <tr>
                    <th scope="col">Rank</th>
                    <th scope="col">Asset</th>
                    <th scope="col">Symbol</th>
                    <th scope="col">
                      <Tooltip content="Momentum score (0-100%). Higher scores indicate better recent performance, market cap rank, and liquidity. Similar to probability score for stocks." position="top">
                        Momentum Score ⓘ
                      </Tooltip>
                    </th>
                    <th scope="col">Price (USD)</th>
                    <th scope="col">
                      <Tooltip content="24-hour price change percentage. Crypto markets are highly volatile - double-digit changes are common." position="top">
                        24h Change ⓘ
                      </Tooltip>
                    </th>
                    <th scope="col">7d Change</th>
                    <th scope="col">Market Cap</th>
                    <th scope="col">Volume/MCap</th>
                  </tr>
                </thead>
                <tbody>
                  {cryptoResults.slice((cryptoPage - 1) * cryptoPerPage, cryptoPage * cryptoPerPage).map((crypto, idx) => {
                    const actualRank = (cryptoPage - 1) * cryptoPerPage + idx + 1
                    const changeClass = crypto.change_24h > 0 ? 'positive' : crypto.change_24h < 0 ? 'negative' : ''
                    const change7dClass = crypto.change_7d > 0 ? 'positive' : crypto.change_7d < 0 ? 'negative' : ''
                    
                    return (
                      <tr key={crypto.crypto_id} style={{cursor: 'default'}}>
                        <td>
                          <span className={actualRank <= 3 ? 'rank-badge gold' : 'rank-badge'}>{actualRank}</span>
                        </td>
                        <td>
                          <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                            {crypto.image && (
                              <img src={crypto.image} alt={crypto.name} style={{width: '24px', height: '24px', borderRadius: '50%'}} />
                            )}
                            <span style={{fontWeight: '600'}}>{crypto.name}</span>
                          </div>
                        </td>
                        <td><span className="ticker-symbol">{crypto.symbol}</span></td>
                        <td>
                          <Tooltip 
                            content={`${(crypto.momentum_score * 100).toFixed(2)}% momentum. Rank #${crypto.market_cap_rank} by market cap. ${crypto.momentum_score >= 0.65 ? 'Strong bullish signal' : crypto.momentum_score >= 0.55 ? 'Bullish momentum' : crypto.momentum_score >= 0.45 ? 'Neutral' : 'Weak momentum'}`}
                            position="top"
                          >
                            <span className={crypto.momentum_score > 0.6 ? 'high-prob' : ''}>
                              {(crypto.momentum_score * 100).toFixed(2)}%
                            </span>
                          </Tooltip>
                        </td>
                        <td>${crypto.price?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 6}) || 'N/A'}</td>
                        <td>
                          <Tooltip 
                            content={`${crypto.change_24h ? crypto.change_24h.toFixed(2) : 'N/A'}% in last 24 hours. ${crypto.change_24h > 10 ? '🚀 Major pump!' : crypto.change_24h > 5 ? 'Strong gain' : crypto.change_24h > 0 ? 'Slight increase' : crypto.change_24h < -10 ? '⚠️ Heavy drop' : crypto.change_24h < -5 ? 'Significant loss' : crypto.change_24h < 0 ? 'Minor decline' : 'Stable'}`}
                            position="top"
                          >
                            <span className={changeClass}>
                              {crypto.change_24h ? `${crypto.change_24h > 0 ? '+' : ''}${crypto.change_24h.toFixed(2)}%` : 'N/A'}
                            </span>
                          </Tooltip>
                        </td>
                        <td>
                          <span className={change7dClass}>
                            {crypto.change_7d ? `${crypto.change_7d > 0 ? '+' : ''}${crypto.change_7d.toFixed(2)}%` : 'N/A'}
                          </span>
                        </td>
                        <td>${crypto.market_cap ? (crypto.market_cap / 1e9).toFixed(2) + 'B' : 'N/A'}</td>
                        <td>
                          <Tooltip 
                            content={`${crypto.volume_to_mcap_ratio ? crypto.volume_to_mcap_ratio.toFixed(2) : 'N/A'}% - Trading volume as % of market cap. Higher = more liquid. 20%+ is excellent, 10-20% is good, <10% is lower liquidity.`}
                            position="top"
                          >
                            {crypto.volume_to_mcap_ratio ? `${crypto.volume_to_mcap_ratio.toFixed(2)}%` : 'N/A'}
                          </Tooltip>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
              
              {/* Pagination Controls */}
              {cryptoResults.length > cryptoPerPage && (
                <nav aria-label="Cryptocurrency results pagination" style={{
                  marginTop: '20px',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  gap: '12px'
                }}>
                  <button
                    onClick={() => setCryptoPage(Math.max(1, cryptoPage - 1))}
                    disabled={cryptoPage === 1}
                    aria-label="Go to previous page"
                    style={{
                      padding: '8px 16px',
                      background: cryptoPage === 1 ? '#e0e0e0' : 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)',
                      color: cryptoPage === 1 ? '#999' : 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: cryptoPage === 1 ? 'not-allowed' : 'pointer',
                      fontWeight: '600',
                      fontSize: '0.9rem'
                    }}
                  >
                    ← Previous
                  </button>
                  
                  <span style={{fontSize: '0.9rem', fontWeight: '500'}} aria-live="polite" aria-atomic="true">
                    Page {cryptoPage} of {Math.ceil(cryptoResults.length / cryptoPerPage)} 
                    <span style={{color: '#666', marginLeft: '8px'}}>
                      ({(cryptoPage - 1) * cryptoPerPage + 1}-{Math.min(cryptoPage * cryptoPerPage, cryptoResults.length)} of {cryptoResults.length})
                    </span>
                  </span>
                  
                  <button
                    onClick={() => setCryptoPage(Math.min(Math.ceil(cryptoResults.length / cryptoPerPage), cryptoPage + 1))}
                    disabled={cryptoPage >= Math.ceil(cryptoResults.length / cryptoPerPage)}
                    aria-label="Go to next page"
                    style={{
                      padding: '8px 16px',
                      background: cryptoPage >= Math.ceil(cryptoResults.length / cryptoPerPage) ? '#e0e0e0' : 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)',
                      color: cryptoPage >= Math.ceil(cryptoResults.length / cryptoPerPage) ? '#999' : 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: cryptoPage >= Math.ceil(cryptoResults.length / cryptoPerPage) ? 'not-allowed' : 'pointer',
                      fontWeight: '600',
                      fontSize: '0.9rem'
                    }}
                  >
                    Next →
                  </button>
                </nav>
              )}
            </div>
          ) : (
            <p style={{color: '#666', fontSize: '0.9rem', margin: '0', textAlign: 'center', padding: '20px'}}>
              Click "Refresh Rankings" to load digital assets data
            </p>
          )}
        </section>
      )}

      {/* Search Section - Only for stocks */}
      {portfolioView === 'stocks' && (
      <>
      <section className="card" role="region" aria-label="Search for individual stocks">
        <div className="card-title">🔍 Search Individual Stock</div>
        <div className="search-controls">
          <label>
            Stock symbol
            <input
              value={searchTicker}
              onChange={(e) => setSearchTicker(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e, performSearch)}
              placeholder="e.g., AMD, META, NFLX"
              aria-label="Enter stock symbol to search"
            />
          </label>
          <button onClick={performSearch} disabled={searchLoading} aria-label="Search for stock by symbol">
            {searchLoading ? (
              <>
                <span className="spinner"></span>
                Searching...
              </>
            ) : (
              '🔎 Search'
            )}
          </button>
        </div>
      </section>

      {/* Search Result */}
      {searchResult && searchResultDetails && (
        <section className="search-result" role="region" aria-label="Stock search results">
          <h2>🎯 Search Result</h2>
          <table aria-label="Search result details table">
            <thead>
              <tr>
                <th scope="col">Stock</th>
                <th scope="col">Name</th>
                <th scope="col">Country</th>
                <th scope="col">
                  <Tooltip content="AI confidence score (0-100%). Higher scores indicate stronger buy signals based on technical indicators, price trends, and market data. 65%+ is strong buy, 55-65% is buy, 45-55% is hold, 35-45% consider selling, below 35% is sell." position="top">
                    Probability ⓘ
                  </Tooltip>
                </th>
                <th scope="col">Price</th>
                <th scope="col">
                  <Tooltip content="Daily price change percentage. Positive (+) values indicate the stock is up today, negative (-) values mean it's down. Strong moves are typically ±3% or more for established stocks." position="top">
                    Change % ⓘ
                  </Tooltip>
                </th>
                <th scope="col">Volume</th>
                <th scope="col">Market Cap</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                onClick={() => openCompanyDetail(searchResult.ticker)}
                style={{ cursor: 'pointer' }}
                title="Click for detailed information"
              >
                <td><span className="ticker-symbol">{searchResult.ticker}</span></td>
                <td>{searchResultDetails[searchResult.ticker]?.name || 'N/A'}</td>
                <td>
                  <span className="country-tag">{searchResultDetails[searchResult.ticker]?.country || 'N/A'}</span>
                </td>
                <td>
                  <Tooltip 
                    content={`${searchResult.prob != null ? `${(searchResult.prob * 100).toFixed(2)}% confidence. ${searchResult.prob >= 0.65 ? 'Strong buy signal' : searchResult.prob >= 0.55 ? 'Buy signal' : searchResult.prob >= 0.45 ? 'Hold' : searchResult.prob >= 0.35 ? 'Consider selling' : 'Sell signal'}` : 'N/A'}`}
                    position="top"
                  >
                    <span className={searchResult.prob > 0.6 ? 'high-prob' : ''}>
                      {searchResult.prob != null ? `${(searchResult.prob * 100).toFixed(2)}%` : 'N/A'}
                    </span>
                  </Tooltip>
                </td>
                <td>{searchResultDetails[searchResult.ticker]?.price != null ? `$${searchResultDetails[searchResult.ticker].price.toFixed(2)}` : 'N/A'}</td>
                <td>
                  <Tooltip 
                    content={`${searchResultDetails[searchResult.ticker]?.change != null ? `${searchResultDetails[searchResult.ticker].change > 0 ? '+' : ''}${searchResultDetails[searchResult.ticker].change.toFixed(2)}% daily change. ${searchResultDetails[searchResult.ticker].change > 3 ? 'Strong upward move!' : searchResultDetails[searchResult.ticker].change > 0 ? 'Positive momentum' : searchResultDetails[searchResult.ticker].change < -3 ? 'Significant drop' : searchResultDetails[searchResult.ticker].change < 0 ? 'Slight decline' : 'No change'}` : 'N/A'}`}
                    position="top"
                  >
                    <span className={searchResultDetails[searchResult.ticker]?.change > 0 ? 'positive' : searchResultDetails[searchResult.ticker]?.change < 0 ? 'negative' : ''}>
                      {searchResultDetails[searchResult.ticker]?.change != null ? `${searchResultDetails[searchResult.ticker].change > 0 ? '+' : ''}${searchResultDetails[searchResult.ticker].change.toFixed(2)}%` : 'N/A'}
                    </span>
                  </Tooltip>
                </td>
                <td>{searchResultDetails[searchResult.ticker]?.volume != null ? searchResultDetails[searchResult.ticker].volume.toLocaleString() : 'N/A'}</td>
                <td>{formatNumber(searchResultDetails[searchResult.ticker]?.market_cap)}</td>
              </tr>
            </tbody>
          </table>
        </section>
      )}
      </>
      )}

      {/* Results Section - Only for stocks */}
      {portfolioView === 'stocks' && results.length > 0 && (
        <>
          {/* AI Analysis Section */}
          <section className="analysis-section" role="region" aria-label="AI analysis context input">
            <label>
              <strong>🤖 Optional context for AI analysis</strong>
              <textarea 
                value={userContext}
                onChange={(e) => setUserContext(e.target.value)}
                placeholder="e.g., I'm interested in tech stocks with growth potential, looking for long-term investments..."
                rows={3}
                aria-label="Enter context for AI analysis"
              />
            </label>
            <button onClick={requestAnalysis} disabled={analyzing} aria-label="Request AI analysis and recommendations">
              {analyzing ? (
                <>
                  <span className="spinner"></span>
                  Analyzing...
                </>
              ) : (
                '✨ Get AI Recommendations'
              )}
            </button>
          </section>

          {/* AI Analysis Result */}
          {analysis && (
            <section className="analysis-result" role="region" aria-label="AI analysis results">
              <h3>💡 AI Analysis & Recommendations</h3>
              <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{analysis}</p>
            </section>
          )}

          {/* Ranked Stocks Table */}
          <h2>Ranked Stocks</h2>
          <table aria-label="Ranked stocks results table">
            <thead>
              <tr>
                <th scope="col">Rank</th>
                <th scope="col">Stock</th>
                <th scope="col">Name</th>
                <th scope="col">Country</th>
                <th scope="col">Signal</th>
                <th scope="col">
                  <Tooltip content="AI confidence score (0-100%). Higher scores indicate stronger buy signals based on technical indicators, price trends, and market data. 65%+ is strong buy, 55-65% is buy, 45-55% is hold, 35-45% consider selling, below 35% is sell." position="top">
                    Probability ⓘ
                  </Tooltip>
                </th>
                <th scope="col">Price</th>
                <th scope="col">
                  <Tooltip content="Daily price change percentage. Positive (+) values indicate the stock is up today, negative (-) values mean it's down. Strong moves are typically ±3% or more for established stocks." position="top">
                    Change % ⓘ
                  </Tooltip>
                </th>
                <th scope="col">Volume</th>
                <th scope="col">Market Cap</th>
              </tr>
            </thead>
            <tbody>
              {results
                .slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
                .map((r, idx) => {
                const rank = results.indexOf(r) + 1
                const detail = tickerDetails[r.ticker] || {}
                const changeClass = detail.change > 0 ? 'positive' : detail.change < 0 ? 'negative' : ''
                return (
                  <tr 
                    key={r.ticker} 
                    onClick={() => openCompanyDetail(r.ticker)}
                    style={{ cursor: 'pointer' }}
                    title="Click for detailed information"
                  >
                    <td>
                      <span className={getRankBadgeClass(rank)}>{rank}</span>
                    </td>
                    <td><span className="ticker-symbol">{r.ticker}</span></td>
                    <td>{detail.name || 'N/A'}</td>
                    <td>
                      <span className="country-tag">{detail.country || 'N/A'}</span>
                    </td>
                    <td>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        padding: '6px 12px',
                        borderRadius: '6px',
                        fontWeight: '600',
                        fontSize: '0.85rem',
                        background: r.prob >= 0.5 ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                        color: 'white',
                        boxShadow: r.prob >= 0.5 ? '0 2px 8px rgba(16, 185, 129, 0.3)' : '0 2px 8px rgba(239, 68, 68, 0.3)'
                      }}>
                        {r.prob >= 0.5 ? '🟢 BUY' : '🔴 SELL'}
                      </span>
                    </td>
                    <td>
                      <Tooltip 
                        content={`${(r.prob * 100).toFixed(2)}% confidence. ${r.prob >= 0.65 ? 'Strong buy signal - High confidence for upward movement' : r.prob >= 0.55 ? 'Buy signal - Good potential for growth' : r.prob >= 0.45 ? 'Hold - Neutral outlook' : r.prob >= 0.35 ? 'Consider selling - Weak performance expected' : 'Sell signal - Strong downward indicator'}`}
                        position="top"
                      >
                        <span className={r.prob > 0.6 ? 'high-prob' : ''}>
                          {(r.prob * 100).toFixed(2)}%
                        </span>
                      </Tooltip>
                    </td>
                    <td>{detail.price ? `$${detail.price.toFixed(2)}` : 'N/A'}</td>
                    <td>
                      <Tooltip 
                        content={`${detail.change ? (detail.change > 0 ? `+${detail.change.toFixed(2)}%` : `${detail.change.toFixed(2)}%`) : 'N/A'} daily change. ${detail.change > 3 ? '🚀 Strong upward move!' : detail.change > 0 ? '✅ Positive momentum' : detail.change < -3 ? '⚠️ Significant drop' : detail.change < 0 ? '⬇️ Slight decline' : 'No change'}`}
                        position="top"
                      >
                        <span className={changeClass}>
                          {detail.change ? `${detail.change > 0 ? '+' : ''}${detail.change.toFixed(2)}%` : 'N/A'}
                        </span>
                      </Tooltip>
                    </td>
                    <td>{detail.volume ? detail.volume.toLocaleString() : 'N/A'}</td>
                    <td>{formatNumber(detail.market_cap)}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>

          {/* Pagination Controls */}
          {results.length > itemsPerPage && (
            <div className="pagination">
              <button 
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))} 
                disabled={currentPage === 1}
              >
                ← Previous
              </button>
              <div className="page-selector">
                <span className="page-info">Page</span>
                <select 
                  value={currentPage} 
                  onChange={(e) => setCurrentPage(Number(e.target.value))}
                  className="page-dropdown"
                >
                  {Array.from({ length: Math.ceil(results.length / itemsPerPage) }, (_, i) => i + 1).map(pageNum => (
                    <option key={pageNum} value={pageNum}>{pageNum}</option>
                  ))}
                </select>
                <span className="page-info">of {Math.ceil(results.length / itemsPerPage)}</span>
              </div>
              <button 
                onClick={() => setCurrentPage(p => Math.min(Math.ceil(results.length / itemsPerPage), p + 1))} 
                disabled={currentPage >= Math.ceil(results.length / itemsPerPage)}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}

      {/* Help Modal */}
      {showHelp && (
        <div className="modal-overlay" onClick={() => setShowHelp(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowHelp(false)}>×</button>
            <h2>📚 How to Use Trading Fun</h2>
            
            <div className="help-section">
              <h3>🚀 Getting Started</h3>
              <p>Rankings load automatically when you open the app. The system analyzes 50 popular stocks using machine learning and provides buy/sell recommendations.</p>
            </div>

            <div className="help-section">
              <h3>📊 Understanding the Rankings</h3>
              <ul>
                <li><strong>Probability:</strong> ML model's confidence in stock outperformance (higher = better)</li>
                <li><strong>Rank Badges:</strong> Top 3 stocks get gold, silver, and bronze badges</li>
                <li><strong>Color Indicators:</strong> Green = price up, Red = price down</li>
              </ul>
            </div>

            <div className="help-section">
              <h3>🎯 Buy/Sell Signals</h3>
              <ul>
                <li><strong>STRONG BUY</strong> (≥65%): High confidence opportunity</li>
                <li><strong>BUY</strong> (≥55%): Good buying opportunity</li>
                <li><strong>HOLD</strong> (45-54%): Maintain position</li>
                <li><strong>CONSIDER SELLING</strong> (35-44%): Weak position</li>
                <li><strong>SELL</strong> (&lt;35%): Exit recommended</li>
              </ul>
            </div>

            <div className="help-section">
              <h3>🔍 Navigation</h3>
              <ul>
                <li><strong>Pagination:</strong> Use dropdown to jump to any page, or Previous/Next buttons</li>
                <li><strong>Click a row:</strong> Opens detailed company information sidebar</li>
                <li><strong>Search:</strong> Look up specific stocks not in the main ranking</li>
                <li><strong>Refresh:</strong> Reload latest market data and rankings</li>
              </ul>
            </div>

            <div className="help-section">
              <h3>🤖 AI Analysis (Optional)</h3>
              <p>Add context like "focus on tech stocks" or "conservative portfolio" to get personalized AI-powered recommendations. The system provides specific buy/sell advice, risk assessment, and action plans.</p>
            </div>

            <div className="help-section">
              <h3>🌓 Theme Toggle</h3>
              <p>Click the sun/moon icon to switch between light and dark modes. Your preference is saved automatically.</p>
            </div>
          </div>
        </div>
      )}

      {/* Company Detail Sidebar */}
      {selectedCompany && (
        <>
          <div className="sidebar-overlay" onClick={() => setSelectedCompany(null)}></div>
          <div className="sidebar">
            <button className="sidebar-close" onClick={() => setSelectedCompany(null)}>×</button>
            
            {selectedCompany.loading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <span className="spinner"></span>
                <p>Loading company details...</p>
              </div>
            ) : selectedCompany.error ? (
              <div style={{ padding: '20px', color: '#e74c3c' }}>
                <p>{selectedCompany.error}</p>
              </div>
            ) : (
              <div className="sidebar-content">
                <h2>{selectedCompany.ticker}</h2>
                <p className="company-name">{selectedCompany.name || 'N/A'}</p>
                {selectedCompany.country && (
                  <p className="company-country">🌍 {selectedCompany.country}</p>
                )}
                
                <div className="detail-section">
                  <h3>🎯 Trading Signal</h3>
                  <div className={`signal-badge signal-${selectedCompany.signal?.toLowerCase().replace(/ /g, '-')}`}>
                    {selectedCompany.signal}
                  </div>
                  <p className="probability">ML Probability: {selectedCompany.prob ? `${(selectedCompany.prob * 100).toFixed(2)}%` : 'N/A'}</p>
                </div>

                <div className="detail-section">
                  <h3>💰 Price Information</h3>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span className="detail-label">Current Price</span>
                      <span className="detail-value">{selectedCompany.price ? `$${selectedCompany.price.toFixed(2)}` : 'N/A'}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Change %</span>
                      <span className={`detail-value ${selectedCompany.change > 0 ? 'positive' : selectedCompany.change < 0 ? 'negative' : ''}`}>
                        {selectedCompany.change ? `${selectedCompany.change > 0 ? '+' : ''}${selectedCompany.change.toFixed(2)}%` : 'N/A'}
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">52-Week High</span>
                      <span className="detail-value">{selectedCompany.fifty_two_week_high ? `$${selectedCompany.fifty_two_week_high.toFixed(2)}` : 'N/A'}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">52-Week Low</span>
                      <span className="detail-value">{selectedCompany.fifty_two_week_low ? `$${selectedCompany.fifty_two_week_low.toFixed(2)}` : 'N/A'}</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h3>📊 Market Data</h3>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span className="detail-label">Market Cap</span>
                      <span className="detail-value">{formatNumber(selectedCompany.market_cap)}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Volume</span>
                      <span className="detail-value">{selectedCompany.volume ? selectedCompany.volume.toLocaleString() : 'N/A'}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">P/E Ratio</span>
                      <span className="detail-value">{selectedCompany.pe_ratio ? selectedCompany.pe_ratio.toFixed(2) : 'N/A'}</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h3>💡 Recommendation</h3>
                  <p className="recommendation-text">
                    {selectedCompany.signal === 'STRONG BUY' && 'This stock shows strong potential for outperformance based on ML analysis. Consider adding to your portfolio.'}
                    {selectedCompany.signal === 'BUY' && 'Positive signals indicate good buying opportunity. Review fundamentals before investing.'}
                    {selectedCompany.signal === 'HOLD' && 'Neutral signals suggest maintaining current position. Monitor for changes.'}
                    {selectedCompany.signal === 'CONSIDER SELLING' && 'Weak signals detected. Consider reducing position or exiting.'}
                    {selectedCompany.signal === 'SELL' && 'ML model suggests poor performance outlook. Consider exiting position.'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </>
      )}
      
      </main>
      
      {/* Footer */}
      <footer style={{
        marginTop: '40px',
        padding: '20px',
        borderTop: '2px solid #e0e0e0',
        textAlign: 'center',
        fontSize: '0.85rem',
        color: '#666'
      }}>
        {portfolioView === 'crypto' && (
          <div style={{marginBottom: '12px'}}>
            <p style={{margin: '0 0 8px 0'}}>
              📊 Digital Assets data powered by <strong>CoinGecko API</strong>
            </p>
            <p style={{margin: '0', fontSize: '0.8rem', color: '#999'}}>
              Live market data • Top {cryptoLimit} cryptocurrencies by market cap • Real-time momentum scoring
            </p>
          </div>
        )}
        <p style={{margin: '8px 0 0 0', fontSize: '0.8rem'}}>
          © 2025 Trading Fun AI Market Predictor • Built with ML & FastAPI
        </p>
      </footer>
    </div>
  )
}

// Wrap with providers and error boundary
export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AppContent />
      </QueryClientProvider>
    </ErrorBoundary>
  )
}
