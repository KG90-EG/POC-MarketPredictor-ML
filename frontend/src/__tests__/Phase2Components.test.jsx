import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { Tabs, TabPanel } from "../components/shared/Tabs";
import AssetCard from "../components/assets/AssetCard";
import TopAssetsPanel from "../components/assets/TopAssetsPanel";

// Mock apiClient
vi.mock("../api", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

import { apiClient } from "../api";

describe("Phase 2 Components", () => {
  describe("Tabs Component", () => {
    const defaultTabs = [
      { id: "tab1", label: "Tab 1" },
      { id: "tab2", label: "Tab 2" },
      { id: "tab3", label: "Tab 3" },
    ];

    it("renders all tabs", () => {
      render(<Tabs tabs={defaultTabs} activeTab="tab1" />);

      expect(screen.getByText("Tab 1")).toBeInTheDocument();
      expect(screen.getByText("Tab 2")).toBeInTheDocument();
      expect(screen.getByText("Tab 3")).toBeInTheDocument();
    });

    it("marks active tab correctly", () => {
      render(<Tabs tabs={defaultTabs} activeTab="tab2" />);

      const tab2 = screen.getByRole("tab", { name: "Tab 2" });
      expect(tab2).toHaveAttribute("aria-selected", "true");
    });

    it("calls onTabChange when clicking a tab", () => {
      const onChange = vi.fn();
      render(<Tabs tabs={defaultTabs} activeTab="tab1" onTabChange={onChange} />);

      fireEvent.click(screen.getByText("Tab 2"));
      expect(onChange).toHaveBeenCalledWith("tab2");
    });

    it("renders tab with icon", () => {
      const tabsWithIcons = [{ id: "shares", label: "Shares", icon: "📈" }];
      render(<Tabs tabs={tabsWithIcons} activeTab="shares" />);

      expect(screen.getByText("📈")).toBeInTheDocument();
    });

    it("renders tab with count", () => {
      const tabsWithCount = [{ id: "shares", label: "Shares", count: 50 }];
      render(<Tabs tabs={tabsWithCount} activeTab="shares" />);

      expect(screen.getByText("50")).toBeInTheDocument();
    });

    it("handles keyboard navigation with arrow keys", () => {
      const onChange = vi.fn();
      render(<Tabs tabs={defaultTabs} activeTab="tab1" onTabChange={onChange} />);

      const tab1 = screen.getByRole("tab", { name: "Tab 1" });
      tab1.focus();

      // Arrow right
      fireEvent.keyDown(tab1, { key: "ArrowRight" });
      expect(document.activeElement).toBe(screen.getByRole("tab", { name: "Tab 2" }));
    });

    it("has proper ARIA attributes", () => {
      render(<Tabs tabs={defaultTabs} activeTab="tab1" />);

      const tablist = screen.getByRole("tablist");
      expect(tablist).toBeInTheDocument();

      const tab = screen.getByRole("tab", { name: "Tab 1" });
      expect(tab).toHaveAttribute("aria-controls", "tabpanel-tab1");
    });

    it("respects disabled tabs", () => {
      const tabsWithDisabled = [
        { id: "tab1", label: "Tab 1" },
        { id: "tab2", label: "Tab 2", disabled: true },
      ];
      const onChange = vi.fn();
      render(<Tabs tabs={tabsWithDisabled} activeTab="tab1" onTabChange={onChange} />);

      fireEvent.click(screen.getByText("Tab 2"));
      expect(onChange).not.toHaveBeenCalled();
    });
  });

  describe("TabPanel Component", () => {
    it("shows content when active", () => {
      render(
        <TabPanel id="test" activeTab="test">
          <div>Panel Content</div>
        </TabPanel>
      );

      expect(screen.getByText("Panel Content")).toBeInTheDocument();
    });

    it("hides content when not active", () => {
      render(
        <TabPanel id="test" activeTab="other">
          <div>Panel Content</div>
        </TabPanel>
      );

      const panel = screen.getByRole("tabpanel", { hidden: true });
      expect(panel).toHaveAttribute("hidden");
    });

    it("has proper ARIA attributes", () => {
      render(
        <TabPanel id="test" activeTab="test">
          <div>Content</div>
        </TabPanel>
      );

      const panel = screen.getByRole("tabpanel");
      expect(panel).toHaveAttribute("aria-labelledby", "tab-test");
    });
  });

  describe("AssetCard Component", () => {
    const defaultProps = {
      rank: 1,
      ticker: "AAPL",
      name: "Apple Inc.",
      price: 175.5,
      change: 2.5,
      score: 85,
      signal: "BUY",
      assetType: "shares",
    };

    it("renders all basic info", () => {
      render(<AssetCard {...defaultProps} />);

      expect(screen.getByText("#1")).toBeInTheDocument();
      expect(screen.getByText("AAPL")).toBeInTheDocument();
      expect(screen.getByText("Apple Inc.")).toBeInTheDocument();
      expect(screen.getByText("$175.50")).toBeInTheDocument();
      expect(screen.getByText("+2.50%")).toBeInTheDocument();
      expect(screen.getByText("85")).toBeInTheDocument();
      expect(screen.getByText("BUY")).toBeInTheDocument();
    });

    it("formats negative change correctly", () => {
      render(<AssetCard {...defaultProps} change={-3.25} />);

      expect(screen.getByText("-3.25%")).toBeInTheDocument();
    });

    it("shows correct signal badge for SELL", () => {
      render(<AssetCard {...defaultProps} signal="SELL" />);

      const signal = screen.getByText("SELL");
      expect(signal).toHaveClass("asset-card__signal--sell");
    });

    it("shows correct signal badge for HOLD", () => {
      render(<AssetCard {...defaultProps} signal="HOLD" />);

      const signal = screen.getByText("HOLD");
      expect(signal).toHaveClass("asset-card__signal--hold");
    });

    it("calls onClick when clicked", () => {
      const onClick = vi.fn();
      render(<AssetCard {...defaultProps} onClick={onClick} />);

      fireEvent.click(screen.getByRole("button"));
      expect(onClick).toHaveBeenCalled();
    });

    it("shows selected state", () => {
      const { container } = render(<AssetCard {...defaultProps} isSelected={true} />);

      expect(container.firstChild).toHaveClass("asset-card--selected");
    });

    it("renders crypto asset icon", () => {
      render(<AssetCard {...defaultProps} assetType="digital_assets" />);

      expect(screen.getByText("🪙")).toBeInTheDocument();
    });

    it("renders commodity asset icon", () => {
      render(<AssetCard {...defaultProps} assetType="commodities" />);

      expect(screen.getByText("🛢️")).toBeInTheDocument();
    });

    it("formats small prices correctly", () => {
      render(<AssetCard {...defaultProps} price={0.00045} />);

      expect(screen.getByText("$0.0005")).toBeInTheDocument();
    });

    it("handles keyboard activation", () => {
      const onClick = vi.fn();
      render(<AssetCard {...defaultProps} onClick={onClick} />);

      const card = screen.getByRole("button");
      fireEvent.keyDown(card, { key: "Enter" });

      expect(onClick).toHaveBeenCalled();
    });
  });

  describe("TopAssetsPanel Component", () => {
    beforeEach(() => {
      vi.clearAllMocks();
    });

    it("renders tabs for all asset types", () => {
      apiClient.get.mockResolvedValue({ data: [] });
      render(<TopAssetsPanel />);

      expect(screen.getByText("Shares")).toBeInTheDocument();
      expect(screen.getByText("Crypto")).toBeInTheDocument();
      expect(screen.getByText("Commodities")).toBeInTheDocument();
    });

    it("fetches data on mount", async () => {
      apiClient.get.mockResolvedValue({
        data: [{ ticker: "AAPL", name: "Apple", price: 175, score: 85, signal: "BUY" }],
      });

      render(<TopAssetsPanel defaultTab="shares" />);

      await waitFor(() => {
        expect(apiClient.get).toHaveBeenCalledWith("/api/ranking/shares", {
          params: { limit: 10 },
        });
      });
    });

    it("shows loading state", () => {
      apiClient.get.mockImplementation(() => new Promise(() => {})); // Never resolves
      render(<TopAssetsPanel />);

      // Should have loading skeleton
      const loadingCards = document.querySelectorAll(".asset-card--loading");
      expect(loadingCards.length).toBeGreaterThan(0);
    });

    it("shows error state with retry button", async () => {
      apiClient.get.mockRejectedValue(new Error("Network error"));
      render(<TopAssetsPanel />);

      await waitFor(() => {
        expect(screen.getByText("Try Again")).toBeInTheDocument();
      });
    });

    it("switches tabs and fetches new data", async () => {
      apiClient.get.mockResolvedValue({ data: [] });
      render(<TopAssetsPanel defaultTab="shares" />);

      // Click crypto tab
      fireEvent.click(screen.getByText("Crypto"));

      await waitFor(() => {
        expect(apiClient.get).toHaveBeenCalledWith("/api/ranking/digital_assets", {
          params: { limit: 10 },
        });
      });
    });

    it("calls onAssetSelect when asset is clicked", async () => {
      apiClient.get.mockResolvedValue({
        data: [{ ticker: "AAPL", name: "Apple", price: 175, score: 85, signal: "BUY" }],
      });

      const onSelect = vi.fn();
      render(<TopAssetsPanel onAssetSelect={onSelect} />);

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText("AAPL"));
      expect(onSelect).toHaveBeenCalled();
    });
  });
});
