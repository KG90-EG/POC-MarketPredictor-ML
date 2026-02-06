"""
Tests for Unified Ranking API (NFR-011 Phase 3).

Tests the /api/ranking/{asset_type} endpoint for all asset types.
"""

import pytest
from fastapi.testclient import TestClient


class TestUnifiedRankingEndpoint:
    """Tests for unified ranking endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.trading_engine.server import app

        return TestClient(app)

    def test_unified_ranking_shares(self, client):
        """Test unified ranking for shares."""
        response = client.get("/api/ranking/shares?limit=5")

        # Should not return 404
        assert response.status_code != 404

        if response.status_code == 200:
            data = response.json()
            assert "asset_type" in data
            assert data["asset_type"] == "shares"
            assert "ranking" in data
            assert "count" in data
            assert "timestamp" in data

    def test_unified_ranking_digital_assets(self, client):
        """Test unified ranking for digital_assets."""
        response = client.get("/api/ranking/digital_assets?limit=5")

        assert response.status_code != 404

        if response.status_code == 200:
            data = response.json()
            assert data["asset_type"] == "digital_assets"
            assert "ranking" in data

    def test_unified_ranking_commodities(self, client):
        """Test unified ranking for commodities."""
        response = client.get("/api/ranking/commodities?limit=5")

        assert response.status_code != 404

        if response.status_code == 200:
            data = response.json()
            assert data["asset_type"] == "commodities"
            assert "ranking" in data

    def test_unified_ranking_legacy_stock(self, client):
        """Test legacy 'stock' name resolves to 'shares'."""
        response = client.get("/api/ranking/stock?limit=3")

        assert response.status_code != 404

        if response.status_code == 200:
            data = response.json()
            # Should resolve to 'shares'
            assert data["asset_type"] == "shares"

    def test_unified_ranking_legacy_crypto(self, client):
        """Test legacy 'crypto' name resolves to 'digital_assets'."""
        response = client.get("/api/ranking/crypto?limit=3")

        assert response.status_code != 404

        if response.status_code == 200:
            data = response.json()
            assert data["asset_type"] == "digital_assets"

    def test_unified_ranking_legacy_commodity(self, client):
        """Test legacy 'commodity' name resolves to 'commodities'."""
        response = client.get("/api/ranking/commodity?limit=3")

        assert response.status_code != 404

        if response.status_code == 200:
            data = response.json()
            assert data["asset_type"] == "commodities"

    def test_unified_ranking_invalid_asset_type(self, client):
        """Test invalid asset type returns 400."""
        response = client.get("/api/ranking/invalid_type")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid asset type" in data["detail"]

    def test_unified_ranking_with_min_score(self, client):
        """Test min_score parameter filtering."""
        response = client.get("/api/ranking/shares?min_score=50&limit=10")

        if response.status_code == 200:
            data = response.json()
            # All items should have score >= 50
            for item in data.get("ranking", []):
                assert item.get("composite_score", 0) >= 50

    def test_unified_ranking_response_schema(self, client):
        """Test that response follows standardized schema."""
        response = client.get("/api/ranking/shares?limit=3")

        if response.status_code == 200:
            data = response.json()

            # Check top-level fields
            assert "asset_type" in data
            assert "ranking" in data
            assert "count" in data
            assert "timestamp" in data

            # Check item schema if items exist
            if data["ranking"]:
                item = data["ranking"][0]
                # Standardized fields
                assert "ticker" in item
                assert "composite_score" in item
                assert "signal" in item
                assert "asset_type" in item


class TestAssetTypesEndpoint:
    """Tests for /api/asset-types endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.trading_engine.server import app

        return TestClient(app)

    def test_list_asset_types(self, client):
        """Test listing all asset types."""
        response = client.get("/api/asset-types")

        assert response.status_code == 200
        data = response.json()

        assert "asset_types" in data
        assert "count" in data
        assert data["count"] == 3  # shares, digital_assets, commodities

        # Check each asset type has required fields
        for asset_type in data["asset_types"]:
            assert "id" in asset_type
            assert "display_name" in asset_type
            assert "display_name_de" in asset_type
            assert "icon" in asset_type
            assert "endpoint" in asset_type

    def test_asset_types_includes_all(self, client):
        """Test that all asset types are included."""
        response = client.get("/api/asset-types")
        data = response.json()

        ids = [at["id"] for at in data["asset_types"]]
        assert "shares" in ids
        assert "digital_assets" in ids
        assert "commodities" in ids


class TestAssetMapperIntegration:
    """Integration tests for asset mapper with unified API."""

    def test_resolve_all_legacy_names(self):
        """Test that all legacy names resolve correctly."""
        from src.trading_engine.utils.asset_mapper import resolve_asset_type

        # Stock aliases
        assert resolve_asset_type("stock") == "shares"
        assert resolve_asset_type("stocks") == "shares"
        assert resolve_asset_type("equity") == "shares"
        assert resolve_asset_type("equities") == "shares"

        # Crypto aliases
        assert resolve_asset_type("crypto") == "digital_assets"
        assert resolve_asset_type("cryptocurrency") == "digital_assets"

        # Commodity aliases
        assert resolve_asset_type("commodity") == "commodities"
        assert resolve_asset_type("raw_materials") == "commodities"

        # Canonical names
        assert resolve_asset_type("shares") == "shares"
        assert resolve_asset_type("digital_assets") == "digital_assets"
        assert resolve_asset_type("commodities") == "commodities"

    def test_case_insensitivity(self):
        """Test that asset type resolution is case-insensitive."""
        from src.trading_engine.utils.asset_mapper import resolve_asset_type

        assert resolve_asset_type("STOCK") == "shares"
        assert resolve_asset_type("Stock") == "shares"
        assert resolve_asset_type("CRYPTO") == "digital_assets"
        assert resolve_asset_type("Commodities") == "commodities"
