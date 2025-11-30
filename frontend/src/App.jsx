import React, { useState, useEffect } from 'react'
import { api, handleApiError } from './api'
import './styles.css'

export default function App() {
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
  const [selectedCountry, setSelectedCountry] = useState('All')
  const [selectedView, setSelectedView] = useState('Global')
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : false
  })

  useEffect(() => {
    document.body.classList.toggle('dark-mode', darkMode)
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  // Auto-load ranking on mount
  useEffect(() => {
    fetchRanking()
  }, [])

  function toggleDarkMode() {
    setDarkMode(!darkMode)
  }

  async function fetchRanking(view = selectedView) {
    setLoading(true)
    setAnalysis(null)
    setCurrentPage(1)
    setLoadingProgress({ current: 0, total: 0 })
    
    try {
      // Fetch ranking
      const resp = await api.getRanking(view)
      const ranking = resp.data.ranking
      setResults(ranking)
      
      // Batch fetch ticker details (much faster than sequential)
      const tickers = ranking.map(r => r.ticker)
      setLoadingProgress({ current: 0, total: tickers.length })
      
      try {
        const batchResp = await api.getTickerInfoBatch(tickers)
        const { results: batchResults, errors } = batchResp.data
        
        // Log any errors but don't fail the whole operation
        if (Object.keys(errors).length > 0) {
          console.warn('Some tickers failed to load:', errors)
        }
        
        setTickerDetails(batchResults || {})
        setLoadingProgress({ current: Object.keys(batchResults || {}).length, total: tickers.length })
      } catch (batchError) {
        console.error('Batch fetch failed, falling back to sequential', batchError)
        // Fallback to sequential if batch fails
        await fetchDetailsSequential(ranking)
      }
    } catch (e) {
      const error = handleApiError(e, 'Error fetching ranking')
      alert(`Error: ${error.message}`)
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
      alert(`Error: ${error.message}`)
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
      setSelectedCompany({ ticker, error: error.message, loading: false })
    }
  }

  return (
    <div className="container">
      <div className="header">
        <button className="theme-toggle" onClick={toggleDarkMode} title="Toggle theme">
          {darkMode ? '☀️' : '🌙'}
        </button>
        <button className="help-button" onClick={() => setShowHelp(true)} title="Help & Guide">
          ❓
        </button>
        <h1><span className="emoji">📈</span> Trading Fun</h1>
        <p>AI-Powered Stock Ranking & Analysis</p>
      </div>
      
      {/* Market View Selector */}
      <div className="card">
        <div className="card-title">🌍 Market View - Select a Region</div>
        <div style={{display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '16px'}}>
          {['Global', 'United States', 'Switzerland', 'Germany', 'United Kingdom', 'France', 'Japan', 'Canada'].map(view => (
            <button
              key={view}
              onClick={() => {
                setSelectedView(view)
                setSelectedCountry('All')
                fetchRanking(view)
              }}
              style={{
                padding: '10px 20px',
                background: selectedView === view ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#f0f0f0',
                color: selectedView === view ? 'white' : '#333',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: selectedView === view ? '600' : '400',
                transition: 'all 0.3s ease',
                boxShadow: selectedView === view ? '0 4px 12px rgba(102, 126, 234, 0.4)' : 'none'
              }}
            >
              {view === 'Global' ? '🌐' : 
               view === 'United States' ? '🇺🇸' : 
               view === 'Switzerland' ? '🇨🇭' : 
               view === 'Germany' ? '🇩🇪' : 
               view === 'United Kingdom' ? '🇬🇧' : 
               view === 'France' ? '🇫🇷' : 
               view === 'Japan' ? '🇯🇵' : 
               view === 'Canada' ? '🇨🇦' : '🌎'} {view}
            </button>
          ))}
        </div>
        
        {loading ? (
          <div style={{textAlign: 'center', padding: '40px'}}>
            <span className="spinner"></span>
            <p>Loading {selectedView} market rankings...</p>
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
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px'}}>
            <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
              <p style={{margin: 0, color: '#666', fontWeight: '600'}}>
                📊 {selectedCountry === 'All' 
                  ? `${results.length} stocks ranked from ${selectedView}` 
                  : `${results.filter(r => tickerDetails[r.ticker]?.country === selectedCountry).length} stocks filtered by ${selectedCountry}`}
              </p>
              {Object.keys(tickerDetails).length > 0 && (
                <select 
                  value={selectedCountry} 
                  onChange={(e) => { setSelectedCountry(e.target.value); setCurrentPage(1); }}
                  style={{padding: '6px 12px', borderRadius: '6px', border: '2px solid #667eea', background: 'white', cursor: 'pointer'}}
                >
                  <option value="All">All Countries</option>
                  {(() => {
                    const countries = [...new Set(Object.values(tickerDetails).map(d => d.country).filter(Boolean))]
                    return countries.sort().map(country => (
                      <option key={country} value={country}>
                        {country === 'United States' ? '🇺🇸' : 
                         country === 'China' ? '🇨🇳' : 
                         country === 'United Kingdom' ? '🇬🇧' : 
                         country === 'Germany' ? '🇩🇪' : 
                         country === 'France' ? '🇫🇷' : 
                         country === 'Japan' ? '🇯🇵' : 
                         country === 'Switzerland' ? '🇨🇭' : 
                         country === 'Canada' ? '🇨🇦' : '🌎'} {country}
                      </option>
                    ))
                  })()}
                </select>
              )}
            </div>
            <button onClick={() => fetchRanking(selectedView)} style={{padding: '8px 16px'}}>
              🔄 Refresh
            </button>
          </div>
        ) : (
          <p style={{color: '#666', fontSize: '0.9rem', margin: '0'}}>
            Select a market view above to analyze top performers for a diversified portfolio
          </p>
        )}
      </div>

      {/* Search Section */}
      <div className="card">
        <div className="card-title">🔍 Search Individual Stock</div>
        <div className="search-controls">
          <label>
            Stock symbol
            <input
              value={searchTicker}
              onChange={(e) => setSearchTicker(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e, performSearch)}
              placeholder="e.g., AMD, META, NFLX"
            />
          </label>
          <button onClick={performSearch} disabled={searchLoading}>
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
      </div>

      {/* Search Result */}
      {searchResult && searchResultDetails && (
        <div className="search-result">
          <h2>🎯 Search Result</h2>
          <table>
            <thead>
              <tr>
                <th>Stock</th>
                <th>Name</th>
                <th>Country</th>
                <th>Probability</th>
                <th>Price</th>
                <th>Change %</th>
                <th>Volume</th>
                <th>Market Cap</th>
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
                  <span className={searchResult.prob > 0.6 ? 'high-prob' : ''}>
                    {searchResult.prob != null ? `${(searchResult.prob * 100).toFixed(2)}%` : 'N/A'}
                  </span>
                </td>
                <td>{searchResultDetails[searchResult.ticker]?.price != null ? `$${searchResultDetails[searchResult.ticker].price.toFixed(2)}` : 'N/A'}</td>
                <td>
                  <span className={searchResultDetails[searchResult.ticker]?.change > 0 ? 'positive' : searchResultDetails[searchResult.ticker]?.change < 0 ? 'negative' : ''}>
                    {searchResultDetails[searchResult.ticker]?.change != null ? `${searchResultDetails[searchResult.ticker].change > 0 ? '+' : ''}${searchResultDetails[searchResult.ticker].change.toFixed(2)}%` : 'N/A'}
                  </span>
                </td>
                <td>{searchResultDetails[searchResult.ticker]?.volume != null ? searchResultDetails[searchResult.ticker].volume.toLocaleString() : 'N/A'}</td>
                <td>{formatNumber(searchResultDetails[searchResult.ticker]?.market_cap)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {/* Results Section */}
      {results.length > 0 && (
        <>
          {/* AI Analysis Section */}
          <div className="analysis-section">
            <label>
              <strong>🤖 Optional context for AI analysis</strong>
              <textarea 
                value={userContext}
                onChange={(e) => setUserContext(e.target.value)}
                placeholder="e.g., I'm interested in tech stocks with growth potential, looking for long-term investments..."
                rows={3}
              />
            </label>
            <button onClick={requestAnalysis} disabled={analyzing}>
              {analyzing ? (
                <>
                  <span className="spinner"></span>
                  Analyzing...
                </>
              ) : (
                '✨ Get AI Recommendations'
              )}
            </button>
          </div>

          {/* AI Analysis Result */}
          {analysis && (
            <div className="analysis-result">
              <h3>💡 AI Analysis & Recommendations</h3>
              <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{analysis}</p>
            </div>
          )}

          {/* Ranked Stocks Table */}
          <h2>Ranked Stocks</h2>
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Stock</th>
                <th>Name</th>
                <th>Country</th>
                <th>Probability</th>
                <th>Price</th>
                <th>Change %</th>
                <th>Volume</th>
                <th>Market Cap</th>
              </tr>
            </thead>
            <tbody>
              {results
                .filter(r => selectedCountry === 'All' || tickerDetails[r.ticker]?.country === selectedCountry)
                .slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
                .map((r, idx) => {
                const rank = results.filter(item => selectedCountry === 'All' || tickerDetails[item.ticker]?.country === selectedCountry).indexOf(r) + 1
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
                      <span className={r.prob > 0.6 ? 'high-prob' : ''}>
                        {(r.prob * 100).toFixed(2)}%
                      </span>
                    </td>
                    <td>{detail.price ? `$${detail.price.toFixed(2)}` : 'N/A'}</td>
                    <td>
                      <span className={changeClass}>
                        {detail.change ? `${detail.change > 0 ? '+' : ''}${detail.change.toFixed(2)}%` : 'N/A'}
                      </span>
                    </td>
                    <td>{detail.volume ? detail.volume.toLocaleString() : 'N/A'}</td>
                    <td>{formatNumber(detail.market_cap)}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>

          {/* Pagination Controls */}
          {results.filter(r => selectedCountry === 'All' || tickerDetails[r.ticker]?.country === selectedCountry).length > itemsPerPage && (
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
                  {Array.from({ length: Math.ceil(results.filter(r => selectedCountry === 'All' || tickerDetails[r.ticker]?.country === selectedCountry).length / itemsPerPage) }, (_, i) => i + 1).map(pageNum => (
                    <option key={pageNum} value={pageNum}>{pageNum}</option>
                  ))}
                </select>
                <span className="page-info">of {Math.ceil(results.filter(r => selectedCountry === 'All' || tickerDetails[r.ticker]?.country === selectedCountry).length / itemsPerPage)}</span>
              </div>
              <button 
                onClick={() => setCurrentPage(p => Math.min(Math.ceil(results.filter(r => selectedCountry === 'All' || tickerDetails[r.ticker]?.country === selectedCountry).length / itemsPerPage), p + 1))} 
                disabled={currentPage >= Math.ceil(results.filter(r => selectedCountry === 'All' || tickerDetails[r.ticker]?.country === selectedCountry).length / itemsPerPage)}
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
    </div>
  )
}
