"""
LLM Service Module for Market Analysis Explanations.

Provides AI-powered explanations for trading signals using various LLM providers.
Supports Groq (default), OpenAI, and Anthropic with caching and fallback logic.
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_CACHE_TTL = int(os.getenv("LLM_CACHE_TTL", "3600"))  # 1 hour default

# Provider configurations
PROVIDER_CONFIGS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.1-70b-versatile",
        "api_key_env": "GROQ_API_KEY",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1/messages",
        "model": "claude-3-haiku-20240307",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
}


# ============================================================================
# FALLBACK EXPLANATIONS
# ============================================================================

FALLBACK_EXPLANATIONS = {
    "BUY": {
        "explanation": (
            "Technical indicators suggest bullish momentum. "
            "The stock shows positive price action with improving volume patterns. "
            "Consider this as a potential buying opportunity."
        ),
        "factors": [
            "Positive momentum indicators",
            "Favorable price action",
            "Volume confirmation",
        ],
        "sentiment": "bullish",
    },
    "SELL": {
        "explanation": (
            "Technical indicators suggest bearish pressure. "
            "The stock shows weakening price action with declining volume. "
            "Consider reducing exposure or taking profits."
        ),
        "factors": [
            "Negative momentum indicators",
            "Weakening price action",
            "Volume decline",
        ],
        "sentiment": "bearish",
    },
    "HOLD": {
        "explanation": (
            "Technical indicators are neutral or mixed. "
            "The stock is consolidating without clear directional bias. "
            "Consider waiting for clearer signals before taking action."
        ),
        "factors": [
            "Mixed signals",
            "Consolidation pattern",
            "Low conviction setup",
        ],
        "sentiment": "neutral",
    },
}


# ============================================================================
# CACHE IMPLEMENTATION
# ============================================================================


class TTLCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, ttl: int = 3600):
        self._cache: Dict[str, tuple] = {}
        self._ttl = ttl

    def _generate_key(self, prefix: str, *args) -> str:
        """Generate a cache key from prefix and arguments."""
        key_data = f"{prefix}:{':'.join(str(a) for a in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get a cached value if it exists and is not expired."""
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        if time.time() - timestamp > self._ttl:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any) -> None:
        """Set a cached value with the current timestamp."""
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def cleanup(self) -> int:
        """Remove expired entries and return count of removed items."""
        now = time.time()
        expired = [k for k, (_, ts) in self._cache.items() if now - ts > self._ttl]
        for k in expired:
            del self._cache[k]
        return len(expired)


# Global cache instance
_llm_cache = TTLCache(ttl=LLM_CACHE_TTL)


# ============================================================================
# LLM SERVICE CLASS
# ============================================================================


