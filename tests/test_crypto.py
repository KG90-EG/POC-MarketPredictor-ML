"""Tests for cryptocurrency module"""
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from trading_fun.crypto import (
    get_crypto_market_data,
    get_crypto_details,
    compute_crypto_features,
    get_crypto_ranking,
    search_crypto,
    DEFAULT_CRYPTOS,
    NFT_TOKENS,
    COINGECKO_BASE_URL,
)


@pytest.fixture
def mock_market_data():
    """Sample market data from CoinGecko API"""
    return [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
            "current_price": 45000.0,
            "market_cap": 850000000000,
            "market_cap_rank": 1,
            "total_volume": 25000000000,
            "price_change_percentage_24h": 5.2,
            "price_change_percentage_7d_in_currency": 10.5,
            "price_change_percentage_30d_in_currency": 25.3,
        },
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "image": "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
            "current_price": 3000.0,
            "market_cap": 360000000000,
            "market_cap_rank": 2,
            "total_volume": 15000000000,
            "price_change_percentage_24h": 3.8,
            "price_change_percentage_7d_in_currency": 8.2,
            "price_change_percentage_30d_in_currency": 15.7,
        },
        {
            "id": "cardano",
            "symbol": "ada",
            "name": "Cardano",
            "image": "https://assets.coingecko.com/coins/images/975/large/cardano.png",
            "current_price": 0.65,
            "market_cap": 23000000000,
            "market_cap_rank": 8,
            "total_volume": 800000000,
            "price_change_percentage_24h": -2.5,
            "price_change_percentage_7d_in_currency": 1.2,
            "price_change_percentage_30d_in_currency": -5.3,
        },
    ]


@pytest.fixture
def mock_crypto_details():
    """Sample detailed crypto data"""
    return {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "market_data": {
            "current_price": {"usd": 45000.0},
            "market_cap": {"usd": 850000000000},
            "total_volume": {"usd": 25000000000},
            "price_change_percentage_24h": 5.2,
            "price_change_percentage_7d": 10.5,
            "price_change_percentage_30d": 25.3,
        },
        "community_data": {
            "twitter_followers": 5000000,
            "reddit_subscribers": 4000000,
        },
    }


