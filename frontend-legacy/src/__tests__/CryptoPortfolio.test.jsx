import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import CryptoPortfolio from "../components/CryptoPortfolio";

describe("CryptoPortfolio Component", () => {
  const mockCryptoResults = [
    {
      crypto_id: "bitcoin",
      name: "Bitcoin",
      symbol: "BTC",
      momentum_score: 0.85,
      price: 42000,
      change_24h: 5.2,
      change_7d: 8.5,
      market_cap: 820000000000,
      market_cap_rank: 1,
      volume_to_mcap_ratio: 15.5,
      image: "https://example.com/btc.png",
    },
    {
      crypto_id: "ethereum",
      name: "Ethereum",
      symbol: "ETH",
      momentum_score: 0.72,
      price: 2200,
      change_24h: -2.1,
      change_7d: 3.2,
      market_cap: 265000000000,
      market_cap_rank: 2,
      volume_to_mcap_ratio: 12.3,
      image: "https://example.com/eth.png",
    },
  ];

  const defaultProps = {
    cryptoResults: mockCryptoResults,
    cryptoLoading: false,
    cryptoPage: 1,
    cryptoPerPage: 20,
    includeNFT: false,
    cryptoLimit: 50,
    onPageChange: vi.fn(),
    onNFTToggle: vi.fn(),
    onLimitChange: vi.fn(),
    onRefresh: vi.fn(),
  };

  it("renders crypto portfolio title", () => {
    render(<CryptoPortfolio {...defaultProps} />);

    expect(screen.getByText(/Digital Assets & Cryptocurrency Rankings/)).toBeInTheDocument();
  });

  it("displays crypto data correctly", () => {
    render(<CryptoPortfolio {...defaultProps} />);

    expect(screen.getByText("Bitcoin")).toBeInTheDocument();
    expect(screen.getByText("BTC")).toBeInTheDocument();
    expect(screen.getByText("85.00%")).toBeInTheDocument();
  });

  it("shows loading state", () => {
    const loadingProps = { ...defaultProps, cryptoLoading: true };
    render(<CryptoPortfolio {...loadingProps} />);

    expect(screen.getByText(/Loading digital assets rankings/)).toBeInTheDocument();
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("renders NFT toggle checkbox", () => {
    render(<CryptoPortfolio {...defaultProps} />);

    const checkbox = screen.getByLabelText(/Include NFT-related tokens/);
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).not.toBeChecked();
  });

  it("calls onNFTToggle when checkbox is clicked", () => {
    render(<CryptoPortfolio {...defaultProps} />);

    const checkbox = screen.getByLabelText(/Include NFT-related tokens/);
    fireEvent.click(checkbox);

    expect(defaultProps.onNFTToggle).toHaveBeenCalledWith(true);
  });

  it("renders limit selector", () => {
    render(<CryptoPortfolio {...defaultProps} />);

    const selector = screen.getByLabelText(/Select number of cryptocurrencies/);
    expect(selector).toBeInTheDocument();
    expect(selector.value).toBe("50");
  });

  it("calls onLimitChange when selector changes", () => {
    render(<CryptoPortfolio {...defaultProps} />);

    const selector = screen.getByLabelText(/Select number of cryptocurrencies/);
    fireEvent.change(selector, { target: { value: "100" } });

    expect(defaultProps.onLimitChange).toHaveBeenCalledWith(100);
  });

  it("calls onRefresh when refresh button is clicked", () => {
    render(<CryptoPortfolio {...defaultProps} />);

    const refreshButton = screen.getByLabelText(/Refresh cryptocurrency rankings/);
    fireEvent.click(refreshButton);

    expect(defaultProps.onRefresh).toHaveBeenCalled();
  });

  it("disables refresh button when loading", () => {
    const loadingProps = { ...defaultProps, cryptoLoading: true };
    render(<CryptoPortfolio {...loadingProps} />);

    const refreshButton = screen.getByLabelText(/Refresh cryptocurrency rankings/);
    expect(refreshButton).toBeDisabled();
  });

  it("displays positive and negative changes correctly", () => {
    render(<CryptoPortfolio {...defaultProps} />);

    expect(screen.getByText("+5.20%")).toHaveClass("positive");
    expect(screen.getByText("-2.10%")).toHaveClass("negative");
  });

  it("formats market cap as billions", () => {
    render(<CryptoPortfolio {...defaultProps} />);

    expect(screen.getByText("$820.00B")).toBeInTheDocument();
    expect(screen.getByText("$265.00B")).toBeInTheDocument();
  });

  it("renders pagination when needed", () => {
    const propsWithPagination = {
      ...defaultProps,
      cryptoResults: Array(50)
        .fill(null)
        .map((_, i) => ({
          ...mockCryptoResults[0],
          crypto_id: `crypto${i}`,
          name: `Crypto ${i}`,
        })),
      cryptoPerPage: 20,
    };

    render(<CryptoPortfolio {...propsWithPagination} />);

    expect(screen.getByLabelText(/Go to previous page/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Go to next page/)).toBeInTheDocument();
  });

  it("shows empty state when no results", () => {
    const emptyProps = { ...defaultProps, cryptoResults: [] };
    render(<CryptoPortfolio {...emptyProps} />);

    expect(
      screen.getByText(/Click "Refresh Rankings" to load digital assets data/)
    ).toBeInTheDocument();
  });

  it("displays crypto images", () => {
    render(<CryptoPortfolio {...defaultProps} />);

    const btcImage = screen.getByAltText("Bitcoin");
    expect(btcImage).toHaveAttribute("src", "https://example.com/btc.png");
  });

  it("shows CoinGecko attribution", () => {
    render(<CryptoPortfolio {...defaultProps} />);

    expect(screen.getByText(/Digital Assets powered by CoinGecko API/)).toBeInTheDocument();
  });
});
