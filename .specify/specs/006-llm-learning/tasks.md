# FR-006: Self-Learning LLM System - Tasks

> **Status:** Draft  
> **Created:** 2026-02-05  
> **Spec:** [spec.md](./spec.md)  
> **Plan:** [plan.md](./plan.md)

---

## 📊 Estimation Summary

| Phase | Story Points | Effort | Timeline |
|-------|-------------|--------|----------|
| Phase 1: Feedback Collection | 13 | ~16h | Week 1-2 |
| Phase 2: Prompt Optimization | 21 | ~20h | Week 3-4 |
| Phase 3: Fine-Tuning (Optional) | 25 | ~30h | Month 2 |
| Phase 4: Learning Dashboard (Optional) | 13 | ~15h | Month 2-3 |
| **TOTAL (Phase 1-2 only)** | **34** | **~36h** | **~4 weeks** |

---

## Phase 1: Feedback Collection ✅

### Task 1.1: Create Feedback Schema
**File:** `src/trading_engine/database.py` (or new `src/trading_engine/feedback_db.py`)

**Requirements:**
- [ ] Add `llm_explanations` table schema
- [ ] Add `llm_feedback` table schema
- [ ] Add `llm_metrics` table schema
- [ ] Add migrations (if using Alembic)
- [ ] Create indexes on `explanation_id`, `created_at`
- [ ] Write schema validation tests

**Implementation Notes:**
- Use SQLite3 (existing)
- Add foreign key constraints
- Add default timestamps
- Create utility functions for common queries

**Acceptance Criteria:**
- ✅ Schema is properly normalized
- ✅ Migrations are tested
- ✅ Can create/query all 3 tables

---

### Task 1.2: Extend LLM Service to Log Explanations
**File:** `src/trading_engine/llm_service.py`

**Requirements:**
- [ ] Add `log_explanation()` method
- [ ] Store every explanation (success or fallback)
- [ ] Include metadata: prompt_version, model, latency, cached
- [ ] Make logging async (non-blocking)
- [ ] Return explanation_id to caller

**Implementation Notes:**
```python
async def explain_signal(self, ...) -> Dict:
    # existing code...
    explanation_id = await self.log_explanation(
        ticker=ticker,
        signal=signal,
        explanation=result,
        prompt_version="v1.0",
        model=self.provider,
        latency_ms=elapsed_ms
    )
    result["explanation_id"] = explanation_id
    return result
```

**Acceptance Criteria:**
- ✅ All explanations are logged
- ✅ Logging doesn't block API responses
- ✅ explanation_id is returned in response

---

### Task 1.3: Add Feedback Endpoint
**File:** `src/trading_engine/server.py`

**Requirements:**
- [ ] Create `POST /api/feedback/{explanation_id}` endpoint
- [ ] Accept payload: `{ "helpful": bool, "rating": int (1-5, optional), "comment": str (optional) }`
- [ ] Validate explanation_id exists
- [ ] Rate-limit (max 10 feedback per user per hour)
- [ ] Return 200 OK immediately (async storage)
- [ ] Return 404 if explanation not found

**Implementation Notes:**
```python
@app.post("/api/feedback/{explanation_id}")
async def submit_feedback(
    explanation_id: UUID,
    feedback: FeedbackRequest  # { helpful, rating?, comment? }
):
    # Validate exists
    if not await db.explanation_exists(explanation_id):
        raise HTTPException(status_code=404)
    
    # Async task (fire-and-forget)
    asyncio.create_task(db.store_feedback(explanation_id, feedback))
    
    return {"received": True}
```

**Acceptance Criteria:**
- ✅ Endpoint is documented in OpenAPI
- ✅ Feedback is stored async
- ✅ Rate limiting works
- ✅ 404 on missing explanation

---

### Task 1.4: Update ExplanationCard Component
**File:** `frontend/src/components/ExplanationCard.jsx`

**Requirements:**
- [ ] Add 👍 👎 buttons below explanation text
- [ ] Add optional rating stars (1-5, collapsible)
- [ ] Add optional comment field (collapsible)
- [ ] Handle loading state while submitting
- [ ] Show success message ("Thanks for feedback!")
- [ ] Don't block explanation display

**Implementation Notes:**
```jsx
<ExplanationCard explanation={explanation}>
  <div className="feedback-section">
    <p className="feedback-prompt">Was this helpful?</p>
    <button onClick={() => submitFeedback(true)}>👍 Yes</button>
    <button onClick={() => submitFeedback(false)}>👎 No</button>
    
    <Collapsible trigger="More feedback...">
      <StarRating onChange={(rating) => setRating(rating)} />
      <textarea placeholder="Optional comment..." />
      <button onClick={submitDetailedFeedback}>Submit</button>
    </Collapsible>
  </div>
</ExplanationCard>
```

