import React, { useState, useEffect, lazy, Suspense } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { api, handleApiError } from './api'
import ErrorBoundary from './components/ErrorBoundary'
import LoadingState from './components/LoadingState'
import HealthCheck from './components/HealthCheck'
import Tooltip from './components/Tooltip'
import HelpModal from './components/HelpModal'
import CompanyDetailSidebar from './components/CompanyDetailSidebar'
import CryptoDetailSidebar from './components/CryptoDetailSidebar'
import AIAnalysisSection from './components/AIAnalysisSection'
import StockRanking from './components/StockRanking'
import CryptoPortfolio from './components/CryptoPortfolio'
import MarketSelector from './components/MarketSelector'
import WatchlistManagerV2 from './components/WatchlistManagerV2'
import BuyOpportunities from './components/BuyOpportunities'
import AlertPanel from './components/AlertPanel'
import EmptyState from './components/EmptyState'
import { ToastContainer } from './components/Toast'
import { SkeletonTable, SkeletonStockRow } from './components/SkeletonLoader'
import AutocompleteSearch from './components/AutocompleteSearch'
import InfoCard from './components/InfoCard'
import Onboarding from './components/Onboarding'
import OnboardingResetBtn from './components/OnboardingResetBtn'
import KeyboardShortcuts from './components/KeyboardShortcuts'
import UsabilityTracker from './components/UsabilityTracker'
import { ABTestProvider, useABTest } from './components/ABTest'
import { AnalyticsProvider } from './components/Analytics'
import analytics, { trackWebVitals } from './components/Analytics'
import './styles.css'

// Lazy load heavy components for better performance
const SimulationDashboardV2 = lazy(() => import('./components/SimulationDashboardV2'))

