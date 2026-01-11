# 📈 Trader's Guide to the Market Predictor System

**Your Guide to Making Better Investment Decisions**

Version: 1.0 | Last Updated: 2026-01-11

---

## 🎯 What This System Does (And Doesn't Do)

### ✅ What It DOES:
- **Ranks stocks** based on multiple quantitative signals
- **Detects market regime** (Risk-On, Neutral, Risk-Off)
- **Provides context** for decision-making
- **Tracks portfolio risk** and allocation limits
- **Validates your allocations** before execution

### ❌ What It DOESN'T Do:
- **Make trades for you** (no automated trading)
- **Guarantee profits** (markets are uncertain)
- **Replace your judgment** (you decide, always)
- **Predict exact prices** (focuses on relative strength)

**Remember:** This is a **Decision Support System**, not a trading robot.

---

## 📊 Understanding the Signals

### Composite Score (0-100)

The system ranks stocks using a **composite score** from 0-100:

```
Composite Score = Technical (40%) + ML (30%) + Momentum (20%) + Regime (10%)
```

**How to interpret:**

| Score Range | Signal | Interpretation | Action |
|-------------|--------|----------------|--------|
| **80-100** | 🟢 **STRONG BUY** | Very bullish across all factors | Consider buying if you have cash |
| **65-79** | 🟢 **BUY** | Positive momentum and technicals | Good entry opportunity |
| **50-64** | 🟡 **HOLD** | Mixed signals, neutral | Wait for clearer signal |
| **35-49** | 🟠 **WEAK HOLD** | Starting to deteriorate | Consider reducing position |
| **20-34** | 🔴 **SELL** | Negative across multiple factors | Exit or avoid |
| **0-19** | 🔴 **STRONG SELL** | Very bearish | Stay away |

**Example:**
- AAPL score: 78 → **BUY signal** (good technical + ML confirmation)
- TSLA score: 42 → **WEAK HOLD** (mixed signals, wait)

---

### Component Breakdown

Click "Show Details" on any stock to see the breakdown:

#### 1. **Technical Score (40% weight)**
Based on 20 technical indicators:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- ADX (Trend strength)
- Moving averages (20-day, 50-day, 200-day)

**When to trust it:** 
- ✅ High technical score (>70) with clear trends
- ⚠️ Be cautious in choppy, sideways markets

#### 2. **ML Prediction (30% weight)**
Random Forest model trained on 5 years of data:
- Accuracy: 82.61% (US stocks), 78.37% (all stocks)
- Predicts: "Will price be higher in 90 days?"

**When to trust it:**
- ✅ When ML confidence is high (>0.65)
- ✅ When it aligns with technical score
- ⚠️ ML can lag in sudden regime changes

#### 3. **Momentum (20% weight)**
Recent price momentum indicators:
- 3-month performance
- Volume trends
- Breakout patterns

**When to trust it:**
- ✅ Strong momentum + high volume = conviction
- ⚠️ Momentum can reverse quickly

#### 4. **Regime Adjustment (10% weight)**
Market environment factor:
- **Risk-On** (VIX < 20): +5-10 points boost
- **Neutral** (VIX 20-30): No adjustment
- **Risk-Off** (VIX > 30): -5-10 points penalty

**Critical:** BUY signals are **blocked** in Risk-Off mode!

---

## 🚦 Market Regime: Your Risk Filter

### What Is Market Regime?

The system detects the overall market environment:

| Regime | VIX Level | S&P 500 Trend | What It Means |
|--------|-----------|---------------|---------------|
| 🟢 **Risk-On** | < 20 | Uptrend | Safe to take new positions |
| 🟡 **Neutral** | 20-30 | Sideways | Be selective, reduce position sizes |
| 🔴 **Risk-Off** | > 30 | Downtrend | **DEFENSIVE MODE** - BUY signals blocked |

### How to Use Regime Detection

#### In Risk-On Mode 🟢
- **Opportunity:** Market is healthy, fear is low
- **Action:** 
  - ✅ Execute BUY signals with confidence
  - ✅ Use full position sizes (up to 10% per stock)
  - ✅ Consider adding crypto exposure (up to 20% total)

