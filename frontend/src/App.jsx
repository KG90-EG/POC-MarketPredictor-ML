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

  function formatNumber(num) {
    if (!num) return 'N/A'
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`
    return `$${num.toFixed(2)}`
  }

  return (
    <div className="container">
      <h1>📈 Trading Fun — AI-Powered Ranking</h1>
      
      <div className="controls">
        <label>
          <strong>Tickers (comma-separated):</strong>
          <input 
            value={tickers} 
            onChange={(e) => setTickers(e.target.value)}
            placeholder="AAPL,MSFT,NVDA"
          />
        </label>
        <button onClick={fetchRanking} disabled={loading}>
          {loading ? 'Loading...' : 'Get Ranking'}
        </button>
      </div>

      {results.length > 0 && (
        <>
          <div className="analysis-section">
            <label>
              <strong>Optional context for LLM analysis:</strong>
              <textarea 
                value={userContext}
                onChange={(e) => setUserContext(e.target.value)}
                placeholder="e.g., I'm interested in tech stocks with growth potential..."
                rows={3}
              />
            </label>
            <button onClick={requestAnalysis} disabled={analyzing}>
              {analyzing ? 'Analyzing...' : '🤖 Get AI Recommendations'}
            </button>
          </div>

          {analysis && (
            <div className="analysis-result">
              <h3>💡 AI Analysis & Recommendations</h3>
              <p style={{ whiteSpace: 'pre-wrap' }}>{analysis}</p>
            </div>
          )}

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
                    <td>{idx + 1}</td>
                    <td><strong>{r.ticker}</strong></td>
                    <td>{detail.name || 'N/A'}</td>
                    <td className={r.prob > 0.6 ? 'high-prob' : ''}>{(r.prob * 100).toFixed(2)}%</td>
                    <td>{detail.price ? `$${detail.price.toFixed(2)}` : 'N/A'}</td>
                    <td className={changeClass}>
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
