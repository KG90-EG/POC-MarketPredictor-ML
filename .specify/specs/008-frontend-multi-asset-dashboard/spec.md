# FR-007: Multi-Asset Trading Dashboard - Specification

> **Status:** IN PROGRESS  
> **Created:** 2026-02-06  
> **Updated:** 2026-02-06  
> **Type:** Feature Request  
> **Priority:** High  
> **Dependencies:** NFR-011 (Backend Multi-Asset)

---

## 📊 Implementation Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1: Dashboard Layout | ✅ COMPLETED | Grid layout, Panel, Header, Footer components |
| Phase 2: Asset Components | ✅ COMPLETED | Tabs, AssetCard, TopAssetsPanel, useAssets hook, App integration |
| Phase 3: Tutorial System | 🔲 NOT STARTED | 5-step onboarding tutorial |
| Phase 4: Settings Panel | 🔲 NOT STARTED | Comprehensive settings modal |

---

## 📋 Executive Summary

This specification defines the frontend architecture for a unified multi-asset trading dashboard. The dashboard consolidates three asset classes (Shares, Digital Assets, Raw Materials/Commodities) into a streamlined, mobile-responsive interface with a merged "Top Assets" panel featuring tabbed navigation.

**Key Deliverables:**
1. **Three-Panel Layout:** Trading Signals, Top Assets (merged), Backtest
2. **Tabbed Navigation:** Asset class switcher within Top Assets panel
3. **5-Step Tutorial:** Guided onboarding (1 step per main feature)
4. **Settings Audit:** Comprehensive settings panel with all configuration options
5. **Mobile-First Design:** Responsive grid layout

---

## 🎯 Goals & Non-Goals

### Goals
- ✅ Unified dashboard for all asset types
- ✅ Intuitive tabbed navigation for asset switching
- ✅ Mobile-responsive layout (breakpoints: 320px, 768px, 1024px, 1440px)
- ✅ 5-step interactive tutorial for new users
- ✅ Centralized settings with all feature flags exposed
- ✅ Consistent UI patterns across all panels
- ✅ Performance: <200ms panel switches

### Non-Goals
- ❌ Real-time WebSocket updates (future enhancement)
- ❌ Multi-language support (future)
- ❌ Custom themes beyond dark/light (future)
- ❌ Drag-and-drop panel customization (future)

---

## 📐 User Stories

### FR-007.1: Three-Panel Dashboard Layout
**As a** trader  
**I want** a clean three-panel dashboard  
**So that** I can quickly access signals, rankings, and backtesting

**Acceptance Criteria:**
- [ ] Panel 1: Trading Signals (full width on mobile, left column on desktop)
- [ ] Panel 2: Top Assets with tabs (center/main area)
- [ ] Panel 3: Backtest (right column on desktop, expandable on mobile)
- [ ] Collapsible panels on mobile
- [ ] Responsive grid with CSS Grid/Flexbox
- [ ] Persistent panel state in localStorage

**Wireframe - Desktop (1440px+):**
```
┌─────────────────────────────────────────────────────────────────┐
│  Header: Logo | Search | Settings ⚙️ | Theme 🌙 | Help ❓        │
├─────────────────────────────────────────────────────────────────┤
│  Tutorial Banner (dismissible)                                   │
├────────────────┬────────────────────────────┬───────────────────┤
│                │                            │                   │
│  PANEL 1       │  PANEL 2                   │  PANEL 3          │
│  Trading       │  Top Assets                │  Backtest         │
│  Signals       │  ┌──────┬──────┬──────┐   │  Simulator        │
│                │  │Shares│Crypto│Commod│   │                   │
│  ⬆ BUY: 12     │  ├──────┴──────┴──────┤   │  Portfolio        │
│  ⬇ SELL: 5     │  │ AAPL    +2.3%      │   │  Value: $100k     │
│  ➡ HOLD: 33    │  │ MSFT    +1.8%      │   │                   │
│                │  │ GOOGL   -0.5%      │   │  Performance      │
│  [View All]    │  └───────────────────┘   │  Chart 📈         │
│                │                            │                   │
└────────────────┴────────────────────────────┴───────────────────┘
│  Footer: Market Regime: RISK_ON | Last Update: 10:30:45         │
└─────────────────────────────────────────────────────────────────┘
```

**Wireframe - Mobile (< 768px):**
```
┌───────────────────────┐
│  ☰  MarketPredictor   │
├───────────────────────┤
│  [Signals ▼]          │  <- Collapsible
│  BUY: 12 | SELL: 5    │
├───────────────────────┤
│  Top Assets           │
│  [Shares][Crypto][◉]  │  <- Tabs (scroll)
│  ┌─────────────────┐  │
│  │ AAPL    +2.3%   │  │
│  │ MSFT    +1.8%   │  │
│  └─────────────────┘  │
├───────────────────────┤
│  [Backtest ▼]         │  <- Collapsible
│  Start Simulation     │
└───────────────────────┘
```

---

### FR-007.2: Tabbed Top Assets Panel
**As a** trader  
**I want** to switch between asset classes with tabs  
**So that** I can quickly compare different markets

