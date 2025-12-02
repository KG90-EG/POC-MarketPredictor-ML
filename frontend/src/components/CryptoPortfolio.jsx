import PropTypes from 'prop-types'
import { useState, useMemo } from 'react'
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
  onRefresh,
  onRowClick
}) {
  const [searchTerm, setSearchTerm] = useState('')
  
  // Filter crypto results based on search term
  const filteredResults = useMemo(() => {
    if (!searchTerm) return cryptoResults
    const term = searchTerm.toLowerCase()
    return cryptoResults.filter(crypto => 
      crypto.name.toLowerCase().includes(term) || 
      crypto.symbol.toLowerCase().includes(term)
    )
  }, [cryptoResults, searchTerm])
  
  const totalPages = Math.ceil(filteredResults.length / cryptoPerPage)
  const paginatedResults = filteredResults.slice((cryptoPage - 1) * cryptoPerPage, cryptoPage * cryptoPerPage)

  // Reset to page 1 when search term changes
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value)
    onPageChange(1)
  }

  return (
    <>
      <h2>🪙 Digital Assets & Cryptocurrency Rankings</h2>
      
      {/* Search Bar */}
      <div style={{marginBottom: '16px'}}>
        <input
          type="text"
          placeholder="🔍 Search by name or symbol (e.g., Bitcoin, BTC)..."
          value={searchTerm}
          onChange={handleSearchChange}
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
        {searchTerm && (
          <p style={{marginTop: '8px', fontSize: '0.85rem', color: '#666'}}>
            Found {filteredResults.length} result{filteredResults.length !== 1 ? 's' : ''} for "{searchTerm}"
          </p>
        )}
      </div>
      
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
        filteredResults.length === 0 ? (
          <div style={{textAlign: 'center', padding: '40px', color: '#666'}}>
            <p style={{fontSize: '1.2rem', marginBottom: '8px'}}>🔍</p>
            <p>No cryptocurrencies found matching "{searchTerm}"</p>
            <button 
              onClick={() => setSearchTerm('')}
              style={{
                marginTop: '12px',
                padding: '8px 16px',
                background: 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              Clear Search
            </button>
          </div>
        ) : (
        <div>
          <div className="table-wrapper">
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
                  <tr 
                    key={crypto.crypto_id} 
                    onClick={() => onRowClick(crypto)}
                    style={{cursor: 'pointer'}}
                    title="Click for detailed information"
                  >
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
          </div>
          
          {/* Pagination Controls */}
          {cryptoResults.length > cryptoPerPage && (
            <div className="pagination">
              <button 
                onClick={() => onPageChange(Math.max(1, cryptoPage - 1))} 
                disabled={cryptoPage === 1}
                aria-label="Go to previous page"
              >
                ← Previous
              </button>
              <div className="page-selector">
                <span className="page-info">Page</span>
                <select 
                  value={cryptoPage} 
                  onChange={(e) => onPageChange(Number(e.target.value))}
                  className="page-dropdown"
                  aria-label="Select page number"
                >
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(pageNum => (
                    <option key={pageNum} value={pageNum}>{pageNum}</option>
                  ))}
                </select>
                <span className="page-info">of {totalPages}</span>
              </div>
              <button 
                onClick={() => onPageChange(Math.min(totalPages, cryptoPage + 1))} 
                disabled={cryptoPage >= totalPages}
                aria-label="Go to next page"
              >
                Next →
              </button>
            </div>
          )}
        </div>
        )
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
  onRefresh: PropTypes.func.isRequired,
  onRowClick: PropTypes.func.isRequired
}

export default CryptoPortfolio
