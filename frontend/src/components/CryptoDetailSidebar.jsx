import React from 'react'
import PropTypes from 'prop-types'

function formatNumber(num) {
  if (!num) return 'N/A'
  if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`
  if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`
  if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`
  if (num >= 1e3) return `$${(num / 1e3).toFixed(2)}K`
  return `$${num.toLocaleString()}`
}

function formatPrice(price) {
  if (!price) return 'N/A'
  if (price < 0.01) return `$${price.toFixed(6)}`
  if (price < 1) return `$${price.toFixed(4)}`
  if (price < 100) return `$${price.toFixed(2)}`
  return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function getMomentumSignal(score) {
  if (score >= 80) return 'VERY BULLISH'
  if (score >= 65) return 'BULLISH'
  if (score >= 50) return 'NEUTRAL'
  if (score >= 35) return 'BEARISH'
  return 'VERY BEARISH'
}

function getMomentumRecommendation(score) {
  if (score >= 80) {
    return 'Exceptional momentum and strong market position. This asset is showing very strong performance across multiple metrics.'
  }
  if (score >= 65) {
    return 'Strong positive momentum with good market cap rank and price trends. Consider this asset for potential gains.'
  }
  if (score >= 50) {
    return 'Moderate momentum signals. Asset is stable but not showing significant movement. Good for holding.'
  }
  if (score >= 35) {
    return 'Weak momentum detected. Price trends and market position are declining. Exercise caution.'
  }
  return 'Very weak momentum with poor recent performance. High volatility and risk. Consider avoiding or exiting position.'
}

function CryptoDetailSidebar({ crypto, onClose }) {
  if (!crypto) return null

  const momentumSignal = getMomentumSignal(crypto.momentum_score)
  const recommendation = getMomentumRecommendation(crypto.momentum_score)

  return (
    <>
      <div className="sidebar-overlay" onClick={onClose} aria-hidden="true"></div>
      <aside className="sidebar" role="complementary" aria-labelledby="sidebar-title">
        <button className="sidebar-close" onClick={onClose} aria-label="Close crypto details">
          ×
        </button>

        {crypto.loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <span className="spinner"></span>
            <p>Loading crypto details...</p>
          </div>
        ) : crypto.error ? (
          <div style={{ padding: '20px', color: '#e74c3c' }} role="alert">
            <p>{crypto.error}</p>
          </div>
        ) : (
          <div className="sidebar-content">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              {crypto.image && (
                <img 
                  src={crypto.image} 
                  alt={crypto.name}
                  style={{ width: '48px', height: '48px', borderRadius: '50%' }}
                />
              )}
              <div>
                <h2 id="sidebar-title" style={{ margin: 0 }}>{crypto.symbol?.toUpperCase()}</h2>
                <p className="company-name" style={{ margin: 0 }}>{crypto.name || 'N/A'}</p>
              </div>
            </div>

            <div className="detail-section">
              <h3>🎯 Momentum Signal</h3>
              <div
                className={`signal-badge signal-${momentumSignal.toLowerCase().replace(/ /g, '-')}`}
              >
                {momentumSignal}
              </div>
              <p className="probability">
                Momentum Score: {crypto.momentum_score ? `${crypto.momentum_score.toFixed(2)}%` : 'N/A'}
              </p>
            </div>

            <div className="detail-section">
              <h3>💰 Price Information</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">Current Price</span>
                  <span className="detail-value">
                    {formatPrice(crypto.price)}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">24h Change</span>
                  <span
                    className={`detail-value ${crypto.change_24h > 0 ? 'positive' : crypto.change_24h < 0 ? 'negative' : ''}`}
                  >
                    {crypto.change_24h != null
                      ? `${crypto.change_24h > 0 ? '+' : ''}${crypto.change_24h.toFixed(2)}%`
                      : 'N/A'}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">7d Change</span>
                  <span
                    className={`detail-value ${crypto.change_7d > 0 ? 'positive' : crypto.change_7d < 0 ? 'negative' : ''}`}
                  >
                    {crypto.change_7d != null
                      ? `${crypto.change_7d > 0 ? '+' : ''}${crypto.change_7d.toFixed(2)}%`
                      : 'N/A'}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">30d Change</span>
                  <span
                    className={`detail-value ${crypto.change_30d > 0 ? 'positive' : crypto.change_30d < 0 ? 'negative' : ''}`}
                  >
                    {crypto.change_30d != null
                      ? `${crypto.change_30d > 0 ? '+' : ''}${crypto.change_30d.toFixed(2)}%`
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
                  <span className="detail-value">{formatNumber(crypto.market_cap)}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Market Cap Rank</span>
                  <span className="detail-value">
                    {crypto.market_cap_rank ? `#${crypto.market_cap_rank}` : 'N/A'}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">24h Volume</span>
                  <span className="detail-value">{formatNumber(crypto.volume_24h)}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Volume/MCap Ratio</span>
                  <span className="detail-value">
                    {crypto.volume_to_mcap_ratio != null 
                      ? crypto.volume_to_mcap_ratio.toFixed(4) 
                      : 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h3>💡 Analysis</h3>
              <p className="recommendation-text">
                {recommendation}
              </p>
              {crypto.ath_change_percentage != null && (
                <p style={{ marginTop: '12px', fontSize: '0.9rem', color: '#666' }}>
                  <strong>From ATH:</strong> {crypto.ath_change_percentage.toFixed(2)}%
                </p>
              )}
            </div>
          </div>
        )}
      </aside>
    </>
  )
}

CryptoDetailSidebar.propTypes = {
  crypto: PropTypes.shape({
    crypto_id: PropTypes.string,
    name: PropTypes.string,
    symbol: PropTypes.string,
    image: PropTypes.string,
    momentum_score: PropTypes.number,
    price: PropTypes.number,
    change_24h: PropTypes.number,
    change_7d: PropTypes.number,
    change_30d: PropTypes.number,
    market_cap: PropTypes.number,
    market_cap_rank: PropTypes.number,
    volume_24h: PropTypes.number,
    volume_to_mcap_ratio: PropTypes.number,
    ath_change_percentage: PropTypes.number,
    loading: PropTypes.bool,
    error: PropTypes.string,
  }),
  onClose: PropTypes.func.isRequired,
}

export default CryptoDetailSidebar