class LLMService:
    """
    Service class for LLM-powered market analysis.

    Supports multiple providers with automatic fallback and caching.
    """

    def __init__(
        self,
        provider: str = LLM_PROVIDER,
        cache_ttl: int = LLM_CACHE_TTL,
    ):
        self.provider = provider
        self.cache = TTLCache(ttl=cache_ttl)
        self._client: Optional[httpx.AsyncClient] = None

        # Get provider config
        if provider not in PROVIDER_CONFIGS:
            logger.warning(f"Unknown provider {provider}, falling back to groq")
            provider = "groq"

        self.config = PROVIDER_CONFIGS[provider]
        self.api_key = os.getenv(self.config["api_key_env"], "")

        if not self.api_key:
            logger.warning(f"No API key found for {provider}. LLM features disabled.")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create an async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """
        Generate text using the configured LLM provider.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens in response
            temperature: Creativity parameter (0-1)

        Returns:
            Generated text or None if failed
        """
        if not self.api_key:
            logger.warning("No API key configured, cannot generate")
            return None

        try:
            client = await self._get_client()

            headers = {
                "Content-Type": "application/json",
            }

            # Provider-specific setup
            if self.provider == "anthropic":
                headers["x-api-key"] = self.api_key
                headers["anthropic-version"] = "2023-06-01"
                payload = {
                    "model": self.config["model"],
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                }
                if system_prompt:
                    payload["system"] = system_prompt
            else:
                # OpenAI-compatible (Groq, OpenAI)
                headers["Authorization"] = f"Bearer {self.api_key}"
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": self.config["model"],
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }

            response = await client.post(
                self.config["base_url"],
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            # Extract content based on provider
            if self.provider == "anthropic":
                return data["content"][0]["text"]
            else:
                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return None

    async def explain_signal(
        self,
        ticker: str,
        signal: str,
        confidence: float,
        indicators: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate an explanation for a trading signal.

        Args:
            ticker: Stock ticker symbol
            signal: Trading signal (BUY/SELL/HOLD)
            confidence: Confidence score (0-100)
            indicators: Optional dict of technical indicators
            use_cache: Whether to use cached responses

        Returns:
            Dict with explanation, factors, sentiment, and metadata
        """
        # Normalize signal
        signal = signal.upper()
        if signal not in ["BUY", "SELL", "HOLD"]:
            signal = "HOLD"

        # Check cache
        cache_key = self.cache._generate_key(
            "explain", ticker, signal, round(confidence, 0), datetime.now().strftime("%Y-%m-%d")
        )

        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                cached["cached"] = True
                return cached

        # Try LLM generation
        result = await self._generate_explanation(ticker, signal, confidence, indicators)

        if result:
            result["cached"] = False
            result["fallback"] = False
            if use_cache:
                self.cache.set(cache_key, result)
            return result

        # Use fallback
        fallback = FALLBACK_EXPLANATIONS.get(signal, FALLBACK_EXPLANATIONS["HOLD"]).copy()
        fallback["ticker"] = ticker
        fallback["signal"] = signal
        fallback["confidence"] = confidence
        fallback["cached"] = False
        fallback["fallback"] = True
        fallback["generated_at"] = datetime.utcnow().isoformat() + "Z"

        return fallback

    async def _generate_explanation(
        self,
        ticker: str,
        signal: str,
        confidence: float,
        indicators: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Internal method to generate explanation via LLM."""
        from .prompts import EXPLAIN_SIGNAL_PROMPT, EXPLAIN_SYSTEM_PROMPT

        # Build indicator context
        indicator_text = ""
        if indicators:
            indicator_lines = [f"- {k}: {v}" for k, v in indicators.items()]
            indicator_text = "\n".join(indicator_lines)

        prompt = EXPLAIN_SIGNAL_PROMPT.format(
            ticker=ticker,
            signal=signal,
            confidence=confidence,
            indicators=indicator_text or "No specific indicators provided",
        )

        response = await self.generate(
            prompt=prompt,
            system_prompt=EXPLAIN_SYSTEM_PROMPT,
            max_tokens=400,
            temperature=0.7,
        )

        if not response:
            return None

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_text = response
            if "```json" in response:
                json_text = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_text = response.split("```")[1].split("```")[0]

            data = json.loads(json_text.strip())

            return {
                "ticker": ticker,
                "signal": signal,
                "confidence": confidence,
                "explanation": data.get("explanation", ""),
                "factors": data.get("factors", [])[:5],  # Max 5 factors
                "sentiment": data.get("sentiment", "neutral"),
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            # Try to extract text directly
            return {
                "ticker": ticker,
                "signal": signal,
                "confidence": confidence,
                "explanation": response[:500],  # Truncate if too long
                "factors": [],
                "sentiment": (
                    "bullish" if signal == "BUY" else "bearish" if signal == "SELL" else "neutral"
                ),
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }

    async def explain_regime(
        self,
        regime: str,
        regime_data: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate an explanation for the current market regime.

        Args:
            regime: Current regime (RISK_ON, RISK_OFF, NEUTRAL)
            regime_data: Optional dict with regime indicators
            use_cache: Whether to use cached responses

        Returns:
            Dict with regime explanation and metadata
        """
        cache_key = self.cache._generate_key("regime", regime, datetime.now().strftime("%Y-%m-%d"))

        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                cached["cached"] = True
                return cached

        result = await self._generate_regime_explanation(regime, regime_data)

        if result:
            result["cached"] = False
            result["fallback"] = False
            if use_cache:
                self.cache.set(cache_key, result)
            return result

        # Fallback
        fallback = {
            "regime": regime,
            "explanation": f"The market is currently in {regime} mode based on technical and macro indicators.",
            "factors": ["VIX levels", "Market breadth", "Sector rotation"],
            "cached": False,
            "fallback": True,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
        return fallback

    async def _generate_regime_explanation(
        self,
        regime: str,
        regime_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Internal method to generate regime explanation via LLM."""
        from .prompts import EXPLAIN_REGIME_PROMPT, EXPLAIN_SYSTEM_PROMPT

        data_text = ""
        if regime_data:
            data_lines = [f"- {k}: {v}" for k, v in regime_data.items()]
            data_text = "\n".join(data_lines)

        prompt = EXPLAIN_REGIME_PROMPT.format(
            regime=regime,
            regime_data=data_text or "No specific data provided",
        )

        response = await self.generate(
            prompt=prompt,
            system_prompt=EXPLAIN_SYSTEM_PROMPT,
            max_tokens=400,
            temperature=0.7,
        )

        if not response:
            return None

        try:
            json_text = response
            if "```json" in response:
                json_text = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_text = response.split("```")[1].split("```")[0]

            data = json.loads(json_text.strip())

            return {
                "regime": regime,
                "explanation": data.get("explanation", ""),
                "factors": data.get("factors", [])[:5],
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
        except json.JSONDecodeError:
            return {
                "regime": regime,
                "explanation": response[:500],
                "factors": [],
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the singleton LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


async def cleanup_llm_service() -> None:
    """Cleanup the LLM service on shutdown."""
    global _llm_service
    if _llm_service:
        await _llm_service.close()
        _llm_service = None
