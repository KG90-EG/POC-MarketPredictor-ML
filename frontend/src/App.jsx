import React, { useState, useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { api, handleApiError } from './api'
import ErrorBoundary from './components/ErrorBoundary'
import HealthCheck from './components/HealthCheck'
import Tooltip from './components/Tooltip'
import HelpModal from './components/HelpModal'
import CompanyDetailSidebar from './components/CompanyDetailSidebar'
import CryptoDetailSidebar from './components/CryptoDetailSidebar'
import AIAnalysisSection from './components/AIAnalysisSection'
import StockRanking from './components/StockRanking'
import CryptoPortfolio from './components/CryptoPortfolio'
import MarketSelector from './components/MarketSelector'
import WatchlistManager from './components/WatchlistManager'
import BuyOpportunities from './components/BuyOpportunities'
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
  const [selectedCrypto, setSelectedCrypto] = useState(null)
  const [selectedMarket, setSelectedMarket] = useState('Global')
  const [showHealthPanel, setShowHealthPanel] = useState(false)
  const [healthStatus, setHealthStatus] = useState('loading')
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : false
  })

  // Digital Assets / Crypto state
  const [portfolioView, setPortfolioView] = useState('stocks') // 'stocks', 'crypto', or 'watchlists'
  const [cryptoResults, setCryptoResults] = useState([])
  const [cryptoLoading, setCryptoLoading] = useState(false)
  const [includeNFT] = useState(true) // Always include NFTs
  const [cryptoLimit, setCryptoLimit] = useState(50)
  const [cryptoPage, setCryptoPage] = useState(1)
  const [cryptoPerPage] = useState(20) // Items per page
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

    try {
      // Fetch ranking for selected market (single selection)
      const resp = await api.getRanking(market)
      const rankings = resp.data.ranking

      setResults(rankings)

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
        <div className="portfolio-toggle-container">
          <button
            className={`portfolio-toggle-button buy-opportunities ${portfolioView === 'buy-opportunities' ? 'active' : ''}`}
            onClick={() => setPortfolioView('buy-opportunities')}
            aria-label="Switch to buy opportunities view"
            aria-pressed={portfolioView === 'buy-opportunities'}
          >
            <div className="icon">🎯</div>
            <div className="title">Buy / Sell</div>
            <div className="description">
              Trading signals
            </div>
          </button>

          <button
            className={`portfolio-toggle-button stocks ${portfolioView === 'stocks' ? 'active' : ''}`}
            onClick={() => {
              setPortfolioView('stocks')
              if (results.length === 0) fetchRanking()
            }}
            aria-label="Switch to stocks and shares portfolio view"
            aria-pressed={portfolioView === 'stocks'}
          >
            <div className="icon">📈</div>
            <div className="title">Stocks</div>
            <div className="description">
              Equities & ETFs
            </div>
          </button>

          <button
            className={`portfolio-toggle-button crypto ${portfolioView === 'crypto' ? 'active' : ''}`}
            onClick={() => {
              setPortfolioView('crypto')
              if (cryptoResults.length === 0) fetchCryptoRanking()
            }}
            aria-label="Switch to digital assets and cryptocurrency portfolio view"
            aria-pressed={portfolioView === 'crypto'}
          >
            <div className="icon">₿</div>
            <div className="title">Crypto</div>
            <div className="description">
              Bitcoin & NFTs
            </div>
          </button>

          <button
            className={`portfolio-toggle-button watchlists ${portfolioView === 'watchlists' ? 'active' : ''}`}
            onClick={() => setPortfolioView('watchlists')}
            aria-label="Switch to watchlists view"
            aria-pressed={portfolioView === 'watchlists'}
          >
            <div className="icon">⭐</div>
            <div className="title">Watchlists</div>
            <div className="description">
              Saved favorites
            </div>
          </button>
        </div>
      </section>

      {/* Market View Selector - Only for stocks */}
      {portfolioView === 'stocks' && (
      <section className="card" role="region" aria-label="Market view selector">
        <div className="card-title">
          🌍 Market View - {selectedMarket}
          {!loading && results.length > 0 && (
            <span style={{marginLeft: '8px', color: '#667eea', fontWeight: 'bold'}}>({results.length})</span>
          )}
        </div>
        <MarketSelector
          selectedMarket={selectedMarket}
          onSelectionChange={(market) => {
            setSelectedMarket(market)
            fetchRanking(market)
          }}
          disabled={loading}
        />

        {loading ? (
          <div style={{textAlign: 'center', padding: '40px'}} role="status" aria-live="polite" aria-atomic="true">
            <span className="spinner"></span>
            <p>Loading {selectedMarket} market rankings...</p>
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
        <>
        {/* Crypto Search Section */}
        <section className="card" role="region" aria-label="Search for digital assets and cryptocurrencies">
          <div className="card-title">🔍 Search Digital Assets</div>
          <div style={{marginBottom: '8px', fontSize: '0.9rem', color: '#666'}}>
            💡 Search by name or symbol (e.g., Bitcoin, BTC, Ethereum, ETH)
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
            ₿ Digital Assets Rankings
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
        </section>
        </>
      )}

      {/* Watchlists View */}
      {portfolioView === 'watchlists' && (
        <WatchlistManager userId="default_user" />
      )}

      {/* Buy Opportunities View */}
      {portfolioView === 'buy-opportunities' && (
        <BuyOpportunities />
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
      </>
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
