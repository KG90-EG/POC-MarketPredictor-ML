# FR-006: Self-Learning LLM System - Implementation Plan

> **Status:** Draft  
> **Created:** 2026-02-05  
> **Spec:** [spec.md](./spec.md)

---

## 🏗️ Architecture Decisions

### AD-1: Feedback Storage Strategy
**Decision:** SQLite for feedback storage (local), optional cloud backup.

**Rationale:**
- Feedback is valuable proprietary data → keep locally
- SQLite is fast, reliable, zero setup
- Can sync to cloud later if needed
- No external dependencies

**Trade-offs:**
- ❌ Not distributed (single server only)
- ✅ Simple to implement
- ✅ Fast queries for analytics
- ✅ Can export for fine-tuning

---

### AD-2: Feedback Collection Timing
**Decision:** Async, non-blocking feedback collection.

**Pattern:**
```python
# User clicks 👍 → async callback
@app.post("/api/feedback/{explanation_id}")
async def submit_feedback(explanation_id: UUID, rating: int):
    # Fire-and-forget async task
    asyncio.create_task(store_feedback(explanation_id, rating))
    return {"received": True}  # Respond immediately
```

**Rationale:**
- Don't block explanation API
- Feedback is low-priority (async is fine)
- User sees ✓ immediately
- Database writes happen in background

---

### AD-3: Prompt Optimization Method
**Decision:** Use OpenAI's prompt generation to create variants, A/B test automatically.

**Process:**
```
Current Prompt (v1.0)
    ↓ (Feed to OpenAI with meta-prompt)
    ↓ "Generate 3 variants of this prompt that are clearer/more concise"
    ↓
Variants: v1.1, v1.2, v1.3
    ↓ (Route traffic: 25% each new, 25% baseline)
    ↓ (Measure feedback rate & quality for 1 week)
    ↓
Winner: v1.2 (81% positive feedback)
    ↓ (Deploy v1.2 as new baseline)
    ↓
Archive v1.0, v1.1, v1.3
```

**Rationale:**
- OpenAI's prompt-gen is cheap ($0.001-0.01 per variant)
- A/B testing is safe (no breaking changes)
- Automatic winner selection (data-driven)
- Can run weekly/monthly

---

### AD-4: Fine-Tuning Strategy (Phase 3)
**Decision:** Only fine-tune if API model underperforms locally.

**Thresholds:**
- Collect 500+ explanations with 5-star feedback
- Fine-tune llama-2-7b-chat locally
- Compare in staging: local vs API
- Only deploy if local scores 10%+ higher

**Rationale:**
- Fine-tuning is expensive in time/compute
- Don't do it unless proven valuable
- Local model = cost savings on API calls
- Use vLLM for fast inference

---

### AD-5: A/B Testing Framework
**Decision:** Percentage-based traffic splitting, automatic winner selection.

**Components:**
```python
class ABTestConfig:
    prompt_version: str  # "v1.0", "v1.1", etc
    model: str          # "groq", "openai", "fine-tuned"
    traffic_split: dict # {"v1.0": 0.25, "v1.1": 0.25, "v1.2": 0.25, "v1.3": 0.25}
    min_duration_days: int  # min 7 days before deciding
    success_metric: str  # "positive_feedback_pct", "avg_rating"
    winner_threshold: float  # 0.80 (80% confidence)
```

**Rationale:**
- Gradual rollout (25% at a time)
- Statistical significance check before winner
- Automatic champion/challenger rotation
- Easy to rollback if something breaks

---

### AD-6: Learning Dashboard Location
**Decision:** Standalone analytics endpoint at `/api/admin/llm-learning`.

**Rationale:**
- Separate from user-facing APIs
- Can require authentication (admin-only)
- Real-time or batch updates
- No impact on user experience

---

## 📅 Implementation Phases

### Phase 1: Feedback Collection (Week 1-2) ✅
**Effort:** ~16 hours

Components:
- Add feedback table to SQLite schema
- Implement `/api/feedback/{explanation_id}` endpoint
- Add 👍👎 buttons to ExplanationCard.jsx
- Create FeedbackStats.jsx dashboard component
- Write tests for feedback storage

Deliverables:
- Working feedback collection system
- Basic analytics dashboard
- Test coverage > 80%

---

### Phase 2: Prompt Optimization (Week 3-4) ✅
**Effort:** ~20 hours

Components:
- Create prompt variant generation (OpenAI meta-prompt)
- Implement A/B testing framework
- Build variant router (percentage-based traffic split)
- Create analytics for variant comparison
- Auto-deploy winner (scheduled job)

Deliverables:
- Automated prompt optimization pipeline
- Working A/B test framework
- Variant performance dashboard
- Champion/challenger rotation logic

