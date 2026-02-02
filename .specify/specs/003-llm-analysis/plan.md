# FR-003: LLM-Powered Market Analysis - Implementation Plan

> **Status:** Draft  
> **Created:** 2026-02-02  
> **Spec:** [spec.md](./spec.md)

---

## 🏗️ Architecture Decisions

### AD-1: LLM Provider Strategy
**Decision:** Start with Groq (Llama 3.1 70B) for cost-efficiency, optional Claude API for premium features.

**Rationale:**
- Groq offers sub-second response times at ~$0.0027/1K tokens
- Claude API is 10x more expensive but higher quality
- Local Ollama requires GPU hardware, not suitable for all deployments

**Trade-offs:**
- ✅ Low cost, fast responses
- ❌ Quality slightly lower than GPT-4/Claude
- ❌ Rate limits on free tier

---

### AD-2: Prompt Engineering Architecture
**Decision:** Use structured prompts with JSON output format.

**Pattern:**
```python
EXPLAIN_SIGNAL_PROMPT = """
You are a financial analyst. Explain this trading signal:
- Ticker: {ticker}
- Signal: {signal}
- Confidence: {confidence}
- Technical Indicators: {indicators}

Respond in JSON format:
{
  "explanation": "2-3 sentence summary",
  "factors": ["factor1", "factor2", "factor3"],
  "sentiment": "bullish|bearish|neutral"
}
"""
```

**Rationale:**
- JSON output is easier to parse and validate
- Structured prompts reduce hallucinations
- Template variables make prompts reusable

---

### AD-3: Caching Strategy
**Decision:** Cache LLM responses for 1 hour per ticker.

**Rationale:**
- LLM calls are expensive (time + cost)
- Market conditions don't change every second
- 1 hour cache balances freshness with efficiency

**Implementation:**
- Use existing Redis/in-memory cache
- Cache key: `llm:{endpoint}:{ticker}:{date}`

---

### AD-4: Fallback Behavior
**Decision:** Return pre-generated explanations if LLM fails.

**Rationale:**
- LLM APIs can be unreliable (rate limits, outages)
- User experience shouldn't break if LLM is down
- Template-based fallbacks are better than empty responses

**Fallback Example:**
```python
FALLBACK_EXPLANATIONS = {
    "BUY": "Technical indicators suggest upward momentum. Consider position sizing.",
    "SELL": "Technical indicators suggest downward pressure. Risk management advised.",
    "HOLD": "Mixed signals - maintaining current position recommended."
}
```

---

### AD-5: Security & Guardrails
**Decision:** Implement input validation and output sanitization.

**Guardrails:**
1. **Input:** Validate ticker format (1-5 uppercase letters)
2. **Input:** Rate limit LLM calls per user (10/min)
3. **Output:** Check for financial advice disclaimers
4. **Output:** Filter out specific price predictions

---

## 📅 Implementation Phases

### Phase 1: Backend Infrastructure (~4h)
- [ ] Create `src/trading_engine/llm_service.py`
- [ ] Implement Groq API client
- [ ] Add `/api/explain/{ticker}` endpoint
- [ ] Implement caching layer
- [ ] Add fallback logic

### Phase 2: Signal Explanations (~3h)
- [ ] Create prompt templates
- [ ] Integrate with existing signal generation
- [ ] Add explanation to `/api/ranking` response
- [ ] Unit tests for LLM service

### Phase 3: Frontend Integration (~3h)
- [ ] Create `ExplanationCard.jsx` component
- [ ] Add explanation tooltip to signal cards
- [ ] Loading states and error handling
- [ ] Styling for explanation text

### Phase 4: News Sentiment (Future - ~6h)
- [ ] Integrate news API (Alpha Vantage, NewsAPI)
- [ ] Sentiment analysis endpoint
- [ ] Frontend sentiment badge
- [ ] Caching for news data

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM hallucinations | Wrong advice | Medium | Guardrails, human review |
| API rate limits | Service unavailable | Medium | Caching, fallbacks |
| High costs | Budget overrun | Low | Usage monitoring, limits |
| Slow responses | Bad UX | Medium | Streaming, caching |

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Time | < 2s | Prometheus latency |
| Cache Hit Rate | > 80% | Cache metrics |
| User Satisfaction | Positive | Feedback widget |
| API Costs | < $50/month | Provider dashboard |

---

## 🔗 Dependencies

- Groq API Key (or OpenAI/Anthropic)
- `groq` Python package
- Optional: `newsapi-python` for news data

---

## 📝 Open Questions

1. Should explanations be generated on-demand or pre-computed?
2. Do we need multi-language support (DE/EN)?
3. Should we log all LLM interactions for improvement?