**Acceptance Criteria:**
- ✅ Buttons are visible and responsive
- ✅ Feedback submits without page reload
- ✅ Loading state is shown
- ✅ Success message appears

---

### Task 1.5: Create Feedback Analytics Dashboard
**File:** `frontend/src/pages/LLMAnalytics.jsx`

**Requirements:**
- [ ] Display total feedback count
- [ ] Show positive/negative feedback rate (%)
- [ ] Show average rating (1-5)
- [ ] Breakdown by signal type (BUY/SELL/HOLD)
- [ ] Breakdown by ticker (top 10)
- [ ] Time-series chart (feedback quality over last 30 days)
- [ ] Refresh data every 5 minutes

**Implementation Notes:**
- Fetch from `GET /api/admin/llm-analytics` endpoint
- Use Chart.js or Recharts for visualizations
- Mobile-responsive design
- Dark mode support

**Acceptance Criteria:**
- ✅ Dashboard loads quickly
- ✅ Data updates automatically
- ✅ All metrics are correct
- ✅ Mobile responsive

---

### Task 1.6: Implement Analytics Endpoint
**File:** `src/trading_engine/server.py`

**Requirements:**
- [ ] Create `GET /api/admin/llm-analytics` endpoint
- [ ] Return: total feedback, positive %, avg rating
- [ ] Include breakdowns by signal, ticker
- [ ] Include time-series (last 30 days)
- [ ] Cache results (5 min TTL)
- [ ] Require admin authentication (basic for now)

**Implementation Notes:**
```python
@app.get("/api/admin/llm-analytics")
async def get_llm_analytics(
    days: int = Query(30, ge=1, le=90),
    auth: str = Header(None)
):
    # Check auth (basic token)
    if not verify_admin_token(auth):
        raise HTTPException(status_code=401)
    
    # Fetch from cache or DB
    stats = await cache.get("llm-analytics")
    if not stats:
        stats = await db.get_llm_analytics(days)
        await cache.set("llm-analytics", stats, ttl=300)
    
    return stats
```

**Acceptance Criteria:**
- ✅ Endpoint returns correct aggregations
- ✅ Caching works
- ✅ Admin auth required
- ✅ Handles edge cases (no data, etc)

---

### Task 1.7: Unit & Integration Tests
**File:** `tests/test_llm_feedback.py`

**Requirements:**
- [ ] Test feedback storage
- [ ] Test analytics calculations
- [ ] Test rate limiting
- [ ] Test explanation logging
- [ ] Integration test: explain + feedback flow
- [ ] Mock database calls

**Implementation Notes:**
```python
@pytest.mark.asyncio
async def test_feedback_flow():
    # 1. Generate explanation
    explanation = await llm.explain_signal("AAPL", "BUY", 0.85)
    exp_id = explanation["explanation_id"]
    
    # 2. Submit feedback
    result = await client.post(
        f"/api/feedback/{exp_id}",
        json={"helpful": True, "rating": 5}
    )
    assert result.status_code == 200
    
    # 3. Check analytics updated
    await asyncio.sleep(0.1)  # wait for async write
    analytics = await db.get_llm_analytics(1)
    assert analytics["total_feedback"] == 1
```

**Acceptance Criteria:**
- ✅ Test coverage > 80%
- ✅ All tests pass
- ✅ Edge cases covered

---

## Phase 2: Prompt Optimization ✅

### Task 2.1: Create Prompt Variant Generator
**File:** `src/trading_engine/prompt_generator.py` (new)

**Requirements:**
- [ ] Create `PromptVariantGenerator` class
- [ ] Use OpenAI to generate variants (meta-prompt)
- [ ] Generate 3 variants per base prompt
- [ ] Store variants in DB (with version numbers)
- [ ] Include guardrails (max tokens, safety checks)

**Implementation Notes:**
```python
class PromptVariantGenerator:
    def __init__(self, openai_client):
        self.client = openai_client
    
    async def generate_variants(
        self,
        base_prompt: str,
        signal_type: str,
        count: int = 3
    ) -> List[str]:
        """Generate prompt variants using meta-prompt"""
        meta_prompt = f"""
        You are a prompt optimization expert for financial analysis.
        
        Original prompt for {signal_type} signals:
        {base_prompt}
        
        Generate {count} improved versions that are:
        1. Clearer and more concise
        2. More likely to produce accurate JSON
        3. Better at avoiding hallucinations
        
        Return JSON: {{"variants": ["variant1", "variant2", "variant3"]}}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": meta_prompt}],
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)["variants"]
```

**Acceptance Criteria:**
- ✅ Generates valid prompt variants
- ✅ Variants are stored in DB
- ✅ Cost is tracked per variant generation
- ✅ Safety guardrails prevent toxic prompts

---

### Task 2.2: Implement A/B Testing Framework
**File:** `src/trading_engine/ab_test.py` (new)

