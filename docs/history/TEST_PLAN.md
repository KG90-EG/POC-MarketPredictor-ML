# 🧪 Full Application & Regression Test Plan

**Date**: 2026-01-01  
**Tester**: AI Assistant  
**Application**: POC Market Predictor  
**Version**: Phase 3 Complete (UX + Accessibility + Performance)

---

## 📋 Test Categories

### 1. Phase 1 Regression Tests (Foundation)

### 2. Phase 2 Regression Tests (Enhancement)

### 3. Phase 3 New Features Tests

### 4. Cross-Browser & Device Tests

### 5. Performance & Accessibility Tests

---

## 1️⃣ Phase 1 Regression Tests - Foundation

### 1.1 Headlines & Copy ✅

- [ ] Page title is user-friendly (not "POC Trading Overview")
- [ ] Subtitle is benefit-focused
- [ ] Section titles are jargon-free
- [ ] Help text is present in all major sections

### 1.2 Portfolio Hierarchy ✅

- [ ] "Buy Opportunities" is visually primary CTA
- [ ] Navigation buttons have clear hierarchy
- [ ] Icons are consistent across all buttons
- [ ] First-time user hint is visible (or onboarding shows)

### 1.3 Empty States & Feedback ✅

- [ ] Empty state shows for stock rankings (no results)
- [ ] Empty state shows for crypto portfolio (no results)
- [ ] Empty state shows for watchlist (empty)
- [ ] Toast notifications appear for actions (add/remove)
- [ ] Error messages are user-friendly

**Test Steps**:

1. Load app with no data
2. Verify empty states in all sections
3. Add item to watchlist → Check for success toast
4. Remove item → Check for toast
5. Trigger error → Check error message clarity

### 1.4 Loading States ✅

- [ ] Skeleton screens show instead of spinners
- [ ] Loading text explains what's happening
- [ ] Progress indicators are visible
- [ ] Skeleton animation is smooth

**Test Steps**:

1. Refresh page
2. Observe skeleton loaders in stock ranking
3. Check loading text appears
4. Verify smooth transitions

### 1.5 Mobile Navigation ✅

- [ ] Navigation is responsive on mobile (<768px)
- [ ] Touch targets are at least 44x44px
- [ ] No horizontal scrolling
- [ ] Buttons stack vertically on small screens

**Test Steps**:

1. Resize browser to 375px width (iPhone SE)
2. Check all buttons are tappable
3. Scroll through all sections
4. Verify no content overflow

---

## 2️⃣ Phase 2 Regression Tests - Enhancement

### 2.1 Stock Table Filters & Sorting ✅

- [ ] FilterBar component renders correctly
- [ ] Search filters stocks by ticker/name
- [ ] Sort dropdown works (Price, Change, Volume, etc.)
- [ ] Country filter shows options and filters
- [ ] Sector filter works correctly
- [ ] Market cap filter ranges work
- [ ] Reset button clears all filters
- [ ] Filter summary shows count (e.g., "Showing 15 of 50")

**Test Steps**:

1. Go to Stock Rankings view
2. Type in search: "AAPL"
3. Select sort: "Price (High to Low)"
4. Filter by country: "United States"
5. Filter by sector: "Technology"
6. Click Reset → All filters cleared

### 2.2 Price Charts in Detail Views ✅

- [ ] PriceChart renders in CompanyDetailSidebar
- [ ] PriceChart renders in CryptoDetailSidebar
- [ ] Chart shows line with gradient fill
- [ ] Period buttons work (1M, 3M, 6M)
- [ ] Chart is responsive
- [ ] Current price and change % displayed
- [ ] Tooltips show on hover (if implemented)
- [ ] ARIA labels present for accessibility

**Test Steps**:

1. Click on any stock in rankings
2. Verify price chart appears in sidebar
3. Click period buttons (1M → 3M → 6M)
4. Check chart updates
5. Verify price summary shows change
6. Repeat for crypto

### 2.3 Autocomplete Search ✅

- [ ] AutocompleteSearch replaces basic input
- [ ] Typing shows dropdown suggestions
- [ ] Suggestions include ticker + name
- [ ] Keyboard navigation works (↑↓ arrows)
- [ ] Enter selects suggestion
- [ ] Escape closes dropdown
- [ ] Clicking suggestion works
- [ ] Empty state shows if no matches

**Test Steps**:

1. Focus search input
2. Type: "APP"
3. Verify dropdown appears with suggestions
4. Use ↓ arrow to navigate
5. Press Enter to select
6. Verify selection works

### 2.4 Watchlist Price Alerts ✅

- [ ] PriceAlert component in WatchlistManager
- [ ] Can set alert above/below current price
- [ ] Alerts save to localStorage
- [ ] Browser notification triggers (if enabled)
- [ ] Alert status shows (active/triggered)
- [ ] Can delete alerts
- [ ] Alerts persist on page reload

**Test Steps**:

1. Add stock to watchlist
2. Click "Set Price Alert"
3. Enter target price above current
4. Save alert
5. Verify alert appears in list
6. Reload page → Alert still there
7. Delete alert

### 2.5 News Integration ✅

- [ ] NewsPanel shows in detail sidebars
- [ ] News items have sentiment badges (Positive/Negative/Neutral)
- [ ] News is collapsible
- [ ] Time-ago format displays correctly
- [ ] News items are scrollable
- [ ] Mock data displays (or API if connected)

**Test Steps**:

1. Open company detail sidebar
2. Scroll to News section
3. Verify news items display
4. Check sentiment colors
5. Expand/collapse panel
6. Verify scroll if many items

### 2.6 Help Tooltips & Documentation ✅

