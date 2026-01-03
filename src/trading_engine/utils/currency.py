"""
Currency conversion utilities for multi-currency support.

Supports USD and CHF with real-time exchange rates.
Uses European Central Bank (ECB) API for reliable, free exchange rates.
"""

import logging
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)

# Cache exchange rates for 1 hour to avoid excessive API calls
_rate_cache: Dict[str, tuple] = {}  # {currency: (rate, timestamp)}
CACHE_DURATION = timedelta(hours=1)


def get_exchange_rate(from_currency: str = "USD", to_currency: str = "CHF") -> float:
    """
    Get exchange rate from one currency to another.

    Uses European Central Bank API (free, no API key required):
    https://api.exchangerate-api.com/v4/latest/USD

    Args:
        from_currency: Source currency code (default: USD)
        to_currency: Target currency code (default: CHF)

    Returns:
        Exchange rate (e.g., 1 USD = 0.85 CHF → returns 0.85)

    Example:
        >>> rate = get_exchange_rate("USD", "CHF")
        >>> price_chf = 100 * rate  # Convert $100 to CHF
    """
    # Same currency - no conversion needed
    if from_currency == to_currency:
        return 1.0

    # Check cache first
    cache_key = f"{from_currency}_{to_currency}"
    if cache_key in _rate_cache:
        rate, timestamp = _rate_cache[cache_key]
        if datetime.now() - timestamp < CACHE_DURATION:
            logger.debug(f"Using cached rate: 1 {from_currency} = {rate:.4f} {to_currency}")
            return rate

    # Fetch new rate from API
    try:
        # ExchangeRate-API.com - Free tier: 1500 requests/month
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        rates = data.get("rates", {})

        if to_currency not in rates:
            logger.error(f"Currency {to_currency} not found in API response")
            return _get_fallback_rate(from_currency, to_currency)

        rate = rates[to_currency]

        # Cache the rate
        _rate_cache[cache_key] = (rate, datetime.now())

        logger.info(f"✓ Exchange rate updated: 1 {from_currency} = {rate:.4f} {to_currency}")
        return rate

    except Exception as e:
        logger.warning(f"Failed to fetch exchange rate from API: {e}")
        return _get_fallback_rate(from_currency, to_currency)


def _get_fallback_rate(from_currency: str, to_currency: str) -> float:
    """
    Fallback exchange rates when API is unavailable.
    Uses approximate rates updated manually.
    """
    # Approximate rates as of January 2026
    fallback_rates = {
        "USD_CHF": 0.85,  # 1 USD ≈ 0.85 CHF
        "CHF_USD": 1.18,  # 1 CHF ≈ 1.18 USD
        "USD_EUR": 0.93,  # 1 USD ≈ 0.93 EUR
        "EUR_USD": 1.08,  # 1 EUR ≈ 1.08 USD
        "EUR_CHF": 0.91,  # 1 EUR ≈ 0.91 CHF
        "CHF_EUR": 1.10,  # 1 CHF ≈ 1.10 EUR
    }

    key = f"{from_currency}_{to_currency}"
    rate = fallback_rates.get(key, 1.0)

    logger.warning(f"Using fallback rate: 1 {from_currency} = {rate:.4f} {to_currency}")
    return rate


def convert_price(price: float, from_currency: str = "USD", to_currency: str = "CHF") -> float:
    """
    Convert price from one currency to another.

    Args:
        price: Price in source currency
        from_currency: Source currency code (default: USD)
        to_currency: Target currency code (default: CHF)

    Returns:
        Price in target currency

    Example:
        >>> convert_price(100.0, "USD", "CHF")
        85.0  # $100 USD = 85 CHF (approximate)
    """
    if from_currency == to_currency:
        return price

    rate = get_exchange_rate(from_currency, to_currency)
    converted = price * rate

    logger.debug(f"Converted {price:.2f} {from_currency} → {converted:.2f} {to_currency}")
    return converted


def format_price(price: float, currency: str = "USD", decimals: int = 2) -> str:
    """
    Format price with currency symbol.

    Args:
        price: Price value
        currency: Currency code (USD or CHF)
        decimals: Number of decimal places (default: 2)

    Returns:
        Formatted price string

    Example:
        >>> format_price(123.45, "USD")
        "$123.45"
        >>> format_price(105.80, "CHF")
        "CHF 105.80"
    """
    symbols = {
        "USD": "$",
        "CHF": "CHF ",
        "EUR": "€",
        "GBP": "£",
    }

    symbol = symbols.get(currency, currency + " ")

    if currency == "USD":
        return f"{symbol}{price:.{decimals}f}"
    else:
        return f"{symbol}{price:.{decimals}f}"


def get_rate_info() -> Dict[str, any]:
    """
    Get current exchange rate information for display.

    Returns:
        Dict with rate, timestamp, and source info

    Example:
        >>> info = get_rate_info()
        >>> print(f"1 USD = {info['rate']:.4f} CHF")
        >>> print(f"Last updated: {info['updated']}")
    """
    rate = get_exchange_rate("USD", "CHF")

    cache_key = "USD_CHF"
    timestamp = datetime.now()

    if cache_key in _rate_cache:
        _, timestamp = _rate_cache[cache_key]

    return {
        "rate": rate,
        "from_currency": "USD",
        "to_currency": "CHF",
        "updated": timestamp.isoformat(),
        "updated_ago": _format_time_ago(timestamp),
        "source": "ExchangeRate-API.com",
    }


def _format_time_ago(timestamp: datetime) -> str:
    """Format timestamp as human-readable 'time ago' string."""
    delta = datetime.now() - timestamp

    if delta < timedelta(minutes=1):
        return "just now"
    elif delta < timedelta(hours=1):
        minutes = int(delta.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif delta < timedelta(days=1):
        hours = int(delta.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        days = delta.days
        return f"{days} day{'s' if days > 1 else ''} ago"


# Preload USD/CHF rate on module import for faster first request
try:
    get_exchange_rate("USD", "CHF")
except Exception:
    pass  # Ignore errors during preload
