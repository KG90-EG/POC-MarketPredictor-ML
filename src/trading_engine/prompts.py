"""
Prompt Templates for LLM-powered Market Analysis.

Contains all prompt templates used by the LLM service for generating
trading signal explanations and market regime analysis.
"""

# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

EXPLAIN_SYSTEM_PROMPT = """You are a professional financial analyst AI assistant.
Your role is to explain trading signals and market conditions in clear, concise language.

Guidelines:
- Be factual and avoid speculation
- Use plain language that retail traders can understand
- Never give specific financial advice
- Always mention that this is AI-generated analysis
- Focus on technical factors, not predictions
- Keep explanations brief (2-3 sentences)
- List concrete factors that support the analysis

Output format: JSON with keys "explanation", "factors" (array of 3-5 strings), "sentiment" (bullish/bearish/neutral)
"""

# ============================================================================
# SIGNAL EXPLANATION PROMPTS
# ============================================================================

EXPLAIN_SIGNAL_PROMPT = """Analyze the following trading signal and provide a clear explanation:

**Stock:** {ticker}
**Signal:** {signal}
**Confidence:** {confidence}%

**Technical Indicators:**
{indicators}

Explain WHY this signal was generated in 2-3 clear sentences.
List 3-5 key factors that support this analysis.
Determine the overall sentiment (bullish/bearish/neutral).

Respond in JSON format:
{{
  "explanation": "2-3 sentence explanation",
  "factors": ["factor 1", "factor 2", "factor 3"],
  "sentiment": "bullish|bearish|neutral"
}}
"""

# ============================================================================
# MARKET REGIME PROMPTS
# ============================================================================

EXPLAIN_REGIME_PROMPT = """Analyze the current market regime and provide a clear explanation:

**Current Regime:** {regime}

**Market Data:**
{regime_data}

Explain WHY the market is in this regime in 2-3 clear sentences.
List 3-5 key macro/technical factors that indicate this regime.

Respond in JSON format:
{{
  "explanation": "2-3 sentence explanation of current market conditions",
  "factors": ["factor 1", "factor 2", "factor 3"]
}}
"""

# ============================================================================
# NEWS SENTIMENT PROMPTS (Future Use)
# ============================================================================

SENTIMENT_ANALYSIS_PROMPT = """Analyze the sentiment of the following news headlines for {ticker}:

Headlines:
{headlines}

Determine the overall market sentiment based on these headlines.
Score from -1.0 (very bearish) to +1.0 (very bullish).

Respond in JSON format:
{{
  "score": 0.5,
  "label": "bullish|bearish|neutral",
  "summary": "Brief summary of news sentiment",
  "key_themes": ["theme 1", "theme 2"]
}}
"""

# ============================================================================
# PORTFOLIO ANALYSIS PROMPTS (Future Use)
# ============================================================================

PORTFOLIO_ANALYSIS_PROMPT = """Analyze the following portfolio and provide insights:

**Holdings:**
{holdings}

**Total Value:** ${total_value}
**Daily P&L:** {daily_pnl}%

Provide a brief analysis of the portfolio's:
1. Diversification
2. Risk exposure
3. Suggested actions (if any)

Respond in JSON format:
{{
  "analysis": "2-3 sentence portfolio analysis",
  "diversification_score": "good|moderate|poor",
  "risk_level": "low|medium|high",
  "suggestions": ["suggestion 1", "suggestion 2"]
}}
"""