---

### Phase 3: Fine-Tuning Pipeline (Month 2) ⏳
**Effort:** ~30 hours (optional, phase later)

Components:
- Export training data from high-rated explanations
- Create fine-tuning script (llama-2-7b)
- Implement local model serving (vLLM)
- Build comparison tests (local vs API)
- Auto-switch logic based on metrics

Deliverables:
- Local fine-tuned model
- A/B test results (local vs API)
- Cost/quality comparison dashboard

---

### Phase 4: Learning Dashboard (Month 2-3) ⏳
**Effort:** ~15 hours (optional, polish phase)

Components:
- Real-time feedback streaming
- Learning curve visualization (quality over time)
- Cost analysis (API $ vs quality gain)
- Anomaly detection (alert on negative trends)
- Feedback heatmap (which signals/tickers struggle?)

Deliverables:
- Professional analytics dashboard
- Real-time alerts
- Export capabilities (CSV, JSON)

---

## ⚠️ Risks & Mitigations

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Feedback collection creates DB bottleneck | Low | High | Async + connection pooling; test load |
| Prompt variants are worse than baseline | Medium | Medium | A/B test before deploy; guardrails |
| Fine-tuning overfits to feedback noise | High | Medium | Validation set; test on unseen data |
| Users don't provide feedback (cold-start) | High | Low | Implicit positive (no feedback = ok); start with 10% sample |

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| OpenAI costs explode | Low | Medium | Rate-limit variant generation (1x/week max) |
| A/B test runs too long (slow decision) | Medium | Low | Set 7-day minimum, then auto-decide |
| Feedback contains sensitive data | Medium | High | Hash user IDs; audit logging; GDPR compliance |

---

## 🎯 Success Criteria

### Phase 1 Success
- ✅ Feedback collection system is live
- ✅ 30%+ of explanations get feedback
- ✅ Dashboard shows basic stats (feedback rate, avg rating)
- ✅ All tests passing

### Phase 2 Success
- ✅ A/B test framework is working
- ✅ Prompt variants show 10%+ variation in feedback rate
- ✅ Auto-winner selection identifies clear winner
- ✅ Positive feedback rate improves from 60% → 70%+

### Phase 3 Success (if pursued)
- ✅ Fine-tuned model outperforms API model
- ✅ Local model is cheaper or same cost as API
- ✅ Quality metrics show 10%+ improvement

### Phase 4 Success (if pursued)
- ✅ Dashboard shows clear learning curve
- ✅ Cost/quality trade-offs are visualized
- ✅ Alerts trigger on negative trends

---

## 📊 Key Metrics to Track

```python
# Daily metrics
- Total explanations generated
- Feedback collection rate (%)
- Positive feedback rate (%)
- Average rating (1-5 stars)
- Cost per explanation (USD)
- Avg latency (ms)

# Per-signal metrics
- BUY signal: feedback rate, positive rate, avg rating
- SELL signal: feedback rate, positive rate, avg rating
- HOLD signal: feedback rate, positive rate, avg rating

# Per-ticker metrics
- Top 10 tickers: which have highest feedback scores?
- Bottom 10 tickers: which struggle?

# A/B test metrics
- Variant A: positive_feedback_pct, avg_rating, cost
- Variant B: positive_feedback_pct, avg_rating, cost
- Variant C: ...
- Confidence level (statistical significance)
- Winner confidence threshold (80%+)
```

---

## 🔗 Dependencies

**Required:**
- Existing LLM Service (llm_service.py) ✅
- SQLite (already in use) ✅
- Async framework (FastAPI) ✅
- Existing frontend components ✅

**Optional (Phase 2+):**
- OpenAI API key (for prompt generation)
- vLLM (for local model serving, Phase 3)
- scikit-learn (for statistical tests)

---

## 📝 Open Questions

1. **Feedback Format:** Binary (👍👎) or 1-5 stars or both?
   - Recommendation: Start with 👍👎 (simpler), add stars later

2. **Feedback Timing:** Immediate after explanation or later?
   - Recommendation: Immediate (while context fresh)

3. **User Tracking:** Anonymous or track session ID?
   - Recommendation: Anonymous session IDs (privacy-first)

4. **Feedback Text:** Allow optional comments?
   - Recommendation: Yes, but optional (helps debug)

5. **Fine-Tuning Hardware:** Where to run? (laptop, cloud GPU, AWS)?
   - Recommendation: Phase 3 problem; decide later

6. **A/B Test Duration:** 7 days minimum? More?
   - Recommendation: 7 days is safe; can adjust based on traffic

7. **Variant Generation Frequency:** Weekly? Monthly?
   - Recommendation: Weekly (fast iteration, low cost)
