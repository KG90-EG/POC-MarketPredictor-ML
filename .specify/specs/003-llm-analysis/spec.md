# FR-003: LLM-Powered Market Analysis

> **Status:** ✅ Completed  
> **Created:** 2026-02-02  
> **Completed:** 2026-02-03  
> **Author:** Kevin Garcia  
> **Priority:** Medium  
> **Type:** Functional Requirement

---

## 📋 Overview

Integration von Large Language Models (LLM) für intelligente Marktanalyse, Sentiment-Erkennung und natürlichsprachliche Erklärungen von Trading-Signalen.

---

## 🎯 User Stories

### FR-3.1: AI-Erklärungen für Trading-Signale ✅
**Als** Trader  
**möchte ich** verstehen WARUM die AI BUY/SELL empfiehlt  
**damit** ich fundierte Entscheidungen treffen kann

**Akzeptanzkriterien:**
- [x] Jedes Signal hat eine menschenlesbare Erklärung
- [x] Erklärung nennt 3-5 Hauptfaktoren
- [x] Erklärung ist in 2-3 Sätzen zusammengefasst
- [x] Keine halluzinierten Fakten (LLM-Guardrails)

**Beispiel:**
```
BUY AAPL (85% Confidence)
"Apple zeigt starkes Momentum nach den Quartalszahlen. 
RSI bei 45 deutet auf Aufwärtspotenzial. 
Volumen 20% über Durchschnitt signalisiert Kaufinteresse."
```

---

### FR-3.2: News Sentiment-Analyse ⏳
**Als** Trader  
**möchte ich** die Marktstimmung zu einem Asset sehen  
**damit** ich News-getriebene Bewegungen verstehe

**Akzeptanzkriterien:**
- [x] Sentiment-Score: Bullish / Neutral / Bearish
- [ ] Top 3 relevante News-Headlines anzeigen (deferred)
- [ ] Sentiment aktualisiert sich mindestens täglich (deferred)
- [ ] Quellen werden angegeben (deferred)

**Note:** Basic sentiment based on technical analysis implemented. Full news integration planned for future.

---

### FR-3.3: Marktregime-Erklärung ✅
**Als** Trader  
**möchte ich** verstehen warum wir in RISK_ON/RISK_OFF sind  
**damit** ich meine Strategie anpassen kann

**Akzeptanzkriterien:**
- [x] LLM erklärt aktuelles Marktregime
- [x] Nennt makroökonomische Faktoren
- [ ] Vergleicht mit historischen Situationen (optional - deferred)

---

### FR-3.4: Chat-Interface (Optional/Future) ⏳
**Als** Trader  
**möchte ich** Fragen zur Marktlage stellen können  
**damit** ich schnell Antworten bekomme

**Akzeptanzkriterien:**
- [ ] Einfaches Chat-Input-Feld
- [ ] Antworten basieren auf aktuellen Daten
- [ ] Kontext-aware (kennt aktuelle Positionen)

---

## 🏗️ Technical Approach

### LLM Provider Options:
| Provider | Pros | Cons |
|----------|------|------|
| **Claude API** | Beste Qualität, lange Kontexte | Kosten, Latenz |
| **OpenAI GPT-4** | Schnell, gut für Summaries | Kosten |
| **Local Ollama** | Kostenlos, privat | Qualität, Hardware |
| **Groq (Llama)** | Sehr schnell, günstig | Qualität variabel |

### Empfehlung:
- **Phase 1:** Groq/Llama für schnelle, günstige Erklärungen
- **Phase 2:** Claude API für komplexe Analysen (optional)

### API Design:
```
GET /api/explain/{ticker}
→ { "explanation": "...", "factors": [...], "sentiment": "bullish" }

GET /api/sentiment/{ticker}
→ { "score": 0.75, "label": "bullish", "headlines": [...] }

GET /api/regime/explain
→ { "regime": "RISK_ON", "explanation": "...", "factors": [...] }
```

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM Halluzinationen | User bekommt falsche Infos | Guardrails, Faktencheck |
| API-Kosten explodieren | Budget-Überschreitung | Rate Limits, Caching |
| Latenz zu hoch | Schlechte UX | Background-Processing, Cache |
| LLM-Ausfall | Feature nicht verfügbar | Graceful Degradation |

---

## 📊 Success Metrics

| Metrik | Zielwert |
|--------|----------|
| Explanation Latency | < 3 Sekunden |
| User Engagement | +20% Time on Page |
| Accuracy (no hallucinations) | > 95% |
| API Cost per User/Day | < $0.05 |

---

## 🔗 Dependencies

- LLM Provider API Key
- News Data Source (Yahoo Finance, Alpha Vantage)
- Existing `/predict` and `/regime` endpoints

---

## 📝 Notes

- Start mit einfachen Template-basierten Erklärungen als Fallback
- LLM nur für "Premium" Erklärungen, nicht für jede Prediction
- Caching aggressive nutzen (gleiche Frage = gleiche Antwort für 1h)
