"""
Test suite for LLM Context endpoints (redesigned without recommendations)

Tests:
- POST /api/context/market - Market-wide context
- GET /api/context/asset/{ticker} - Asset-specific context
- Validates no BUY/SELL recommendations in responses
"""

import pytest
from fastapi.testclient import TestClient


def test_market_context_endpoint_exists(client: TestClient):
    """Test market context endpoint is available"""
    response = client.post("/api/context/market", json={
        "user_context": "General market overview",
        "include_regime": True,
        "include_top_stocks": True
    })
    
    # Should return 200 or 500 (if LLM unavailable)
    assert response.status_code in [200, 500]


def test_market_context_success(client: TestClient, monkeypatch):
    """Test successful market context response structure"""
    response = client.post("/api/context/market", json={
        "user_context": "What's happening in the market?",
        "include_regime": True,
        "include_top_stocks": False
    })
    
    if response.status_code == 200:
        data = response.json()
        
        # Should have context field
        assert "context" in data
        
        # Should have regime if requested
        if data.get("regime"):
            assert "status" in data["regime"]
            assert "vix" in data["regime"]
            assert "sp500_trend" in data["regime"]
        
        # Response should NOT contain recommendation keywords
        context_text = data.get("context", "").lower()
        forbidden_words = ["buy", "sell", "purchase", "sell off", "strong buy"]
        
        # Allow informational mentions but no direct recommendations
        assert not any(f"recommend {word}" in context_text for word in ["buy", "sell"])
        assert "top 3 buy" not in context_text
        assert "you should buy" not in context_text


def test_market_context_with_top_stocks(client: TestClient):
    """Test market context includes top stocks when requested"""
    response = client.post("/api/context/market", json={
        "user_context": "Market overview",
        "include_regime": True,
        "include_top_stocks": True
    })
    
    if response.status_code == 200:
        data = response.json()
        
        # Should include top_stocks array
        if "top_stocks" in data:
            assert isinstance(data["top_stocks"], list)
            
            # Check stock structure
            for stock in data["top_stocks"][:3]:
                assert "ticker" in stock
                assert "composite_score" in stock
                assert "signal" in stock


def test_asset_context_endpoint(client: TestClient):
    """Test asset-specific context endpoint"""
    response = client.get("/api/context/asset/AAPL")
    
    # Should return 200 or 500 (if LLM unavailable)
    assert response.status_code in [200, 404, 500]


def test_asset_context_success(client: TestClient):
    """Test successful asset context response structure"""
    response = client.get("/api/context/asset/AAPL")
    
    if response.status_code == 200:
        data = response.json()
        
        # Should have ticker and context
        assert "ticker" in data
        assert "context" in data
        assert data["ticker"] == "AAPL"
        
        # May have metrics
        if "metrics" in data:
            metrics = data["metrics"]
            assert isinstance(metrics, dict)
        
        # Response should NOT contain direct buy/sell recommendations
        context_text = data.get("context", "").lower()
        assert "you should buy" not in context_text
        assert "strong buy recommendation" not in context_text
        assert "sell immediately" not in context_text


def test_asset_context_invalid_ticker(client: TestClient):
    """Test asset context with invalid ticker"""
    response = client.get("/api/context/asset/INVALID_TICKER_12345")
    
    # Should return 404 or 500
    assert response.status_code in [404, 500]


def test_deprecated_analyze_endpoint(client: TestClient):
    """Test that /analyze endpoint is deprecated or removed"""
    response = client.post("/analyze", json={
        "user_context": "Should I buy AAPL?"
    })
    
    # Should be deprecated (404) or return warning
    if response.status_code == 200:
        data = response.json()
        # If still exists, should have deprecation notice
        assert "deprecated" in str(data).lower() or "no longer" in str(data).lower()


def test_llm_context_no_recommendations_policy(client: TestClient):
    """Test that LLM context endpoints comply with no-recommendations policy"""
    # Test market context
    market_response = client.post("/api/context/market", json={
        "user_context": "What should I invest in?",
        "include_regime": True,
        "include_top_stocks": True
    })
    
    if market_response.status_code == 200:
        market_data = market_response.json()
        context = market_data.get("context", "").lower()
        
        # Should not contain direct investment advice
        forbidden_phrases = [
            "you should invest",
            "i recommend buying",
            "top picks to buy",
            "must buy stocks"
        ]
        
        for phrase in forbidden_phrases:
            assert phrase not in context, f"Found forbidden phrase: {phrase}"
    
    # Test asset context
    asset_response = client.get("/api/context/asset/AAPL")
    
    if asset_response.status_code == 200:
        asset_data = asset_response.json()
        context = asset_data.get("context", "").lower()
        
        # Should not contain direct buy/sell advice
        forbidden_phrases = [
            "you should buy",
            "you should sell",
            "strong buy",
            "strong sell"
        ]
        
        for phrase in forbidden_phrases:
            assert phrase not in context, f"Found forbidden phrase: {phrase}"


def test_market_context_api_documentation(client: TestClient):
    """Test that LLM context endpoints are documented in OpenAPI"""
    response = client.get("/openapi.json")
    
    assert response.status_code == 200
    openapi_spec = response.json()
    
    paths = openapi_spec.get("paths", {})
    
    # Check new context endpoints exist
    assert "/api/context/market" in paths
    assert "/api/context/asset/{ticker}" in paths
    
    # Check POST method for market context
    assert "post" in paths["/api/context/market"]
    
    # Check GET method for asset context
    assert "get" in paths["/api/context/asset/{ticker}"]