class TestGetCryptoMarketData:
    """Test crypto market data fetching"""

    @patch("trading_fun.crypto.requests.get")
    def test_get_market_data_with_specific_cryptos(self, mock_get, mock_market_data):
        """Test fetching market data for specific cryptocurrencies"""
        mock_response = Mock()
        mock_response.json.return_value = mock_market_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_crypto_market_data(crypto_ids=["bitcoin", "ethereum"])

        assert len(result) == 3
        assert result[0]["id"] == "bitcoin"
        assert result[1]["id"] == "ethereum"
        mock_get.assert_called_once()

        # Check that the request was made with correct parameters
        call_args = mock_get.call_args
        assert call_args[0][0] == f"{COINGECKO_BASE_URL}/coins/markets"
        assert "bitcoin,ethereum" in call_args[1]["params"]["ids"]

    @patch("trading_fun.crypto.requests.get")
    def test_get_market_data_top_cryptos(self, mock_get, mock_market_data):
        """Test fetching top cryptocurrencies by market cap"""
        mock_response = Mock()
        mock_response.json.return_value = mock_market_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_crypto_market_data(crypto_ids=None, limit=50)

        assert len(result) == 3
        mock_get.assert_called_once()

        # Check parameters for top cryptos
        call_args = mock_get.call_args
        assert call_args[1]["params"]["order"] == "market_cap_desc"
        assert call_args[1]["params"]["per_page"] == 50

    @patch("trading_fun.crypto.requests.get")
    def test_get_market_data_with_nft_tokens(self, mock_get, mock_market_data):
        """Test that NFT tokens are included when requested"""
        mock_response = Mock()
        mock_response.json.return_value = mock_market_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_crypto_market_data(
            crypto_ids=DEFAULT_CRYPTOS, include_nft=True
        )

        # Should include both DEFAULT_CRYPTOS and NFT_TOKENS
        call_args = mock_get.call_args
        ids_param = call_args[1]["params"]["ids"]
        assert len(ids_param.split(",")) == len(DEFAULT_CRYPTOS) + len(NFT_TOKENS)

    @patch("trading_fun.crypto.requests.get")
    def test_get_market_data_request_exception(self, mock_get):
        """Test handling of request exceptions"""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        result = get_crypto_market_data(crypto_ids=["bitcoin"])

        assert result == []

    @patch("trading_fun.crypto.requests.get")
    def test_get_market_data_timeout(self, mock_get):
        """Test handling of timeout errors"""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        result = get_crypto_market_data(crypto_ids=["bitcoin"])

        assert result == []

    @patch("trading_fun.crypto.requests.get")
    def test_get_market_data_http_error(self, mock_get):
        """Test handling of HTTP errors"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Not Found"
        )
        mock_get.return_value = mock_response

        result = get_crypto_market_data(crypto_ids=["invalid-crypto"])

        assert result == []


class TestGetCryptoDetails:
    """Test crypto details fetching"""

    @patch("trading_fun.crypto.requests.get")
    def test_get_crypto_details_success(self, mock_get, mock_crypto_details):
        """Test successful fetching of crypto details"""
        mock_response = Mock()
        mock_response.json.return_value = mock_crypto_details
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_crypto_details("bitcoin")

        assert result is not None
        assert result["id"] == "bitcoin"
        assert result["symbol"] == "btc"
        assert "market_data" in result
        assert "community_data" in result

        # Verify correct endpoint called
        call_args = mock_get.call_args
        assert call_args[0][0] == f"{COINGECKO_BASE_URL}/coins/bitcoin"

    @patch("trading_fun.crypto.requests.get")
    def test_get_crypto_details_not_found(self, mock_get):
        """Test handling when crypto is not found"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404"
        )
        mock_get.return_value = mock_response

        result = get_crypto_details("invalid-crypto-id")

        assert result is None

    @patch("trading_fun.crypto.requests.get")
    def test_get_crypto_details_exception(self, mock_get):
        """Test handling of general exceptions"""
        mock_get.side_effect = Exception("Unexpected error")

        result = get_crypto_details("bitcoin")

        assert result is None


