import React from 'react'
import PropTypes from 'prop-types'

/**
 * Reusable loading spinner component
 */
export function LoadingSpinner({ size = 'medium', message = 'Loading...' }) {
  const sizeClasses = {
    small: 'spinner-small',
    medium: 'spinner-medium',
    large: 'spinner-large'
  }
  
  return (
    <div className="loading-container">
      <div className={`spinner ${sizeClasses[size]}`}></div>
      {message && <p className="loading-message">{message}</p>}
    </div>
  )
}

LoadingSpinner.propTypes = {
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  message: PropTypes.string
}

/**
 * Progress bar for batch operations
 */
export function ProgressBar({ current, total, label }) {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0
  
  return (
    <div className="progress-container">
      {label && <div className="progress-label">{label}</div>}
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={current}
          aria-valuemin={0}
          aria-valuemax={total}
        >
          {percentage}%
        </div>
      </div>
      <div className="progress-text">
        {current} / {total} items
      </div>
    </div>
  )
}

ProgressBar.propTypes = {
  current: PropTypes.number.isRequired,
  total: PropTypes.number.isRequired,
  label: PropTypes.string
}

/**
 * Skeleton loader for tables
 */
export function SkeletonRow({ columns = 8 }) {
  return (
    <tr className="skeleton-row">
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i}>
          <div className="skeleton-box"></div>
        </td>
      ))}
    </tr>
  )
}

SkeletonRow.propTypes = {
  columns: PropTypes.number
}

/**
 * Empty state placeholder
 */
export function EmptyState({ 
  icon = '📊', 
  title = 'No data available', 
  message = 'Try adjusting your filters or refresh the page',
  action
}) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">{icon}</div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-message">{message}</p>
      {action && (
        <button onClick={action.onClick} className="btn-primary">
          {action.label}
        </button>
      )}
    </div>
  )
}

EmptyState.propTypes = {
  icon: PropTypes.string,
  title: PropTypes.string,
  message: PropTypes.string,
  action: PropTypes.shape({
    label: PropTypes.string.isRequired,
    onClick: PropTypes.func.isRequired
  })
}

export default {
  LoadingSpinner,
  ProgressBar,
  SkeletonRow,
  EmptyState
}
