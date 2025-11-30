import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './index.css'

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

  return (
    <div className="container">
      <header className="app-header">
        <h1>📈 Trading Fun — AI-Powered Ranking</h1>
        <p className="subtitle">Insights, ranking, and quick search powered by ML + LLM</p>
      </header>
      
      <div className="controls card">
        <label>
          <strong>Tickers (comma-separated):</strong>
          <input 
            value={tickers} 
            onChange={(e) => setTickers(e.target.value)}
            placeholder="AAPL,MSFT,NVDA"
          />
        </label>
        <button className="btn primary" onClick={fetchRanking} disabled={loading}>
          {loading ? 'Loading...' : 'Get Ranking'}
        </button>
      </div>

      <div className="search-controls card">
        <label>
          <strong>Search Ticker:</strong>
          <input
            value={searchTicker}
            onChange={(e) => setSearchTicker(e.target.value)}
            placeholder="e.g., AMD"
          />
        </label>
        <button className="btn" onClick={performSearch} disabled={searchLoading}>
          {searchLoading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {searchResult && (
        <div className="search-result card">
          <h2>Search Result</h2>
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
                <td><strong>{searchResult.ticker}</strong></td>
                <td>{searchResult.name}</td>
                <td>{searchResult.prob != null ? `${(searchResult.prob * 100).toFixed(2)}%` : 'N/A'}</td>
                <td>{searchResult.price != null ? `$${searchResult.price.toFixed(2)}` : 'N/A'}</td>
                <td className={searchResult.change > 0 ? 'positive badge' : searchResult.change < 0 ? 'negative badge' : 'badge'}>
                  {searchResult.change != null ? `${searchResult.change > 0 ? '+' : ''}${searchResult.change.toFixed(2)}%` : 'N/A'}
                </td>
                <td>{searchResult.volume != null ? searchResult.volume.toLocaleString() : 'N/A'}</td>
                <td>{formatNumber(searchResult.market_cap)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {results.length > 0 && (
        <>
          <div className="analysis-section card">
            <label>
              <strong>Optional context for LLM analysis:</strong>
              <textarea 
                value={userContext}
                onChange={(e) => setUserContext(e.target.value)}
                placeholder="e.g., I'm interested in tech stocks with growth potential..."
                rows={3}
              />
            </label>
            <button className="btn accent" onClick={requestAnalysis} disabled={analyzing}>
              {analyzing ? 'Analyzing...' : '🤖 Get AI Recommendations'}
            </button>
          </div>

          {analysis && (
            <div className="analysis-result card">
              <h3>💡 AI Analysis & Recommendations</h3>
              <p style={{ whiteSpace: 'pre-wrap' }}>{analysis}</p>
            </div>
          )}

          <h2>Ranked Stocks</h2>
          <table className="table">
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
                    <td>{idx + 1}</td>
                    <td><strong>{r.ticker}</strong></td>
                    <td>{detail.name || 'N/A'}</td>
                    <td className={r.prob > 0.6 ? 'high-prob badge' : 'badge'}>{(r.prob * 100).toFixed(2)}%</td>
                    <td>{detail.price ? `$${detail.price.toFixed(2)}` : 'N/A'}</td>
                    <td className={`${changeClass} badge`}>
                      {detail.change ? `${detail.change > 0 ? '+' : ''}${detail.change.toFixed(2)}%` : 'N/A'}
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
    </div>
  )
}
