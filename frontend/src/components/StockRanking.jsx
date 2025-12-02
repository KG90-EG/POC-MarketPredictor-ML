import PropTypes from 'prop-types'
import Tooltip from './Tooltip'

function StockRanking({
  results,
  tickerDetails,
  currentPage,
  itemsPerPage,
  onPageChange,
  onRowClick
}) {
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

  const totalPages = Math.ceil(results.length / itemsPerPage)
  const paginatedResults = results.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)

  return (
    <>
      {/* Ranked Stocks Table */}
      <h2>Ranked Stocks</h2>
      <div className="table-wrapper">
        <table aria-label="Ranked stocks results table">
          <thead>
            <tr>
              <th scope="col">Rank</th>
              <th scope="col">Stock</th>
              <th scope="col">Name</th>
              <th scope="col">Country</th>
              <th scope="col">
                <Tooltip
                  content="AI confidence score (0-100%). Higher scores indicate stronger buy signals based on technical indicators, price trends, and market data. 65%+ is strong buy, 55-65% is buy, 45-55% is hold, 35-45% consider selling, below 35% is sell."
                  position="top"
                >
                  Probability ⓘ
                </Tooltip>
              </th>
              <th scope="col">Price</th>
            <th scope="col">
              <Tooltip
                content="Daily price change percentage. Positive (+) values indicate the stock is up today, negative (-) values mean it's down. Strong moves are typically ±3% or more for established stocks."
                position="top"
              >
                Change % ⓘ
              </Tooltip>
            </th>
            <th scope="col">Volume</th>
            <th scope="col">Market Cap</th>
          </tr>
        </thead>
        <tbody>
          {paginatedResults.map((r) => {
            const rank = results.indexOf(r) + 1
            const detail = tickerDetails[r.ticker] || {}
            const changeClass = detail.change > 0 ? 'positive' : detail.change < 0 ? 'negative' : ''

            return (
              <tr
                key={r.ticker}
                onClick={() => onRowClick(r.ticker)}
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
                  <Tooltip
                    content={`${(r.prob * 100).toFixed(2)}% confidence. ${
                      r.prob >= 0.65
                        ? 'Strong buy signal - High confidence for upward movement'
                        : r.prob >= 0.55
                        ? 'Buy signal - Good potential for growth'
                        : r.prob >= 0.45
                        ? 'Hold - Neutral outlook'
                        : r.prob >= 0.35
                        ? 'Consider selling - Weak performance expected'
                        : 'Sell signal - Strong downward indicator'
                    }`}
                    position="top"
                  >
                    <span className={r.prob > 0.6 ? 'high-prob' : ''}>
                      {(r.prob * 100).toFixed(2)}%
                    </span>
                  </Tooltip>
                </td>
                <td>{detail.price ? `$${detail.price.toFixed(2)}` : 'N/A'}</td>
                <td>
                  <Tooltip
                    content={`${
                      detail.change
                        ? (detail.change > 0 ? `+${detail.change.toFixed(2)}%` : `${detail.change.toFixed(2)}%`)
                        : 'N/A'
                    } daily change. ${
                      detail.change > 3
                        ? '🚀 Strong upward move!'
                        : detail.change > 0
                        ? '✅ Positive momentum'
                        : detail.change < -3
                        ? '⚠️ Significant drop'
                        : detail.change < 0
                        ? '⬇️ Slight decline'
                        : 'No change'
                    }`}
                    position="top"
                  >
                    <span className={changeClass}>
                      {detail.change ? `${detail.change > 0 ? '+' : ''}${detail.change.toFixed(2)}%` : 'N/A'}
                    </span>
                  </Tooltip>
                </td>
                <td>{detail.volume ? detail.volume.toLocaleString() : 'N/A'}</td>
                <td>{formatNumber(detail.market_cap)}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
      </div>

      {/* Pagination Controls */}
      {results.length > itemsPerPage && (
        <div className="pagination">
          <button
            onClick={() => onPageChange(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
          >
            ← Previous
          </button>
          <div className="page-selector">
            <span className="page-info">Page</span>
            <select
              value={currentPage}
              onChange={(e) => onPageChange(Number(e.target.value))}
              className="page-dropdown"
            >
              {Array.from({ length: totalPages }, (_, i) => i + 1).map(pageNum => (
                <option key={pageNum} value={pageNum}>{pageNum}</option>
              ))}
            </select>
            <span className="page-info">of {totalPages}</span>
          </div>
          <button
            onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage >= totalPages}
          >
            Next →
          </button>
        </div>
      )}
    </>
  )
}

StockRanking.propTypes = {
  results: PropTypes.arrayOf(PropTypes.shape({
    ticker: PropTypes.string.isRequired,
    prob: PropTypes.number.isRequired
  })).isRequired,
  tickerDetails: PropTypes.objectOf(PropTypes.shape({
    name: PropTypes.string,
    country: PropTypes.string,
    price: PropTypes.number,
    change: PropTypes.number,
    volume: PropTypes.number,
    market_cap: PropTypes.number
  })).isRequired,
  currentPage: PropTypes.number.isRequired,
  itemsPerPage: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  onRowClick: PropTypes.func.isRequired
}

export default StockRanking