**Acceptance Criteria:**
- [ ] Three tabs: Shares | Digital Assets | Commodities
- [ ] Active tab highlighted with accent color
- [ ] Tab counter showing number of assets per type
- [ ] Keyboard navigation (Arrow keys, Enter)
- [ ] Swipe gesture on mobile
- [ ] Tab state persisted in URL query param
- [ ] Lazy loading of inactive tab content

**Tab Component:**
```jsx
<AssetTabs 
  tabs={[
    { id: 'shares', label: 'Shares', count: 50, icon: '📈' },
    { id: 'digital_assets', label: 'Digital Assets', count: 30, icon: '₿' },
    { id: 'commodities', label: 'Commodities', count: 8, icon: '🛢️' }
  ]}
  activeTab={selectedTab}
  onTabChange={handleTabChange}
/>
```

---

### FR-007.3: Asset Ranking Cards
**As a** trader  
**I want** to see asset rankings in a consistent card format  
**So that** I can quickly scan opportunities

**Acceptance Criteria:**
- [ ] Card shows: Ticker, Name, Price, 24h Change, Score, Signal
- [ ] Color-coded signals (Green=BUY, Red=SELL, Gray=HOLD)
- [ ] Sparkline chart for 7-day trend
- [ ] Risk indicator badge
- [ ] Click to expand with details
- [ ] Skeleton loading state

**Card Design:**
```
┌──────────────────────────────────────┐
│  📈 AAPL                    Score: 85 │
│  Apple Inc.                  🟢 BUY   │
│  $178.50        +2.3%     [────▲───] │
│  Risk: Low      Vol: $45M            │
└──────────────────────────────────────┘
```

---

### FR-007.4: Five-Step Tutorial Onboarding
**As a** new user  
**I want** a guided tutorial  
**So that** I can learn how to use all features

**Acceptance Criteria:**
- [ ] 5 steps covering main features
- [ ] Modal with spotlight on target element
- [ ] Progress indicator (1/5, 2/5, etc.)
- [ ] Skip button and "Don't show again" checkbox
- [ ] Restartable from Settings
- [ ] Persisted completion state

**Tutorial Steps:**
| Step | Target | Title | Description |
|------|--------|-------|-------------|
| 1 | Header | Welcome | Introduction to the platform |
| 2 | Panel 1 | Trading Signals | How signals work |
| 3 | Panel 2 + Tabs | Top Assets | Browsing and comparing assets |
| 4 | Panel 3 | Backtest | Running simulations |
| 5 | Settings Icon | Settings | Customizing your experience |

**Spotlight Component:**
```jsx
<TutorialSpotlight
  step={currentStep}
  target={targetRef}
  title="Trading Signals"
  description="View buy/sell recommendations powered by ML models. 
               Green indicates BUY opportunities, red indicates SELL."
  onNext={handleNext}
  onSkip={handleSkip}
/>
```

---

### FR-007.5: Settings Panel Audit
**As a** user  
**I want** access to all platform settings  
**So that** I can customize my experience

**Acceptance Criteria:**
- [ ] Settings accessible via ⚙️ icon in header
- [ ] Grouped into logical sections
- [ ] Changes saved immediately (or with Save button)
- [ ] Reset to defaults option
- [ ] Keyboard accessible

**Settings Structure:**
```
Settings
├── 📊 Display
│   ├── Theme (Light/Dark/System)
│   ├── Currency (USD/EUR/GBP)
│   ├── Compact Mode (on/off)
│   └── Show Sparklines (on/off)
│
├── 📈 Trading
│   ├── Default Asset Type (Shares/Digital Assets/Commodities)
│   ├── Risk Tolerance (Low/Medium/High)
│   ├── Minimum Score Filter (0-100 slider)
│   └── Auto-refresh Interval (1m/5m/15m/off)
│
├── 🔔 Notifications
│   ├── Price Alerts (on/off)
│   ├── Signal Changes (on/off)
│   └── Email Notifications (on/off)
│
├── 📊 Backtest
│   ├── Default Initial Capital ($)
│   ├── Default Time Period (1M/3M/6M/1Y)
│   └── Show Transaction Costs (on/off)
│
├── 🧠 AI Features
│   ├── LLM Analysis (on/off)
│   ├── Send Feedback (on/off)
│   └── Show AI Explanations (on/off)
│
└── ⚙️ Advanced
    ├── API Endpoint Override
    ├── Cache Duration
    ├── Debug Mode
    └── Export Settings (JSON)
```

---

### FR-007.6: Mobile-Responsive Grid
**As a** mobile user  
**I want** a responsive layout  
**So that** I can trade on any device

**Acceptance Criteria:**
- [ ] Breakpoints: 320px, 768px, 1024px, 1440px
- [ ] Touch-friendly tap targets (min 44px)
- [ ] Swipe gestures for tabs
- [ ] Collapsible panels
- [ ] Bottom navigation on mobile
- [ ] No horizontal scroll

