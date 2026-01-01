# 🚀 UX Improvement Backlog

**Project**: POC Market Predictor - User Experience Overhaul  
**Created**: 2026-01-01  
**Current Score**: 6.5/10 → **Target Score**: 8.5/10

---

## 📋 Phase 1 - Foundation (Week 1-2)

**Goal**: Fix critical UX blockers and improve first impression  
**Target**: Score 7.5/10

### 1.1 Headlines & Copy Improvements ⚡ (2 hours)

- [ ] **P0** - Replace "POC Trading Overview" with user-friendly title
- [ ] **P0** - Improve subtitle from technical to benefit-focused
- [ ] **P0** - Simplify section titles (remove jargon)
- [ ] **P1** - Add contextual help text to all major sections

**Files**: `App.jsx`, `styles.css`

### 1.2 Portfolio View Hierarchy 🎯 (4 hours)

- [ ] **P0** - Reduce 5 equal options to clear hierarchy
- [ ] **P0** - Make "Buy Opportunities" the primary CTA
- [ ] **P1** - Add onboarding hint for first-time users
- [ ] **P1** - Improve icon consistency across buttons

**Files**: `App.jsx`, `styles.css`

### 1.3 Empty States & Feedback ✨ (3 hours)

- [ ] **P0** - Add empty state for stock rankings
- [ ] **P0** - Add empty state for crypto results
- [ ] **P0** - Add empty state for watchlists
- [ ] **P1** - Add success toast notifications
- [ ] **P1** - Improve error messages (user-friendly)

**Files**: `App.jsx`, Create `EmptyState.jsx`, Create `Toast.jsx`

### 1.4 Loading States Enhancement 🔄 (2 hours)

- [ ] **P1** - Replace spinners with skeleton screens
- [ ] **P1** - Add loading text that explains what's happening
- [ ] **P1** - Improve progress bar visibility

**Files**: `App.jsx`, `LoadingStates.jsx`, `styles.css`

### 1.5 Mobile Navigation Optimization 📱 (5 hours)

- [ ] **P0** - Create bottom navigation bar for mobile
- [ ] **P0** - Stack portfolio buttons vertically on small screens
- [ ] **P0** - Improve toolbar touch targets (min 44px)
- [ ] **P1** - Add swipe gestures for navigation

**Files**: `App.jsx`, `styles.css`, Create `MobileNav.jsx`

**Phase 1 Total**: ~16 hours / 2 weeks

---

## 📋 Phase 2 - Enhancement (Week 3-5)

**Goal**: Add missing features and improve discoverability  
**Target**: Score 8.0/10

### 2.1 Stock Table Improvements 📊 (6 hours)

- [ ] **P0** - Add column sorting (click header to sort)
- [ ] **P0** - Add filter bar (country, sector, market cap)
- [ ] **P1** - Reduce visible columns on mobile (card layout)
- [ ] **P1** - Add "Compare" checkbox to compare 2-3 stocks
- [ ] **P2** - Add export to CSV/Excel

**Files**: `StockRanking.jsx`, Create `FilterBar.jsx`, `styles.css`

### 2.2 Price Charts in Detail Views 📈 (8 hours)

- [ ] **P0** - Add 1D/1W/1M/1Y price chart to Company Sidebar
- [ ] **P0** - Add volume bars below price chart
- [ ] **P1** - Add technical indicators (MA, RSI)
- [ ] **P1** - Add chart for Crypto Detail Sidebar
- [ ] **P2** - Add comparison chart (overlay 2 stocks)

**Files**: `CompanyDetailSidebar.jsx`, `CryptoDetailSidebar.jsx`, Install `recharts`

### 2.3 Smart Search with Autocomplete 🔍 (6 hours)

- [ ] **P0** - Add autocomplete dropdown for stock search
- [ ] **P0** - Search by company name (not just ticker)
- [ ] **P1** - Show recent searches
- [ ] **P1** - Add keyboard navigation (arrow keys)
- [ ] **P2** - Add fuzzy search (typo tolerance)

**Files**: Create `AutocompleteSearch.jsx`, `App.jsx`, `api.js`

### 2.4 Watchlist Alerts & Enhancements ⭐ (8 hours)

- [ ] **P0** - Add price alert triggers (above/below price)
- [ ] **P0** - Add "Quick Add to Watchlist" button everywhere
- [ ] **P1** - Add email/browser notifications
- [ ] **P1** - Add notes to watchlist items
- [ ] **P2** - Add watchlist sharing (public link)

**Files**: `WatchlistManager.jsx`, Create `AlertConfig.jsx`, Backend endpoint

### 2.5 News Integration 📰 (6 hours)

- [ ] **P1** - Show latest 3 news in Company Detail Sidebar
- [ ] **P1** - Add news sentiment indicator (positive/negative)
- [ ] **P2** - Add news filter by date
- [ ] **P2** - Link news to price movements

**Files**: `CompanyDetailSidebar.jsx`, Backend API integration

### 2.6 Market Selector Context 🌍 (3 hours)