#### In Neutral Mode 🟡
- **Caution:** Market is uncertain
- **Action:**
  - ⚠️ Reduce position sizes by 30-50%
  - ⚠️ Only buy top-ranked stocks (score >75)
  - ⚠️ Keep 20-30% cash reserve

#### In Risk-Off Mode 🔴
- **WARNING:** Market is in danger zone
- **Action:**
  - 🚫 **NO new BUY signals** (system blocks them)
  - 💰 Increase cash to 30-40%
  - 📉 Consider selling weak positions (score <40)
  - 🛡️ Hold defensive stocks only (consumer staples, utilities)

**Pro Tip:** The regime status is shown at the top of the dashboard. **Never ignore it!**

---

## 💡 When to Follow Recommendations

### ✅ Follow When:

1. **High Conviction Signals**
   - Composite score >75
   - All 4 components agree (technical, ML, momentum, regime)
   - Market regime is Risk-On or Neutral

2. **Regime Confirmation**
   - BUY signal + Risk-On regime = Strong go
   - SELL signal + Risk-Off regime = Definitely exit

3. **Your Risk Tolerance Allows**
   - Position size fits your portfolio (max 10% per stock)
   - You can afford to hold for 30-90 days
   - Loss wouldn't impact your financial goals

4. **Multiple Stocks Agree**
   - If top 5 stocks in same sector all show BUY → sector rotation
   - If top stocks are diversified → broad market strength

### ⚠️ Think Twice When:

1. **Mixed Signals**
   - High technical score but low ML prediction (or vice versa)
   - Composite score 45-55 (neutral zone)
   - Different timeframe indicators conflict

2. **Regime Mismatch**
   - BUY signal but regime just turned Neutral/Risk-Off
   - System shows BUY but VIX is spiking

3. **Overconcentration Risk**
   - You already own 3+ stocks in same sector
   - Single position would exceed 10% of portfolio
   - Crypto allocation already at 20%

4. **Fundamental Concerns**
   - Company has negative news (check news tab!)
   - Earnings miss or guidance cut
   - Regulatory/legal issues

### 🚫 Ignore When:

1. **Personal Circumstances**
   - You need the money soon (holding period <90 days)
   - You're emotionally stressed (avoid emotional trading)
   - You don't understand the company/asset

2. **Portfolio Already Full**
   - System says "Portfolio Limit Reached"
   - Cash reserve below 10%
   - Total equity exposure >70%

3. **Extreme Market Conditions**
   - VIX >40 (panic mode)
   - Major geopolitical events unfolding
   - Flash crash / circuit breaker situation

**Golden Rule:** The system provides signals, **you provide judgment**.

---

## 🛡️ Risk Management Best Practices

### Position Sizing

**System Limits (enforced automatically):**
```
Maximum per stock:    10% of portfolio
Maximum per crypto:    5% of portfolio
Total equity exposure: 70% max
Total crypto exposure: 20% max
Minimum cash reserve:  10%
```

**Your Personal Limits (recommended):**
```
Start small:           5% per position (first month)
High-conviction only:  8-10% positions
Moderate conviction:   3-5% positions
Low conviction:        Don't trade (wait for better setup)
```

**Example Portfolio ($100k):**
```
Cash Reserve:          $10,000 (10%)
10 Stock Positions:    $7,000 each (70% total)
4 Crypto Positions:    $5,000 each (20% total)
```

---

### Diversification Rules

#### ✅ DO:
- Hold 8-12 stocks across different sectors
- Include 1-2 defensive stocks (consumer staples, healthcare)
- Keep 10-20% in cash (dry powder for opportunities)
- Limit crypto to 15-20% max (higher volatility)

#### ❌ DON'T:
- Put >30% in one sector (even if all show BUY)
- Go all-in on top-ranked stock (concentration risk)
- Hold 20+ positions (too hard to monitor)
- Chase every BUY signal (quality over quantity)

---

### Stop-Loss Strategy

**System doesn't set stop-losses (you decide), but here's guidance:**

**Conservative Approach:**
```
Initial stop-loss:     -8% from entry
Trailing stop:         -10% from highest price
Time stop:             Exit after 90 days if no profit
```

**Aggressive Approach:**
```
Initial stop-loss:     -12% from entry
Trailing stop:         -15% from highest price
Time stop:             Hold up to 6 months
```

