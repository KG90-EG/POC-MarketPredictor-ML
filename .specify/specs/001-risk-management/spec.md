# Phase 4: Risk Management Enhancement

## Übersicht

**Feature ID:** 001-risk-management  
**Status:** In Development  
**Priorität:** HIGH (letzte kritische Phase vor Production)  
**Geschätzte Dauer:** 6 Tage  

## Problem Statement

Das aktuelle System hat grundlegende Risk Management Features (Market Regime, Position Limits), aber es fehlen:

1. **Regime-basierte Position-Reduktion**: Bei Risk-Off werden Limits nicht angepasst
2. **Individual Asset Risk Scoring**: User sieht nicht, wie riskant ein einzelnes Asset ist
3. **Portfolio Exposure Tracking**: Keine Warnung wenn Limits überschritten werden

## User Stories

### US-1: Regime-basierte Risk Controls
**Als** Investor  
**Möchte ich** dass das System bei Risk-Off automatisch in einen Defensiv-Modus wechselt  
**Damit** mein Kapital bei Markt-Stress geschützt wird

**Akzeptanzkriterien:**
- [ ] UI zeigt "🔴 DEFENSIVE MODE" Banner wenn Regime = RISK_OFF
- [ ] Position Limits werden auf 50% reduziert (10% → 5%, 5% → 2.5%)
- [ ] Cash Reserve Minimum steigt auf 30%
- [ ] Alle BUY-Signale zeigen "⚠️ CAUTION" Badge
- [ ] Logmeldung bei Regime-Wechsel

### US-2: Individual Asset Risk Score
**Als** Investor  
**Möchte ich** für jedes Asset einen Risk-Score (0-100) sehen  
**Damit** ich verstehe, wie riskant ein Investment ist

**Akzeptanzkriterien:**
- [ ] Risk Score berechnet aus:
  - Volatilität (ATR, 40% Gewicht)
  - Max Drawdown (3 Monate, 35% Gewicht)
  - Korrelation zu S&P 500 (25% Gewicht)
- [ ] UI zeigt Risk Score neben Composite Score
- [ ] Farbkodierung: Grün (0-40), Gelb (41-70), Rot (71-100)
- [ ] "High Risk" Badge für Score > 70
- [ ] Risk Score in API-Response enthalten

### US-3: Portfolio Exposure Limits
**Als** Investor  
**Möchte ich** gewarnt werden wenn mein Portfolio über den Limits liegt  
**Damit** ich nicht überexponiert bin

**Akzeptanzkriterien:**
- [ ] BUY-Signale werden blockiert wenn:
  - Total Equity > 70%
  - Total Crypto > 20%
  - Single Sector > 30%
- [ ] UI zeigt "Portfolio Limit Reached" Warnung
- [ ] Pie Chart mit aktueller Allokation
- [ ] API Endpoint `/api/portfolio/exposure` gibt aktuelle Limits zurück

## Scope

### In Scope
- Regime-based risk controls (Backend + Frontend)
- Individual asset risk scoring (Backend + Frontend)
- Portfolio exposure tracking (Backend + Frontend)
- Tests für alle neuen Features

### Out of Scope
- Automatisches Rebalancing
- Stop-Loss Funktionalität
- Multi-Portfolio Support

## Abhängigkeiten

- ✅ Market Regime Detection (bereits implementiert)
- ✅ Composite Scoring System (bereits implementiert)
- ✅ Capital Allocation Framework (bereits implementiert)

## Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| ATR-Berechnung bei wenig Daten | Medium | Low | Fallback auf Standardwert |
| Langsame API bei vielen Assets | Low | Medium | Caching nutzen |
| Fehlende historische Daten | Low | Medium | Graceful degradation |

## Erfolgskriterien

1. ✅ Alle 3 User Stories implementiert
2. ✅ Tests grün (Unit + Integration)
3. ✅ UI zeigt Risk Score und Exposure
4. ✅ Defensive Mode funktioniert bei RISK_OFF
5. ✅ Performance: API Response < 2s
