"""
Cryptocurrency data fetching and analysis module.
Uses CoinGecko API (free, no API key required for basic usage).
"""

import logging
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# CoinGecko API base URL (free tier)
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Default cryptocurrencies to track
DEFAULT_CRYPTOS = [
    "bitcoin",
    "ethereum",
    "binancecoin",  # BNB
    "ripple",  # XRP
    "cardano",  # ADA
    "solana",  # SOL
    "polkadot",  # DOT
    "dogecoin",  # DOGE
    "matic-network",  # MATIC/Polygon
    "avalanche-2",  # AVAX
    "chainlink",  # LINK
    "uniswap",  # UNI
    "litecoin",  # LTC
    "cosmos",  # ATOM
    "algorand",  # ALGO
]

# NFT-related tokens
NFT_TOKENS = [
    "decentraland",  # MANA
    "the-sandbox",  # SAND
    "axie-infinity",  # AXS
    "enjincoin",  # ENJ
    "apecoin",  # APE
]


def get_crypto_market_data(
    crypto_ids: Optional[List[str]] = None,
    vs_currency: str = "usd",
    include_nft: bool = True,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Fetch current market data for cryptocurrencies from CoinGecko.

    Args:
        crypto_ids: List of crypto IDs (e.g., ['bitcoin', 'ethereum']).
                   If None, fetches top cryptos by market cap
        vs_currency: Currency to compare against (default: 'usd')
        include_nft: Include NFT-related tokens when crypto_ids is None
        limit: Number of top cryptos to fetch when crypto_ids is None (default: 50)

    Returns:
        List of dictionaries with crypto market data
    """
    try:
        # CoinGecko API endpoint for market data
        url = f"{COINGECKO_BASE_URL}/coins/markets"

        if crypto_ids is None:
            # Fetch top cryptos by market cap dynamically
            params = {
                "vs_currency": vs_currency,
                "order": "market_cap_desc",
                "per_page": limit,
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "24h,7d,30d",
            }
            logger.info(f"Fetching top {limit} cryptos by market cap")
        else:
            # Fetch specific cryptos
            if include_nft and crypto_ids == DEFAULT_CRYPTOS:
                crypto_ids = crypto_ids + NFT_TOKENS

            params = {
                "vs_currency": vs_currency,
                "ids": ",".join(crypto_ids),
                "order": "market_cap_desc",
                "per_page": len(crypto_ids),
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "24h,7d,30d",
            }
            logger.info(f"Fetching crypto data for {len(crypto_ids)} specific assets")

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        logger.info(f"Successfully fetched data for {len(data)} cryptocurrencies")
        return data

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch crypto data: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching crypto data: {e}")
        return []


def get_crypto_details(crypto_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed information for a specific cryptocurrency.

    Args:
        crypto_id: CoinGecko crypto ID (e.g., 'bitcoin', 'ethereum')

    Returns:
        Dictionary with detailed crypto information
    """
    try:
        url = f"{COINGECKO_BASE_URL}/coins/{crypto_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "true",
            "developer_data": "false",
            "sparkline": "false",
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch details for {crypto_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching {crypto_id} details: {e}")
        return None


def compute_crypto_features(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute trading features and signals for cryptocurrency.

    Args:
        market_data: Market data from CoinGecko API

    Returns:
        Dictionary with computed features and signals
    """
    try:
        # Extract key metrics
        price_change_24h = market_data.get("price_change_percentage_24h", 0) or 0
        price_change_7d = (
            market_data.get("price_change_percentage_7d_in_currency", 0) or 0
        )
        price_change_30d = (
            market_data.get("price_change_percentage_30d_in_currency", 0) or 0
        )

        market_cap_rank = market_data.get("market_cap_rank", 999)
        total_volume = market_data.get("total_volume", 0) or 0
        market_cap = market_data.get("market_cap", 0) or 0

        # Volume/Market Cap ratio (liquidity indicator)
        volume_to_mcap = (total_volume / market_cap * 100) if market_cap > 0 else 0

        # Compute simple momentum score (0-1 scale)
        # Based on: rank, 24h change, 7d trend, 30d trend, liquidity
        momentum_score = 0.0

        # Rank contribution (top 10 = 0.3, top 50 = 0.15, else = 0)
        if market_cap_rank <= 10:
            momentum_score += 0.3
        elif market_cap_rank <= 50:
            momentum_score += 0.15

        # 24h change contribution (max 0.25)
        if price_change_24h > 5:
            momentum_score += 0.25
        elif price_change_24h > 0:
            momentum_score += 0.15
        elif price_change_24h > -3:
            momentum_score += 0.05

        # 7d trend contribution (max 0.2)
        if price_change_7d > 10:
            momentum_score += 0.2
        elif price_change_7d > 0:
            momentum_score += 0.1

        # 30d trend contribution (max 0.15)
        if price_change_30d > 20:
            momentum_score += 0.15
        elif price_change_30d > 0:
            momentum_score += 0.08

        # Liquidity contribution (max 0.1)
        if volume_to_mcap > 20:  # High liquidity
            momentum_score += 0.1
        elif volume_to_mcap > 10:
            momentum_score += 0.05

        # Cap at 1.0
        momentum_score = min(momentum_score, 1.0)

        return {
            "symbol": market_data.get("symbol", "").upper(),
            "name": market_data.get("name", ""),
            "price": market_data.get("current_price", 0),
            "change_24h": price_change_24h,
            "change_7d": price_change_7d,
            "change_30d": price_change_30d,
            "market_cap": market_cap,
            "market_cap_rank": market_cap_rank,
            "volume": total_volume,
            "volume_to_mcap_ratio": volume_to_mcap,
            "momentum_score": momentum_score,
            "probability": momentum_score,  # Use momentum as probability for consistency
            "image": market_data.get("image", ""),
            "crypto_id": market_data.get("id", ""),
        }

    except Exception as e:
        logger.error(f"Error computing crypto features: {e}")
        return {}


def get_crypto_ranking(
    crypto_ids: Optional[List[str]] = None,
    include_nft: bool = True,
    min_probability: float = 0.0,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Get ranked list of cryptocurrencies with trading signals.

    Args:
        crypto_ids: List of crypto IDs to analyze. If None, fetches top by market cap
        include_nft: Include NFT-related tokens (only when crypto_ids is None)
        min_probability: Minimum probability threshold
        limit: Number of top cryptos to fetch when crypto_ids is None (default: 50)

    Returns:
        List of ranked cryptocurrencies with features and signals
    """
    market_data_list = get_crypto_market_data(
        crypto_ids=crypto_ids, include_nft=include_nft, limit=limit
    )

    if not market_data_list:
        logger.warning("No crypto market data available")
        return []

    # Compute features for each crypto
    crypto_rankings = []
    for market_data in market_data_list:
        features = compute_crypto_features(market_data)
        if features and features.get("probability", 0) >= min_probability:
            crypto_rankings.append(features)

    # Sort by probability (momentum score)
    crypto_rankings.sort(key=lambda x: x.get("probability", 0), reverse=True)

    logger.info(f"Ranked {len(crypto_rankings)} cryptocurrencies")
    return crypto_rankings


def search_crypto(query: str) -> Optional[Dict[str, Any]]:
    """
    Search for a cryptocurrency by name or symbol.

    Args:
        query: Search query (name or symbol)

    Returns:
        Dictionary with crypto details if found
    """
    try:
        # First, search for the crypto
        url = f"{COINGECKO_BASE_URL}/search"
        params = {"query": query}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        coins = data.get("coins", [])

        if not coins:
            logger.warning(f"No crypto found for query: {query}")
            return None

        # Get the first match (usually most relevant)
        crypto_id = coins[0]["id"]

        # Fetch detailed data
        market_data_list = get_crypto_market_data([crypto_id])
        if not market_data_list:
            return None

        features = compute_crypto_features(market_data_list[0])
        return features if features else None

    except Exception as e:
        logger.error(f"Error searching for crypto '{query}': {e}")
        return None