**Requirements:**
- [ ] Create `ABTestManager` class
- [ ] Store active test config in DB
- [ ] Implement percentage-based traffic splitting
- [ ] Track which variant served for each explanation
- [ ] Measure performance metrics per variant
- [ ] Auto-select winner after min_duration

**Implementation Notes:**
```python
class ABTestManager:
    async def get_variant(self, signal_type: str) -> str:
        """Get prompt variant for this request"""
        config = await db.get_ab_test_config(signal_type)
        if not config:
            return "v1.0"  # baseline
        
        # Weighted random selection
        variants = list(config.traffic_split.keys())
        weights = list(config.traffic_split.values())
        return random.choices(variants, weights=weights, k=1)[0]
    
    async def select_winner(self) -> Optional[str]:
        """Run statistical test to select winner"""
        config = await db.get_ab_test_config()
        metrics = await db.get_variant_metrics(
            config.signal_type,
            days=config.min_duration_days
        )
        
        # Chi-square test for statistical significance
        winner = self._statistical_test(metrics)
        if winner and winner != config.champion:
            await db.promote_variant(winner)
            return winner
        
        return None
```

**Acceptance Criteria:**
- ✅ Traffic is split according to config
- ✅ Winner is selected based on metrics
- ✅ Winner is promoted to production
- ✅ Old variants are archived

---

### Task 2.3: Update LLM Service for Variants
**File:** `src/trading_engine/llm_service.py` (extend)

**Requirements:**
- [ ] Add `variant_version` parameter to explain methods
- [ ] Select variant automatically if A/B test active
- [ ] Log which variant was used per explanation
- [ ] Support fallback to baseline if variant fails
- [ ] Track variant performance in metrics

**Implementation Notes:**
- Minimal changes to existing code
- A/B test variant selection is transparent to caller
- Fallback is automatic

**Acceptance Criteria:**
- ✅ Variants are selected and logged
- ✅ Fallback works correctly
- ✅ No breaking changes to API

---

### Task 2.4: Create Variant Performance Dashboard
**File:** `frontend/src/pages/PromptABTest.jsx`

**Requirements:**
- [ ] Display active A/B test config
- [ ] Show metrics per variant:
  - Positive feedback rate (%)
  - Average rating
  - Cost (USD)
  - Sample size (n)
- [ ] Show statistical significance (confidence level)
- [ ] Show winner candidate (if any)
- [ ] Allow manual variant promotion
- [ ] History of past A/B tests

**Implementation Notes:**
- Fetch from `/api/admin/llm-ab-tests` endpoint
- Update every 5 minutes
- Show confidence level with visual indicator

**Acceptance Criteria:**
- ✅ All variant metrics are visible
- ✅ Winner selection logic is clear
- ✅ Manual override is possible

---

### Task 2.5: Scheduled Variant Generation Job
**File:** `src/trading_engine/scheduled_jobs.py` (new or extend)

**Requirements:**
- [ ] Create scheduled job (runs weekly, e.g., Monday 2am UTC)
- [ ] Generates new prompt variants (if enabled)
- [ ] Analyzes feedback from previous variants
- [ ] Selects winner if ready
- [ ] Sets up new A/B test
- [ ] Sends alert email on new test

**Implementation Notes:**
```python
@scheduled_task(name="generate_prompt_variants", schedule="0 2 * * 1")  # Weekly Monday 2am
async def generate_new_variants():
    for signal_type in ["BUY", "SELL", "HOLD"]:
        # Check if previous test is complete
        winner = await ab_test.select_winner(signal_type)
        
        if winner:
            logger.info(f"Promoted {winner} for {signal_type}")
        
        # Generate new variants
        base_prompt = await db.get_prompt(signal_type, "latest")
        new_variants = await variant_gen.generate_variants(
            base_prompt, signal_type, count=3
        )
        
        # Start new A/B test
        await db.create_ab_test(
            signal_type=signal_type,
            variants=new_variants,
            champion=winner or base_prompt,
            traffic_split={
                winner or base_prompt: 0.25,
                new_variants[0]: 0.25,
                new_variants[1]: 0.25,
                new_variants[2]: 0.25
            },
            min_duration_days=7
        )
        
        # Send alert
        await send_email(
            "admin@example.com",
            "New Prompt A/B Test Started",
            f"Testing 3 new variants for {signal_type} signals"
        )
```

**Acceptance Criteria:**
- ✅ Job runs on schedule
- ✅ Variants are generated and tested
- ✅ Winners are promoted
- ✅ Alerts are sent

---

### Task 2.6: Statistical Testing Utilities
**File:** `src/trading_engine/stats_utils.py` (new)

**Requirements:**
- [ ] Implement chi-square test for variant comparison
- [ ] Calculate confidence intervals (95%)
- [ ] Compute sample size requirements
- [ ] Generate summary statistics
- [ ] Export results for reporting

