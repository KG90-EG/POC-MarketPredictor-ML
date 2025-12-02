import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import MarketSelector from '../components/MarketSelector'
import { MARKET_VIEWS } from '../constants'

describe('MarketSelector Component', () => {
  const mockOnSelectionChange = vi.fn()

  const defaultProps = {
    selectedView: 'Global',
    onSelectionChange: mockOnSelectionChange,
    disabled: false
  }

  beforeEach(() => {
    mockOnSelectionChange.mockClear()
  })

  it('renders all market views from constants', () => {
    render(<MarketSelector {...defaultProps} />)
    
    // Check that all markets from MARKET_VIEWS are rendered
    MARKET_VIEWS.forEach(view => {
      expect(screen.getByText(view.label, { exact: false })).toBeInTheDocument()
    })
  })

  it('shows the currently selected market', () => {
    render(<MarketSelector {...defaultProps} />)
    
    const globalButton = screen.getByText('🌐 Global', { exact: false })
    expect(globalButton.closest('button')).toHaveClass('selected')
  })

  it('calls onSelectionChange when a different market is clicked', () => {
    render(<MarketSelector {...defaultProps} />)
    
    const switzerlandButton = screen.getByText('🇨🇭 Switzerland', { exact: false })
    fireEvent.click(switzerlandButton)
    
    expect(mockOnSelectionChange).toHaveBeenCalledWith('Switzerland')
  })

  it('allows only single selection', () => {
    const { rerender } = render(<MarketSelector {...defaultProps} />)
    
    // Click on Germany
    const germanyButton = screen.getByText('🇩🇪 Germany', { exact: false })
    fireEvent.click(germanyButton)
    
    expect(mockOnSelectionChange).toHaveBeenCalledWith('Germany')
    
    // Rerender with Germany selected
    rerender(<MarketSelector {...defaultProps} selectedView="Germany" />)
    
    // Now only Germany should be selected
    expect(germanyButton.closest('button')).toHaveClass('selected')
    
    const globalButton = screen.getByText('🌐 Global', { exact: false })
    expect(globalButton.closest('button')).not.toHaveClass('selected')
  })

  it('does not call onSelectionChange when disabled', () => {
    render(<MarketSelector {...defaultProps} disabled={true} />)
    
    const usButton = screen.getByText('🇺🇸 United States', { exact: false })
    fireEvent.click(usButton)
    
    expect(mockOnSelectionChange).not.toHaveBeenCalled()
  })

  it('shows checkmark only for selected market', () => {
    render(<MarketSelector {...defaultProps} />)
    
    // Global should have checkmark
    const globalButton = screen.getByText('🌐 Global', { exact: false }).closest('button')
    expect(globalButton.textContent).toContain('✓')
    
    // Other markets should not have checkmark
    const japanButton = screen.getByText('🇯🇵 Japan', { exact: false }).closest('button')
    expect(japanButton.textContent).not.toContain('✓')
  })

  it('sets correct aria-pressed attribute', () => {
    render(<MarketSelector {...defaultProps} selectedView="France" />)
    
    const franceButton = screen.getByText('🇫🇷 France', { exact: false }).closest('button')
    expect(franceButton).toHaveAttribute('aria-pressed', 'true')
    
    const canadaButton = screen.getByText('🇨🇦 Canada', { exact: false }).closest('button')
    expect(canadaButton).toHaveAttribute('aria-pressed', 'false')
  })

  it('uses dynamic market views from constants', () => {
    render(<MarketSelector {...defaultProps} />)
    
    // Should render exactly the number of markets from MARKET_VIEWS
    const buttons = screen.getAllByRole('button')
    expect(buttons.length).toBe(MARKET_VIEWS.length)
  })
})
