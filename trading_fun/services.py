"""
Business logic services layer.
Separates business logic from API routes for better maintainability.
"""
from typing import List, Dict, Optional, Any, Tuple
import yfinance as yf
import pandas as pd
import logging
import concurrent.futures
from .config import config
from .cache import cache

logger = logging.getLogger(__name__)


class StockService:
    """Service for stock-related operations"""
    
    @staticmethod
    def get_stocks_by_country(country: str, limit: int = 30) -> List[str]:
        """
        Get top stocks for a country with dynamic validation and ranking.
        
        Args:
            country: Country name (e.g., "Switzerland", "Germany")
            limit: Maximum number of stocks to return
            
        Returns:
            List of validated stock tickers ranked by market cap
        """
        # Check cache first
        cache_key = f"country_stocks:{country}:{limit}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Returning cached stocks for {country}")
            return cached
        
        # Get seed list for country
        seed_list = config.market.country_seeds.get(country, config.market.default_stocks)
        
        # Validate and rank by market cap in parallel
        validated_stocks = StockService._validate_stocks_parallel(seed_list, country)
        
        # Sort by market cap descending
        validated_stocks.sort(key=lambda x: x['market_cap'], reverse=True)
        
        # Extract tickers
        result = [s['ticker'] for s in validated_stocks[:limit]]
        
        # Cache result
        cache.set(cache_key, result, ttl=config.cache.country_stocks_ttl)
        
        logger.info(f"Validated {len(result)} stocks for {country}")
        return result
    
    @staticmethod
    def _validate_stocks_parallel(tickers: List[str], country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Validate stocks in parallel using ThreadPoolExecutor.
        
        Args:
            tickers: List of ticker symbols
            country: Optional country filter
            
        Returns:
            List of validated stock data with market cap
        """
        def validate_ticker(ticker: str) -> Optional[Dict[str, Any]]:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                market_cap = info.get("marketCap", 0)
                ticker_country = info.get("country", "")
                
                # Only include if has market cap data
                if market_cap and market_cap > 0:
                    return {
                        "ticker": ticker,
                        "market_cap": market_cap,
                        "country": ticker_country,
                    }
            except Exception as e:
                logger.debug(f"Validation failed for {ticker}: {e}")
            return None
        
        validated = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            results = executor.map(validate_ticker, tickers)
            validated = [r for r in results if r is not None]
        
        return validated
    
    @staticmethod
    def get_ticker_info(ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive information for a single ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with stock information
            
        Raises:
            ValueError: If ticker is invalid or data unavailable
        """
        # Check cache first
        cache_key = f"ticker_info:{ticker}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1y")
            
            if hist.empty:
                raise ValueError(f"No historical data available for {ticker}")
            
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
            prev_close = hist['Close'].iloc[-2] if len(hist) >= 2 else current_price
            
            result = {
                "name": info.get("longName", info.get("shortName", "N/A")),
                "price": float(current_price) if current_price else None,
                "change": float(current_price - prev_close) if current_price and prev_close else None,
                "volume": int(info.get("volume", 0)) if info.get("volume") else None,
                "market_cap": info.get("marketCap", None),
                "pe_ratio": info.get("forwardPE", info.get("trailingPE", None)),
                "country": info.get("country", "N/A"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh", None),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow", None),
            }
            
            # Cache result
            cache.set(cache_key, result, ttl=config.cache.ticker_info_ttl)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching info for {ticker}: {e}")
            raise ValueError(f"Unable to fetch data for ticker {ticker}")
    
    @staticmethod
    def get_ticker_info_batch(tickers: List[str]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str]]:
        """
        Get information for multiple tickers in parallel.
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Tuple of (results_dict, errors_dict)
        """
        results = {}
        errors = {}
        
        def fetch_ticker(ticker: str) -> Tuple[str, Optional[Dict[str, Any]], Optional[str]]:
            try:
                info = StockService.get_ticker_info(ticker)
                return ticker, info, None
            except Exception as e:
                return ticker, None, str(e)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fetch_ticker, t): t for t in tickers}
            
            for future in concurrent.futures.as_completed(futures):
                ticker, info, error = future.result()
                if error:
                    errors[ticker] = error
                else:
                    results[ticker] = info
        
        return results, errors


