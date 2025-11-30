import React, { useState } from 'react'
import axios from 'axios'

export default function App() {
  const [tickers, setTickers] = useState('AAPL,MSFT,NVDA')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  async function fetchRanking() {
    setLoading(true)
    try {
      const url = `http://localhost:8000/ranking?tickers=${encodeURIComponent(tickers)}`
      const resp = await axios.get(url)
      setResults(resp.data.ranking)
    } catch (e) {
      console.error(e)
      alert('Error fetching ranking')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>Trading Fun — Ranking</h1>
      <div className="controls">
        <input value={tickers} onChange={(e) => setTickers(e.target.value)} />
        <button onClick={fetchRanking} disabled={loading}>Get Ranking</button>
      </div>
      <table>
        <thead>
          <tr><th>Ticker</th><th>Probability</th></tr>
        </thead>
        <tbody>
          {results.map(r => (
            <tr key={r.ticker}><td>{r.ticker}</td><td>{(r.prob*100).toFixed(2)}%</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
