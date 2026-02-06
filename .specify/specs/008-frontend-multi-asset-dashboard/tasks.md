# FR-007: Multi-Asset Trading Dashboard - Tasks

> **Status:** ⏳ IN PROGRESS  
> **Created:** 2026-02-06  
> **Updated:** 2026-02-06  
> **Plan:** [plan.md](./plan.md)

---

## 📊 Progress Summary

| Phase | Status | Completed |
|-------|--------|-----------|
| Phase 1: Dashboard Layout | ✅ COMPLETED | 6/6 |
| Phase 2: Asset Components | ✅ COMPLETED | 5/5 (P0 tasks) |
| Phase 3: Tutorial System | 🔲 NOT STARTED | 0/6 |
| Phase 4: Settings Panel | 🔲 NOT STARTED | 0/? |

**Note:** P1/P2 tasks (virtualization, skeleton, swipe gestures) deferred for later optimization.

**App Integration:** DashboardPage is now integrated into App.jsx as the default landing view.

---

## 🎯 Phase 1: Dashboard Layout (Week 1)

### TASK-007-001: Create Dashboard Grid Container ✅
**Priority:** P0 | **Effort:** 3h | **Owner:** -

**Description:**
Create the main Dashboard component with CSS Grid layout.

**Acceptance Criteria:**
- [x] Grid layout with named areas
- [x] Three-column layout on desktop
- [x] Two-column on tablet
- [x] Single column on mobile
- [x] Gap spacing consistent
- [x] 100vh full height

**Code Location:** `frontend/src/components/layout/Dashboard.jsx`

**Completed:** 2026-02-06

**Starter Code:**
```jsx
export function Dashboard({ children }) {
  return (
    <div className="dashboard">
      <header className="dashboard__header">{/* Header */}</header>
      <aside className="dashboard__signals">{/* Panel 1 */}</aside>
      <main className="dashboard__assets">{/* Panel 2 */}</main>
      <aside className="dashboard__backtest">{/* Panel 3 */}</aside>
      <footer className="dashboard__footer">{/* Footer */}</footer>
    </div>
  );
}
```

---

### TASK-007-002: Create Panel Wrapper Component ✅
**Priority:** P0 | **Effort:** 2h | **Owner:** -

**Description:**
Create reusable Panel component with collapsible functionality.

**Acceptance Criteria:**
- [x] Collapsible on mobile
- [x] Animated expand/collapse
- [x] Header with title and toggle button
- [x] Accessible (ARIA expanded)
- [x] Persists state in localStorage

**Code Location:** `frontend/src/components/layout/Panel.jsx`

**Completed:** 2026-02-06

---

### TASK-007-003: Create Header Component ✅
**Priority:** P0 | **Effort:** 2h | **Owner:** -

**Description:**
Create Header with logo, search, and action buttons.

**Acceptance Criteria:**
- [x] Logo with link to home
- [x] Search input (optional, can be empty first)
- [x] Settings button (⚙️)
- [x] Theme toggle (🌙/☀️)
- [x] Help button (❓)
- [x] Mobile hamburger menu

**Code Location:** `frontend/src/components/layout/Header.jsx`

**Completed:** 2026-02-06

---

### TASK-007-004: Create Footer Component ✅
**Priority:** P1 | **Effort:** 1h | **Owner:** -

**Description:**
Create Footer with status indicators.

**Acceptance Criteria:**
- [x] Market regime indicator
- [x] Last update timestamp
- [x] Connection status
- [x] Responsive layout

**Code Location:** `frontend/src/components/layout/Footer.jsx`

**Completed:** 2026-02-06

---

### TASK-007-005: Create Responsive CSS Grid ✅
**Priority:** P0 | **Effort:** 3h | **Owner:** -

**Description:**
Implement responsive grid styles with breakpoints.

**Acceptance Criteria:**
- [x] Breakpoints: 768px (mobile), 1200px (tablet), 1600px (large desktop)
- [x] Named grid areas (signals, assets, backtest)
- [x] Consistent gap spacing (20px desktop, 12px mobile)
- [x] No horizontal scroll
- [ ] Test on real devices (deferred to TASK-007-007)

