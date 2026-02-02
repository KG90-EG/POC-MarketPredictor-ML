# FR-003: LLM-Powered Market Analysis - Tasks

> **Status:** Draft  
> **Created:** 2026-02-02  
> **Spec:** [spec.md](./spec.md)  
> **Plan:** [plan.md](./plan.md)

---

## 📊 Estimation Summary

| Phase | Tasks | Manual Effort | With Agent |
|-------|-------|---------------|------------|
| Phase 1 | 5 | ~4h | ~1h |
| Phase 2 | 4 | ~3h | ~45min |
| Phase 3 | 4 | ~3h | ~45min |
| Phase 4 | 4 | ~6h | ~1.5h |
| **Total** | **17** | **~16h** | **~4h** |

---

## Phase 1: Backend Infrastructure

### Task 1.1: Create LLM Service Module
**File:** `src/trading_engine/llm_service.py`

**Requirements:**
- [ ] Create `LLMService` class with async methods
- [ ] Implement Groq API client (default provider)
- [ ] Add environment variable `GROQ_API_KEY`
- [ ] Support for multiple providers (future)

**Acceptance Criteria:**
```python
llm = LLMService()
response = await llm.generate("Explain AAPL stock")
assert response is not None
```

---

### Task 1.2: Implement Explain Endpoint
**File:** `src/trading_engine/server.py`

**Requirements:**
- [ ] Add `GET /api/explain/{ticker}` endpoint
- [ ] Validate ticker format (1-5 uppercase letters)
- [ ] Return JSON with explanation, factors, sentiment
- [ ] Handle errors gracefully

**Response Format:**
```json
{
  "ticker": "AAPL",
  "signal": "BUY",
  "explanation": "Apple shows strong momentum...",
  "factors": ["RSI oversold", "Volume spike", "Earnings beat"],
  "sentiment": "bullish",
  "cached": false,
  "generated_at": "2026-02-02T12:00:00Z"
}
```

---

### Task 1.3: Add Caching Layer
**File:** `src/trading_engine/llm_service.py`

**Requirements:**
- [ ] Cache LLM responses for 1 hour
- [ ] Cache key format: `llm:explain:{ticker}:{date}`
- [ ] Use in-memory cache (dict with TTL)
- [ ] Add `cached: true/false` to response

---

### Task 1.4: Implement Fallback Logic
**File:** `src/trading_engine/llm_service.py`

**Requirements:**
- [ ] Define fallback explanations for BUY/SELL/HOLD
- [ ] Return fallback if LLM call fails
- [ ] Log failures for monitoring
- [ ] Add `fallback: true` to response if used

---

### Task 1.5: Environment Configuration
**Files:** `.env.example`, `docs/TRADER_GUIDE.md`

**Requirements:**
- [ ] Add `GROQ_API_KEY` to `.env.example`
- [ ] Add `LLM_PROVIDER` (groq/openai/anthropic)
- [ ] Add `LLM_CACHE_TTL` (default: 3600)
- [ ] Document setup in TRADER_GUIDE.md

---

## Phase 2: Signal Explanations

### Task 2.1: Create Prompt Templates
**File:** `src/trading_engine/prompts.py`

**Requirements:**
- [ ] Create `EXPLAIN_SIGNAL_PROMPT` template
- [ ] Create `EXPLAIN_REGIME_PROMPT` template
- [ ] Use f-string formatting with clear placeholders
- [ ] Include JSON output instructions

---

### Task 2.2: Integrate with Signal Generation
**File:** `src/trading_engine/scoring.py` or `ranking.py`

**Requirements:**
- [ ] After generating signal, call LLM service
- [ ] Pass ticker, signal, confidence, indicators
- [ ] Make LLM call optional (feature flag)
- [ ] Don't block signal generation if LLM slow

---

### Task 2.3: Extend Ranking Response
**File:** `src/trading_engine/server.py`

**Requirements:**
- [ ] Add `explanation` field to ranking response
- [ ] Make explanations optional (query param)
- [ ] Example: `GET /api/ranking?include_explanations=true`

---

### Task 2.4: Unit Tests for LLM Service
**File:** `tests/test_llm_service.py`

**Requirements:**
- [ ] Test LLM service initialization
- [ ] Test caching behavior
- [ ] Test fallback logic
- [ ] Mock LLM API calls in tests

---

## Phase 3: Frontend Integration

### Task 3.1: Create ExplanationCard Component
**File:** `frontend/src/components/ExplanationCard.jsx`

**Requirements:**
- [ ] Display explanation text
- [ ] Show factor chips/tags
- [ ] Sentiment indicator (bullish/bearish/neutral)
- [ ] "AI Generated" disclaimer

---

### Task 3.2: Add Explanation Tooltip
**Files:** `frontend/src/components/SignalCard.jsx` (or similar)

**Requirements:**
- [ ] Info icon next to signal
- [ ] Click/hover shows explanation
- [ ] Lazy load explanation on demand
- [ ] Loading state while fetching

---

### Task 3.3: API Integration
**File:** `frontend/src/api.js`

**Requirements:**
- [ ] Add `getExplanation(ticker)` function
- [ ] Handle loading/error states
- [ ] Cache responses client-side

---

### Task 3.4: Styling
**File:** `frontend/src/components/ExplanationCard.css`

**Requirements:**
- [ ] Clean, readable typography
- [ ] Factor tags with colors
- [ ] Responsive design
- [ ] Dark mode support

---

## Phase 4: News Sentiment (Future)

### Task 4.1: News API Integration
**File:** `src/trading_engine/news_service.py`

**Requirements:**
- [ ] Integrate NewsAPI or Alpha Vantage News
- [ ] Fetch top 5 headlines per ticker
- [ ] Rate limit handling

---

### Task 4.2: Sentiment Endpoint
**File:** `src/trading_engine/server.py`

**Requirements:**
- [ ] Add `GET /api/sentiment/{ticker}`
- [ ] Return sentiment score, label, headlines
- [ ] Cache for 4 hours

---

### Task 4.3: Frontend Sentiment Badge
**File:** `frontend/src/components/SentimentBadge.jsx`

**Requirements:**
- [ ] Small badge showing sentiment
- [ ] Click expands to show headlines
- [ ] Color coded (green/gray/red)

---

### Task 4.4: Sentiment Integration
**Files:** Multiple frontend components

**Requirements:**
- [ ] Add sentiment badge to stock cards
- [ ] Add sentiment to portfolio view
- [ ] Make sentiment optional (feature flag)

---

## 📝 Notes

- Phase 1+2+3 are MVP scope
- Phase 4 is "nice-to-have" for later
- Start with Groq for cost efficiency
- All LLM features should be optional (graceful degradation)
