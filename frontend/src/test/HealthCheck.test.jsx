import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { HealthCheck } from '../components/HealthCheck';

describe('HealthCheck Component', () => {
  it('renders health check status', () => {
    const mockHealth = {
      status: 'healthy',
      model_loaded: true,
      openai_configured: true,
    };

    render(<HealthCheck health={mockHealth} />);
    
    expect(screen.getByText(/healthy/i)).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<HealthCheck health={null} />);
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('displays error state when unhealthy', () => {
    const mockHealth = {
      status: 'unhealthy',
      model_loaded: false,
      openai_configured: false,
    };

    render(<HealthCheck health={mockHealth} />);
    
    expect(screen.getByText(/unhealthy/i)).toBeInTheDocument();
  });
});