**Implementation Notes:**
```python
def compare_variants(metrics: Dict[str, List[float]]) -> Dict:
    """
    Compare multiple variants using chi-square test
    Returns: {winner, confidence, p_value, effect_size}
    """
    # Extract success/failure for each variant
    # (positive feedback = success)
    
    # Chi-square test
    chi2, p_value = chi2_contingency(contingency_table)
    
    # Effect size (Cramér's V)
    effect_size = cramers_v(chi2, n, k)
    
    # Determine winner (p < 0.05, not by chance)
    if p_value < 0.05 and effect_size > 0.1:
        winner = variant_with_highest_rate
        confidence = 1 - p_value
    else:
        winner = None
        confidence = 0
    
    return {
        "winner": winner,
        "confidence": confidence,
        "p_value": p_value,
        "effect_size": effect_size
    }
```

**Acceptance Criteria:**
- ✅ Statistical tests are correct
- ✅ Results match manual calculations
- ✅ Edge cases handled (low sample size, etc)

---

### Task 2.7: Unit & Integration Tests (Phase 2)
**File:** `tests/test_ab_testing.py` (new)

**Requirements:**
- [ ] Test variant selection (traffic split)
- [ ] Test winner selection (statistical test)
- [ ] Test promotion logic
- [ ] Test fallback if variant fails
- [ ] Integration test: full A/B test flow
- [ ] Test scheduled job

**Acceptance Criteria:**
- ✅ Test coverage > 80%
- ✅ All tests pass
- ✅ Edge cases covered (low traffic, tie, etc)

---

## Phase 3: Fine-Tuning Pipeline ⏳
### (Deferred - implement after Phase 1-2 are validated)

---

## Phase 4: Learning Dashboard ⏳
### (Deferred - implement after Phase 1-2 are validated)

---

## 📝 Files Created/Modified

### Phase 1 Deliverables
1. `src/trading_engine/feedback_db.py` - Feedback database schema
2. `src/trading_engine/llm_service.py` - Extended with logging
3. `src/trading_engine/server.py` - Feedback endpoint + analytics
4. `frontend/src/components/ExplanationCard.jsx` - Feedback buttons
5. `frontend/src/pages/LLMAnalytics.jsx` - Analytics dashboard
6. `tests/test_llm_feedback.py` - Feedback tests

### Phase 2 Deliverables
7. `src/trading_engine/prompt_generator.py` - Variant generation
8. `src/trading_engine/ab_test.py` - A/B testing framework
9. `src/trading_engine/stats_utils.py` - Statistical tests
10. `src/trading_engine/scheduled_jobs.py` - Scheduled tasks
11. `frontend/src/pages/PromptABTest.jsx` - A/B test dashboard
12. `tests/test_ab_testing.py` - A/B testing tests

### Phase 3 Deliverables (later)
13. `src/training/fine_tune.py` - Fine-tuning pipeline
14. `src/training/fine_tune_requirements.txt` - Dependencies

### Phase 4 Deliverables (later)
15. `frontend/src/pages/LLMLearningDashboard.jsx` - Full dashboard

---

## 📊 Test Results (Template)

### Phase 1 Tests
```
tests/test_llm_feedback.py::test_feedback_storage PASSED
tests/test_llm_feedback.py::test_analytics_calculation PASSED
tests/test_llm_feedback.py::test_rate_limiting PASSED
tests/test_llm_feedback.py::test_explanation_logging PASSED
tests/test_llm_feedback.py::test_feedback_flow PASSED

Coverage: 85%
```

### Phase 2 Tests (TBD)
```
tests/test_ab_testing.py::test_variant_selection PENDING
tests/test_ab_testing.py::test_winner_selection PENDING
tests/test_ab_testing.py::test_promotion_logic PENDING
tests/test_ab_testing.py::test_scheduled_job PENDING

Coverage: TBD
```

---

## 🔗 Next Steps

1. **Approve Spec** - Review FR-006 spec with team
2. **Start Phase 1** - Begin with feedback collection
3. **Monitor Progress** - Daily standup on implementation
4. **Validate Early** - Get user feedback on feedback system
5. **Plan Phase 2** - After Phase 1 is live and stable

---

## 📌 Success Definition

**Phase 1 is complete when:**
- ✅ Users can rate explanations (👍👎)
- ✅ Analytics dashboard shows feedback metrics
- ✅ Feedback collection rate is 20%+
- ✅ Positive feedback rate is 60%+
- ✅ All tests passing, no errors in production

**Phase 2 is complete when:**
- ✅ A/B test framework is live
- ✅ Prompt variants are generated weekly
- ✅ Winner selection is automatic and correct
- ✅ Positive feedback rate improves to 70%+
- ✅ No additional API costs (prompt gen is within budget)