**Code Location:** `frontend/src/components/layout/Dashboard.css`

**Completed:** 2026-02-06

---

### TASK-007-006: Implement Panel Collapse Logic ✅
**Priority:** P1 | **Effort:** 2h | **Owner:** -

**Description:**
Add state management for collapsible panels.

**Acceptance Criteria:**
- [x] Toggle panels individually
- [x] Persist state in localStorage
- [x] Animate transitions (max-height)
- [x] Update ARIA attributes (aria-expanded, aria-controls)

**Code Location:** `frontend/src/components/layout/Panel.jsx`

**Completed:** 2026-02-06

---

### TASK-007-007: Device Testing Setup
**Priority:** P1 | **Effort:** 3h | **Owner:** -

**Description:**
Set up testing on real devices and browsers.

**Acceptance Criteria:**
- [ ] Test on iOS Safari
- [ ] Test on Android Chrome
- [ ] Test on Desktop Chrome/Firefox/Safari
- [ ] Document any issues
- [ ] Fix critical issues

---

## 📊 Phase 2: Top Assets with Tabs (Week 2)

### TASK-007-008: Create Generic Tabs Component ✅
**Priority:** P0 | **Effort:** 3h | **Owner:** -

**Description:**
Create reusable Tabs component for asset type switching.

**Acceptance Criteria:**
- [x] Accepts array of tab definitions
- [x] Active tab styling
- [x] Keyboard navigation (←→ arrows, Enter, Home, End)
- [x] ARIA roles (tablist, tab, tabpanel)
- [x] Optional badge/counter per tab
- [x] Swipe support on mobile

**Code Location:** `frontend/src/components/shared/Tabs.jsx`

**Completed:** 2026-02-06

**Usage:**
```jsx
<Tabs
  tabs={[
    { id: 'shares', label: 'Shares', count: 50 },
    { id: 'digital_assets', label: 'Digital Assets', count: 30 },
    { id: 'commodities', label: 'Commodities', count: 8 }
  ]}
  activeTab="shares"
  onTabChange={handleChange}
/>
```

---

### TASK-007-009: Create TopAssetsPanel Component ✅
**Priority:** P0 | **Effort:** 4h | **Owner:** -

**Description:**
Create the main Top Assets panel with integrated tabs.

**Acceptance Criteria:**
- [x] Tabs for Shares/Digital Assets/Commodities
- [x] Fetches data from unified API (/api/ranking/{asset_type})
- [x] Loading skeleton state
- [x] Error state with retry
- [ ] URL-driven tab state (deferred to Phase 3)

**Code Location:** `frontend/src/components/assets/TopAssetsPanel.jsx`

**Completed:** 2026-02-06

---

### TASK-007-010: Create AssetCard Component ✅
**Priority:** P0 | **Effort:** 3h | **Owner:** -

**Description:**
Create card component for displaying asset ranking.

**Acceptance Criteria:**
- [x] Shows: ticker, name, price, change, score, signal
- [x] Color-coded signal badges
- [ ] Sparkline chart (7-day) - deferred
- [x] Risk indicator
- [x] Click to expand details
- [x] Hover state

**Code Location:** `frontend/src/components/assets/AssetCard.jsx`

**Completed:** 2026-02-06

**Card Layout:**
```
┌──────────────────────────────────┐
│ 📈 AAPL               Score: 85  │
│ Apple Inc.             🟢 BUY    │
│ $178.50     +2.3%   [─▲───]     │
│ Risk: Low   Vol: $45M           │
└──────────────────────────────────┘
```

---

### TASK-007-011: Create AssetList with Virtualization
**Priority:** P1 | **Effort:** 3h | **Owner:** -

**Description:**
Create virtualized list for efficient rendering of many assets.

**Acceptance Criteria:**
- [ ] Virtualized scrolling (react-window or similar)
- [ ] Handles 50+ items smoothly
- [ ] Scroll position preserved on tab switch
- [ ] Pull-to-refresh on mobile

