# FR-006: Self-Learning LLM System

> **Status:** Draft  
> **Created:** 2026-02-05  
> **Priority:** High  
> **Type:** Functional Requirement

---

## 📋 Overview

Transform the static LLM explanation system into a self-learning system that:
- Collects user feedback on explanation quality
- Analyzes patterns in successful vs unsuccessful explanations
- Optimizes prompts and parameters iteratively
- Fine-tunes models based on domain-specific data
- Measures improvement through metrics

**Goal:** LLM explanations become progressively better over time based on real user interactions.

---

## 🎯 User Stories

### FR-6.1: Feedback Collection
**Als** Trader  
**möchte ich** bewerten ob eine LLM-Erklärung hilfreich war  
**damit** das System von meinem Feedback lernt

**Akzeptanzkriterien:**
- [x] UI für Daumen-rauf/runter pro Erklärung
- [x] Optional: Detailliertes Feedback (1-5 Stars, Kommentar)
- [x] Feedback wird in DB gespeichert mit Kontext
- [x] Keine Identifikation von User erforderlich (anonym)

---

### FR-6.2: Feedback Analysis
**Als** System  
**möchte ich** Feedback-Patterns analysieren  
**damit** ich erkenne welche Erklärungen funktionieren

**Akzeptanzkriterien:**
- [x] Aggregiere Feedback pro Signal-Type (BUY/SELL/HOLD)
- [x] Aggregiere nach Ticker (welche Stocks funktionieren besser?)
- [x] Erkenne Fehler-Pattern (z.B. "Factor X wird oft kritisiert")
- [x] Dashboard zur Visualisierung der Insights

---

### FR-6.3: Prompt Optimization
**Als** System  
**möchte ich** Prompts automatisch verbessern  
**damit** bessere Erklärungen entstehen

**Akzeptanzkriterien:**
- [x] Generiere A/B-Varianten von bestehenden Prompts
- [x] Teste neue Prompts gegen alte
- [x] Messe Erfolgsquote (positive feedback %)
- [x] Deploy beste Prompt-Version automatisch
- [x] Versionierung aller Prompts tracken

---

### FR-6.4: Fine-Tuning Pipeline
**Als** System  
**möchte ich** optional ein lokales Model fine-tunen  
**damit** ich Domain-spezifisches Wissen habe

**Akzeptanzkriterien:**
- [ ] Sammle hochwertige Explanations (5+ Stars) als Training Data
- [ ] Fine-tune llama-2-7b mit historischen Daten
- [ ] Vergleiche Fine-Tuned vs API-Model
- [ ] Auto-Switch zu besserem Model
- [ ] (Optional) Lokal hosten falls besser/günstiger

---

### FR-6.5: Learning Dashboard
**Als** Analyst  
**möchte ich** sehen wie gut das LLM-Learning funktioniert  
**damit** ich Verbesserungen messe

**Akzeptanzkriterien:**
- [ ] Feedback-Statistiken (gesamt, per Signal, per Ticker)
- [ ] Prompt-Performance-Vergleich (A vs B)
- [ ] Learning Curve (feedback quality über Zeit)
- [ ] Cost-Benefit Analysis (API costs vs quality gain)
- [ ] Alerts wenn negative Trend erkannt wird

---

## 🏗️ Technical Approach

### Architecture Components

```
┌─────────────────────────────────────────────┐
│         User Feedback Collection             │
│  (UI Button: 👍 / 👎 + Optional Details)     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      Feedback Storage & Logging              │
│  (SQLite: explanations + feedback + metrics) │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│    Feedback Analysis Pipeline (Daily)        │
│  - Pattern Recognition                       │
│  - Success Rate per Signal/Ticker            │
│  - Prompt Performance Comparison             │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   ┌─────────────┐   ┌──────────────────┐
   │ Prompt Gen  │   │ Model Fine-Tune  │
   │ (OpenAI)    │   │ (Local)          │
   └────┬────────┘   └────────┬─────────┘
        │                     │
        └──────────┬──────────┘
                   ▼
        ┌──────────────────────┐
        │  A/B Test & Deploy   │
        │  (Champion Model)    │
        └──────────────────────┘
```