// Create a React Query client with optimized cache settings
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes - data considered fresh
      cacheTime: 10 * 60 * 1000, // 10 minutes - cache persists
      refetchOnMount: false, // Don't refetch if data is fresh
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
  const [selectedCrypto, setSelectedCrypto] = useState(null)
  const [selectedMarket, setSelectedMarket] = useState('Global')
  const [showHealthPanel, setShowHealthPanel] = useState(false)
  const [healthStatus, setHealthStatus] = useState('loading')
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : false
  })
  const [language, setLanguage] = useState(() => localStorage.getItem('app_language') || 'en')
  const [currency, setCurrency] = useState(() => localStorage.getItem('currency') || 'USD')
  const [exchangeRate, setExchangeRate] = useState(null)
  const [rateSource, setRateSource] = useState('loading')

  // Toast notifications
  const [toasts, setToasts] = useState([])

  // Helper function to show toast
  const showToast = (message, type = 'info', duration = 3000) => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type, duration }])
  }

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }

  // Digital Assets / Crypto state
  const [portfolioView, setPortfolioView] = useState('stocks') // 'stocks', 'crypto', 'watchlists', 'simulation', or 'buy-opportunities'
  const [cryptoResults, setCryptoResults] = useState([])
  const [cryptoLoading, setCryptoLoading] = useState(false)
  const [includeNFT] = useState(true) // Always include NFTs
  const [cryptoLimit, setCryptoLimit] = useState(50)
  const [cryptoPage, setCryptoPage] = useState(1)
  const [cryptoPerPage] = useState(10) // Items per page
  const [cryptoSearchTerm, setCryptoSearchTerm] = useState('')

  // Filter crypto results based on search term
  const filteredCryptoResults = React.useMemo(() => {
    if (!cryptoSearchTerm) return cryptoResults
    const term = cryptoSearchTerm.toLowerCase()
    return cryptoResults.filter(crypto =>
      crypto.name.toLowerCase().includes(term) ||
      crypto.symbol.toLowerCase().includes(term)
    )
  }, [cryptoResults, cryptoSearchTerm])

  function handleCryptoSearchChange(e) {
    setCryptoSearchTerm(e.target.value)
    setCryptoPage(1) // Reset to page 1 when search changes
  }

  useEffect(() => {
    document.body.classList.toggle('dark-mode', darkMode)
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  useEffect(() => {
    localStorage.setItem('app_language', language)
  }, [language])

  useEffect(() => {
    localStorage.setItem('currency', currency)
  }, [currency])

  // Fetch exchange rate when currency changes
  useEffect(() => {
    async function fetchExchangeRate() {
      try {
        const response = await api.get('/currency')
        if (response.data.status === 'ok') {
          setExchangeRate(response.data.data.rate)
          setRateSource(response.data.data.source)
        }
      } catch (error) {
        console.error('Failed to fetch exchange rate:', error)
        setExchangeRate(0.85) // Fallback rate
        setRateSource('fallback')
      }
    }
    if (currency === 'CHF') {
      fetchExchangeRate()
    }
  }, [currency])
  // Initialize analytics and track web vitals
  useEffect(() => {
    trackWebVitals()
    analytics.trackPageView('Market Predictor Dashboard')
  }, [])

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

  async function fetchRanking(market = selectedMarket) {
    setLoading(true)
    setAnalysis(null)
    setCurrentPage(1)
    setLoadingProgress({ current: 0, total: 0 })

    // Track feature usage
    analytics.trackFeature('stock_ranking', 'load', { market })

    try {
      const startTime = Date.now()
      // Fetch ranking for selected market (single selection)
      const resp = await api.getRanking(market)
      const rankings = resp.data.ranking

      setResults(rankings)

      // Track performance
      analytics.trackPerformance('ranking_load', Date.now() - startTime)

      // Success toast
      showToast(`✅ Loaded ${rankings.length} ${market} stocks`, 'success', 2000)

      // Batch fetch ticker details (much faster than sequential)
      const tickers = rankings.map(r => r.ticker)
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
          showToast('⚠️ Network error: Please check your connection', 'warning')
        }
        // Fallback to sequential if batch fails
        await fetchDetailsSequential(rankings)
      }
    } catch (e) {
      const error = handleApiError(e, 'Error fetching ranking')
      if (error.isNetworkError) {
        showToast('⚠️ Unable to connect to server. Please ensure backend is running.', 'error', 5000)
      } else if (error.isRateLimit) {
        showToast('⏱️ Rate limit exceeded. Please wait a moment.', 'warning', 4000)
      } else {
        showToast(`Failed to load rankings: ${error.message}`, 'error')
      }
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
      showToast(`✅ Loaded ${rankings.length} cryptocurrencies`, 'success', 2000)
    } catch (e) {
      const error = handleApiError(e, 'Error fetching crypto rankings')
      if (error.isNetworkError) {
        showToast('⚠️ Unable to connect to server', 'error')
      } else if (error.isRateLimit) {
        showToast('⏱️ Rate limit exceeded. Please wait.', 'warning')
      } else {
        showToast(`Failed to load crypto: ${error.message}`, 'error')
      }
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
        showToast('⏱️ Rate limit reached. Please wait 30-60 seconds.', 'warning', 5000)
      } else {
        showToast(`Analysis error: ${error.message}`, 'error', 4000)
      }
    } finally {
      setAnalyzing(false)
    }
  }

  async function performSearch(tickerInput) {
    const t = typeof tickerInput === 'string' ? tickerInput.trim().toUpperCase() : (searchTicker || '').trim().toUpperCase()
    if (!t) {
      showToast('Please enter a stock symbol', 'warning')
      return
    }
    setSearchTicker(t) // Update input field

    // Track search
    analytics.trackSearch(t)

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
      showToast(`✅ Found ${info.name || t}`, 'success')
    } catch (e) {
      const error = handleApiError(e, 'Search failed')
      if (error.isNetworkError) {
        showToast('⚠️ Network error: Check connection', 'error')
      } else if (error.status === 404) {
        showToast(`❌ Ticker "${t}" not found`, 'error', 4000)
      } else if (error.isRateLimit) {
        showToast('⏱️ Rate limit exceeded. Wait a moment.', 'warning')
      } else {
        showToast(`Search failed: ${error.message}`, 'error')
      }
      console.error('Search error:', error)
    } finally {
      setSearchLoading(false)
    }
  }

  // Prepare autocomplete suggestions from current results
  const autocompleteSuggestions = React.useMemo(() => {
    return results.map(r => ({
      ticker: r.ticker,
      name: tickerDetails[r.ticker]?.name || '',
      country: tickerDetails[r.ticker]?.country || '',
      sector: tickerDetails[r.ticker]?.sector || '',
      price: tickerDetails[r.ticker]?.price || null,
      change: tickerDetails[r.ticker]?.change || null
    }))
  }, [results, tickerDetails])

  function formatNumber(num) {
    if (!num) return 'N/A'
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`
    return `$${num.toFixed(2)}`
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

  function openCryptoDetail(crypto) {
    // Crypto data is already complete from CoinGecko, just set it
    setSelectedCrypto({
      ...crypto,
      loading: false
    })
  }

  return (
    <div className="container">
      {/* Onboarding Flow */}
      <Onboarding />

      {/* Keyboard Shortcuts Helper */}
      <KeyboardShortcuts />

      {/* Skip Navigation Link */}
      <a href="#main-content" className="skip-link">Skip to main content</a>

      {/* Modern Fixed Toolbar - Option 2: Compact icons + separate language */}
      <div className="header-toolbar" aria-label="Application controls">
        {/* Icon group */}
        <div className="toolbar-icons">
          <button
            className={`toolbar-btn health-indicator ${healthStatus}`}
            onClick={() => setShowHealthPanel(!showHealthPanel)}
            aria-label={`System health: ${healthStatus}`}
            aria-expanded={showHealthPanel}
            title="System Health"
          >
            {healthStatus === 'healthy' && '✅'}
            {healthStatus === 'warning' && '⚠️'}
            {healthStatus === 'error' && '❌'}
            {healthStatus === 'loading' && '⏳'}
          </button>

          <button
            className="toolbar-btn theme-toggle"
            onClick={toggleDarkMode}
            aria-label={`Switch to ${darkMode ? 'light' : 'dark'} mode`}
            title={`Toggle ${darkMode ? 'light' : 'dark'} mode`}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>

          <button
            className="toolbar-btn currency-toggle"
            onClick={() => setCurrency(currency === 'USD' ? 'CHF' : 'USD')}
            aria-label={`Switch to ${currency === 'USD' ? 'CHF' : 'USD'}`}
            title={`Currency: ${currency}${currency === 'CHF' && exchangeRate ? ` (1 USD = ${exchangeRate.toFixed(4)} CHF)` : ''}`}
          >
            {currency}
          </button>

          <AlertPanel />

          <button
            className="toolbar-btn help-button"
            onClick={() => setShowHelp(true)}
            aria-label="Open help guide"
            title="Help & Guide"
          >
            ❓
          </button>
        </div>

        {/* Language selector - separate */}
        <div className="language-control">
          <label htmlFor="language-select" className="sr-only">Language</label>
          <select
            id="language-select"
            value={language}
            onChange={e => setLanguage(e.target.value)}
            aria-label="Select language"
          >
            <option value="de">🇩🇪 DE</option>
            <option value="en">🇬🇧 EN</option>
            <option value="it">🇮🇹 IT</option>
            <option value="es">🇪🇸 ES</option>
            <option value="fr">🇫🇷 FR</option>
          </select>
        </div>
      </div>

      <header className="header" role="banner">
        <h1><span className="emoji" aria-hidden="true">📈</span> Smart Trading Dashboard</h1>
        <p>Find the best stocks and crypto to buy today</p>
      </header>

      {/* Health Check Section - Toggle visibility */}
      <HealthCheck isOpen={showHealthPanel} onClose={() => setShowHealthPanel(false)} />

      <main id="main-content" role="main">
      {/* Portfolio View Toggle */}
      <section className="card" style={{marginBottom: '24px'}} role="region" aria-label="Portfolio view selector">
        <div className="card-title">📊 What would you like to explore?</div>
        {results.length === 0 && cryptoResults.length === 0 && portfolioView === 'stocks' && (
          <div className="onboarding-hint" style={{
            background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
            border: '2px solid #667eea30',
            borderRadius: '12px',
            padding: '16px',
            marginBottom: '16px',
            fontSize: '0.95rem',
            color: '#4a4a4a'
          }}>
            👋 <strong>New here?</strong> Start with <strong style={{color: '#667eea'}}>"Trading Signals"</strong> to see today's best opportunities, or explore <strong>"Top Stocks"</strong> ranked by AI.
          </div>
        )}
        <div className="portfolio-toggle-container">
          <button
            className={`portfolio-toggle-button buy-opportunities primary-cta ${portfolioView === 'buy-opportunities' ? 'active' : ''}`}
            onClick={() => setPortfolioView('buy-opportunities')}
            aria-label="Switch to trading signals view"
            aria-pressed={portfolioView === 'buy-opportunities'}
          >
            <div className="icon">🎯</div>
            <div className="title">Trading Signals</div>
          </button>

          <button
            className={`portfolio-toggle-button stocks ${portfolioView === 'stocks' ? 'active' : ''}`}
            onClick={() => {
              setPortfolioView('stocks')
              if (results.length === 0) fetchRanking()
            }}
            aria-label="Switch to top stocks portfolio view"
            aria-pressed={portfolioView === 'stocks'}
          >
            <div className="icon">📈</div>
            <div className="title">Top Stocks</div>
          </button>

          <button
            className={`portfolio-toggle-button crypto ${portfolioView === 'crypto' ? 'active' : ''}`}
            onClick={() => {
              setPortfolioView('crypto')
              if (cryptoResults.length === 0) fetchCryptoRanking()
            }}
            aria-label="Switch to cryptocurrency portfolio view"
            aria-pressed={portfolioView === 'crypto'}
          >
            <div className="icon">₿</div>
            <div className="title">Crypto</div>
          </button>

          <button
            className={`portfolio-toggle-button watchlists ${portfolioView === 'watchlists' ? 'active' : ''}`}
            onClick={() => setPortfolioView('watchlists')}
            aria-label="Switch to watchlists view"
            aria-pressed={portfolioView === 'watchlists'}
          >
            <div className="icon">⭐</div>
            <div className="title">Watchlist</div>
          </button>

          <button
            className={`portfolio-toggle-button simulation ${portfolioView === 'simulation' ? 'active' : ''}`}
            onClick={() => setPortfolioView('simulation')}
            aria-label="Switch to trading simulation view"
            aria-pressed={portfolioView === 'simulation'}
          >
            <div className="icon">🎮</div>
            <div className="title">Practice</div>
          </button>
        </div>
      </section>

      {/* Market View Selector - Only for stocks */}
      {portfolioView === 'stocks' && (
      <section className="card" role="region" aria-label="Market view selector">
        <div className="card-title">
          🌍 Choose Your Market - {selectedMarket}
          {!loading && results.length > 0 && (
            <span style={{marginLeft: '8px', color: '#667eea', fontWeight: 'bold'}}>({results.length})</span>
          )}
        </div>

        {/* Help InfoCard */}
        {results.length === 0 && !loading && (
          <InfoCard title="How to use" type="tip" dismissible={false}>
            <p>Select a market to see AI-ranked stocks based on predicted performance:</p>
            <ul>
              <li><strong>Global:</strong> Top stocks from worldwide markets</li>
              <li><strong>US:</strong> NYSE & NASDAQ companies</li>
              <li><strong>Europe:</strong> European exchanges</li>
              <li><strong>Asia:</strong> Asian markets including Japan, China, India</li>
            </ul>
            <p>Each stock shows an <strong>AI probability score</strong> indicating potential for upward movement.</p>
          </InfoCard>
        )}

        <MarketSelector
          selectedMarket={selectedMarket}
          onSelectionChange={(market) => {
            setSelectedMarket(market)
            fetchRanking(market)
          }}
          disabled={loading}
        />

        {loading ? (
          <LoadingState
            message={`Loading ${selectedMarket} market rankings...`}
            progress={loadingProgress.total > 0 ? (loadingProgress.current / loadingProgress.total) * 100 : null}
            itemCount={loadingProgress.total > 0 ? loadingProgress.total : null}
            itemLabel="company details"
            size="medium"
          />
        ) : results.length > 0 ? (
          <div style={{marginBottom: '16px'}}>
          </div>
        ) : (
          <div style={{textAlign: 'center', padding: '20px'}}>
            <p style={{color: '#667eea', fontSize: '1.1rem', fontWeight: '600', margin: '0 0 8px 0'}}>
              👆 Select a market to get started
            </p>
            <p style={{color: '#666', fontSize: '0.9rem', margin: '0'}}>
              We'll show you the top performing stocks ranked by our AI model
            </p>
          </div>
        )}
      </section>
      )}

      {/* Digital Assets / Crypto View */}
      {portfolioView === 'crypto' && (
        <div>
        {/* Help InfoCard for Crypto */}
        {cryptoResults.length === 0 && !cryptoLoading && (
          <InfoCard title="Understanding Crypto Rankings" type="tip">
            <p>Our cryptocurrency rankings use a <strong>momentum scoring system</strong>:</p>
            <ul>
              <li><strong>80-100:</strong> Very Bullish - Exceptional momentum</li>
              <li><strong>65-79:</strong> Bullish - Strong positive trends</li>
              <li><strong>50-64:</strong> Neutral - Stable performance</li>
              <li><strong>35-49:</strong> Bearish - Weakening signals</li>
              <li><strong>0-34:</strong> Very Bearish - High risk</li>
            </ul>
            <p>Scores consider: market cap rank, price trends (24h/7d/30d), volume, and momentum indicators.</p>
          </InfoCard>
        )}

        {/* Crypto Search Section */}
        <section className="card" role="region" aria-label="Search for digital assets and cryptocurrencies">
          <div className="card-title">🔍 Find Cryptocurrencies</div>
          <div style={{marginBottom: '8px', fontSize: '0.9rem', color: '#666'}}>
            💡 Search by name or symbol • Examples: Bitcoin, BTC, Ethereum, ETH
          </div>
          <div style={{marginTop: '16px'}}>
            <input
              type="text"
              placeholder="🔍 Search by name or symbol..."
              value={cryptoSearchTerm}
              onChange={handleCryptoSearchChange}
              aria-label="Search cryptocurrencies by name or symbol"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #ddd',
                borderRadius: '8px',
                fontSize: '0.95rem',
                outline: 'none',
                transition: 'border-color 0.3s ease'
              }}
              onFocus={(e) => e.target.style.borderColor = '#f59e0b'}
              onBlur={(e) => e.target.style.borderColor = '#ddd'}
            />
            {cryptoSearchTerm && (
              <p style={{marginTop: '8px', fontSize: '0.85rem', color: '#666'}}>
                Found {filteredCryptoResults.length} result{filteredCryptoResults.length !== 1 ? 's' : ''} for "{cryptoSearchTerm}"
                {filteredCryptoResults.length > 0 && (
                  <button
                    onClick={() => setCryptoSearchTerm('')}
                    style={{
                      marginLeft: '12px',
                      padding: '4px 12px',
                      background: '#f0f0f0',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.85rem'
                    }}
                  >
                    ✕ Clear
                  </button>
                )}
              </p>
            )}
          </div>
        </section>

        {/* Crypto Rankings Section */}
        <section className="card" role="region" aria-label="Digital assets and cryptocurrency rankings">
          <div className="card-title">
            ₿ Top Cryptocurrencies
            {!cryptoLoading && cryptoResults.length > 0 && (
              <span style={{marginLeft: '8px', color: '#f59e0b', fontWeight: 'bold'}}>({cryptoResults.length})</span>
            )}
          </div>

          <CryptoPortfolio
            cryptoResults={filteredCryptoResults}
            cryptoLoading={cryptoLoading}
            cryptoPage={cryptoPage}
            cryptoPerPage={cryptoPerPage}
            includeNFT={includeNFT}
            cryptoLimit={cryptoLimit}
            onPageChange={setCryptoPage}
            onNFTToggle={() => {}} // No-op since NFT toggle is removed
            onLimitChange={setCryptoLimit}
            onRefresh={fetchCryptoRanking}
            onRowClick={openCryptoDetail}
            searchTerm={cryptoSearchTerm}
          />

          {!cryptoLoading && cryptoResults.length === 0 && (
            <EmptyState
              icon="₿"
              title="No cryptocurrencies loaded"
              description="Click the button below to load the top cryptocurrencies ranked by market cap and momentum"
              actionLabel="Load Crypto Rankings"
              onAction={fetchCryptoRanking}
            />
          )}
        </section>
        </div>
      )}

      {/* Watchlists View */}
      {portfolioView === 'watchlists' && (
        <>
          <InfoCard title="Watchlist Pro Tips" type="tip" dismissible={false}>
            <p>Get the most out of your watchlists:</p>
            <ul>
              <li><strong>Price Alerts:</strong> Set alerts to get notified when a stock hits your target price</li>
              <li><strong>AI Predictions:</strong> View real-time buy/sell/hold signals for each stock</li>
              <li><strong>Mix Assets:</strong> Add both stocks and cryptocurrencies to the same watchlist</li>
              <li><strong>Notes:</strong> Add personal notes to track your investment thesis</li>
            </ul>
          </InfoCard>
          <WatchlistManagerV2 userId="default_user" />
        </>
      )}

      {/* Trading Simulation View */}
      {portfolioView === 'simulation' && (
        <Suspense fallback={<div style={{ textAlign: 'center', padding: '40px' }}><SkeletonTable /></div>}>
          <SimulationDashboardV2 />
        </Suspense>
      )}

      {/* Buy Opportunities View */}
      {portfolioView === 'buy-opportunities' && (
        <BuyOpportunities currency={currency} exchangeRate={exchangeRate} />
      )}

      {/* Search Section - Only for stocks */}
      {portfolioView === 'stocks' && (
      <div>
      <section className="card" role="region" aria-label="Search for individual stocks">
        <div className="card-title">🔍 Look Up Any Stock</div>

        <InfoCard type="info" dismissible={false}>
          <p><strong>Pro tip:</strong> Start typing a ticker symbol or company name to see suggestions. The autocomplete will help you find stocks from the current market rankings.</p>
        </InfoCard>

        <p style={{color: '#666', fontSize: '0.9rem', marginBottom: '16px'}}>
          Search by ticker symbol to get AI predictions and detailed analysis
        </p>
        <AutocompleteSearch
          suggestions={autocompleteSuggestions}
          onSearch={performSearch}
          placeholder="e.g., AMD, META, NFLX"
          loading={searchLoading}
          disabled={searchLoading}
        />
      </section>

      {/* Search Result */}
      {searchResult && searchResultDetails && (
        <section className="search-result" role="region" aria-label="Stock search results">
          <h2>🎯 Search Result</h2>
          <div className="table-wrapper">
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
          </div>
        </section>
          )}
        </div>
      )}

      {/* Results Section - Only for stocks */}
      {portfolioView === 'stocks' && results.length > 0 && (
        <>
          {/* Ranked Stocks Table */}
          <StockRanking
            results={results}
            tickerDetails={tickerDetails}
            currentPage={currentPage}
            itemsPerPage={itemsPerPage}
            onPageChange={setCurrentPage}
            onRowClick={openCompanyDetail}
          />
        </>
      )}

      {/* Help Modal */}
      <HelpModal isOpen={showHelp} onClose={() => setShowHelp(false)} />

      {/* Company Detail Sidebar */}
      <CompanyDetailSidebar company={selectedCompany} onClose={() => setSelectedCompany(null)} />

      {/* Crypto Detail Sidebar */}
      <CryptoDetailSidebar crypto={selectedCrypto} onClose={() => setSelectedCrypto(null)} />

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

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      {/* Onboarding Reset Button (Dev Only) */}
      <OnboardingResetBtn />

      {/* Usability Tracker */}
      <UsabilityTracker enabled={import.meta.env.DEV || import.meta.env.VITE_ENABLE_USABILITY_TRACKING === 'true'} />
    </div>
  )
}

// Define A/B Test experiments
const abTestExperiments = {
  'stock_card_layout': {
    variants: ['A', 'B'],
    weights: [0.5, 0.5]
  },
  'cta_button_text': {
    variants: ['A', 'B', 'C'],
    weights: [0.33, 0.33, 0.34]
  },
  'price_chart_default': {
    variants: ['candlestick', 'line'],
    weights: [0.5, 0.5]
  }
}

// Wrap with providers and error boundary
export default function App() {
  return (
    <ErrorBoundary>
      <AnalyticsProvider>
        <ABTestProvider experiments={abTestExperiments}>
          <QueryClientProvider client={queryClient}>
            <AppContent />
          </QueryClientProvider>
        </ABTestProvider>
      </AnalyticsProvider>
    </ErrorBoundary>
  )
}
