import React from 'react'
import PropTypes from 'prop-types'
import './PriceChart.css'

/**
 * PriceChart Component
 * Displays a simple line chart for price history
 * Uses SVG for lightweight rendering without external dependencies
 */
function PriceChart({ data, width = 400, height = 200, color = '#667eea' }) {
  if (!data || data.length === 0) {
    return (
      <div className="price-chart-empty" style={{ width, height }}>
        <div className="empty-icon">📊</div>
        <p>No price data available</p>
      </div>
    )
  }

  // Find min and max prices for scaling
  const prices = data.map(d => d.price)
  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)
  const priceRange = maxPrice - minPrice || 1 // Avoid division by zero

  // Add padding
  const padding = { top: 20, right: 20, bottom: 40, left: 60 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom

  // Calculate points for the line
  const points = data.map((d, i) => {
    const x = padding.left + (i / (data.length - 1)) * chartWidth
    const y = padding.top + chartHeight - ((d.price - minPrice) / priceRange) * chartHeight
    return { x, y, ...d }
  })

  // Create path for line chart
  const linePath = points.map((p, i) => 
    `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`
  ).join(' ')

  // Create path for gradient fill area
  const areaPath = `${linePath} L ${points[points.length - 1].x} ${height - padding.bottom} L ${padding.left} ${height - padding.bottom} Z`

  // Format date for x-axis labels
  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    const month = date.toLocaleDateString('en-US', { month: 'short' })
    const day = date.getDate()
    return `${month} ${day}`
  }

  // Select 5 evenly spaced dates for x-axis
  const xAxisLabels = [0, Math.floor(data.length / 4), Math.floor(data.length / 2), Math.floor(3 * data.length / 4), data.length - 1]
    .filter((i, idx, arr) => arr.indexOf(i) === idx) // Remove duplicates
    .map(i => ({
      x: padding.left + (i / (data.length - 1)) * chartWidth,
      label: formatDate(data[i].date)
    }))

  // Y-axis labels (min, mid, max)
  const yAxisLabels = [
    { y: padding.top, label: `$${maxPrice.toFixed(2)}` },
    { y: padding.top + chartHeight / 2, label: `$${((minPrice + maxPrice) / 2).toFixed(2)}` },
    { y: padding.top + chartHeight, label: `$${minPrice.toFixed(2)}` }
  ]

  // Calculate price change
  const firstPrice = data[0].price
  const lastPrice = data[data.length - 1].price
  const priceChange = lastPrice - firstPrice
  const priceChangePercent = (priceChange / firstPrice) * 100
  const isPositive = priceChange >= 0

  return (
    <div className="price-chart-container">
      {/* Price Summary */}
      <div className="price-summary">
        <div className="current-price">
          <span className="label">Current Price</span>
          <span className="value">${lastPrice.toFixed(2)}</span>
        </div>
        <div className={`price-change ${isPositive ? 'positive' : 'negative'}`}>
          <span className="label">Change</span>
          <span className="value">
            {isPositive ? '+' : ''}{priceChange.toFixed(2)} ({isPositive ? '+' : ''}{priceChangePercent.toFixed(2)}%)
          </span>
        </div>
      </div>

      {/* SVG Chart */}
      <svg width={width} height={height} className="price-chart" role="img" aria-label="Price history chart">
        {/* Gradient for area fill */}
        <defs>
          <linearGradient id={`gradient-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0.05" />
          </linearGradient>
        </defs>

        {/* Grid lines */}
        {yAxisLabels.map((label, i) => (
          <line
            key={`grid-${i}`}
            x1={padding.left}
            y1={label.y}
            x2={width - padding.right}
            y2={label.y}
            stroke="#e0e0e0"
            strokeWidth="1"
            strokeDasharray="4 4"
            opacity="0.5"
          />
        ))}

        {/* Area fill */}
        <path
          d={areaPath}
          fill={`url(#gradient-${color})`}
          stroke="none"
        />

        {/* Line chart */}
        <path
          d={linePath}
          fill="none"
          stroke={color}
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {points.map((p, i) => (
          <circle
            key={`point-${i}`}
            cx={p.x}
            cy={p.y}
            r="4"
            fill={color}
            stroke="white"
            strokeWidth="2"
            className="chart-point"
          >
            <title>{`${formatDate(p.date)}: $${p.price.toFixed(2)}`}</title>
          </circle>
        ))}

        {/* Y-axis labels */}
        {yAxisLabels.map((label, i) => (
          <text
            key={`y-label-${i}`}
            x={padding.left - 10}
            y={label.y}
            textAnchor="end"
            alignmentBaseline="middle"
            className="axis-label"
          >
            {label.label}
          </text>
        ))}

        {/* X-axis labels */}
        {xAxisLabels.map((label, i) => (
          <text
            key={`x-label-${i}`}
            x={label.x}
            y={height - padding.bottom + 20}
            textAnchor="middle"
            className="axis-label"
          >
            {label.label}
          </text>
        ))}
      </svg>

      {/* Time period indicator */}
      <div className="chart-period">
        <span>{data.length} day{data.length > 1 ? 's' : ''} history</span>
      </div>
    </div>
  )
}

PriceChart.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    date: PropTypes.string.isRequired,
    price: PropTypes.number.isRequired
  })).isRequired,
  width: PropTypes.number,
  height: PropTypes.number,
  color: PropTypes.string
}

export default PriceChart
