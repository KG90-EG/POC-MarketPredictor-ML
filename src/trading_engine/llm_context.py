"""
LLM Context Provider - Provides contextual information without making decisions.

This module follows the principle: "Context Provider, NOT Decision Maker"
- LLM summarizes news and events
- LLM identifies risk factors
- LLM provides narrative context
- LLM adjustment limited to ±5% maximum
- Quantitative signals drive decisions
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AssetContext:
    """Contextual information about an asset"""

    ticker: str
    news_summary: str
    risk_events: List[str]
    positive_catalysts: List[str]
    sentiment_score: float  # -1.0 to 1.0
    context_adjustment: float  # -5.0 to +5.0 (percentage points)
    last_updated: datetime


class LLMContextProvider:
    """
    Provides contextual analysis without making direct buy/sell decisions.

    Philosophy:
    - Quantitative signals (technical, ML, momentum) = Primary (95%)
    - LLM context = Modifier only (±5% max)
    - LLM never generates "BUY" or "SELL" recommendations
    - LLM summarizes information for human decision-making
    """

    def __init__(self, openai_client, news_api_key: Optional[str] = None):
        """
        Initialize context provider.

        Args:
            openai_client: OpenAI client for LLM analysis
            news_api_key: API key for news service (NewsAPI or similar)
        """
        self.openai = openai_client
        self.news_api_key = news_api_key
        self.MAX_ADJUSTMENT = 5.0  # ±5% maximum adjustment

    async def get_asset_context(self, ticker: str, current_score: float, lookback_days: int = 7) -> AssetContext:
        """
        Get contextual information for an asset.

        Args:
            ticker: Stock ticker symbol
            current_score: Current quantitative score (0-100)
            lookback_days: Days to look back for news (default: 7)

        Returns:
            AssetContext with news summary, risks, and limited adjustment
        """
        try:
            # Fetch recent news (would integrate with NewsAPI here)
            news_items = await self._fetch_news(ticker, lookback_days)

            if not news_items:
                return self._create_empty_context(ticker)

            # Ask LLM to summarize and analyze (NOT to recommend)
            context = await self._analyze_news_with_llm(ticker=ticker, news_items=news_items, current_score=current_score)

            return context

        except Exception as e:
            logger.error(f"Failed to get context for {ticker}: {e}")
            return self._create_empty_context(ticker)

    async def _fetch_news(self, ticker: str, days: int) -> List[Dict]:
        """
        Fetch recent news articles for a ticker.

        In production, integrate with:
        - NewsAPI (newsapi.org)
        - Alpha Vantage News
        - Financial Modeling Prep

        For now, returns placeholder.
        """
        # TODO: Implement actual news API integration
        # Example with NewsAPI:
        # from newsapi import NewsApiClient
        # newsapi = NewsApiClient(api_key=self.news_api_key)
        # news = newsapi.get_everything(
        #     q=ticker,
        #     from_param=(datetime.now() - timedelta(days=days)).isoformat(),
        #     language='en',
        #     sort_by='relevancy'
        # )
        # return news.get('articles', [])

        logger.debug(f"News fetch not implemented - returning empty for {ticker}")
        return []

    async def _analyze_news_with_llm(self, ticker: str, news_items: List[Dict], current_score: float) -> AssetContext:
        """
        Ask LLM to analyze news WITHOUT making buy/sell decisions.

        Prompt design ensures LLM provides context only.
        """
        # Prepare news text for analysis
        news_text = self._format_news_for_analysis(news_items)

        # Carefully designed prompt: NO BUY/SELL, only context
        prompt = f"""You are a financial news analyst. Analyze recent news for {ticker}.

NEWS ARTICLES (last 7 days):
{news_text}

YOUR TASK:
1. Summarize the news in 3 sentences or less
2. List positive catalysts (if any)
3. List risk factors or negative events (if any)
4. Assess sentiment: positive (0.5 to 1.0), neutral (-0.5 to 0.5), or negative (-1.0 to -0.5)