**Grid Layout (CSS Grid):**
```css
/* Desktop (1024px+) */
.dashboard {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  grid-template-rows: auto 1fr auto;
  gap: 16px;
}

/* Tablet (768px - 1023px) */
@media (max-width: 1023px) {
  .dashboard {
    grid-template-columns: 1fr 1fr;
  }
  .backtest-panel {
    grid-column: span 2;
  }
}

/* Mobile (< 768px) */
@media (max-width: 767px) {
  .dashboard {
    grid-template-columns: 1fr;
  }
}
```

---

## 🧩 Component Architecture

```
src/
├── components/
│   ├── layout/
│   │   ├── Dashboard.jsx           # Main grid container
│   │   ├── Header.jsx              # Top bar
│   │   ├── Footer.jsx              # Status bar
│   │   └── Panel.jsx               # Collapsible panel wrapper
│   │
│   ├── signals/
│   │   ├── SignalPanel.jsx         # Panel 1
│   │   ├── SignalCard.jsx          # Individual signal
│   │   └── SignalSummary.jsx       # BUY/SELL/HOLD counts
│   │
│   ├── assets/
│   │   ├── TopAssetsPanel.jsx      # Panel 2 with tabs
│   │   ├── AssetTabs.jsx           # Tab navigation
│   │   ├── AssetCard.jsx           # Ranking card
│   │   ├── AssetList.jsx           # Virtualized list
│   │   └── AssetDetail.jsx         # Expanded view
│   │
│   ├── backtest/
│   │   ├── BacktestPanel.jsx       # Panel 3
│   │   ├── BacktestForm.jsx        # Configuration form
│   │   ├── PortfolioBuilder.jsx    # Asset selector
│   │   └── ResultsChart.jsx        # Performance chart
│   │
│   ├── settings/
│   │   ├── SettingsModal.jsx       # Modal container
│   │   ├── SettingsSection.jsx     # Grouped settings
│   │   └── SettingControl.jsx      # Individual control
│   │
│   ├── tutorial/
│   │   ├── TutorialProvider.jsx    # Context provider
│   │   ├── TutorialSpotlight.jsx   # Spotlight overlay
│   │   └── TutorialProgress.jsx    # Step indicator
│   │
│   └── shared/
│       ├── Tabs.jsx                # Generic tab component
│       ├── Card.jsx                # Base card
│       ├── Skeleton.jsx            # Loading state
│       ├── Badge.jsx               # Signal badges
│       └── Sparkline.jsx           # Mini chart
│
├── hooks/
│   ├── useAssets.js                # Asset data fetching
│   ├── useSettings.js              # Settings state
│   ├── useTutorial.js              # Tutorial state
│   └── useResponsive.js            # Breakpoint detection
│
├── store/
│   ├── assetsSlice.js              # Asset state (if Redux)
│   ├── settingsSlice.js            # Settings state
│   └── uiSlice.js                  # UI state (panels, tabs)
│
└── styles/
    ├── variables.css               # CSS custom properties
    ├── grid.css                    # Grid layouts
    └── responsive.css              # Media queries
```

---

## 🎨 Design System

### Colors
```css
:root {
  /* Signals */
  --signal-buy: #10B981;      /* Emerald 500 */
  --signal-sell: #EF4444;     /* Red 500 */
  --signal-hold: #6B7280;     /* Gray 500 */
  
  /* Asset Types */
  --asset-shares: #3B82F6;    /* Blue 500 */
  --asset-crypto: #F59E0B;    /* Amber 500 */
  --asset-commodity: #8B5CF6; /* Violet 500 */
  
  /* UI */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F3F4F6;
  --text-primary: #111827;
  --text-secondary: #6B7280;
  --border: #E5E7EB;
  --accent: #3B82F6;
}

[data-theme="dark"] {
  --bg-primary: #111827;
  --bg-secondary: #1F2937;
  --text-primary: #F9FAFB;
  --text-secondary: #9CA3AF;
  --border: #374151;
}
```

### Typography
```css
:root {
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
}
```

### Spacing
```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
}
```

---

## ⚠️ Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Tutorial abandonment | Medium | Low | Keep steps short, allow skip |
| Settings overwhelming | Medium | Medium | Group logically, show defaults |
| Slow tab switching | Low | High | Lazy loading, skeleton states |
| Mobile usability | Medium | High | User testing, real device testing |
| Accessibility | Medium | High | WCAG 2.1 AA audit |

---

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Tutorial completion rate | >60% | - |
| Tab switch latency | <200ms | - |
| Mobile Lighthouse score | >90 | - |
| Settings panel usage | >30% users | - |
| Bounce rate reduction | -20% | - |

---

## 🔗 Dependencies

- **NFR-011:** Backend Multi-Asset (unified API endpoints)
- **FR-006:** LLM Learning (AI features in settings)
- **React:** 18+ (existing)
- **Vite:** 5+ (existing)
- **CSS:** Native CSS Grid/Flexbox (no framework)

---

## 📝 Open Questions

1. ✅ **Panel arrangement:** Trading Signals | Top Assets | Backtest
2. ✅ **Tutorial length:** 5 steps (1 per main feature)
3. ✅ **Settings persistence:** localStorage (cloud sync later)
4. ⏳ **Charts library:** Recharts vs Visx? (TBD)
5. ⏳ **State management:** Context API vs Redux? (evaluate)