class TestComputeCryptoFeatures:
    """Test crypto feature computation"""

    def test_compute_features_high_momentum(self, mock_market_data):
        """Test feature computation for high momentum crypto"""
        result = compute_crypto_features(mock_market_data[0])  # Bitcoin

        assert result["symbol"] == "BTC"
        assert result["name"] == "Bitcoin"
        assert result["price"] == 45000.0
        assert result["change_24h"] == 5.2
        assert result["change_7d"] == 10.5
        assert result["change_30d"] == 25.3
        assert result["market_cap_rank"] == 1
        assert result["momentum_score"] > 0.8  # High momentum
        assert result["probability"] == result["momentum_score"]
        assert result["crypto_id"] == "bitcoin"

    def test_compute_features_low_momentum(self, mock_market_data):
        """Test feature computation for low momentum crypto"""
        result = compute_crypto_features(mock_market_data[2])  # Cardano

        assert result["symbol"] == "ADA"
        assert result["change_24h"] == -2.5
        assert result["momentum_score"] < 0.5  # Lower momentum
        assert 0 <= result["momentum_score"] <= 1.0

    def test_compute_features_volume_ratio(self, mock_market_data):
        """Test volume to market cap ratio calculation"""
        result = compute_crypto_features(mock_market_data[0])

        expected_ratio = (25000000000 / 850000000000) * 100
        assert abs(result["volume_to_mcap_ratio"] - expected_ratio) < 0.01

    def test_compute_features_rank_contribution(self):
        """Test that market cap rank contributes to momentum score"""
        # Top 10 crypto
        top_crypto = {
            "id": "test1",
            "symbol": "test",
            "name": "Test",
            "market_cap_rank": 5,
            "current_price": 100,
            "market_cap": 1000000000,
            "total_volume": 50000000,
            "price_change_percentage_24h": 0,
            "price_change_percentage_7d_in_currency": 0,
            "price_change_percentage_30d_in_currency": 0,
        }

        result_top = compute_crypto_features(top_crypto)

        # Outside top 50
        low_crypto = top_crypto.copy()
        low_crypto["market_cap_rank"] = 100

        result_low = compute_crypto_features(low_crypto)

        # Top ranked should have higher momentum
        assert result_top["momentum_score"] > result_low["momentum_score"]

    def test_compute_features_missing_data(self):
        """Test handling of missing or None values"""
        incomplete_data = {
            "id": "test",
            "symbol": "test",
            "name": "Test",
            "current_price": 100,
            "market_cap": 1000000,
            "total_volume": 50000,
            "market_cap_rank": 50,
            "price_change_percentage_24h": None,  # Missing
            "price_change_percentage_7d_in_currency": None,  # Missing
            "price_change_percentage_30d_in_currency": None,  # Missing
        }

        result = compute_crypto_features(incomplete_data)

        assert result["change_24h"] == 0
        assert result["change_7d"] == 0
        assert result["change_30d"] == 0
        assert result["momentum_score"] >= 0

    def test_compute_features_zero_market_cap(self):
        """Test handling of zero market cap (avoid division by zero)"""
        data = {
            "id": "test",
            "symbol": "test",
            "name": "Test",
            "current_price": 0.001,
            "market_cap": 0,  # Zero market cap
            "total_volume": 1000,
            "market_cap_rank": 999,
            "price_change_percentage_24h": 5,
            "price_change_percentage_7d_in_currency": 10,
            "price_change_percentage_30d_in_currency": 15,
        }

        result = compute_crypto_features(data)

        assert result["volume_to_mcap_ratio"] == 0
        assert result["momentum_score"] >= 0

    def test_compute_features_exception_handling(self):
        """Test that invalid data returns default values gracefully"""
        invalid_data = {"invalid": "data"}

        result = compute_crypto_features(invalid_data)

        # Function handles missing data gracefully with defaults
        assert isinstance(result, dict)
        assert result["symbol"] == ""
        assert result["momentum_score"] >= 0


class TestGetCryptoRanking:
    """Test crypto ranking functionality"""

    @patch("trading_fun.crypto.get_crypto_market_data")
    def test_get_ranking_with_filtering(self, mock_get_data, mock_market_data):
        """Test ranking with probability filtering"""
        mock_get_data.return_value = mock_market_data

        result = get_crypto_ranking(min_probability=0.5)

        # Should filter out low momentum cryptos
        assert len(result) <= len(mock_market_data)
        for crypto in result:
            assert crypto["probability"] >= 0.5

    @patch("trading_fun.crypto.get_crypto_market_data")
    def test_get_ranking_sorted_by_momentum(self, mock_get_data, mock_market_data):
        """Test that results are sorted by momentum score"""
        mock_get_data.return_value = mock_market_data

        result = get_crypto_ranking()

        # Should be sorted descending by probability
        for i in range(len(result) - 1):
            assert result[i]["probability"] >= result[i + 1]["probability"]

    @patch("trading_fun.crypto.get_crypto_market_data")
    def test_get_ranking_empty_data(self, mock_get_data):
        """Test handling of empty market data"""
        mock_get_data.return_value = []

        result = get_crypto_ranking()

        assert result == []

    @patch("trading_fun.crypto.get_crypto_market_data")
    def test_get_ranking_with_custom_limit(self, mock_get_data, mock_market_data):
        """Test custom limit parameter"""
        mock_get_data.return_value = mock_market_data

        result = get_crypto_ranking(limit=100)

        mock_get_data.assert_called_once()
        call_args = mock_get_data.call_args
        assert call_args[1]["limit"] == 100

    @patch("trading_fun.crypto.get_crypto_market_data")
    def test_get_ranking_with_specific_cryptos(self, mock_get_data, mock_market_data):
        """Test ranking specific cryptocurrencies"""
        mock_get_data.return_value = mock_market_data

        crypto_list = ["bitcoin", "ethereum"]
        result = get_crypto_ranking(crypto_ids=crypto_list)

        mock_get_data.assert_called_once_with(
            crypto_ids=crypto_list, include_nft=True, limit=50
        )


