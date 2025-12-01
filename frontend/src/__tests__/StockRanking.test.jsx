import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import StockRanking from '../components/StockRanking'

describe('StockRanking Component', () => {
  const mockResults = [
    { ticker: 'AAPL', prob: 0.75 },
    { ticker: 'GOOGL', prob: 0.68 },
    { ticker: 'MSFT', prob: 0.62 },
  ]

  const mockTickerDetails = {
    AAPL: {
      name: 'Apple Inc.',
      country: 'US',
      price: 180.5,
      change: 2.5,
      volume: 50000000,
      market_cap: 2800000000000,
    },
    GOOGL: {
      name: 'Alphabet Inc.',
      country: 'US',
      price: 140.2,
      change: -1.2,
      volume: 25000000,
      market_cap: 1750000000000,
    },
    MSFT: {
      name: 'Microsoft Corporation',
      country: 'US',
      price: 380.0,
      change: 0.5,
      volume: 30000000,
      market_cap: 2820000000000,
    },
  }

  const defaultProps = {
    results: mockResults,
    tickerDetails: mockTickerDetails,
    currentPage: 1,
    itemsPerPage: 10,
    onPageChange: vi.fn(),
    onRowClick: vi.fn(),
  }

  it('renders stock ranking table', () => {
    render(<StockRanking {...defaultProps} />)
    
    expect(screen.getByText('Ranked Stocks')).toBeInTheDocument()
    expect(screen.getByLabelText('Ranked stocks results table')).toBeInTheDocument()
  })

  it('displays stock data correctly', () => {
    render(<StockRanking {...defaultProps} />)
    
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('Apple Inc.')).toBeInTheDocument()
    expect(screen.getByText('75.00%')).toBeInTheDocument()
    expect(screen.getByText('$180.50')).toBeInTheDocument()
  })

  it('shows buy/sell signals based on probability', () => {
    render(<StockRanking {...defaultProps} />)
    
    const buySignals = screen.getAllByText(/🟢 BUY/)
    expect(buySignals.length).toBeGreaterThan(0)
  })

  it('displays rank badges correctly', () => {
    render(<StockRanking {...defaultProps} />)
    
    expect(screen.getByText('1')).toHaveClass('gold')
    expect(screen.getByText('2')).toHaveClass('silver')
    expect(screen.getByText('3')).toHaveClass('bronze')
  })

  it('calls onRowClick when row is clicked', () => {
    render(<StockRanking {...defaultProps} />)
    
    const row = screen.getByText('AAPL').closest('tr')
    fireEvent.click(row)
    
    expect(defaultProps.onRowClick).toHaveBeenCalledWith('AAPL')
  })

  it('renders pagination controls when needed', () => {
    const propsWithPagination = {
      ...defaultProps,
      results: Array(25).fill(null).map((_, i) => ({ ticker: `STOCK${i}`, prob: 0.65 })),
      itemsPerPage: 10,
    }
    
    render(<StockRanking {...propsWithPagination} />)
    
    expect(screen.getByText('← Previous')).toBeInTheDocument()
    expect(screen.getByText('Next →')).toBeInTheDocument()
  })

  it('handles page change', () => {
    const propsWithPagination = {
      ...defaultProps,
      results: Array(25).fill(null).map((_, i) => ({ ticker: `STOCK${i}`, prob: 0.65 })),
      itemsPerPage: 10,
      currentPage: 1,
    }
    
    render(<StockRanking {...propsWithPagination} />)
    
    const nextButton = screen.getByText('Next →')
    fireEvent.click(nextButton)
    
    expect(defaultProps.onPageChange).toHaveBeenCalledWith(2)
  })

  it('formats market cap correctly', () => {
    render(<StockRanking {...defaultProps} />)
    
    expect(screen.getByText('$2.80T')).toBeInTheDocument()
    expect(screen.getByText('$1.75T')).toBeInTheDocument()
  })

  it('shows positive/negative change styling', () => {
    render(<StockRanking {...defaultProps} />)
    
    const positiveChange = screen.getByText('+2.50%')
    expect(positiveChange).toHaveClass('positive')
    
    const negativeChange = screen.getByText('-1.20%')
    expect(negativeChange).toHaveClass('negative')
  })
})