**Code Location:** `frontend/src/components/assets/AssetList.jsx`

---

### TASK-007-012: Create useAssets Hook ✅
**Priority:** P0 | **Effort:** 2h | **Owner:** -

**Description:**
Create data fetching hook for asset rankings.

**Acceptance Criteria:**
- [x] Fetches from `/api/ranking/{asset_type}`
- [x] Caches results (1 min stale time)
- [x] Auto-refresh (5 min interval)
- [x] Returns loading/error states
- [x] Uses custom caching (React Query not needed)

**Code Location:** `frontend/src/hooks/useAssets.js`

**Completed:** 2026-02-06

---

### TASK-007-012b: Create DashboardPage and Integrate with App ✅
**Priority:** P0 | **Effort:** 2h | **Owner:** -

**Description:**
Create DashboardPage component that assembles the full dashboard layout and integrate it into the main App.jsx.

**Acceptance Criteria:**
- [x] DashboardPage combines Header, Footer, Panel, TopAssetsPanel
- [x] SignalsPlaceholder and BacktestPlaceholder for future content
- [x] Import DashboardPage in App.jsx
- [x] Add 'dashboard' view to ViewSelectorMenu
- [x] Dashboard is default view on app load
- [x] Pass darkMode, toggleDarkMode, onOpenHelp, marketRegime props

**Code Location:** 
- `frontend/src/components/pages/DashboardPage.jsx`
- `frontend/src/App.jsx`

**Completed:** 2026-02-06

---

### TASK-007-013: Add Skeleton Loading State
**Priority:** P1 | **Effort:** 1.5h | **Owner:** -

**Description:**
Create skeleton loading components.

**Acceptance Criteria:**
- [ ] Skeleton card matching AssetCard layout
- [ ] Animated shimmer effect
- [ ] Renders during loading
- [ ] Accessible (aria-busy)

**Code Location:** `frontend/src/components/shared/Skeleton.jsx`

---

### TASK-007-014: Add Mobile Swipe Gestures
**Priority:** P2 | **Effort:** 2h | **Owner:** -

**Description:**
Add swipe left/right to change tabs on mobile.

**Acceptance Criteria:**
- [ ] Swipe detection (touch events)
- [ ] Threshold for activation
- [ ] Visual feedback during swipe
- [ ] Works on iOS and Android

**Code Location:** `frontend/src/hooks/useSwipe.js`

---

## 📚 Phase 3: Tutorial System (Week 3)

### TASK-007-015: Create TutorialProvider Context
**Priority:** P0 | **Effort:** 2h | **Owner:** -

**Description:**
Create context for tutorial state management.

**Acceptance Criteria:**
- [ ] Tracks current step (0-5)
- [ ] Tracks completion status
- [ ] Provides next/prev/skip actions
- [ ] Persists state in localStorage

**Code Location:** `frontend/src/components/tutorial/TutorialProvider.jsx`

---

### TASK-007-016: Create TutorialSpotlight Overlay
**Priority:** P0 | **Effort:** 4h | **Owner:** -

**Description:**
Create spotlight overlay that highlights tutorial targets.

**Acceptance Criteria:**
- [ ] Dark overlay with cutout for target
- [ ] Tooltip with title/description
- [ ] Next/Back/Skip buttons
- [ ] Smooth transitions between steps
- [ ] Portal rendering (z-index safe)
- [ ] Focus management

**Code Location:** `frontend/src/components/tutorial/TutorialSpotlight.jsx`

---

### TASK-007-017: Create TutorialProgress Indicator
**Priority:** P1 | **Effort:** 1.5h | **Owner:** -

**Description:**
Create progress dots/steps indicator.

**Acceptance Criteria:**
- [ ] Shows 5 dots
- [ ] Active dot highlighted
- [ ] Completed dots filled
- [ ] Clickable to jump (optional)

**Code Location:** `frontend/src/components/tutorial/TutorialProgress.jsx`

---

### TASK-007-018: Define Tutorial Steps Content
**Priority:** P0 | **Effort:** 1.5h | **Owner:** -