class TestSearchCrypto:
    """Test crypto search functionality"""

    @patch("trading_fun.crypto.requests.get")
    @patch("trading_fun.crypto.get_crypto_market_data")
    def test_search_crypto_found(self, mock_get_data, mock_requests_get, mock_market_data):
        """Test successful crypto search"""
        # Mock search API response
        mock_search_response = Mock()
        mock_search_response.json.return_value = {
            "coins": [
                {"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC"}
            ]
        }
        mock_search_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_search_response

        # Mock market data
        mock_get_data.return_value = [mock_market_data[0]]

        result = search_crypto("bitcoin")

        assert result is not None
        assert result["name"] == "Bitcoin"
        assert result["symbol"] == "BTC"

    @patch("trading_fun.crypto.requests.get")
    def test_search_crypto_not_found(self, mock_get):
        """Test search when no results found"""
        mock_response = Mock()
        mock_response.json.return_value = {"coins": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = search_crypto("nonexistent-crypto")

        assert result is None

    @patch("trading_fun.crypto.requests.get")
    def test_search_crypto_exception(self, mock_get):
        """Test search with exception"""
        mock_get.side_effect = Exception("Search failed")

        result = search_crypto("bitcoin")

        assert result is None

    @patch("trading_fun.crypto.requests.get")
    @patch("trading_fun.crypto.get_crypto_market_data")
    def test_search_crypto_no_market_data(self, mock_get_data, mock_requests_get):
        """Test search when market data fetch fails"""
        # Mock search succeeds
        mock_search_response = Mock()
        mock_search_response.json.return_value = {
            "coins": [{"id": "bitcoin"}]
        }
        mock_search_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_search_response

        # Mock market data fails
        mock_get_data.return_value = []

        result = search_crypto("bitcoin")

        assert result is None


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_momentum_score_capped_at_one(self):
        """Test that momentum score never exceeds 1.0"""
        # Create data with all maximum positive values
        perfect_data = {
            "id": "test",
            "symbol": "test",
            "name": "Test",
            "market_cap_rank": 1,  # Top rank
            "current_price": 100000,
            "market_cap": 1000000000000,
            "total_volume": 500000000000,  # Very high volume
            "price_change_percentage_24h": 50,  # Huge gains
            "price_change_percentage_7d_in_currency": 100,
            "price_change_percentage_30d_in_currency": 200,
        }

        result = compute_crypto_features(perfect_data)

        assert result["momentum_score"] <= 1.0
        assert result["momentum_score"] == 1.0  # Should be capped

    def test_negative_momentum_score(self):
        """Test that momentum score is never negative"""
        # Create data with all negative values
        bad_data = {
            "id": "test",
            "symbol": "test",
            "name": "Test",
            "market_cap_rank": 999,
            "current_price": 0.0001,
            "market_cap": 1000,
            "total_volume": 10,
            "price_change_percentage_24h": -50,
            "price_change_percentage_7d_in_currency": -75,
            "price_change_percentage_30d_in_currency": -90,
        }

        result = compute_crypto_features(bad_data)

        assert result["momentum_score"] >= 0


class TestConstants:
    """Test module constants"""

    def test_default_cryptos_list(self):
        """Test DEFAULT_CRYPTOS is properly defined"""
        assert isinstance(DEFAULT_CRYPTOS, list)
        assert len(DEFAULT_CRYPTOS) > 0
        assert "bitcoin" in DEFAULT_CRYPTOS
        assert "ethereum" in DEFAULT_CRYPTOS

    def test_nft_tokens_list(self):
        """Test NFT_TOKENS is properly defined"""
        assert isinstance(NFT_TOKENS, list)
        assert len(NFT_TOKENS) > 0
        # Check for known NFT tokens
        assert any("sand" in token or "mana" in token for token in NFT_TOKENS)

    def test_base_url(self):
        """Test COINGECKO_BASE_URL is correct"""
        assert COINGECKO_BASE_URL == "https://api.coingecko.com/api/v3"