**When to Override:**
- ✅ Company fundamentals still strong → hold through dip
- ✅ Market regime caused temporary selloff → opportunity to add
- 🚫 Composite score drops below 40 → exit regardless of loss

---

### Rebalancing Frequency

**Monthly Rebalancing (recommended):**
1. Check portfolio every month (1st week)
2. Sell positions with score <40
3. Trim positions that exceeded 12% (take profits)
4. Buy new BUY signals (top 3-5 ranked)
5. Adjust for regime changes

**Weekly Monitoring:**
- Check regime status (top of dashboard)
- Look for STRONG BUY signals (score >80)
- Review any stocks that dropped >15%

**Daily (optional):**
- Glance at regime badge
- Check alerts
- Don't overtrade!

---

## 📉 Handling Losses

### Expected Loss Rate

**Reality check:**
```
System Win Rate:       ~60-70% (based on backtesting)
Expected losers:       3-4 out of 10 trades
Largest single loss:   -15% (if stops followed)
```

**This is NORMAL.** Focus on risk-adjusted returns, not win rate.

### When a Trade Goes Against You

**Score drops 40 → 30:**
- **Action:** Exit 50% of position, keep 50% with tight stop

**Score drops 40 → 20:**
- **Action:** Exit entire position immediately

**Regime changes Risk-On → Risk-Off:**
- **Action:** Review all positions, sell scores <50

**Stock drops -10% but score still 65+:**
- **Action:** Hold if fundamentals intact, consider adding

---

## 🎓 Learning from the System

### Track Your Performance

**Manual Tracking (recommended):**
```markdown
Trade Journal Template:

Date: 2026-01-11
Ticker: AAPL
Entry: $175.00
Signal: BUY (score 78)
Regime: Risk-On
Position Size: 8% ($8,000)
Reason: Strong technical + ML confirmation

Exit: TBD
Actual Return: TBD
Lesson: TBD
```

**Use the Performance Dashboard:**
- Compare your returns vs system recommendations
- Track adherence rate ("Did you follow signals?")
- Identify which signals work best for you

### Common Mistakes to Avoid

1. **Overtrading**
   - ❌ Trading every BUY signal
   - ✅ Only trade top 5 ranked stocks

2. **Ignoring Regime**
   - ❌ Buying in Risk-Off mode
   - ✅ Wait for regime to improve

3. **Emotional Override**
   - ❌ "I know better" (on STRONG SELL stocks)
   - ✅ Trust the data, not your gut

4. **Position Sizing**
   - ❌ 20% in one stock because "I love it"
   - ✅ Stick to 10% max

5. **No Stop-Losses**
   - ❌ "It'll come back" (famous last words)
   - ✅ Cut losses at -10-12%

---

## 🚀 Advanced Strategies

### Strategy 1: Momentum Rotation
**Goal:** Ride sector momentum

**Method:**
1. Identify top sector (e.g., 5 of top 10 stocks are Tech)
2. Buy top 3 Tech stocks (scores >70)
3. Hold for 30 days
4. Rotate to new top sector

**Best for:** Risk-On markets, active traders

---

### Strategy 2: Core + Satellite
**Goal:** Stable base with opportunistic trades

**Method:**
```
Core (70%):    Buy and hold top 5 stocks (scores >75)
                Only sell if score drops <40
                Rebalance quarterly

Satellite (20%): Trade BUY signals aggressively
                 Hold 30-60 days
                 Rebalance monthly

Cash (10%):     Dry powder for crashes
```

**Best for:** Long-term investors with patience

---

### Strategy 3: Defensive Mode
**Goal:** Preserve capital in uncertain markets

**Method:**
1. Only buy scores >80
2. Sell anything <50 immediately
3. Keep 30% cash minimum
4. Focus on low-volatility stocks (consumer staples, utilities)
5. Reduce crypto to 5-10%

**Best for:** Risk-Off regimes, pre-retirees

---

### Strategy 4: Contrarian
**Goal:** Buy fear, sell greed

**Method:**
1. Wait for Risk-Off regime
2. Identify stocks that held scores >60 during selloff
3. Buy when regime turns Neutral
4. Sell when everyone is euphoric (VIX <15)

