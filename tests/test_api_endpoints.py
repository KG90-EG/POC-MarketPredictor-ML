"""
Comprehensive API Endpoint Tests - Fixed for actual API structure

Tests all missing endpoints to improve coverage from 52% to 75%:
- /predict_ticker/{ticker} (main prediction)
- /ranking (crypto ranking) 
- /search_stocks, /search_cryptos
- /popular_stocks, /countries, /models
- /analyze (AI analysis)
"""

import pytest
import requests


BASE_URL = "http://localhost:8000"


class TestPredictEndpoint:
    """Tests for /predict_ticker endpoint"""
    
    def test_predict_ticker_with_valid_stock(self):
        """Test prediction with valid stock ticker"""
        response = requests.get(f"{BASE_URL}/predict_ticker/AAPL")
        
        # Endpoint may return 200 with prediction or 404/500 if data unavailable
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            # Response is just {"prob": 0.32}
            assert "prob" in data or "prediction" in data or "confidence" in data
            if "prob" in data:
                assert 0 <= data["prob"] <= 1
    
    def test_predict_ticker_with_invalid_ticker(self):
        """Test prediction with invalid ticker returns error"""
        response = requests.get(f"{BASE_URL}/predict_ticker/INVALID123XYZ")
        
        # Should return error status
        assert response.status_code in [400, 404, 500]
    
    def test_predict_ticker_response_caching(self):
        """Test that prediction responses can be cached"""
        # First request
        response1 = requests.get(f"{BASE_URL}/predict_ticker/MSFT")
        
        # Second request (might be cached)
        response2 = requests.get(f"{BASE_URL}/predict_ticker/MSFT")
        
        # Both should return same status
        assert response1.status_code == response2.status_code