### Data Model

**Table: `llm_explanations`**
```sql
id: UUID (PK)
ticker: string
signal: string (BUY/SELL/HOLD)
confidence: float
indicators: JSON
explanation: text
factors: JSON
sentiment: string
prompt_version: string (v1.0, v1.1, etc)
model_used: string (groq, openai, fine-tuned)
generated_at: timestamp
cached: boolean
fallback: boolean
latency_ms: integer
```

**Table: `llm_feedback`**
```sql
id: UUID (PK)
explanation_id: UUID (FK)
rating: integer (1-5, or null for binary)
helpful: boolean (👍/👎)
comment: text (optional)
feedback_type: string (auto/manual)
user_session: UUID (anonymous)
created_at: timestamp
```

**Table: `llm_metrics`**
```sql
id: UUID (PK)
date: date
signal_type: string
prompt_version: string
model_used: string
total_explanations: integer
positive_feedback_pct: float
avg_rating: float
cost_usd: float
latency_ms: float
created_at: timestamp
```

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| LLM Halluzinationen verstärken sich | Users get worse explanations | Guardrails: fact-check gegen Datenquellen |
| Feedback-Bias (nur power-users geben Feedback) | Unrepräsentative Optimierung | Track non-feedback als implicit positive (no complaint = ok) |
| API-Kosten explodieren durch Prompt-Gen | Budget-Überschreitung | Rate-limit prompt generation (max 1x daily) |
| Model drift wenn schlecht fine-tuned | Performance verschlechtert sich | Always A/B test new model vor deployment |
| Cold-start Problem (keine Feedback initial) | System funktioniert nicht | Start mit Template-basierten Prompts (low-cost) |

---

## 📊 Success Metrics

| Metrik | Baseline | Zielwert (3 Monate) |
|--------|----------|------------------|
| Positive Feedback Rate | 60% | 80%+ |
| Avg Explanation Rating | 3.0 Stars | 4.2 Stars |
| Prompt Performance Lift | - | +25% vs v1.0 |
| Cost per Quality Explanation | $0.002-0.005 | $0.002 (same, but better) |
| Model Fine-Tune Lift | - | +15% vs API model |
| Feedback Collection Rate | - | 30%+ of explanations |

---

## 🔗 Dependencies

- Existing LLM Service (llm_service.py)
- Existing Feedback UI Components (ready to build)
- SQLite for feedback storage (existing)
- OpenAI API for prompt generation (optional paid feature)
- vLLM or LocalAI for fine-tuning (optional)

---

## 📝 Notes

### Phase Strategy
1. **Phase 1 (Week 1-2):** Feedback Collection + Analysis
   - Add 👍👎 buttons to UI
   - Store feedback in DB
   - Create basic analytics

2. **Phase 2 (Week 3-4):** Prompt Optimization
   - Analyze feedback patterns
   - Generate prompt variants with OpenAI
   - A/B test automatically

3. **Phase 3 (Month 2):** Fine-Tuning (Optional)
   - Collect training data from high-rated explanations
   - Fine-tune llama-2-7b locally
   - Compare local vs API model

4. **Phase 4 (Month 2-3):** Learning Dashboard
   - Visualize all metrics
   - Real-time feedback streaming
   - Auto-alerts on negative trends

### Implementation Strategy
- Start with **simple feedback (👍👎)** - don't over-engineer
- Phase 1 should take **1-2 weeks max**
- Don't build fine-tuning until feedback system proves valuable
- Use **OpenAI's prompt optimization API** (easy, cheap)
- Keep **champion/challenger pattern** for safety

### Questions to Address
1. Should users be able to provide detailed feedback (comments)?
2. Do we want real-time feedback or batch analysis (daily)?
3. Should we fine-tune a model or stay with API models?
4. How much feedback is "enough" before we start optimizing?
