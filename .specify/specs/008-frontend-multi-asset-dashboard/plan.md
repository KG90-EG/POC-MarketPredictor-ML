# FR-007: Multi-Asset Trading Dashboard - Implementation Plan

> **Status:** Draft  
> **Created:** 2026-02-06  
> **Spec:** [spec.md](./spec.md)

---

## 🏗️ Architecture Decisions

### AD-1: State Management Approach
**Decision:** Use React Context API with useReducer for global state.

**Rationale:**
- Existing app uses React hooks
- No need for Redux overhead for current scale
- Context provides adequate state sharing
- Easy migration to Redux/Zustand later if needed

**Implementation:**
```jsx
// contexts/AppContext.jsx
const AppContext = createContext();

const initialState = {
  activeTab: 'shares',
  settings: {},
  tutorialStep: 0,
  panels: { signals: true, backtest: true }
};

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_TAB': return { ...state, activeTab: action.payload };
    case 'UPDATE_SETTINGS': return { ...state, settings: { ...state.settings, ...action.payload } };
    case 'NEXT_TUTORIAL_STEP': return { ...state, tutorialStep: state.tutorialStep + 1 };
    case 'TOGGLE_PANEL': return { ...state, panels: { ...state.panels, [action.payload]: !state.panels[action.payload] } };
    default: return state;
  }
}
```

---

### AD-2: Responsive Grid Strategy
**Decision:** CSS Grid with named areas for layout regions.

**Rationale:**
- Native CSS, no library overhead
- Named areas make responsive changes intuitive
- Good browser support (>95%)
- Works with existing Vite/PostCSS setup

**Implementation:**
```css
/* Desktop */
.dashboard {
  display: grid;
  grid-template-areas:
    "header header header"
    "signals assets backtest"
    "footer footer footer";
  grid-template-columns: 280px 1fr 320px;
  grid-template-rows: auto 1fr auto;
}

/* Tablet */
@media (max-width: 1023px) {
  .dashboard {
    grid-template-areas:
      "header header"
      "signals assets"
      "backtest backtest"
      "footer footer";
    grid-template-columns: 1fr 2fr;
  }
}

/* Mobile */
@media (max-width: 767px) {
  .dashboard {
    grid-template-areas:
      "header"
      "signals"
      "assets"
      "backtest"
      "footer";
    grid-template-columns: 1fr;
  }
}
```

---

### AD-3: Tab Navigation Pattern
**Decision:** URL-driven tabs with query parameters.

**Rationale:**
- Deep-linkable (share specific asset type)
- Browser back/forward works
- Bookmarkable
- SEO-friendly if SSR added later

**Implementation:**
```jsx
// URL: /dashboard?tab=digital_assets
const [searchParams, setSearchParams] = useSearchParams();
const activeTab = searchParams.get('tab') || 'shares';

const handleTabChange = (tab) => {
  setSearchParams({ tab });
};
```

---

### AD-4: Tutorial System Design
**Decision:** Floating spotlight overlay with portal rendering.

**Rationale:**
- Non-blocking (user can still interact)
- Portals prevent z-index issues
- Minimal DOM manipulation
- Easy to test

**Implementation:**
```jsx
// Tutorial renders outside main DOM tree
<TutorialProvider>
  <Dashboard />
  {createPortal(
    <TutorialSpotlight />,
    document.getElementById('tutorial-root')
  )}
</TutorialProvider>
```

---

### AD-5: Settings Persistence Strategy
**Decision:** localStorage with JSON serialization.

**Rationale:**
- No backend changes needed
- Instant save/load
- Works offline
- 5MB limit sufficient for settings

**Migration Path:**
1. Phase 1: localStorage only
2. Phase 2: Add optional cloud sync via `/api/user/settings`

**Implementation:**
```jsx
// hooks/useSettings.js
const STORAGE_KEY = 'market-predictor-settings';

export function useSettings() {
  const [settings, setSettings] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : defaultSettings;
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  }, [settings]);

  return [settings, setSettings];
}
```

---

### AD-6: Charts Library Selection
**Decision:** Recharts for data visualization.

**Rationale:**
- Already used in existing codebase (if applicable)
- React-native components
- Good documentation
- Lightweight enough for sparklines
- SSR compatible

**Alternative Considered:**
- Visx: More flexible but steeper learning curve
- Chart.js: Canvas-based, less React-friendly

---

## 📅 Implementation Phases

### Phase 1: Dashboard Layout (Week 1)
**Effort:** ~16 hours

**Tasks:**
- [ ] Create Dashboard grid container
- [ ] Create Panel wrapper component
- [ ] Implement Header with navigation
- [ ] Implement Footer with status
- [ ] Add responsive breakpoints
- [ ] Add collapsible panel logic
- [ ] Test on real devices

**Deliverables:**
- `components/layout/Dashboard.jsx`
- `components/layout/Header.jsx`
- `components/layout/Footer.jsx`
- `components/layout/Panel.jsx`
- `styles/grid.css`

---

### Phase 2: Top Assets with Tabs (Week 2)
**Effort:** ~20 hours

