/*
 * Frontend component tests for new features
 *
 * Tests:
 * - BacktestDashboard component
 * - MarketContextModal component
 * - AssetContextButton component
 */

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import BacktestDashboard from "../src/components/BacktestDashboard";
import MarketContextModal from "../src/components/MarketContextModal";
import AssetContextButton from "../src/components/AssetContextButton";
import { apiClient } from "../src/api";

// Mock API client
vi.mock("../src/api", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe("BacktestDashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders backtest configuration panel", () => {
    render(<BacktestDashboard />);

    expect(screen.getByText(/Historical Backtest Comparison/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Start Date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/End Date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Initial Capital/i)).toBeInTheDocument();
  });

  it("displays ticker selection chips", () => {
    render(<BacktestDashboard />);

    expect(screen.getByText("AAPL")).toBeInTheDocument();
    expect(screen.getByText("MSFT")).toBeInTheDocument();
    expect(screen.getByText("GOOGL")).toBeInTheDocument();
  });

  it("toggles ticker selection on click", () => {
    render(<BacktestDashboard />);

    const aaplChip = screen.getByText("AAPL");

    // Initially selected
    expect(aaplChip.parentElement).toHaveClass("selected");

    // Click to deselect
    fireEvent.click(aaplChip);

    // Should be deselected
    expect(aaplChip.parentElement).not.toHaveClass("selected");
  });

  it("shows empty state when no backtest run", () => {
    render(<BacktestDashboard />);

    expect(screen.getByText(/No Backtest Results Yet/i)).toBeInTheDocument();
    expect(screen.getByText(/Configure the settings above/i)).toBeInTheDocument();
  });

  it("calls API when run backtest button clicked", async () => {
    apiClient.post.mockResolvedValueOnce({
      data: {
        backtest_period: {
          start_date: "2025-01-01",
          end_date: "2026-01-11",
          duration_days: 376,
        },
        strategies: {
          composite: {
            metrics: {
              total_return: 15.2,
              max_drawdown: 8.5,
              sharpe_ratio: 1.45,
              win_rate: 68.0,
              calmar_ratio: 1.79,
            },
            equity_curve: [],
          },
          ml_only: {
            metrics: {
              total_return: 12.1,
              max_drawdown: 10.2,
              sharpe_ratio: 1.15,
              win_rate: 62.0,
              calmar_ratio: 1.19,
            },
            equity_curve: [],
          },
          sp500: {
            metrics: {
              total_return: 10.5,
              max_drawdown: 7.8,
              sharpe_ratio: 1.2,
              win_rate: 100.0,
              calmar_ratio: 1.35,
            },
            equity_curve: [],
          },
        },
        comparison: {
          winner_by_return: {
            strategy: "Composite Score System",
            return: 15.2,
          },
          alpha_vs_benchmark: {
            alpha: 4.7,
            interpretation: "Outperformed",
          },
        },
      },
    });

    render(<BacktestDashboard />);

    const runButton = screen.getByText(/Run Backtest/i);
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith("/api/backtest/run", expect.any(Object));
    });
  });

  it("displays error message on API failure", async () => {
    apiClient.post.mockRejectedValueOnce(new Error("API Error"));

    render(<BacktestDashboard />);

    const runButton = screen.getByText(/Run Backtest/i);
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText(/Failed to run backtest/i)).toBeInTheDocument();
    });
  });
});

describe("MarketContextModal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("does not render when closed", () => {
    render(<MarketContextModal isOpen={false} onClose={() => {}} />);

    expect(screen.queryByText(/Market Context/i)).not.toBeInTheDocument();
  });

  it("renders when opened", () => {
    render(<MarketContextModal isOpen={true} onClose={() => {}} />);

    expect(screen.getByText(/Market Context/i)).toBeInTheDocument();
  });

  it("fetches market context on open", async () => {
    apiClient.post.mockResolvedValueOnce({
      data: {
        regime: {
          status: "Risk-On",
          vix: 18.5,
          sp500_trend: "uptrend",
        },
        context: "Market is showing positive momentum with low volatility.",
        top_stocks: [
          { ticker: "AAPL", composite_score: 78.5, signal: "BUY" },
          { ticker: "MSFT", composite_score: 75.2, signal: "BUY" },
        ],
      },
    });

    render(<MarketContextModal isOpen={true} onClose={() => {}} />);

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith("/api/context/market", expect.any(Object));
    });
  });

  it("displays market regime badge", async () => {
    apiClient.post.mockResolvedValueOnce({
      data: {
        regime: {
          status: "Risk-On",
          vix: 18.5,
          sp500_trend: "uptrend",
        },
        context: "Market analysis here",
      },
    });

    render(<MarketContextModal isOpen={true} onClose={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText("Risk-On")).toBeInTheDocument();
    });
  });

  it("displays disclaimer", async () => {
    apiClient.post.mockResolvedValueOnce({
      data: {
        context: "Market analysis",
      },
    });

    render(<MarketContextModal isOpen={true} onClose={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText(/Important Disclaimer/i)).toBeInTheDocument();
      expect(screen.getByText(/informational purposes only/i)).toBeInTheDocument();
    });
  });

  it("calls onClose when close button clicked", () => {
    const onClose = vi.fn();
    render(<MarketContextModal isOpen={true} onClose={onClose} />);

    const closeButton = screen.getByLabelText(/Close modal/i);
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalled();
  });
});

describe("AssetContextButton", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders insights button", () => {
    render(<AssetContextButton ticker="AAPL" companyName="Apple Inc." />);

    expect(screen.getByText(/Insights/i)).toBeInTheDocument();
  });

  it("fetches asset context on click", async () => {
    apiClient.get.mockResolvedValueOnce({
      data: {
        ticker: "AAPL",
        context: "Apple Inc. is showing strong technical indicators.",
        metrics: {
          composite_score: 78.5,
          signal: "BUY",
          price: 175.5,
        },
      },
    });

    render(<AssetContextButton ticker="AAPL" companyName="Apple Inc." />);

    const button = screen.getByText(/Insights/i);
    fireEvent.click(button);

    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalledWith("/api/context/asset/AAPL");
    });
  });

  it("displays asset context in popover", async () => {
    apiClient.get.mockResolvedValueOnce({
      data: {
        ticker: "AAPL",
        context: "Strong technical momentum detected.",
        metrics: {
          composite_score: 78.5,
          signal: "BUY",
          price: 175.5,
        },
      },
    });

    render(<AssetContextButton ticker="AAPL" companyName="Apple Inc." />);

    const button = screen.getByText(/Insights/i);
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText("AAPL")).toBeInTheDocument();
      expect(screen.getByText(/Strong technical momentum/i)).toBeInTheDocument();
    });
  });

  it("displays disclaimer in popover", async () => {
    apiClient.get.mockResolvedValueOnce({
      data: {
        ticker: "AAPL",
        context: "Analysis text",
      },
    });

    render(<AssetContextButton ticker="AAPL" companyName="Apple Inc." />);

    const button = screen.getByText(/Insights/i);
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Informational Only/i)).toBeInTheDocument();
    });
  });

  it("handles API error gracefully", async () => {
    apiClient.get.mockRejectedValueOnce(new Error("Network error"));

    render(<AssetContextButton ticker="AAPL" companyName="Apple Inc." />);

    const button = screen.getByText(/Insights/i);
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load asset context/i)).toBeInTheDocument();
    });
  });
});
