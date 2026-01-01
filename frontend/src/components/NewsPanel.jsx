import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import './NewsPanel.css'

/**
 * NewsPanel Component
 * Displays financial news related to a ticker
 */
function NewsPanel({ ticker, limit = 5 }) {
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [expanded, setExpanded] = useState(false)

  useEffect(() => {
    if (!ticker) {
      setNews([])
      return
    }

    fetchNews()
  }, [ticker, limit])

  const fetchNews = async () => {
    setLoading(true)
    setError(null)

    try {
      // TODO: Replace with real news API
      // const response = await api.getNews(ticker, limit)
      // setNews(response.data.news)

      // Mock data for demo
      const mockNews = generateMockNews(ticker, limit)
      setNews(mockNews)
    } catch (err) {
      console.error('Failed to fetch news:', err)
      setError('Failed to load news')
    } finally {
      setLoading(false)
    }
  }

  // Generate mock news data
  const generateMockNews = (symbol, count) => {
    const templates = [
      { title: `${symbol} Reports Strong Q4 Earnings`, sentiment: 'positive' },
      { title: `Analysts Upgrade ${symbol} to Buy`, sentiment: 'positive' },
      { title: `${symbol} Announces New Product Line`, sentiment: 'positive' },
      { title: `${symbol} Faces Regulatory Challenges`, sentiment: 'negative' },
      { title: `${symbol} CEO Steps Down Amid Controversy`, sentiment: 'negative' },
      { title: `${symbol} Stock Price Volatility Continues`, sentiment: 'neutral' },
      { title: `Institutional Investors Increase ${symbol} Holdings`, sentiment: 'positive' },
      { title: `${symbol} Market Share Under Pressure`, sentiment: 'negative' },
      { title: `${symbol} Maintains Steady Growth Trajectory`, sentiment: 'neutral' },
      { title: `Breaking: ${symbol} Announces Major Acquisition`, sentiment: 'positive' }
    ]

    const sources = ['Bloomberg', 'Reuters', 'CNBC', 'WSJ', 'Financial Times', 'MarketWatch']
    
    return Array.from({ length: count }, (_, i) => {
      const template = templates[i % templates.length]
      const hoursAgo = Math.floor(Math.random() * 24) + 1
      const source = sources[Math.floor(Math.random() * sources.length)]

      return {
        id: `news-${ticker}-${i}`,
        title: template.title,
        source,
        published_at: new Date(Date.now() - hoursAgo * 60 * 60 * 1000).toISOString(),
        url: `https://example.com/news/${ticker.toLowerCase()}-${i}`,
        sentiment: template.sentiment,
        summary: `Latest developments regarding ${symbol}. This article discusses recent market movements and analyst perspectives on the company's future outlook.`
      }
    })
  }

  const formatTimeAgo = (dateString) => {
    const now = new Date()
    const published = new Date(dateString)
    const diffMs = now - published
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)

    if (diffHours < 1) return 'Just now'
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays}d ago`
    return published.toLocaleDateString()
  }

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '📈'
      case 'negative': return '📉'
      default: return '📊'
    }
  }

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '#28a745'
      case 'negative': return '#dc3545'
      default: return '#6c757d'
    }
  }

  if (!ticker) {
    return (
      <div className="news-panel">
        <div className="news-empty">
          <span className="empty-icon">📰</span>
          <p>Select a stock to see related news</p>
        </div>
      </div>
    )
  }

  return (
    <div className="news-panel">
      <div className="news-header">
        <h3>📰 Latest News: {ticker}</h3>
        <button
          onClick={() => setExpanded(!expanded)}
          className="expand-btn"
          aria-label={expanded ? 'Collapse news' : 'Expand news'}
        >
          {expanded ? '▼' : '▶'}
        </button>
      </div>

      {loading ? (
        <div className="news-loading">
          <span className="spinner-small"></span>
          <span>Loading news...</span>
        </div>
      ) : error ? (
        <div className="news-error">
          <span>⚠️ {error}</span>
          <button onClick={fetchNews} className="retry-btn">Retry</button>
        </div>
      ) : expanded && news.length > 0 ? (
        <div className="news-list">
          {news.map((article) => (
            <article key={article.id} className="news-item">
              <div className="news-item-header">
                <span
                  className="sentiment-badge"
                  style={{ color: getSentimentColor(article.sentiment) }}
                  title={`${article.sentiment} sentiment`}
                >
                  {getSentimentIcon(article.sentiment)}
                </span>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="news-title"
                >
                  {article.title}
                </a>
              </div>
              <div className="news-meta">
                <span className="news-source">{article.source}</span>
                <span className="news-divider">•</span>
                <span className="news-time">{formatTimeAgo(article.published_at)}</span>
              </div>
              {article.summary && (
                <p className="news-summary">{article.summary}</p>
              )}
            </article>
          ))}
        </div>
      ) : expanded ? (
        <div className="news-empty">
          <span className="empty-icon">📰</span>
          <p>No news available for {ticker}</p>
        </div>
      ) : (
        <div className="news-collapsed">
          <p>Click to view {news.length} recent article{news.length !== 1 ? 's' : ''}</p>
        </div>
      )}
    </div>
  )
}

NewsPanel.propTypes = {
  ticker: PropTypes.string,
  limit: PropTypes.number
}

export default NewsPanel