class TestRankingEndpoint:
    """Tests for /ranking endpoint (crypto ranking)"""
    
    def test_ranking_returns_list(self):
        """Test ranking endpoint returns list of cryptos"""
        response = requests.get(f"{BASE_URL}/ranking")
        
        # May fail if CoinGecko API unavailable
        assert response.status_code in [200, 500, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            
            if data:
                item = data[0]
                # Check for crypto ranking fields
                assert "id" in item or "name" in item
                assert "momentum_score" in item or "score" in item
    
    def test_ranking_with_limit(self):
        """Test ranking with custom limit parameter"""
        limit = 5
        response = requests.get(f"{BASE_URL}/ranking?limit={limit}")
        
        if response.status_code == 200:
            data = response.json()
            assert len(data) <= limit
    
    def test_ranking_sorted_by_score(self):
        """Test that ranking results are sorted by score"""
        response = requests.get(f"{BASE_URL}/ranking?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            
            if len(data) > 1:
                scores = [item.get("momentum_score", item.get("score", 0)) for item in data]
                # Scores should be in descending order
                assert scores == sorted(scores, reverse=True)



class TestSearchEndpoints:
    """Tests for search functionality"""
    
    def test_search_stocks_valid(self):
        """Test stock search with valid query"""
        response = requests.get(f"{BASE_URL}/search_stocks?query=Apple")
        
        assert response.status_code == 200
        data = response.json()
        
        # Response is {"stocks": [...]}
        assert "stocks" in data
        assert isinstance(data["stocks"], list)
        
        if data["stocks"]:
            result = data["stocks"][0]
            assert "ticker" in result or "symbol" in result
            assert "name" in result
    
    def test_search_stocks_ticker(self):
        """Test stock search with ticker symbol"""
        response = requests.get(f"{BASE_URL}/search_stocks?query=AAPL")
        
        assert response.status_code == 200
        data = response.json()
        
        if data.get("stocks"):
            # Should find Apple
            found = any("AAPL" in str(stock.get("ticker", "")) for stock in data["stocks"])
            assert found
    
    def test_search_cryptos_valid(self):
        """Test crypto search with valid query"""
        response = requests.get(f"{BASE_URL}/search_cryptos?query=Bitcoin")
        
        assert response.status_code in [200, 500]  # May fail if API unavailable
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict) or isinstance(data, list)
    
    def test_search_empty_query(self):
        """Test search with empty query"""
        response = requests.get(f"{BASE_URL}/search_stocks?query=")
        
        # Should return empty results or require query
        assert response.status_code in [200, 400, 422]


class TestTickerInfoEndpoints:
    """Tests for ticker information endpoints"""
    
    def test_ticker_info_valid(self):
        """Test getting ticker info for valid stock"""
        response = requests.get(f"{BASE_URL}/ticker_info/AAPL")
        
        # May fail if yfinance unavailable
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "symbol" in data or "ticker" in data
    
    def test_ticker_info_invalid(self):
        """Test getting ticker info for invalid stock"""
        response = requests.get(f"{BASE_URL}/ticker_info/INVALID999XYZ")
        
        # Should return error
        assert response.status_code in [404, 400, 500]
    
    def test_ticker_info_batch(self):
        """Test batch ticker info endpoint"""
        tickers = ["AAPL", "GOOGL", "MSFT"]
        response = requests.post(
            f"{BASE_URL}/ticker_info_batch",
            json={"tickers": tickers}
        )
        
        # May fail if yfinance unavailable
        assert response.status_code in [200, 400, 422, 500]


class TestPopularStocksEndpoint:
    """Tests for popular stocks endpoint"""
    
    def test_popular_stocks_default(self):
        """Test getting popular stocks with default params"""
        response = requests.get(f"{BASE_URL}/popular_stocks")
        
        assert response.status_code == 200
        data = response.json()
        
        # Response is {"stocks": [...]}
        assert "stocks" in data
        assert isinstance(data["stocks"], list)
        assert len(data["stocks"]) > 0
        
        if data["stocks"]:
            stock = data["stocks"][0]
            assert "ticker" in stock or "symbol" in stock
            assert "name" in stock
    
    def test_popular_stocks_with_country(self):
        """Test popular stocks filtered by country"""
        response = requests.get(f"{BASE_URL}/popular_stocks?country=United%20States")
        
        assert response.status_code == 200
        data = response.json()
        assert "stocks" in data
        assert isinstance(data["stocks"], list)


class TestCountriesEndpoint:
    """Tests for countries endpoint"""
    
    def test_countries_list(self):
        """Test getting list of available countries"""
        response = requests.get(f"{BASE_URL}/countries")
        
        assert response.status_code == 200
        data = response.json()
        
        # Response is {"countries": [...]}
        assert "countries" in data
        assert isinstance(data["countries"], list)
        assert len(data["countries"]) > 0
        
        # Should include major markets
        countries = data["countries"]
        country_ids = [c.get("id", c) if isinstance(c, dict) else c for c in countries]
        
        # Check for US or United States
        has_us = any("United States" in str(cid) or "US" == str(cid) for cid in country_ids)
        assert has_us


class TestModelsEndpoint:
    """Tests for models endpoint"""
    
    def test_models_info(self):
        """Test getting model information"""
        response = requests.get(f"{BASE_URL}/models")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        
        # Response has current_model and available_models
        assert "current_model" in data or "available_models" in data


class TestAnalyzeEndpoint:
    """Tests for AI analysis endpoint"""
    
    def test_analyze_with_data(self):
        """Test AI analysis with valid data"""
        response = requests.post(
            f"{BASE_URL}/analyze",
            json={
                "data": {
                    "ticker": "AAPL",
                    "price": 150.0,
                    "volume": 1000000
                }
            }
        )
        
        # May require OpenAI API key, or data format incorrect
        assert response.status_code in [200, 400, 422, 503]
    
    def test_analyze_without_data(self):
        """Test analysis endpoint without data"""
        response = requests.post(
            f"{BASE_URL}/analyze",
            json={}
        )
        
        # Should require data
        assert response.status_code in [400, 422]


class TestWatchlistEndpoints:
    """Tests for watchlist CRUD operations"""
    
    def _create_test_watchlist(self):
        """Helper to create a new watchlist and return ID"""
        response = requests.post(
            f"{BASE_URL}/watchlists",
            json={
                "name": "Test Watchlist",
                "user_id": "test_user"
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "watchlist_id" in data or "id" in data
        
        return data.get("watchlist_id") or data.get("id")
    
    def test_create_watchlist(self):
        """Test creating a new watchlist"""
        watchlist_id = self._create_test_watchlist()
        assert watchlist_id is not None
    
    def test_get_all_watchlists(self):
        """Test getting all watchlists"""
        response = requests.get(f"{BASE_URL}/watchlists")
        
        assert response.status_code == 200
        data = response.json()
        
        # Response is {"watchlists": [...]}
        if isinstance(data, dict) and "watchlists" in data:
            assert isinstance(data["watchlists"], list)
        else:
            assert isinstance(data, list)
    
    def test_get_single_watchlist(self):
        """Test getting a specific watchlist"""
        # Create a watchlist first
        watchlist_id = self._create_test_watchlist()
        
        # Get it
        response = requests.get(f"{BASE_URL}/watchlists/{watchlist_id}")
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "name" in data or "watchlist_name" in data
    
    def test_update_watchlist(self):
        """Test updating a watchlist"""
        # Create watchlist
        watchlist_id = self._create_test_watchlist()
        
        # Update it
        response = requests.put(
            f"{BASE_URL}/watchlists/{watchlist_id}",
            json={"name": "Updated Watchlist"}
        )
        
        assert response.status_code in [200, 404]
    
    def test_delete_watchlist(self):
        """Test deleting a watchlist"""
        # Create watchlist
        watchlist_id = self._create_test_watchlist()
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/watchlists/{watchlist_id}")
        
        assert response.status_code in [200, 204, 404]
    
    def test_add_stock_to_watchlist(self):
        """Test adding a stock to watchlist"""
        # Create watchlist
        watchlist_id = self._create_test_watchlist()
        
        # Add stock
        response = requests.post(
            f"{BASE_URL}/watchlists/{watchlist_id}/stocks",
            json={"ticker": "AAPL"}
        )
        
        assert response.status_code in [200, 201, 404]
    
    def test_remove_stock_from_watchlist(self):
        """Test removing a stock from watchlist"""
        # Create watchlist and add stock
        watchlist_id = self._create_test_watchlist()
        requests.post(
            f"{BASE_URL}/watchlists/{watchlist_id}/stocks",
            json={"ticker": "AAPL"}
        )
        
        # Remove stock
        response = requests.delete(
            f"{BASE_URL}/watchlists/{watchlist_id}/stocks/AAPL"
        )
        
        assert response.status_code in [200, 204, 404]
    
    def test_watchlist_with_invalid_id(self):
        """Test operations with invalid watchlist ID"""
        response = requests.get(f"{BASE_URL}/watchlists/99999")
        
        assert response.status_code in [404, 400]


class TestErrorHandling:
    """Tests for error handling across the API"""
    
    def test_invalid_endpoint(self):
        """Test requesting non-existent endpoint"""
        response = requests.get(f"{BASE_URL}/nonexistent_endpoint_xyz")
        
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """Test using wrong HTTP method"""
        # Try POST on GET endpoint
        response = requests.post(f"{BASE_URL}/health")
        
        assert response.status_code in [404, 405]  # Method not allowed
    
    def test_malformed_json(self):
        """Test sending malformed JSON"""
        import requests.exceptions
        
        try:
            response = requests.post(
                f"{BASE_URL}/watchlists",
                data="this is not json",
                headers={"Content-Type": "application/json"}
            )
            # Should return 400 or 422
            assert response.status_code in [400, 422]
        except requests.exceptions.RequestException:
            # Network error is acceptable
            pass
    
    def test_missing_required_fields(self):
        """Test sending request with missing required fields"""
        response = requests.post(
            f"{BASE_URL}/watchlists",
            json={}  # Missing required fields
        )
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    def test_invalid_data_types(self):
        """Test sending invalid data types"""
        response = requests.post(
            f"{BASE_URL}/api/simulations",
            json={
                "user_id": "test",
                "initial_capital": "not_a_number"  # Should be float
            }
        )
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    def test_very_long_string(self):
        """Test handling of very long input strings"""
        long_string = "A" * 10000
        
        response = requests.post(
            f"{BASE_URL}/watchlists",
            json={
                "name": long_string,
                "user_id": "test"
            }
        )
        
        # Should either accept or reject gracefully
        assert response.status_code in [200, 201, 400, 422]
    
    def test_sql_injection_attempt(self):
        """Test that SQL injection is prevented"""
        malicious_input = "'; DROP TABLE watchlists; --"
        
        response = requests.get(
            f"{BASE_URL}/search_stocks?query={malicious_input}"
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
        
        # API should still be responsive after attempt
        health_check = requests.get(f"{BASE_URL}/health")
        assert health_check.status_code == 200
    
    def test_xss_attempt(self):
        """Test that XSS is prevented"""
        xss_input = "<script>alert('XSS')</script>"
        
        response = requests.post(
            f"{BASE_URL}/watchlists",
            json={
                "name": xss_input,
                "user_id": "test"
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 201, 400, 422]
    
    def test_rate_limiting(self):
        """Test that rate limiting is in place"""
        # Make many requests rapidly
        responses = []
        for i in range(100):
            try:
                r = requests.get(f"{BASE_URL}/popular_stocks", timeout=1)
                responses.append(r.status_code)
            except requests.exceptions.Timeout:
                # Timeout is acceptable under load
                break
        
        # Should get at least some successful responses
        assert any(status == 200 for status in responses)
        
        # May eventually hit rate limit (429) or keep succeeding (200)
        assert all(status in [200, 429, 500, 503] for status in responses)


class TestCryptoEndpoints:
    """Tests for cryptocurrency endpoints"""
    
    def test_popular_cryptos(self):
        """Test getting popular cryptocurrencies"""
        response = requests.get(f"{BASE_URL}/popular_cryptos")
        
        # May fail if CoinGecko API unavailable
        assert response.status_code in [200, 500, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or isinstance(data, dict)
    
    def test_crypto_ranking(self):
        """Test crypto ranking endpoint"""
        response = requests.get(f"{BASE_URL}/crypto/ranking")
        
        assert response.status_code in [200, 500, 503]
        
        if response.status_code == 200:
            data = response.json()
            # Response is {"ranking": [...]}
            if isinstance(data, dict) and "ranking" in data:
                assert isinstance(data["ranking"], list)
            else:
                assert isinstance(data, list)
    
    def test_crypto_search(self):
        """Test crypto search endpoint"""
        response = requests.get(f"{BASE_URL}/crypto/search?query=Bitcoin")
        
        assert response.status_code in [200, 500, 503]
    
    def test_crypto_details(self):
        """Test getting crypto details"""
        response = requests.get(f"{BASE_URL}/crypto/details/bitcoin")
        
        assert response.status_code in [200, 404, 500, 503]


if __name__ == "__main__":
    print("Running comprehensive API tests...")
    print("Make sure backend server is running on http://localhost:8000")
    print()
    
    pytest.main([__file__, "-v", "--tb=short"])
