import React from 'react'
import PropTypes from 'prop-types'

/**
 * Pagination component for table navigation
 */
export function Pagination({ 
  currentPage, 
  totalPages, 
  onPageChange, 
  itemsPerPage,
  totalItems 
}) {
  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1)
    }
  }

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1)
    }
  }

  const handlePageSelect = (e) => {
    const page = parseInt(e.target.value, 10)
    onPageChange(page)
  }

  // Calculate displayed item range
  const startItem = (currentPage - 1) * itemsPerPage + 1
  const endItem = Math.min(currentPage * itemsPerPage, totalItems)

  if (totalPages <= 1) {
    return null // Don't show pagination if only one page
  }

  return (
    <div className="pagination">
      <div className="pagination-info">
        Showing {startItem}-{endItem} of {totalItems} results
      </div>
      
      <div className="pagination-controls">
        <button
          onClick={handlePrevious}
          disabled={currentPage === 1}
          className="pagination-btn"
          aria-label="Previous page"
        >
          ← Previous
        </button>

        <div className="pagination-page-select">
          <label htmlFor="page-selector">Page</label>
          <select
            id="page-selector"
            value={currentPage}
            onChange={handlePageSelect}
            className="page-dropdown"
            aria-label="Select page"
          >
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
              <option key={page} value={page}>
                {page}
              </option>
            ))}
          </select>
          <span className="pagination-total">of {totalPages}</span>
        </div>

        <button
          onClick={handleNext}
          disabled={currentPage === totalPages}
          className="pagination-btn"
          aria-label="Next page"
        >
          Next →
        </button>
      </div>
    </div>
  )
}

Pagination.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  itemsPerPage: PropTypes.number.isRequired,
  totalItems: PropTypes.number.isRequired
}

export default Pagination