**Tasks:**
- [ ] Create Tabs component (generic)
- [ ] Create TopAssetsPanel with asset tabs
- [ ] Create AssetCard component
- [ ] Create AssetList with virtualization
- [ ] Integrate with unified ranking API
- [ ] Add loading/error states
- [ ] Add keyboard navigation
- [ ] Add swipe gestures (mobile)

**Deliverables:**
- `components/shared/Tabs.jsx`
- `components/assets/TopAssetsPanel.jsx`
- `components/assets/AssetCard.jsx`
- `components/assets/AssetList.jsx`
- `hooks/useAssets.js`

---

### Phase 3: Tutorial System (Week 3)
**Effort:** ~12 hours

**Tasks:**
- [ ] Create TutorialProvider context
- [ ] Create TutorialSpotlight overlay
- [ ] Create TutorialProgress indicator
- [ ] Define 5 tutorial steps
- [ ] Add skip/restart functionality
- [ ] Persist completion state
- [ ] A11y: Focus management

**Deliverables:**
- `components/tutorial/TutorialProvider.jsx`
- `components/tutorial/TutorialSpotlight.jsx`
- `components/tutorial/TutorialProgress.jsx`
- `hooks/useTutorial.js`

---

### Phase 4: Settings Panel (Week 4)
**Effort:** ~16 hours

**Tasks:**
- [ ] Create SettingsModal component
- [ ] Create SettingsSection groupings
- [ ] Create SettingControl for each type
- [ ] Implement all setting categories
- [ ] Add localStorage persistence
- [ ] Add reset to defaults
- [ ] Add export/import JSON

**Deliverables:**
- `components/settings/SettingsModal.jsx`
- `components/settings/SettingsSection.jsx`
- `components/settings/SettingControl.jsx`
- `hooks/useSettings.js`

---

### Phase 5: Polish & Testing (Week 5)
**Effort:** ~12 hours

**Tasks:**
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Performance optimization
- [ ] Cross-browser testing
- [ ] Mobile device testing
- [ ] Unit tests (Vitest)
- [ ] Integration tests
- [ ] Documentation

**Deliverables:**
- Accessibility report
- Test coverage >80%
- Performance benchmark

---

## 📱 Responsive Breakpoints

| Breakpoint | Width | Columns | Panel Behavior |
|------------|-------|---------|----------------|
| Mobile | < 768px | 1 | Stacked, collapsible |
| Tablet | 768px - 1023px | 2 | Backtest spans full width |
| Desktop | 1024px - 1439px | 3 | All visible |
| Large Desktop | ≥ 1440px | 3 | Wider panels |

---

## 🔌 API Integration

**Endpoints Used (from NFR-011):**

```javascript
// Asset Rankings
GET /api/ranking/{asset_type}?limit=50

// Portfolio Validation  
POST /api/portfolio/validate
{ "positions": [...] }

// Backtest
POST /api/backtest/run
GET /api/backtest/{id}

// Settings (future)
GET /api/user/settings
PUT /api/user/settings
```

**Data Fetching:**
```javascript
// hooks/useAssets.js
import { useQuery } from '@tanstack/react-query';

export function useAssetRanking(assetType) {
  return useQuery({
    queryKey: ['ranking', assetType],
    queryFn: () => fetch(`/api/ranking/${assetType}`).then(r => r.json()),
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 5 * 60 * 1000, // 5 minutes
  });
}
```

---

## ♿ Accessibility Checklist

- [ ] Keyboard navigation for all interactive elements
- [ ] Focus visible indicators
- [ ] ARIA labels for icons
- [ ] Screen reader announcements for tab changes
- [ ] Color contrast ≥ 4.5:1
- [ ] Reduced motion preference support
- [ ] Focus trap in modals
- [ ] Skip navigation link

---

## 📊 Performance Budget

| Metric | Target | Measurement |
|--------|--------|-------------|
| First Contentful Paint | < 1.5s | Lighthouse |
| Largest Contentful Paint | < 2.5s | Lighthouse |
| Time to Interactive | < 3.5s | Lighthouse |
| Cumulative Layout Shift | < 0.1 | Lighthouse |
| Tab Switch | < 200ms | Custom metric |
| Settings Save | < 50ms | Custom metric |

---

## 🧪 Testing Strategy

**Unit Tests (Vitest):**
- All hooks
- Utility functions
- Component rendering

**Integration Tests:**
- Tab navigation
- Settings persistence
- Tutorial flow

**E2E Tests (Playwright):**
- Full dashboard flow
- Mobile responsive behavior
- Accessibility checks

---

## 🔗 Dependencies

**New Dependencies:**
```json
{
  "@tanstack/react-query": "^5.0.0",
  "recharts": "^2.12.0"
}
```

**Dev Dependencies:**
```json
{
  "@testing-library/react": "^14.0.0",
  "playwright": "^1.40.0"
}
```

---

## 📝 Open Questions (Resolved)

1. ✅ **State management?** Context API with useReducer
2. ✅ **Charts library?** Recharts
3. ✅ **Settings storage?** localStorage (cloud sync later)
4. ✅ **Tutorial library?** Custom implementation
5. ⏳ **React Query vs SWR?** React Query (more features)
