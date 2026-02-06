"""
Commodity Data Fetching and Analysis Module.

Uses yfinance to fetch data for commodity futures (Gold, Oil, Silver, etc.).
Implements NFR-011: Multi-Asset Support.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

from src.trading_engine.core.cache import cache
from src.trading_engine.core.config_loader import get_config_loader

logger = logging.getLogger(__name__)


@dataclass
class CommodityData:
    """Commodity market data structure."""

    ticker: str
    name: str
    category: str
    unit: str
    price: float
    change_24h: float
    change_7d: float
    change_30d: float
    volume: float
    high_52w: Optional[float]
    low_52w: Optional[float]
    last_updated: datetime


@dataclass
class CommodityRanking:
    """Commodity with computed scores."""

    ticker: str
    name: str
    category: str
    price: float
    change_24h: float
    change_7d: float
    momentum_score: float
    volatility_score: float
    composite_score: float
    signal: str
    risk_level: str


class CommodityService:
    """
    Service for fetching and analyzing commodity data.

    Uses yfinance for commodity futures data with caching.
    """

    # Cache TTL from config (default 5 minutes)
    DEFAULT_CACHE_TTL = 300

    def __init__(self):
        """Initialize commodity service."""
        self.config = get_config_loader()
        self._commodity_info = self._load_commodity_info()

    def _load_commodity_info(self) -> Dict[str, Dict[str, Any]]:
        """Load commodity ticker info from config."""
        info = {}
        categories = self.config.get_commodity_categories()

        for category_name, category_data in categories.items():
            for ticker_info in category_data.get("tickers", []):
                ticker = ticker_info["ticker"]
                info[ticker] = {
                    "name": ticker_info["name"],
                    "category": category_name,
                    "category_display": category_data.get("display_name", category_name),
                    "unit": ticker_info.get("unit", "unit"),
                }

        return info

    def get_all_tickers(self) -> List[str]:
        """Get list of all commodity tickers."""
        return list(self._commodity_info.keys())

    def get_tickers_by_category(self, category: str) -> List[str]:
        """Get commodity tickers for a specific category."""
        return [
            ticker for ticker, info in self._commodity_info.items() if info["category"] == category
        ]

    def get_commodity_data(self, ticker: str, use_cache: bool = True) -> Optional[CommodityData]:
        """
        Fetch market data for a single commodity.

        Args:
            ticker: Commodity ticker (e.g., 'GC=F' for Gold)
            use_cache: Whether to use cached data

        Returns:
            CommodityData object or None if failed
        """
        cache_key = f"commodity:{ticker}"

        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for commodity: {ticker}")
                return cached

        try:
            commodity = yf.Ticker(ticker)
            hist = commodity.history(period="3mo")

            if hist.empty:
                logger.warning(f"No data available for commodity: {ticker}")
                return None

            current_price = float(hist["Close"].iloc[-1])

            # Calculate price changes
            change_24h = self._calc_pct_change(hist, 1)
            change_7d = self._calc_pct_change(hist, 5)  # 5 trading days ≈ 1 week
            change_30d = self._calc_pct_change(hist, 21)  # 21 trading days ≈ 1 month

            # 52-week high/low
            hist_1y = commodity.history(period="1y")
            high_52w = float(hist_1y["High"].max()) if not hist_1y.empty else None
            low_52w = float(hist_1y["Low"].min()) if not hist_1y.empty else None

            # Volume
            volume = float(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0

            # Get commodity info
            info = self._commodity_info.get(ticker, {})

            data = CommodityData(
                ticker=ticker,
                name=info.get("name", ticker),
                category=info.get("category", "unknown"),
                unit=info.get("unit", "unit"),
                price=current_price,
                change_24h=change_24h,
                change_7d=change_7d,
                change_30d=change_30d,
                volume=volume,
                high_52w=high_52w,
                low_52w=low_52w,
                last_updated=datetime.now(),
            )

            # Cache result
            cache_ttl = self.config.get_cache_ttl("commodities")
            cache.set(cache_key, data, ttl_seconds=cache_ttl)

            return data

        except Exception as e:
            logger.error(f"Error fetching commodity data for {ticker}: {e}")
            return None

    def _calc_pct_change(self, hist: pd.DataFrame, days: int) -> float:
        """Calculate percentage change over N days."""
        if len(hist) < days + 1:
            return 0.0

        current = hist["Close"].iloc[-1]
        past = hist["Close"].iloc[-(days + 1)]

        if past == 0:
            return 0.0

        return ((current - past) / past) * 100

    def get_all_commodities(self, use_cache: bool = True) -> List[CommodityData]:
        """
        Fetch data for all configured commodities.

        Args:
            use_cache: Whether to use cached data

        Returns:
            List of CommodityData objects
        """
        results = []
        tickers = self.get_all_tickers()

        logger.info(f"Fetching data for {len(tickers)} commodities")

        for ticker in tickers:
            data = self.get_commodity_data(ticker, use_cache=use_cache)
            if data:
                results.append(data)

        logger.info(f"Successfully fetched {len(results)}/{len(tickers)} commodities")
        return results

    def compute_commodity_scores(self, data: CommodityData) -> CommodityRanking:
        """
        Compute momentum and risk scores for a commodity.

        Args:
            data: CommodityData to analyze

        Returns:
            CommodityRanking with computed scores
        """
        # Momentum score based on price changes (0-100)
        momentum_score = self._calc_momentum_score(data.change_24h, data.change_7d, data.change_30d)

        # Volatility score (lower is better for commodities)
        volatility_score = self._calc_volatility_score(data.ticker)

        # Risk multiplier from config
        risk_multiplier = self.config.get_risk_multiplier("commodities")

        # Composite score (weighted average)
        # For commodities: higher momentum + lower volatility = better
        composite_score = (momentum_score * 0.6 + (100 - volatility_score) * 0.4) * risk_multiplier

        # Clamp to 0-100
        composite_score = max(0, min(100, composite_score))

        # Determine signal based on composite score
        signal = self._get_signal(composite_score)
        risk_level = self._get_risk_level(volatility_score)

        return CommodityRanking(
            ticker=data.ticker,
            name=data.name,
            category=data.category,
            price=data.price,
            change_24h=data.change_24h,
            change_7d=data.change_7d,
            momentum_score=momentum_score,
            volatility_score=volatility_score,
            composite_score=composite_score,
            signal=signal,
            risk_level=risk_level,
        )

    def _calc_momentum_score(self, change_24h: float, change_7d: float, change_30d: float) -> float:
        """
        Calculate momentum score based on price changes.

        Weights: 24h (20%), 7d (30%), 30d (50%)
        """

        # Normalize changes to score (positive change = higher score)
        # Cap at ±20% change for normalization
        def normalize(change: float) -> float:
            capped = max(-20, min(20, change))
            return 50 + (capped * 2.5)  # Maps -20% to 0, +20% to 100

        score = (
            normalize(change_24h) * 0.2 + normalize(change_7d) * 0.3 + normalize(change_30d) * 0.5
        )

        return max(0, min(100, score))

    def _calc_volatility_score(self, ticker: str) -> float:
        """
        Calculate volatility score based on historical data.

        Returns score 0-100 where higher = more volatile.
        """
        cache_key = f"commodity_volatility:{ticker}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            commodity = yf.Ticker(ticker)
            hist = commodity.history(period="3mo")

            if len(hist) < 20:
                return 50.0  # Default medium volatility

            # Calculate daily returns
            returns = hist["Close"].pct_change().dropna()

            # Annualized volatility
            volatility = returns.std() * np.sqrt(252) * 100

            # Map volatility to score (0-50% vol maps to 0-100 score)
            score = min(100, volatility * 2)

            # Cache for 1 hour
            cache.set(cache_key, score, ttl_seconds=3600)

            return score

        except Exception as e:
            logger.error(f"Error calculating volatility for {ticker}: {e}")
            return 50.0

    def _get_signal(self, composite_score: float) -> str:
        """Get trading signal based on composite score."""
        thresholds = self.config.get_scoring_thresholds()

        if composite_score >= thresholds.get("strong_buy", {}).get("min_score", 85):
            return "STRONG_BUY"
        elif composite_score >= thresholds.get("buy", {}).get("min_score", 65):
            return "BUY"
        elif composite_score >= thresholds.get("hold", {}).get("min_score", 45):
            return "HOLD"
        elif composite_score >= thresholds.get("consider_selling", {}).get("min_score", 35):
            return "CONSIDER_SELLING"
        else:
            return "SELL"

    def _get_risk_level(self, volatility_score: float) -> str:
        """Get risk level based on volatility."""
        if volatility_score < 30:
            return "LOW"
        elif volatility_score < 60:
            return "MEDIUM"
        else:
            return "HIGH"

    def get_commodity_ranking(
        self,
        category: Optional[str] = None,
        min_score: float = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get ranked list of commodities.

        Args:
            category: Optional category filter
            min_score: Minimum composite score
            limit: Maximum number of results

        Returns:
            List of ranked commodities as dictionaries
        """
        cache_key = f"commodity_ranking:{category or 'all'}:{min_score}:{limit}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Get all commodity data
        all_data = self.get_all_commodities()

        # Filter by category if specified
        if category:
            all_data = [d for d in all_data if d.category == category]

        # Compute scores for each
        rankings = []
        for data in all_data:
            ranking = self.compute_commodity_scores(data)
            if ranking.composite_score >= min_score:
                rankings.append(ranking)

        # Sort by composite score (descending)
        rankings.sort(key=lambda x: x.composite_score, reverse=True)

        # Limit results
        rankings = rankings[:limit]

        # Convert to dict for API response
        result = [
            {
                "ticker": r.ticker,
                "name": r.name,
                "category": r.category,
                "price": round(r.price, 2),
                "change_24h": round(r.change_24h, 2),
                "change_7d": round(r.change_7d, 2),
                "momentum_score": round(r.momentum_score, 1),
                "volatility_score": round(r.volatility_score, 1),
                "composite_score": round(r.composite_score, 1),
                "signal": r.signal,
                "risk_level": r.risk_level,
                "asset_type": "commodity",
            }
            for r in rankings
        ]

        # Cache for 5 minutes
        cache.set(cache_key, result, ttl_seconds=300)

        return result


# Singleton instance
_commodity_service: Optional[CommodityService] = None


def get_commodity_service() -> CommodityService:
    """Get singleton CommodityService instance."""
    global _commodity_service
    if _commodity_service is None:
        _commodity_service = CommodityService()
    return _commodity_service


def warm_commodity_cache() -> None:
    """Pre-warm the commodity cache on startup."""
    logger.info("Warming commodity cache...")
    try:
        service = get_commodity_service()
        data = service.get_all_commodities(use_cache=False)
        logger.info(f"Commodity cache warmed with {len(data)} items")
    except Exception as e:
        logger.error(f"Failed to warm commodity cache: {e}")
