import React from 'react'
import PropTypes from 'prop-types'

function formatNumber(num) {
  if (!num) return 'N/A'
  if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`
  if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`
  if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`
  return `$${num.toLocaleString()}`
}

function CompanyDetailSidebar({ company, onClose }) {
  if (!company) return null

  return (
    <>
      <div className="sidebar-overlay" onClick={onClose} aria-hidden="true"></div>
      <aside className="sidebar" role="complementary" aria-labelledby="sidebar-title">
        <button className="sidebar-close" onClick={onClose} aria-label="Close company details">
          ×
        </button>

        {company.loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <span className="spinner"></span>
            <p>Loading company details...</p>
          </div>
        ) : company.error ? (
          <div style={{ padding: '20px', color: '#e74c3c' }} role="alert">
            <p>{company.error}</p>
          </div>
        ) : (
          <div className="sidebar-content">
            <h2 id="sidebar-title">{company.ticker}</h2>
            <p className="company-name">{company.name || 'N/A'}</p>
            {company.country && <p className="company-country">🌍 {company.country}</p>}

            <div className="detail-section">
              <h3>🎯 Trading Signal</h3>
              <div
                className={`signal-badge signal-${company.signal?.toLowerCase().replace(/ /g, '-')}`}
              >
                {company.signal}
              </div>
              <p className="probability">
                ML Probability:{' '}
                {company.prob ? `${(company.prob * 100).toFixed(2)}%` : 'N/A'}
              </p>
            </div>

            <div className="detail-section">
              <h3>💰 Price Information</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">Current Price</span>
                  <span className="detail-value">
                    {company.price ? `$${company.price.toFixed(2)}` : 'N/A'}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Change %</span>
                  <span
                    className={`detail-value ${company.change > 0 ? 'positive' : company.change < 0 ? 'negative' : ''}`}
                  >
                    {company.change
                      ? `${company.change > 0 ? '+' : ''}${company.change.toFixed(2)}%`
                      : 'N/A'}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">52-Week High</span>
                  <span className="detail-value">
                    {company.fifty_two_week_high
                      ? `$${company.fifty_two_week_high.toFixed(2)}`
                      : 'N/A'}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">52-Week Low</span>
                  <span className="detail-value">
                    {company.fifty_two_week_low
                      ? `$${company.fifty_two_week_low.toFixed(2)}`
                      : 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h3>📊 Market Data</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">Market Cap</span>
                  <span className="detail-value">{formatNumber(company.market_cap)}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Volume</span>
                  <span className="detail-value">
                    {company.volume ? company.volume.toLocaleString() : 'N/A'}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">P/E Ratio</span>
                  <span className="detail-value">
                    {company.pe_ratio ? company.pe_ratio.toFixed(2) : 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h3>💡 Recommendation</h3>
              <p className="recommendation-text">
                {company.signal === 'STRONG BUY' &&
                  'This stock shows strong potential for outperformance based on ML analysis. Consider adding to your portfolio.'}
                {company.signal === 'BUY' &&
                  'Positive signals indicate good buying opportunity. Review fundamentals before investing.'}
                {company.signal === 'HOLD' &&
                  'Neutral signals suggest maintaining current position. Monitor for changes.'}
                {company.signal === 'CONSIDER SELLING' &&
                  'Weak signals detected. Consider reducing position or exiting.'}
                {company.signal === 'SELL' &&
                  'ML model suggests poor performance outlook. Consider exiting position.'}
              </p>
            </div>
          </div>
        )}
      </aside>
    </>
  )
}

CompanyDetailSidebar.propTypes = {
  company: PropTypes.shape({
    ticker: PropTypes.string,
    name: PropTypes.string,
    country: PropTypes.string,
    signal: PropTypes.string,
    prob: PropTypes.number,
    price: PropTypes.number,
    change: PropTypes.number,
    fifty_two_week_high: PropTypes.number,
    fifty_two_week_low: PropTypes.number,
    market_cap: PropTypes.number,
    volume: PropTypes.number,
    pe_ratio: PropTypes.number,
    loading: PropTypes.bool,
    error: PropTypes.string,
  }),
  onClose: PropTypes.func.isRequired,
}

export default CompanyDetailSidebar
