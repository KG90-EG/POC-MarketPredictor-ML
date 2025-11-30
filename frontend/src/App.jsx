import React, { useState, useEffect } from 'react'
import axios from 'axios'

export default function App() {
  const [tickers, setTickers] = useState('AAPL,MSFT,NVDA,GOOGL,TSLA')
  const [results, setResults] = useState([])
  const [tickerDetails, setTickerDetails] = useState({})
  const [analysis, setAnalysis] = useState(null)
  const [userContext, setUserContext] = useState('')
  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [searchTicker, setSearchTicker] = useState('')
  const [searchLoading, setSearchLoading] = useState(false)
  const [searchResult, setSearchResult] = useState(null)

  async function fetchRanking() {
    setLoading(true)
    setAnalysis(null)
    try {
      const url = `http://localhost:8000/ranking?tickers=${encodeURIComponent(tickers)}`
      const resp = await axios.get(url)
      setResults(resp.data.ranking)
      // Fetch details for each ticker
      const details = {}
      for (const r of resp.data.ranking) {
        try {
          const infoResp = await axios.get(`http://localhost:8000/ticker_info/${r.ticker}`)
          details[r.ticker] = infoResp.data
        } catch (e) {
          console.error(`Failed to fetch info for ${r.ticker}`, e)
        }
      }
      setTickerDetails(details)
    } catch (e) {
      console.error(e)
      alert('Error fetching ranking')
    } finally {
      setLoading(false)
    }
  }

  async function requestAnalysis() {
    if (results.length === 0) return
    setAnalyzing(true)
    try {
      const resp = await axios.post('http://localhost:8000/analyze', {
        ranking: results,
        user_context: userContext || null
      })
      const cachedNote = resp.data.cached ? ' (cached result)' : ''
      setAnalysis(resp.data.analysis + cachedNote)
    } catch (e) {
      console.error(e)
      const errorDetail = e.response?.data?.detail || 'Analysis failed.'
      if (e.response?.status === 429) {
        alert('⏱️ Rate limit reached. Please wait 30-60 seconds and try again.\n\n' + errorDetail)
      } else {
        alert(errorDetail + '\n\nMake sure OPENAI_API_KEY is set correctly.')
      }
    } finally {
      setAnalyzing(false)
    }
  }

  async function performSearch() {
    const t = (searchTicker || '').trim().toUpperCase()
    if (!t) {
      alert('Please enter a ticker to search.')
      return
    }
    setSearchLoading(true)
    setSearchResult(null)
    try {
      const [infoResp, predResp] = await Promise.all([
        axios.get(`http://localhost:8000/ticker_info/${t}`),
        axios.get(`http://localhost:8000/predict_ticker/${t}`)
      ])
      const info = infoResp.data || {}
      const prob = predResp.data?.prob || null
      setSearchResult({
        ticker: t,
        name: info.name || 'N/A',
        price: info.price || null,
        change: info.change || null,
        volume: info.volume || null,
        market_cap: info.market_cap || null,
        prob
      })
    } catch (e) {
      console.error('Search error', e)
      const detail = e.response?.data?.detail || 'Failed to fetch ticker info.'
      alert(detail)
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

  return (
    <div className="container">
      <div className="header">
        <h1><span className="emoji">📈</span> Trading Fun</h1>
        <p>AI-Powered Stock Ranking & Analysis</p>
      </div>
      
      {/* Ranking Section */}
      <div className="card">
        <div className="card-title">📊 Stock Ranking</div>
        <div className="controls">
          <label>
            Enter stock tickers (comma-separated)
            <div className="input-group">
              <input 
                value={tickers} 
                onChange={(e) => setTickers(e.target.value)}
                onKeyPress={(e) => handleKeyPress(e, fetchRanking)}
                placeholder="AAPL,MSFT,NVDA,GOOGL,TSLA"
              />
              <button onClick={fetchRanking} disabled={loading}>
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Loading...
                  </>
                ) : (
                  '🚀 Get Ranking'
                )}
              </button>
            </div>
          </label>
        </div>
      </div>

      {/* Search Section */}
      <div className="card">
        <div className="card-title">🔍 Search Individual Ticker</div>
        <div className="search-controls">
          <label>
            Ticker symbol
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
      {searchResult && (
        <div className="search-result">
          <h2>🎯 Search Result</h2>
          <table>
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Name</th>
                <th>Probability</th>
                <th>Price</th>
                <th>Change %</th>
                <th>Volume</th>
                <th>Market Cap</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><span className="ticker-symbol">{searchResult.ticker}</span></td>
                <td>{searchResult.name}</td>
                <td>
                  <span className={searchResult.prob > 0.6 ? 'high-prob' : ''}>
                    {searchResult.prob != null ? `${(searchResult.prob * 100).toFixed(2)}%` : 'N/A'}
                  </span>
                </td>
                <td>{searchResult.price != null ? `$${searchResult.price.toFixed(2)}` : 'N/A'}</td>
                <td>
                  <span className={searchResult.change > 0 ? 'positive' : searchResult.change < 0 ? 'negative' : ''}>
                    {searchResult.change != null ? `${searchResult.change > 0 ? '+' : ''}${searchResult.change.toFixed(2)}%` : 'N/A'}
                  </span>
                </td>
                <td>{searchResult.volume != null ? searchResult.volume.toLocaleString() : 'N/A'}</td>
                <td>{formatNumber(searchResult.market_cap)}</td>
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
                <th>Ticker</th>
                <th>Name</th>
                <th>Probability</th>
                <th>Price</th>
                <th>Change %</th>
                <th>Volume</th>
                <th>Market Cap</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, idx) => {
                const detail = tickerDetails[r.ticker] || {}
                const changeClass = detail.change > 0 ? 'positive' : detail.change < 0 ? 'negative' : ''
                return (
                  <tr key={r.ticker}>
                    <td>
                      <span className={getRankBadgeClass(idx + 1)}>{idx + 1}</span>
                    </td>
                    <td><span className="ticker-symbol">{r.ticker}</span></td>
                    <td>{detail.name || 'N/A'}</td>
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
        </>
      )}

      {/* Empty State */}
      {results.length === 0 && !loading && (
        <div className="empty-state">
          <div className="empty-state-icon">📊</div>
          <p>Enter stock tickers above and click "Get Ranking" to see AI-powered predictions</p>
        </div>
      )}
    </div>
  )
}