- [ ] **P1** - Add description for each market
- [ ] **P1** - Show market stats (total stocks, avg performance)
- [ ] **P2** - Add market comparison view

**Files**: `MarketSelector.jsx`, `styles.css`

**Phase 2 Total**: ~37 hours / 3 weeks

---

## 📋 Phase 3 - Polish & Optimization (Week 6-7)

**Goal**: Perfect the experience and validate with users  
**Target**: Score 8.5/10

### 3.1 Onboarding Flow 🎓 (8 hours)

- [ ] **P0** - Create welcome modal for first-time users
- [ ] **P0** - Add 3-question personalization
- [ ] **P0** - Show guided tour (highlight key features)
- [ ] **P1** - Add "Skip tour" and "Remind me later" options
- [ ] **P1** - Persist onboarding state to localStorage

**Files**: Create `OnboardingFlow.jsx`, `App.jsx`, `styles.css`

### 3.2 Accessibility Audit 🦾 (6 hours)

- [ ] **P0** - Run axe-core audit and fix critical issues
- [ ] **P0** - Improve keyboard navigation (tab order)
- [ ] **P0** - Add ARIA labels to all interactive elements
- [ ] **P1** - Test with screen reader (NVDA/VoiceOver)
- [ ] **P1** - Ensure color contrast meets WCAG AA
- [ ] **P2** - Add reduced-motion support

**Files**: All components, `styles.css`

### 3.3 Performance Optimization ⚡ (6 hours)

- [ ] **P0** - Code-split routes (lazy loading)
- [ ] **P0** - Optimize bundle size (tree-shaking)
- [ ] **P1** - Add React.memo to expensive components
- [ ] **P1** - Debounce search inputs
- [ ] **P1** - Optimize images (WebP, lazy loading)
- [ ] **P2** - Add service worker for offline support

**Files**: `main.jsx`, All components, `vite.config.js`

### 3.4 Usability Testing 🧪 (8 hours)

- [ ] **P0** - Conduct 5-second test with 5 users
- [ ] **P0** - Run first-click test on key tasks
- [ ] **P0** - Measure task success rate (target >90%)
- [ ] **P1** - Collect feedback via in-app survey
- [ ] **P1** - A/B test portfolio view layouts
- [ ] **P2** - Heatmap analysis (Hotjar/Microsoft Clarity)

**Files**: Testing scripts, Analytics setup

### 3.5 Design System Refinement 🎨 (5 hours)

- [ ] **P1** - Create consistent spacing scale (4px, 8px, 16px...)
- [ ] **P1** - Define typography hierarchy (sizes, weights)
- [ ] **P1** - Expand color palette (not just purple gradient)
- [ ] **P1** - Create reusable component library
- [ ] **P2** - Document design tokens

**Files**: Create `design-system.css`, Update all components

### 3.6 Advanced Features 🚀 (8 hours)

- [ ] **P1** - Add comparison view (side-by-side stocks)
- [ ] **P1** - Add portfolio performance tracking
- [ ] **P2** - Add custom alerts (e.g., "RSI > 70")
- [ ] **P2** - Add dark/light/auto theme detection
- [ ] **P2** - Add keyboard shortcuts (e.g., "/" for search)

**Files**: Create `ComparisonView.jsx`, `PortfolioTracker.jsx`, etc.

**Phase 3 Total**: ~41 hours / 2 weeks

---

## 📊 Success Metrics

### Phase 1 Success Criteria

- ✅ New users understand the app within 5 seconds
- ✅ Mobile users can navigate without horizontal scroll
- ✅ All empty states have clear CTAs
- ✅ Loading states show progress, not just spinners

### Phase 2 Success Criteria

- ✅ Users can find any stock in <10 seconds (search)
- ✅ Users can filter rankings by 3+ criteria
- ✅ Detail views show price chart + news
- ✅ Watchlist alerts work reliably

### Phase 3 Success Criteria

- ✅ 80%+ new users complete onboarding
- ✅ WCAG AA compliance score >95%
- ✅ Lighthouse score >90 (all categories)
- ✅ Task success rate >90% in user testing

---

## 🎯 Priority Legend

- **P0** = Critical (Must have)
- **P1** = High (Should have)
- **P2** = Medium (Nice to have)
- **P3** = Low (Future consideration)

---

## 📈 Progress Tracking

### Overall Progress

- [ ] Phase 1 - Foundation (0/5 tasks)
- [ ] Phase 2 - Enhancement (0/6 tasks)
- [ ] Phase 3 - Polish (0/6 tasks)

**Current Score**: 6.5/10  
**Target Score**: 8.5/10  
**Estimated Timeline**: 7 weeks  
**Total Effort**: ~94 hours

---

## 🔄 Next Steps

1. ✅ Review and approve backlog
2. ⏭️ Start Phase 1.1 - Headlines & Copy
3. ⏭️ Continue with Phase 1.2 - Portfolio Hierarchy
4. Track progress in this document
5. Iterate based on user feedback

---

**Last Updated**: 2026-01-01  
**Status**: Ready to start Phase 1
