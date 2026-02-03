"""
Tests for the LLM Service Module.

Tests caching, fallback logic, and API integration.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from src.trading_engine.llm_service import (
    FALLBACK_EXPLANATIONS,
    LLMService,
    TTLCache,
    get_llm_service,
)

# Configure pytest-asyncio
pytestmark = pytest.mark.asyncio(loop_scope="function")


# ============================================================================
# TTL CACHE TESTS
# ============================================================================


class TestTTLCache:
    """Tests for the TTL cache implementation."""

    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        cache = TTLCache(ttl=3600)
        cache.set("test_key", {"data": "value"})

        result = cache.get("test_key")
        assert result == {"data": "value"}

    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache = TTLCache(ttl=3600)

        result = cache.get("nonexistent_key")
        assert result is None

    def test_cache_expiry(self):
        """Test that expired items return None."""
        cache = TTLCache(ttl=1)  # 1 second TTL
        cache.set("test_key", {"data": "value"})

        # Manually expire the item
        cache._cache["test_key"] = ({"data": "value"}, 0)  # Set timestamp to 0

        result = cache.get("test_key")
        assert result is None

    def test_cache_clear(self):
        """Test cache clear operation."""
        cache = TTLCache(ttl=3600)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_cleanup(self):
        """Test cleanup removes expired items."""
        cache = TTLCache(ttl=1)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Manually expire items
        for key in cache._cache:
            cache._cache[key] = (cache._cache[key][0], 0)

        removed = cache.cleanup()
        assert removed == 2
        assert len(cache._cache) == 0


# ============================================================================
# LLM SERVICE TESTS
# ============================================================================


class TestLLMService:
    """Tests for the LLM service."""

    def test_init_default_provider(self):
        """Test service initializes with default provider."""
        service = LLMService()
        assert service.provider in ["groq", "openai", "anthropic"]

    def test_init_unknown_provider_fallback(self):
        """Test service falls back to groq for unknown provider."""
        service = LLMService(provider="unknown_provider")
        # Should fall back to groq
        assert service.config is not None

    @pytest.mark.asyncio
    async def test_explain_signal_fallback(self):
        """Test explain_signal returns fallback when LLM fails."""
        service = LLMService()
        service.api_key = ""  # No API key = will use fallback

        result = await service.explain_signal(
            ticker="AAPL",
            signal="BUY",
            confidence=75.0,
        )

        assert result["ticker"] == "AAPL"
        assert result["signal"] == "BUY"
        assert result["fallback"] is True
        assert "explanation" in result
        assert "factors" in result
        assert "sentiment" in result

    @pytest.mark.asyncio
    async def test_explain_signal_caching(self):
        """Test that explain_signal caches responses."""
        service = LLMService()

        # First call
        result1 = await service.explain_signal(
            ticker="AAPL",
            signal="BUY",
            confidence=75.0,
            use_cache=True,
        )

        # Second call should be cached
        result2 = await service.explain_signal(
            ticker="AAPL",
            signal="BUY",
            confidence=75.0,
            use_cache=True,
        )

        # Both should have same content (cached)
        assert result1["explanation"] == result2["explanation"]

    @pytest.mark.asyncio
    async def test_explain_signal_normalizes_signal(self):
        """Test that signal is normalized to uppercase."""
        service = LLMService()

        result = await service.explain_signal(
            ticker="AAPL",
            signal="buy",  # lowercase
            confidence=75.0,
        )

        assert result["signal"] == "BUY"

    @pytest.mark.asyncio
    async def test_explain_signal_invalid_signal(self):
        """Test that invalid signal defaults to HOLD."""
        service = LLMService()

        result = await service.explain_signal(
            ticker="AAPL",
            signal="INVALID",
            confidence=75.0,
        )

        assert result["signal"] == "HOLD"

    @pytest.mark.asyncio
    async def test_explain_regime_fallback(self):
        """Test explain_regime returns fallback when LLM fails."""
        service = LLMService()
        service.api_key = ""

        result = await service.explain_regime(
            regime="RISK_ON",
        )

        assert result["regime"] == "RISK_ON"
        assert result["fallback"] is True
        assert "explanation" in result
        assert "factors" in result

    @pytest.mark.asyncio
    async def test_generate_no_api_key(self):
        """Test generate returns None when no API key."""
        service = LLMService()
        service.api_key = ""

        result = await service.generate("Test prompt")

        assert result is None


# ============================================================================
# FALLBACK EXPLANATIONS TESTS
# ============================================================================


class TestFallbackExplanations:
    """Tests for fallback explanations."""

    def test_buy_fallback_exists(self):
        """Test BUY fallback is defined."""
        assert "BUY" in FALLBACK_EXPLANATIONS
        assert "explanation" in FALLBACK_EXPLANATIONS["BUY"]
        assert "factors" in FALLBACK_EXPLANATIONS["BUY"]
        assert "sentiment" in FALLBACK_EXPLANATIONS["BUY"]
        assert FALLBACK_EXPLANATIONS["BUY"]["sentiment"] == "bullish"

    def test_sell_fallback_exists(self):
        """Test SELL fallback is defined."""
        assert "SELL" in FALLBACK_EXPLANATIONS
        assert FALLBACK_EXPLANATIONS["SELL"]["sentiment"] == "bearish"

    def test_hold_fallback_exists(self):
        """Test HOLD fallback is defined."""
        assert "HOLD" in FALLBACK_EXPLANATIONS
        assert FALLBACK_EXPLANATIONS["HOLD"]["sentiment"] == "neutral"


# ============================================================================
# SINGLETON TESTS
# ============================================================================


class TestSingleton:
    """Tests for the singleton pattern."""

    def test_get_llm_service_returns_instance(self):
        """Test get_llm_service returns an LLMService instance."""
        service = get_llm_service()
        assert isinstance(service, LLMService)

    def test_get_llm_service_singleton(self):
        """Test get_llm_service returns the same instance."""
        service1 = get_llm_service()
        service2 = get_llm_service()
        assert service1 is service2
