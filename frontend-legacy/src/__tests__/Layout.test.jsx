import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Dashboard, Panel, Header, Footer } from "../components/layout";

describe("Layout Components", () => {
  describe("Dashboard Component", () => {
    it("renders with all panels", () => {
      render(
        <Dashboard
          header={<div>Header Content</div>}
          signalsPanel={<div>Signals Panel</div>}
          assetsPanel={<div>Assets Panel</div>}
          backtestPanel={<div>Backtest Panel</div>}
          footer={<div>Footer Content</div>}
        />
      );

      expect(screen.getByText("Header Content")).toBeInTheDocument();
      expect(screen.getByText("Signals Panel")).toBeInTheDocument();
      expect(screen.getByText("Assets Panel")).toBeInTheDocument();
      expect(screen.getByText("Backtest Panel")).toBeInTheDocument();
      expect(screen.getByText("Footer Content")).toBeInTheDocument();
    });

    it("renders with only required assetsPanel", () => {
      render(<Dashboard assetsPanel={<div>Main Content</div>} />);

      expect(screen.getByText("Main Content")).toBeInTheDocument();
    });

    it("has proper ARIA roles", () => {
      render(
        <Dashboard
          signalsPanel={<div>Signals</div>}
          assetsPanel={<div>Assets</div>}
          backtestPanel={<div>Backtest</div>}
        />
      );

      expect(screen.getByRole("main")).toBeInTheDocument();
      expect(screen.getAllByRole("complementary")).toHaveLength(2);
    });

    it("applies custom className", () => {
      const { container } = render(
        <Dashboard assetsPanel={<div>Content</div>} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass("dashboard", "custom-class");
    });
  });

  describe("Panel Component", () => {
    it("renders with title and content", () => {
      render(
        <Panel id="test-panel" title="Test Panel">
          <div>Panel Content</div>
        </Panel>
      );

      expect(screen.getByText("Test Panel")).toBeInTheDocument();
      expect(screen.getByText("Panel Content")).toBeInTheDocument();
    });

    it("renders with icon", () => {
      render(
        <Panel id="test-panel" title="Test Panel" icon="🔥">
          <div>Content</div>
        </Panel>
      );

      expect(screen.getByText("🔥")).toBeInTheDocument();
    });

    it("toggles collapsed state on click", () => {
      render(
        <Panel id="toggle-test" title="Toggle Panel">
          <div>Content</div>
        </Panel>
      );

      const header = screen.getByRole("button");
      expect(header).toHaveAttribute("aria-expanded", "true");

      fireEvent.click(header);
      expect(header).toHaveAttribute("aria-expanded", "false");

      fireEvent.click(header);
      expect(header).toHaveAttribute("aria-expanded", "true");
    });

    it("respects defaultCollapsed prop", () => {
      // Clear localStorage
      localStorage.clear();

      render(
        <Panel id="collapsed-test" title="Collapsed Panel" defaultCollapsed={true}>
          <div>Content</div>
        </Panel>
      );

      const header = screen.getByRole("button");
      expect(header).toHaveAttribute("aria-expanded", "false");
    });

    it("shows loading state", () => {
      render(
        <Panel id="loading-test" title="Loading Panel" loading={true}>
          <div>Content</div>
        </Panel>
      );

      expect(screen.getByText("Loading...")).toBeInTheDocument();
    });

    it("renders header actions", () => {
      render(
        <Panel id="actions-test" title="Actions Panel" headerActions={<button>Action</button>}>
          <div>Content</div>
        </Panel>
      );

      expect(screen.getByRole("button", { name: "Action" })).toBeInTheDocument();
    });

    it("is not collapsible when collapsible=false", () => {
      render(
        <Panel id="non-collapsible" title="Non-Collapsible" collapsible={false}>
          <div>Content</div>
        </Panel>
      );

      expect(screen.queryByRole("button")).not.toBeInTheDocument();
    });
  });

  describe("Header Component", () => {
    it("renders with default title", () => {
      render(<Header />);

      expect(screen.getByText("Market Predictor")).toBeInTheDocument();
    });

    it("renders with custom title", () => {
      render(<Header title="Custom Title" />);

      expect(screen.getByText("Custom Title")).toBeInTheDocument();
    });

    it("shows dark mode toggle", () => {
      const onToggle = vi.fn();
      render(<Header darkMode={false} onToggleDarkMode={onToggle} />);

      const themeButton = screen.getByLabelText("Switch to dark mode");
      expect(themeButton).toBeInTheDocument();

      fireEvent.click(themeButton);
      expect(onToggle).toHaveBeenCalled();
    });

    it("shows correct icon for dark mode", () => {
      render(<Header darkMode={true} />);

      expect(screen.getByLabelText("Switch to light mode")).toBeInTheDocument();
    });

    it("renders settings button when handler provided", () => {
      const onSettings = vi.fn();
      render(<Header onOpenSettings={onSettings} />);

      const settingsButton = screen.getByLabelText("Open settings");
      fireEvent.click(settingsButton);

      expect(onSettings).toHaveBeenCalled();
    });

    it("renders help button when handler provided", () => {
      const onHelp = vi.fn();
      render(<Header onOpenHelp={onHelp} />);

      const helpButton = screen.getByLabelText("Open help");
      fireEvent.click(helpButton);

      expect(onHelp).toHaveBeenCalled();
    });

    it("renders search component slot", () => {
      render(<Header searchComponent={<input placeholder="Search..." />} />);

      expect(screen.getByPlaceholderText("Search...")).toBeInTheDocument();
    });

    it("has accessible logo link", () => {
      render(<Header />);

      const logoLink = screen.getByLabelText("Go to homepage");
      expect(logoLink).toHaveAttribute("href", "/");
    });
  });

  describe("Footer Component", () => {
    it("renders market regime indicator", () => {
      render(<Footer marketRegime="bull" />);

      expect(screen.getByText("Bull Market")).toBeInTheDocument();
    });

    it("renders all regime types", () => {
      const regimes = ["bull", "bear", "neutral", "volatile"];
      const labels = ["Bull Market", "Bear Market", "Neutral", "High Volatility"];

      regimes.forEach((regime, index) => {
        const { unmount } = render(<Footer marketRegime={regime} />);
        expect(screen.getByText(labels[index])).toBeInTheDocument();
        unmount();
      });
    });

    it("formats last update time", () => {
      const date = new Date("2026-02-06T14:30:00");
      render(<Footer lastUpdate={date} />);

      // The exact format depends on locale, but should contain time
      expect(screen.getByText(/Updated:/)).toBeInTheDocument();
    });

    it("renders connection status", () => {
      render(<Footer connectionStatus="connected" />);

      expect(screen.getByText("Connected")).toBeInTheDocument();
    });

    it("renders disconnected status", () => {
      render(<Footer connectionStatus="disconnected" />);

      expect(screen.getByText("Disconnected")).toBeInTheDocument();
    });

    it("renders reconnecting status", () => {
      render(<Footer connectionStatus="reconnecting" />);

      expect(screen.getByText("Reconnecting...")).toBeInTheDocument();
    });

    it("renders version when provided", () => {
      render(<Footer version="1.2.3" />);

      expect(screen.getByText("v1.2.3")).toBeInTheDocument();
    });

    it("renders custom children", () => {
      render(
        <Footer>
          <span>Custom Footer Content</span>
        </Footer>
      );

      expect(screen.getByText("Custom Footer Content")).toBeInTheDocument();
    });

    it("has accessible status indicator", () => {
      render(<Footer connectionStatus="connected" />);

      const statusIndicator = screen.getByRole("status");
      expect(statusIndicator).toBeInTheDocument();
    });
  });
});