**Description:**
Define content for each of the 5 tutorial steps.

**Acceptance Criteria:**
- [ ] Step 1: Welcome/Overview
- [ ] Step 2: Trading Signals panel
- [ ] Step 3: Top Assets + Tabs
- [ ] Step 4: Backtest panel
- [ ] Step 5: Settings
- [ ] Clear, concise copy

**Code Location:** `frontend/src/data/tutorialSteps.js`

**Content:**
```javascript
export const tutorialSteps = [
  {
    id: 1,
    target: 'header',
    title: 'Welcome to MarketPredictor! 👋',
    description: 'This quick tour will show you how to use all the features. Let\'s get started!',
  },
  {
    id: 2,
    target: 'signals-panel',
    title: 'Trading Signals',
    description: 'View real-time buy/sell/hold recommendations powered by our ML models.',
  },
  // ... etc
];
```

---

### TASK-007-019: Add Tutorial Restart from Settings
**Priority:** P1 | **Effort:** 1h | **Owner:** -

**Description:**
Allow users to restart the tutorial from Settings.

**Acceptance Criteria:**
- [ ] Button in Settings → Help section
- [ ] Resets tutorial step to 0
- [ ] Clears completion flag
- [ ] Opens tutorial immediately

---

### TASK-007-020: Tutorial Accessibility
**Priority:** P1 | **Effort:** 2h | **Owner:** -

**Description:**
Ensure tutorial is fully accessible.

**Acceptance Criteria:**
- [ ] Focus trapped in tooltip
- [ ] Escape key closes tutorial
- [ ] Screen reader announces step changes
- [ ] Keyboard-only navigation works

---

## ⚙️ Phase 4: Settings Panel (Week 4)

### TASK-007-021: Create SettingsModal Component
**Priority:** P0 | **Effort:** 3h | **Owner:** -

**Description:**
Create modal container for settings.

**Acceptance Criteria:**
- [ ] Triggered by ⚙️ button
- [ ] Overlay with blur background
- [ ] Close button and Escape key
- [ ] Scrollable content area
- [ ] Accessible (focus trap, ARIA)

**Code Location:** `frontend/src/components/settings/SettingsModal.jsx`

---

### TASK-007-022: Create SettingsSection Component
**Priority:** P1 | **Effort:** 1.5h | **Owner:** -

**Description:**
Create section grouping for related settings.

**Acceptance Criteria:**
- [ ] Collapsible sections
- [ ] Icon + title header
- [ ] Consistent spacing

**Code Location:** `frontend/src/components/settings/SettingsSection.jsx`

---

### TASK-007-023: Create Setting Control Components
**Priority:** P0 | **Effort:** 3h | **Owner:** -

**Description:**
Create individual setting control types.

**Acceptance Criteria:**
- [ ] Toggle switch (boolean)
- [ ] Dropdown select (enum)
- [ ] Slider (range)
- [ ] Input (text/number)
- [ ] All with labels and descriptions

**Code Location:** `frontend/src/components/settings/controls/`

---

### TASK-007-024: Implement Display Settings
**Priority:** P0 | **Effort:** 2h | **Owner:** -

**Description:**
Implement Display settings section.

**Settings:**
- [ ] Theme (Light/Dark/System)
- [ ] Currency (USD/EUR/GBP)
- [ ] Compact Mode
- [ ] Show Sparklines

---

### TASK-007-025: Implement Trading Settings
**Priority:** P0 | **Effort:** 2h | **Owner:** -

**Description:**
Implement Trading settings section.

**Settings:**
- [ ] Default Asset Type
- [ ] Risk Tolerance
- [ ] Minimum Score Filter
- [ ] Auto-refresh Interval

---

### TASK-007-026: Implement Notification Settings
**Priority:** P1 | **Effort:** 1.5h | **Owner:** -

**Description:**
Implement Notification settings section.

**Settings:**
- [ ] Price Alerts
- [ ] Signal Changes
- [ ] Email Notifications

---

### TASK-007-027: Implement Backtest Settings
**Priority:** P1 | **Effort:** 1.5h | **Owner:** -