STRICT RULES:
- Do NOT recommend BUY, SELL, or HOLD
- Do NOT make investment decisions
- Provide factual summary only
- Sentiment is for context, not trading signals

Current quantitative score: {current_score}/100 (provided for reference only)

Format your response as JSON:
{{
    "summary": "3-sentence news summary",
    "positive_catalysts": ["catalyst1", "catalyst2"],
    "risk_factors": ["risk1", "risk2"],
    "sentiment": 0.5
}}
"""

        try:
            response = await self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial news analyst who provides context, not trading advice.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )

            # Parse LLM response
            import json

            analysis = json.loads(response.choices[0].message.content)

            # Calculate context adjustment (strictly limited to ±5%)
            sentiment = float(analysis.get("sentiment", 0.0))
            adjustment = self._calculate_context_adjustment(
                sentiment=sentiment,
                positive_catalysts=analysis.get("positive_catalysts", []),
                risk_factors=analysis.get("risk_factors", []),
            )

            return AssetContext(
                ticker=ticker,
                news_summary=analysis.get("summary", "No recent news"),
                risk_events=analysis.get("risk_factors", []),
                positive_catalysts=analysis.get("positive_catalysts", []),
                sentiment_score=sentiment,
                context_adjustment=adjustment,
                last_updated=datetime.now(),
            )

        except Exception as e:
            logger.error(f"LLM analysis failed for {ticker}: {e}")
            return self._create_empty_context(ticker)

    def _calculate_context_adjustment(self, sentiment: float, positive_catalysts: List[str], risk_factors: List[str]) -> float:
        """
        Calculate context adjustment with STRICT ±5% limit.

        Logic:
        - Sentiment contributes ±3%
        - Catalysts add up to +2%
        - Risk factors subtract up to -2%
        - Total capped at ±5%
        """
        # Base adjustment from sentiment (-3% to +3%)
        adjustment = sentiment * 3.0

        # Positive catalysts bonus (max +2%)
        catalyst_bonus = min(len(positive_catalysts) * 0.5, 2.0)
        adjustment += catalyst_bonus

        # Risk factors penalty (max -2%)
        risk_penalty = min(len(risk_factors) * 0.5, 2.0)
        adjustment -= risk_penalty

        # STRICT CAP at ±5%
        adjustment = max(-self.MAX_ADJUSTMENT, min(self.MAX_ADJUSTMENT, adjustment))

        logger.info(
            f"Context adjustment calculated: {adjustment:.2f}% "
            f"(sentiment: {sentiment:.2f}, catalysts: {len(positive_catalysts)}, "
            f"risks: {len(risk_factors)})"
        )

        return adjustment

    def _format_news_for_analysis(self, news_items: List[Dict]) -> str:
        """Format news articles for LLM prompt"""
        if not news_items:
            return "No recent news articles found."

        formatted = []
        for i, article in enumerate(news_items[:10], 1):  # Max 10 articles
            title = article.get("title", "No title")
            description = article.get("description", "")
            formatted.append(f"{i}. {title}\n   {description}")

        return "\n\n".join(formatted)

    def _create_empty_context(self, ticker: str) -> AssetContext:
        """Create empty context when no news available"""
        return AssetContext(
            ticker=ticker,
            news_summary="No recent news or analysis available",
            risk_events=[],
            positive_catalysts=[],
            sentiment_score=0.0,
            context_adjustment=0.0,
            last_updated=datetime.now(),
        )


# Global instance (initialized in server.py)
_context_provider: Optional[LLMContextProvider] = None


def initialize_context_provider(openai_client, news_api_key: Optional[str] = None):
    """Initialize global context provider"""
    global _context_provider
    _context_provider = LLMContextProvider(openai_client, news_api_key)
    logger.info("LLM Context Provider initialized (context-only mode, no decisions)")


def get_context_provider() -> Optional[LLMContextProvider]:
    """Get global context provider instance"""
    return _context_provider
