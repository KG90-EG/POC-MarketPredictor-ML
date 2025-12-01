import PropTypes from 'prop-types'
import Tooltip from './Tooltip'

function CryptoPortfolio({
  cryptoResults,
  cryptoLoading,
  cryptoPage,
  cryptoPerPage,
  includeNFT,
  cryptoLimit,
  onPageChange,
  onNFTToggle,
  onLimitChange,
  onRefresh
}) {
  const totalPages = Math.ceil(cryptoResults.length / cryptoPerPage)
  const paginatedResults = cryptoResults.slice((cryptoPage - 1) * cryptoPerPage, cryptoPage * cryptoPerPage)

  return (
    <>
      <h2>🪙 Digital Assets & Cryptocurrency Rankings</h2>
      
      <div style={{marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap'}}>
        <label style={{display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer'}}>
          <input 
            type="checkbox" 
            checked={includeNFT}
            onChange={(e) => {
              onNFTToggle(e.target.checked)
              // Auto-refresh if crypto data is already loaded
              if (cryptoResults.length > 0) {
                onRefresh()
              }
            }}
            aria-label="Include NFT-related tokens in rankings"
            style={{width: '18px', height: '18px'}}
          />
          <span style={{fontSize: '0.95rem'}}>Include NFT tokens</span>
        </label>
        
        <label style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
          <span style={{fontSize: '0.95rem', fontWeight: '500'}}>Top:</span>
          <select 
            value={cryptoLimit}
            onChange={(e) => {
              onLimitChange(Number(e.target.value))
              // Auto-refresh if crypto data is already loaded
              if (cryptoResults.length > 0) {
                setTimeout(() => onRefresh(), 100)
              }
            }}
            aria-label="Select number of cryptocurrencies to display"
            style={{
              padding: '6px 12px',
              border: '2px solid #ddd',
              borderRadius: '6px',
              fontSize: '0.9rem',
              cursor: 'pointer'
            }}
          >
            <option value={20}>20 cryptos</option>
            <option value={50}>50 cryptos</option>
            <option value={100}>100 cryptos</option>
            <option value={200}>200 cryptos</option>
          </select>
        </label>
        
        <button 
          onClick={onRefresh}
          disabled={cryptoLoading}
          aria-label="Refresh cryptocurrency rankings from CoinGecko"
          style={{
            padding: '8px 16px',
            background: 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: cryptoLoading ? 'not-allowed' : 'pointer',
            fontWeight: '600',
            fontSize: '0.9rem'
          }}
        >
          {cryptoLoading ? '⟳ Refreshing...' : '🔄 Refresh Rankings'}
        </button>
      </div>
      
      {cryptoLoading ? (
        <div style={{textAlign: 'center', padding: '40px'}} role="status" aria-live="polite" aria-atomic="true">
          <span className="spinner"></span>
          <p>Loading digital assets rankings...</p>
        </div>
      ) : cryptoResults.length > 0 ? (
        <div>
          <div style={{marginBottom: '16px', padding: '12px', background: '#fef3c7', borderRadius: '8px', fontSize: '0.9rem'}}>
            ℹ️ <strong>Digital Assets powered by CoinGecko API.</strong> Momentum scores consider market cap rank, price trends (24h/7d/30d), and liquidity.
          </div>
          
          <table aria-label="Digital assets and cryptocurrency rankings table">
            <thead>
              <tr>
                <th scope="col">Rank</th>
                <th scope="col">Asset</th>
                <th scope="col">Symbol</th>
                <th scope="col">
                  <Tooltip 
                    content="Momentum score (0-100%). Higher scores indicate better recent performance, market cap rank, and liquidity. Similar to probability score for stocks." 
                    position="top"
                  >
                    Momentum Score ⓘ
                  </Tooltip>
                </th>
                <th scope="col">Price (USD)</th>
                <th scope="col">
                  <Tooltip 
                    content="24-hour price change percentage. Crypto markets are highly volatile - double-digit changes are common." 
                    position="top"
                  >
                    24h Change ⓘ
                  </Tooltip>
                </th>
                <th scope="col">7d Change</th>
                <th scope="col">Market Cap</th>
                <th scope="col">Volume/MCap</th>
              </tr>
            </thead>
            <tbody>
              {paginatedResults.map((crypto, idx) => {
                const actualRank = (cryptoPage - 1) * cryptoPerPage + idx + 1
                const changeClass = crypto.change_24h > 0 ? 'positive' : crypto.change_24h < 0 ? 'negative' : ''
                const change7dClass = crypto.change_7d > 0 ? 'positive' : crypto.change_7d < 0 ? 'negative' : ''
                
                return (
                  <tr key={crypto.crypto_id} style={{cursor: 'default'}}>
                    <td>
                      <span className={actualRank <= 3 ? 'rank-badge gold' : 'rank-badge'}>{actualRank}</span>
                    </td>
                    <td>
                      <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                        {crypto.image && (
                          <img src={crypto.image} alt={crypto.name} style={{width: '24px', height: '24px', borderRadius: '50%'}} />
                        )}
                        <span style={{fontWeight: '600'}}>{crypto.name}</span>
                      </div>
                    </td>
                    <td><span className="ticker-symbol">{crypto.symbol}</span></td>
                    <td>
                      <Tooltip 
                        content={`${(crypto.momentum_score * 100).toFixed(2)}% momentum. Rank #${crypto.market_cap_rank} by market cap. ${
                          crypto.momentum_score >= 0.65 
                            ? 'Strong bullish signal' 
                            : crypto.momentum_score >= 0.55 
                            ? 'Bullish momentum' 
                            : crypto.momentum_score >= 0.45 
                            ? 'Neutral' 
                            : 'Weak momentum'
                        }`}
                        position="top"
                      >
                        <span className={crypto.momentum_score > 0.6 ? 'high-prob' : ''}>
                          {(crypto.momentum_score * 100).toFixed(2)}%
                        </span>
                      </Tooltip>
                    </td>
                    <td>${crypto.price?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 6}) || 'N/A'}</td>
                    <td>
                      <Tooltip 
                        content={`${crypto.change_24h ? crypto.change_24h.toFixed(2) : 'N/A'}% in last 24 hours. ${
                          crypto.change_24h > 10 
                            ? '🚀 Major pump!' 
                            : crypto.change_24h > 5 
                            ? 'Strong gain' 
                            : crypto.change_24h > 0 
                            ? 'Slight increase' 
                            : crypto.change_24h < -10 
                            ? '⚠️ Heavy drop' 
                            : crypto.change_24h < -5 
                            ? 'Significant loss' 
                            : crypto.change_24h < 0 
                            ? 'Minor decline' 
                            : 'Stable'
                        }`}
                        position="top"
                      >
                        <span className={changeClass}>
                          {crypto.change_24h ? `${crypto.change_24h > 0 ? '+' : ''}${crypto.change_24h.toFixed(2)}%` : 'N/A'}
                        </span>
                      </Tooltip>
                    </td>
                    <td>
                      <span className={change7dClass}>
                        {crypto.change_7d ? `${crypto.change_7d > 0 ? '+' : ''}${crypto.change_7d.toFixed(2)}%` : 'N/A'}
                      </span>
                    </td>
                    <td>${crypto.market_cap ? (crypto.market_cap / 1e9).toFixed(2) + 'B' : 'N/A'}</td>
                    <td>
                      <Tooltip 
                        content={`${crypto.volume_to_mcap_ratio ? crypto.volume_to_mcap_ratio.toFixed(2) : 'N/A'}% - Trading volume as % of market cap. Higher = more liquid. 20%+ is excellent, 10-20% is good, <10% is lower liquidity.`}
                        position="top"
                      >
                        {crypto.volume_to_mcap_ratio ? `${crypto.volume_to_mcap_ratio.toFixed(2)}%` : 'N/A'}
                      </Tooltip>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
          
          {/* Pagination Controls */}
          {cryptoResults.length > cryptoPerPage && (
            <nav aria-label="Cryptocurrency results pagination" style={{
              marginTop: '20px',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '12px'
            }}>
              <button
                onClick={() => onPageChange(Math.max(1, cryptoPage - 1))}
                disabled={cryptoPage === 1}
                aria-label="Go to previous page"
                style={{
                  padding: '8px 16px',
                  background: cryptoPage === 1 ? '#e0e0e0' : 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)',
                  color: cryptoPage === 1 ? '#999' : 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: cryptoPage === 1 ? 'not-allowed' : 'pointer',
                  fontWeight: '600',
                  fontSize: '0.9rem'
                }}
              >
                ← Previous
              </button>
              
              <span style={{fontSize: '0.9rem', fontWeight: '500'}} aria-live="polite" aria-atomic="true">
                Page {cryptoPage} of {totalPages} 
                <span style={{color: '#666', marginLeft: '8px'}}>
                  ({(cryptoPage - 1) * cryptoPerPage + 1}-{Math.min(cryptoPage * cryptoPerPage, cryptoResults.length)} of {cryptoResults.length})
                </span>
              </span>
              
              <button
                onClick={() => onPageChange(Math.min(totalPages, cryptoPage + 1))}
                disabled={cryptoPage >= totalPages}
                aria-label="Go to next page"
                style={{
                  padding: '8px 16px',
                  background: cryptoPage >= totalPages ? '#e0e0e0' : 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)',
                  color: cryptoPage >= totalPages ? '#999' : 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: cryptoPage >= totalPages ? 'not-allowed' : 'pointer',
                  fontWeight: '600',
                  fontSize: '0.9rem'
                }}
              >
                Next →
              </button>
            </nav>
          )}
        </div>
      ) : (
        <p style={{color: '#666', fontSize: '0.9rem', margin: '0', textAlign: 'center', padding: '20px'}}>
          Click "Refresh Rankings" to load digital assets data
        </p>
      )}
    </>
  )
}

CryptoPortfolio.propTypes = {
  cryptoResults: PropTypes.arrayOf(PropTypes.shape({
    crypto_id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    symbol: PropTypes.string.isRequired,
    momentum_score: PropTypes.number.isRequired,
    price: PropTypes.number,
    change_24h: PropTypes.number,
    change_7d: PropTypes.number,
    market_cap: PropTypes.number,
    market_cap_rank: PropTypes.number,
    volume_to_mcap_ratio: PropTypes.number,
    image: PropTypes.string
  })).isRequired,
  cryptoLoading: PropTypes.bool.isRequired,
  cryptoPage: PropTypes.number.isRequired,
  cryptoPerPage: PropTypes.number.isRequired,
  includeNFT: PropTypes.bool.isRequired,
  cryptoLimit: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  onNFTToggle: PropTypes.func.isRequired,
  onLimitChange: PropTypes.func.isRequired,
  onRefresh: PropTypes.func.isRequired
}

export default CryptoPortfolio