**Description:**
Implement Backtest settings section.

**Settings:**
- [ ] Default Initial Capital
- [ ] Default Time Period
- [ ] Show Transaction Costs

---

### TASK-007-028: Implement AI Features Settings
**Priority:** P1 | **Effort:** 1.5h | **Owner:** -

**Description:**
Implement AI Features settings section.

**Settings:**
- [ ] LLM Analysis enabled
- [ ] Send Feedback
- [ ] Show AI Explanations

---

### TASK-007-029: Implement Advanced Settings
**Priority:** P2 | **Effort:** 2h | **Owner:** -

**Description:**
Implement Advanced settings section.

**Settings:**
- [ ] API Endpoint Override
- [ ] Cache Duration
- [ ] Debug Mode
- [ ] Export/Import Settings (JSON)

---

### TASK-007-030: Create useSettings Hook
**Priority:** P0 | **Effort:** 2h | **Owner:** -

**Description:**
Create hook for settings state management.

**Acceptance Criteria:**
- [ ] Loads from localStorage
- [ ] Saves on change
- [ ] Provides update function
- [ ] Provides reset function
- [ ] TypeScript types (if using TS)

**Code Location:** `frontend/src/hooks/useSettings.js`

---

## ✨ Phase 5: Polish & Testing (Week 5)

### TASK-007-031: Accessibility Audit
**Priority:** P0 | **Effort:** 3h | **Owner:** -

**Description:**
Perform WCAG 2.1 AA accessibility audit.

**Checklist:**
- [ ] Color contrast ≥ 4.5:1
- [ ] Keyboard navigation all elements
- [ ] Screen reader testing (VoiceOver/NVDA)
- [ ] Focus visible indicators
- [ ] ARIA attributes correct
- [ ] Document and fix issues

---

### TASK-007-032: Performance Optimization
**Priority:** P0 | **Effort:** 3h | **Owner:** -

**Description:**
Optimize performance for target metrics.

**Checklist:**
- [ ] Code splitting (lazy load panels)
- [ ] Image optimization
- [ ] Bundle size analysis
- [ ] Memoization of expensive components
- [ ] Lighthouse score ≥ 90

---

### TASK-007-033: Cross-Browser Testing
**Priority:** P1 | **Effort:** 2h | **Owner:** -

**Description:**
Test on major browsers.

**Browsers:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Document and fix issues

---

### TASK-007-034: Unit Tests
**Priority:** P0 | **Effort:** 4h | **Owner:** -

**Description:**
Write unit tests for all new components.

**Acceptance Criteria:**
- [ ] Test all hooks
- [ ] Test component rendering
- [ ] Test user interactions
- [ ] Coverage ≥ 80%

**Code Location:** `frontend/src/**/*.test.jsx`

---

### TASK-007-035: Integration Tests
**Priority:** P1 | **Effort:** 2h | **Owner:** -

**Description:**
Write integration tests for key flows.

**Flows:**
- [ ] Tab navigation
- [ ] Settings save/load
- [ ] Tutorial completion
- [ ] Panel collapse

---

### TASK-007-036: Documentation Update
**Priority:** P1 | **Effort:** 2h | **Owner:** -

**Description:**
Update documentation for new components.

**Deliverables:**
- [ ] Component README
- [ ] Settings reference
- [ ] Screenshot gallery
- [ ] Update main README

---

## 📋 Summary

| Phase | Tasks | Effort | Priority |
|-------|-------|--------|----------|
| Dashboard Layout | 7 | 16h | P0-P1 |
| Top Assets + Tabs | 7 | 18.5h | P0-P2 |
| Tutorial System | 6 | 12h | P0-P1 |
| Settings Panel | 10 | 20h | P0-P2 |
| Polish & Testing | 6 | 16h | P0-P1 |
| **Total** | **36** | **~82.5h** | - |

---

## 🔗 Cross-References

- **NFR-011:** Backend Multi-Asset (provides APIs)
- **FR-006:** LLM Learning (AI settings integration)
- **005:** Config Consolidation (settings alignment)
