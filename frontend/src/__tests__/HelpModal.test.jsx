import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import HelpModal from '../components/HelpModal'

describe('HelpModal Component', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
  }

  it('renders when isOpen is true', () => {
    render(<HelpModal {...defaultProps} />)
    
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('Help & Guide')).toBeInTheDocument()
  })

  it('does not render when isOpen is false', () => {
    render(<HelpModal {...defaultProps} isOpen={false} />)
    
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', () => {
    render(<HelpModal {...defaultProps} />)
    
    const closeButton = screen.getByLabelText('Close help modal')
    fireEvent.click(closeButton)
    
    expect(defaultProps.onClose).toHaveBeenCalled()
  })

  it('calls onClose when overlay is clicked', () => {
    render(<HelpModal {...defaultProps} />)
    
    const overlay = screen.getByRole('dialog').parentElement
    fireEvent.click(overlay)
    
    expect(defaultProps.onClose).toHaveBeenCalled()
  })

  it('displays all help sections', () => {
    render(<HelpModal {...defaultProps} />)
    
    expect(screen.getByText('🚀 Getting Started')).toBeInTheDocument()
    expect(screen.getByText('📊 Understanding Rankings')).toBeInTheDocument()
    expect(screen.getByText('💹 Buy/Sell Signals')).toBeInTheDocument()
    expect(screen.getByText('🧭 Navigation')).toBeInTheDocument()
    expect(screen.getByText('🤖 AI Analysis')).toBeInTheDocument()
    expect(screen.getByText('🎨 Theme Toggle')).toBeInTheDocument()
  })

  it('has proper ARIA attributes', () => {
    render(<HelpModal {...defaultProps} />)
    
    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
    expect(dialog).toHaveAttribute('aria-labelledby', 'help-modal-title')
  })

  it('contains keyboard shortcut information', () => {
    render(<HelpModal {...defaultProps} />)
    
    expect(screen.getByText(/Keyboard shortcut/)).toBeInTheDocument()
  })
})