**Best for:** Experienced traders with strong conviction

---

## 📱 Using the System Day-to-Day

### Morning Routine (5 min)
```
1. Check regime status (top of dashboard)
   - Risk-On → Green light for action
   - Neutral → Caution
   - Risk-Off → Defensive mode

2. Review top 10 ranked stocks
   - Any new STRONG BUY (>80)?
   - Any holdings dropped to SELL (<35)?

3. Check alerts
   - Price alerts triggered?
   - Volatility warnings?
   - Regime change notifications?

4. Make decisions
   - Place orders if needed
   - Update stop-losses
   - Rebalance if necessary
```

### Weekly Review (30 min)
```
1. Portfolio health check
   - Total exposure within limits?
   - Sector concentration OK?
   - Cash reserve adequate?

2. Performance analysis
   - Which trades worked? Why?
   - Which failed? Lesson learned?
   - Adherence rate to signals?

3. Watchlist maintenance
   - Add new high-score stocks
   - Remove consistently low scorers
   - Research fundamentals

4. Plan for next week
   - Dry powder available?
   - Expected regime changes?
   - Earnings calendar?
```

### Monthly Rebalance (1-2 hours)
```
1. Full portfolio review
2. Sell all scores <40
3. Trim winners >12% position size
4. Buy top 3-5 new BUY signals
5. Update tracking spreadsheet
6. Adjust strategy if needed
```

---

## ❓ FAQ

**Q: Why did a BUY signal change to SELL overnight?**
A: Signals update daily with new data. Rapid changes can happen due to:
- Earnings report
- Regime shift
- Technical indicator reversal
- Market-wide selloff

**Q: Should I buy ALL top 10 stocks?**
A: No! Focus on top 3-5 that fit your portfolio. Quality > quantity.

**Q: The system says BUY but news is bad. What do I do?**
A: Trust fundamentals > signals. If company has major issues, skip it.

**Q: Can I use this for day trading?**
A: No. System is designed for 30-90 day holding periods. Day trading requires different tools.

**Q: Why are BUY signals blocked in Risk-Off?**
A: Historical data shows buying in Risk-Off leads to poor returns. System protects you from bad timing.

**Q: Should I sell everything in Risk-Off?**
A: Not necessarily. Sell weak positions (score <50), hold strong ones (>60). Increase cash to 30%.

**Q: The backtest shows system beats S&P 500. Guaranteed?**
A: **NO.** Past performance ≠ future results. Backtests are **simulations**, not guarantees.

**Q: How often should I check the system?**
A: Daily check (5 min), weekly review (30 min), monthly rebalance (1-2 hours).

**Q: Can I ignore the regime and just trade signals?**
A: You can, but you'll likely underperform. Regime is the **risk filter** for a reason.

**Q: What if I disagree with a signal?**
A: You're the boss! System provides data, you make decisions. But track your overrides to see if you're improving or hurting returns.

---

## 🎯 Key Takeaways

1. **Regime > Signals** - Never ignore market regime
2. **Position Size Matters** - Stick to 10% max per stock
3. **Diversify Always** - Don't put all eggs in one basket
4. **Stop-Losses Save Lives** - Cut losses at -10-12%
5. **Quality > Quantity** - Trade less, win more
6. **Track Everything** - Learn from wins AND losses
7. **You Decide** - System supports, you execute
8. **Risk Management First** - Protect capital, then grow it

---

## 📞 Next Steps

1. **Read this guide fully** (you're almost done!)
2. **Paper trade first** (use simulation mode for 1 month)
3. **Start small** (5% positions maximum)
4. **Track performance** (compare vs system recommendations)
5. **Iterate and improve** (adjust strategy based on results)

**Remember:** This system is a **tool**, not a crystal ball. Use it to enhance your decision-making, not replace your judgment.

---

## 📚 Additional Resources

- **Requirements Doc:** `docs/DECISION_SUPPORT_SYSTEM_REQUIREMENTS.md`
- **API Reference:** `http://localhost:8000/docs`
- **Backtest Results:** Run `/api/backtest/run` for historical validation
- **Model Info:** Check `/api/ml/model/info` for current model accuracy

---

**Good luck, and trade smart! 🚀📈**

*Last Updated: 2026-01-11*