class SignalService:
    """Service for generating trading signals"""
    
    @staticmethod
    def get_signal(probability: float) -> str:
        """Get trading signal for a probability score"""
        return config.signal.get_signal(probability)
    
    @staticmethod
    def get_signal_color(signal: str) -> str:
        """Get color code for a signal"""
        colors = {
            "STRONG BUY": "#00C853",
            "BUY": "#4CAF50",
            "HOLD": "#FFC107",
            "CONSIDER SELLING": "#FF9800",
            "SELL": "#F44336"
        }
        return colors.get(signal, "#757575")
    
    @staticmethod
    def get_signal_badge(probability: float) -> Dict[str, str]:
        """Get signal badge with color and text"""
        signal = SignalService.get_signal(probability)
        return {
            "signal": signal,
            "color": SignalService.get_signal_color(signal),
            "emoji": "🟢" if probability >= 0.5 else "🔴"
        }


class ValidationService:
    """Service for input validation"""
    
    @staticmethod
    def validate_ticker(ticker: str) -> str:
        """
        Validate and normalize ticker symbol.
        
        Args:
            ticker: Raw ticker input
            
        Returns:
            Normalized ticker symbol
            
        Raises:
            ValueError: If ticker is invalid
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        
        ticker = ticker.strip().upper()
        
        if len(ticker) > 10:
            raise ValueError("Ticker symbol too long (max 10 characters)")
        
        # Basic validation - alphanumeric, dots, hyphens
        if not all(c.isalnum() or c in ['.', '-', '='] for c in ticker):
            raise ValueError("Ticker contains invalid characters")
        
        return ticker
    
    @staticmethod
    def validate_country(country: str) -> str:
        """
        Validate country parameter.
        
        Args:
            country: Country name
            
        Returns:
            Validated country name
            
        Raises:
            ValueError: If country is invalid
        """
        valid_countries = ["Global", "United States"] + list(config.market.country_seeds.keys())
        
        if country not in valid_countries:
            raise ValueError(f"Invalid country. Must be one of: {', '.join(valid_countries)}")
        
        return country
    
    @staticmethod
    def validate_probability(prob: float) -> float:
        """
        Validate probability value.
        
        Args:
            prob: Probability value
            
        Returns:
            Validated probability
            
        Raises:
            ValueError: If probability is out of range
        """
        if not isinstance(prob, (int, float)):
            raise ValueError("Probability must be a number")
        
        if not 0 <= prob <= 1:
            raise ValueError("Probability must be between 0 and 1")
        
        return float(prob)


class HealthService:
    """Service for health check operations"""
    
    @staticmethod
    def check_model_health() -> Dict[str, Any]:
        """Check if ML model is loaded and available"""
        import os
        model_path = config.model.prod_model_path
        
        return {
            "model_loaded": os.path.exists(model_path),
            "model_path": model_path
        }
    
    @staticmethod
    def check_openai_health() -> Dict[str, Any]:
        """Check OpenAI API availability"""
        return {
            "openai_configured": bool(config.api.openai_api_key),
            "openai_model": config.api.openai_model
        }
    
    @staticmethod
    def check_cache_health() -> Dict[str, Any]:
        """Check cache backend health"""
        cache_backend = "redis" if config.api.redis_url else "in-memory"
        redis_status = "not_used"
        
        if config.api.redis_url:
            try:
                # Try to set/get a test value
                cache.set("health_check", "ok", ttl=5)
                test_val = cache.get("health_check")
                redis_status = "connected" if test_val == "ok" else "error"
            except Exception:
                redis_status = "error"
        
        return {
            "cache_backend": cache_backend,
            "redis_status": redis_status
        }