- [ ] InfoCard shows in market selector section
- [ ] InfoCard shows in crypto section
- [ ] InfoCard shows in watchlist section
- [ ] InfoCard shows in search section
- [ ] InfoCards are dismissible
- [ ] Color coding works (info/tip/warning/success)
- [ ] Content is helpful and clear

**Test Steps**:

1. Navigate to each section
2. Find InfoCard components
3. Read content for clarity
4. Click dismiss (X) button
5. Verify card disappears

---

## 3️⃣ Phase 3 New Features Tests

### 3.1 Onboarding Flow ✅

- [ ] Onboarding shows on first visit
- [ ] 5 steps display correctly
- [ ] Progress dots are clickable
- [ ] Back/Next buttons work
- [ ] Skip button works
- [ ] localStorage persists completion
- [ ] Doesn't show on subsequent visits
- [ ] Reset button works in dev mode
- [ ] Mobile: Bottom sheet layout
- [ ] Animations are smooth

**Test Steps**:

1. Clear localStorage: `localStorage.removeItem('onboarding_completed')`
2. Reload page
3. Verify onboarding modal appears
4. Click through all 5 steps
5. Click "Start Exploring"
6. Reload page → Onboarding doesn't show
7. Click "Reset Tutorial" button (dev only)
8. Verify onboarding reappears

### 3.2 Accessibility Features ✅

- [ ] All interactive elements keyboard accessible
- [ ] Tab navigation works logically
- [ ] Focus indicators visible (3px outline + glow)
- [ ] Skip to main content link works
- [ ] Toast notifications have aria-live
- [ ] Charts have descriptive aria-labels
- [ ] All buttons have aria-labels
- [ ] Keyboard shortcuts overlay works (press ?)
- [ ] ConfirmDialog has focus trap
- [ ] Reduced motion respected
- [ ] High contrast mode works

**Test Steps**:

1. Use only keyboard (no mouse)
2. Press Tab repeatedly → All elements focusable
3. Verify visible focus rings
4. Press ? → Keyboard shortcuts overlay appears
5. Test all shortcuts listed
6. Add to watchlist → Check for confirmation
7. Screen reader test (if available)

### 3.3 Performance Optimizations ✅

- [ ] Initial page load < 2 seconds
- [ ] No unnecessary re-renders visible
- [ ] Lazy loading works for SimulationDashboard
- [ ] React Query caches data (no refetch on mount)
- [ ] Filters update smoothly (no lag)
- [ ] Charts render quickly
- [ ] Bundle size reduced (check Network tab)
- [ ] Code splitting evident (multiple chunks)

**Test Steps**:

1. Open DevTools → Network tab
2. Hard reload (Cmd+Shift+R)
3. Check main bundle size < 300KB
4. Verify multiple chunks loaded
5. Go to Simulation view → Check lazy load
6. Use React DevTools Profiler
7. Filter stocks → Check re-render count
8. Check React Query cache in DevTools

---

## 4️⃣ Cross-Browser & Device Tests

### Browser Compatibility

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Device Tests

- [ ] Desktop (1920x1080)
- [ ] Laptop (1440x900)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667 - iPhone SE)
- [ ] Mobile (414x896 - iPhone 11 Pro)

### Responsive Breakpoints

- [ ] 1024px+ : Full desktop layout
- [ ] 768px-1024px : Tablet layout
- [ ] 480px-768px : Large mobile
- [ ] <480px : Small mobile

**Test Steps**:

1. Open DevTools → Device Toolbar
2. Test each device preset
3. Check layout integrity
4. Verify touch targets
5. Test in actual browsers

---

## 5️⃣ Performance & Accessibility Audits

### Lighthouse Audit

- [ ] Performance score > 90
- [ ] Accessibility score > 95
- [ ] Best Practices score > 90
- [ ] SEO score > 80

**Test Steps**:

1. Open DevTools → Lighthouse
2. Run audit (Desktop + Mobile)
3. Review recommendations
4. Fix critical issues

### WAVE Accessibility

- [ ] No errors
- [ ] No contrast errors
- [ ] All ARIA valid
- [ ] No alerts (or minimal)

**Test Steps**:

1. Install WAVE extension
2. Run on each page view
3. Check for errors
4. Fix flagged issues

### axe DevTools

- [ ] No violations
- [ ] All critical issues resolved
- [ ] No serious issues
- [ ] Best practices followed

**Test Steps**:

1. Install axe DevTools
2. Run scan
3. Review violations
4. Address issues

---

## 🐛 Bug Tracking

### Critical Bugs (Blocker)

- None found

### High Priority Bugs

- None found

### Medium Priority Bugs

- None found

### Low Priority / Enhancement Ideas

- None found

---

## ✅ Test Results Summary

**Total Tests**: 100+  
**Passed**: TBD  
**Failed**: TBD  
**Blocked**: TBD  
**Not Tested**: TBD

### Phase 1 Results

- **Headlines & Copy**: ⏳ Testing
- **Portfolio Hierarchy**: ⏳ Testing
- **Empty States**: ⏳ Testing
- **Loading States**: ⏳ Testing
- **Mobile Navigation**: ⏳ Testing

### Phase 2 Results

- **Filters & Sorting**: ⏳ Testing
- **Price Charts**: ⏳ Testing
- **Autocomplete**: ⏳ Testing
- **Price Alerts**: ⏳ Testing
- **News Panel**: ⏳ Testing
- **Help Cards**: ⏳ Testing

### Phase 3 Results

- **Onboarding**: ⏳ Testing
- **Accessibility**: ⏳ Testing
- **Performance**: ⏳ Testing

---

## 🚀 Next Steps

1. Execute all test cases manually
2. Document results and screenshots
3. Fix any discovered bugs
4. Re-run failed tests
5. Generate final test report
6. Deploy to production (if all pass)

---

**Last Updated**: 2026-01-01  
**Status**: Ready to Test
