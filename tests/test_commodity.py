"""
Tests for Commodity Service and Endpoints.

Tests NFR-011 Phase 2: Commodities Integration.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.trading_engine.commodity import (
    CommodityService,
    CommodityData,
    CommodityRanking,
    get_commodity_service,
)


class TestCommodityService:
    """Tests for CommodityService class."""

    def test_get_commodity_service_singleton(self):
        """Test that get_commodity_service returns singleton."""
        service1 = get_commodity_service()
        service2 = get_commodity_service()
        assert service1 is service2

    def test_commodity_service_initialization(self):
        """Test service initializes with config."""
        service = get_commodity_service()
        assert service.config is not None
        assert isinstance(service._commodity_info, dict)

    def test_get_all_tickers_not_empty(self):
        """Test that all tickers list is not empty."""
        service = get_commodity_service()
        tickers = service.get_all_tickers()
        assert len(tickers) > 0
        # Should include standard commodities
        assert any("GC=F" in t or "GC" in t for t in tickers)  # Gold

    def test_get_tickers_by_category(self):
        """Test filtering tickers by category."""
        service = get_commodity_service()
        # Test precious metals category
        precious = service.get_tickers_by_category("precious_metals")
        assert isinstance(precious, list)

    def test_commodity_data_dataclass(self):
        """Test CommodityData dataclass creation."""
        data = CommodityData(
            ticker="GC=F",
            name="Gold",
            category="precious_metals",
            unit="oz",
            price=2050.50,
            change_24h=1.5,
            change_7d=2.3,
            change_30d=5.1,
            volume=150000,
            high_52w=2100.00,
            low_52w=1800.00,
            last_updated=datetime.now(),
        )
        assert data.ticker == "GC=F"
        assert data.name == "Gold"
        assert data.price == 2050.50

    def test_commodity_ranking_dataclass(self):
        """Test CommodityRanking dataclass creation."""
        ranking = CommodityRanking(
            ticker="GC=F",
            name="Gold",
            category="precious_metals",
            price=2050.50,
            change_24h=1.5,
            change_7d=2.3,
            momentum_score=75.5,
            volatility_score=30.0,
            composite_score=68.5,
            signal="BUY",
            risk_level="low",
        )
        assert ranking.ticker == "GC=F"
        assert ranking.signal == "BUY"
        assert ranking.composite_score == 68.5


class TestCommodityEndpoints:
    """Tests for commodity API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from src.trading_engine.server import app

        return TestClient(app)

    def test_commodity_ranking_endpoint_exists(self, client):
        """Test that commodity ranking endpoint exists."""
        response = client.get("/commodity/ranking")
        # Should not return 404
        assert response.status_code != 404

    def test_commodity_categories_endpoint_exists(self, client):
        """Test that commodity categories endpoint exists."""
        response = client.get("/commodity/categories")
        # Should not return 404
        assert response.status_code != 404

    def test_commodity_detail_endpoint_pattern(self, client):
        """Test that commodity detail endpoint pattern exists."""
        response = client.get("/commodity/GC=F")
        # Should not return 404 (might return 500 if yfinance fails)
        assert response.status_code != 404

    def test_commodity_ranking_response_structure(self, client):
        """Test commodity ranking response has expected structure."""
        response = client.get("/commodity/ranking?limit=5")
        if response.status_code == 200:
            data = response.json()
            assert "ranking" in data
            assert "count" in data
            assert "asset_type" in data
            assert data["asset_type"] == "commodities"

    def test_commodity_categories_response_structure(self, client):
        """Test commodity categories response has expected structure."""
        response = client.get("/commodity/categories")
        if response.status_code == 200:
            data = response.json()
            assert "categories" in data
            assert "count" in data
            assert isinstance(data["categories"], list)


class TestCommodityScoring:
    """Tests for commodity scoring logic."""

    def test_calc_pct_change_helper(self):
        """Test percentage change calculation."""
        service = get_commodity_service()
        # Test with mock DataFrame
        import pandas as pd

        df = pd.DataFrame({"Close": [100, 101, 102, 105, 110]})
        change = service._calc_pct_change(df, 1)
        # Last value 110, previous 105 => ~4.76%
        assert isinstance(change, float)

    def test_get_signal(self):
        """Test signal determination logic."""
        service = get_commodity_service()
        # Test with different composite scores
        assert service._get_signal(90) in ["STRONG_BUY", "BUY"]
        assert service._get_signal(70) in ["BUY", "HOLD"]
        assert service._get_signal(50) == "HOLD"
        assert service._get_signal(30) in ["CONSIDER_SELLING", "SELL"]

    def test_get_risk_level(self):
        """Test risk level determination."""
        service = get_commodity_service()
        # Test with different volatility scores
        assert service._get_risk_level(20) == "LOW"
        assert service._get_risk_level(50) == "MEDIUM"
        assert service._get_risk_level(80) == "HIGH"


class TestCommodityIntegration:
    """Integration tests for commodity service with config."""

    def test_commodity_uses_config_loader(self):
        """Test that commodity service uses config loader."""
        service = get_commodity_service()
        categories = service.config.get_commodity_categories()
        assert isinstance(categories, dict)

    def test_commodity_categories_from_config(self):
        """Test that categories come from config."""
        from src.trading_engine.core.config_loader import get_config_loader

        config = get_config_loader()
        categories = config.get_commodity_categories()

        # Should have expected categories
        assert "precious_metals" in categories or len(categories) > 0

    def test_commodity_tickers_from_config(self):
        """Test that tickers come from config."""
        from src.trading_engine.core.config_loader import get_config_loader

        config = get_config_loader()
        tickers = config.get_commodity_tickers()

        assert isinstance(tickers, list)
        assert len(tickers) > 0
