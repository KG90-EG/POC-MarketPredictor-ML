"""
Tests for NFR-011: Multi-Asset Configuration and Asset Mapper.
"""

import json
from pathlib import Path

import pytest

from src.trading_engine.core.config_loader import (
    ConfigLoader,
    get_asset_config,
    get_commodity_tickers,
    get_config_loader,
    resolve_asset_type,
)
from src.trading_engine.utils.asset_mapper import (
    ASSET_TYPE_COMMODITIES,
    ASSET_TYPE_DIGITAL_ASSETS,
    ASSET_TYPE_SHARES,
    get_display_name,
    get_icon,
    get_legacy_name,
    is_commodity,
    is_crypto,
    is_equity,
    is_valid_asset_type,
)
from src.trading_engine.utils.asset_mapper import (
    resolve_asset_type as mapper_resolve,
)


class TestConfigLoader:
    """Tests for ConfigLoader class."""

    def test_singleton_pattern(self):
        """ConfigLoader should be a singleton."""
        loader1 = get_config_loader()
        loader2 = get_config_loader()
        assert loader1 is loader2

    def test_get_enabled_asset_types(self):
        """Should return all enabled asset types."""
        loader = get_config_loader()
        asset_types = loader.get_enabled_asset_types()

        assert "shares" in asset_types
        assert "digital_assets" in asset_types
        assert "commodities" in asset_types
        assert len(asset_types) == 3

    def test_resolve_asset_type_legacy_stock(self):
        """Should resolve 'stock' to 'shares'."""
        loader = get_config_loader()
        assert loader.resolve_asset_type("stock") == "shares"
        assert loader.resolve_asset_type("stocks") == "shares"
        assert loader.resolve_asset_type("equity") == "shares"

    def test_resolve_asset_type_legacy_crypto(self):
        """Should resolve 'crypto' to 'digital_assets'."""
        loader = get_config_loader()
        assert loader.resolve_asset_type("crypto") == "digital_assets"
        assert loader.resolve_asset_type("cryptocurrency") == "digital_assets"

    def test_resolve_asset_type_canonical(self):
        """Canonical names should resolve to themselves."""
        loader = get_config_loader()
        assert loader.resolve_asset_type("shares") == "shares"
        assert loader.resolve_asset_type("digital_assets") == "digital_assets"
        assert loader.resolve_asset_type("commodities") == "commodities"

    def test_get_asset_type_config(self):
        """Should return configuration for asset type."""
        loader = get_config_loader()

        shares_config = loader.get_asset_type("shares")
        assert shares_config is not None
        assert shares_config["display_name"] == "Shares"
        assert shares_config["enabled"] is True
        assert shares_config["data_source"] == "yfinance"

    def test_get_asset_type_with_alias(self):
        """Should resolve alias and return config."""
        loader = get_config_loader()

        # Using legacy name 'stock'
        config = loader.get_asset_type("stock")
        assert config is not None
        assert config["display_name"] == "Shares"

    def test_get_popular_tickers_shares(self):
        """Should return popular stock tickers."""
        loader = get_config_loader()
        tickers = loader.get_popular_tickers("shares")

        assert len(tickers) > 0
        assert "AAPL" in tickers
        assert "MSFT" in tickers

    def test_get_commodity_tickers_all(self):
        """Should return all commodity tickers."""
        tickers = get_commodity_tickers()

        assert len(tickers) > 0
        ticker_symbols = [t["ticker"] for t in tickers]
        assert "GC=F" in ticker_symbols  # Gold
        assert "CL=F" in ticker_symbols  # Crude Oil

    def test_get_commodity_tickers_by_category(self):
        """Should return commodity tickers filtered by category."""
        tickers = get_commodity_tickers("precious_metals")

        assert len(tickers) > 0
        ticker_symbols = [t["ticker"] for t in tickers]
        assert "GC=F" in ticker_symbols  # Gold
        assert "SI=F" in ticker_symbols  # Silver
        assert "CL=F" not in ticker_symbols  # Oil is not precious metal

    def test_get_cache_ttl(self):
        """Should return cache TTL for asset types."""
        loader = get_config_loader()

        assert loader.get_cache_ttl("shares") == 300
        assert loader.get_cache_ttl("digital_assets") == 120
        assert loader.get_cache_ttl("commodities") == 300

    def test_get_risk_multiplier(self):
        """Should return risk multiplier for asset types."""
        loader = get_config_loader()

        assert loader.get_risk_multiplier("shares") == 1.0
        assert loader.get_risk_multiplier("digital_assets") == 1.5
        assert loader.get_risk_multiplier("commodities") == 0.8

    def test_get_max_position_pct(self):
        """Should return max position percentage from risk limits."""
        loader = get_config_loader()

        assert loader.get_max_position_pct("shares") == 10.0
        assert loader.get_max_position_pct("digital_assets") == 5.0
        assert loader.get_max_position_pct("commodities") == 8.0

    def test_get_regime_adjustments(self):
        """Should return regime adjustments."""
        loader = get_config_loader()

        risk_on = loader.get_regime_adjustments("RISK_ON")
        assert risk_on["equity_multiplier"] == 1.0

        risk_off = loader.get_regime_adjustments("RISK_OFF")
        assert risk_off["equity_multiplier"] == 0.7
        assert risk_off["cash_requirement"] == 25.0


class TestAssetMapper:
    """Tests for asset_mapper utilities."""

    def test_resolve_asset_type_stock(self):
        """Should resolve stock to shares."""
        assert mapper_resolve("stock") == ASSET_TYPE_SHARES
        assert mapper_resolve("stocks") == ASSET_TYPE_SHARES
        assert mapper_resolve("equity") == ASSET_TYPE_SHARES
        assert mapper_resolve("equities") == ASSET_TYPE_SHARES

    def test_resolve_asset_type_crypto(self):
        """Should resolve crypto to digital_assets."""
        assert mapper_resolve("crypto") == ASSET_TYPE_DIGITAL_ASSETS
        assert mapper_resolve("cryptocurrency") == ASSET_TYPE_DIGITAL_ASSETS
        assert mapper_resolve("digital_asset") == ASSET_TYPE_DIGITAL_ASSETS

    def test_resolve_asset_type_commodity(self):
        """Should resolve commodity to commodities."""
        assert mapper_resolve("commodity") == ASSET_TYPE_COMMODITIES
        assert mapper_resolve("raw_material") == ASSET_TYPE_COMMODITIES
        assert mapper_resolve("raw_materials") == ASSET_TYPE_COMMODITIES

    def test_get_legacy_name(self):
        """Should return legacy names for canonical types."""
        assert get_legacy_name("shares") == "stock"
        assert get_legacy_name("digital_assets") == "crypto"
        assert get_legacy_name("commodities") == "commodity"

    def test_is_valid_asset_type(self):
        """Should validate asset types."""
        assert is_valid_asset_type("stock") is True
        assert is_valid_asset_type("crypto") is True
        assert is_valid_asset_type("shares") is True
        assert is_valid_asset_type("commodities") is True
        assert is_valid_asset_type("invalid") is False
        assert is_valid_asset_type("foo") is False

    def test_get_display_name_english(self):
        """Should return English display names."""
        assert get_display_name("shares", "en") == "Shares"
        assert get_display_name("digital_assets", "en") == "Digital Assets"
        assert get_display_name("commodities", "en") == "Commodities"

    def test_get_display_name_german(self):
        """Should return German display names."""
        assert get_display_name("shares", "de") == "Aktien"
        assert get_display_name("digital_assets", "de") == "Kryptowährungen"
        assert get_display_name("commodities", "de") == "Rohstoffe"

    def test_get_icon(self):
        """Should return emoji icons for asset types."""
        assert get_icon("shares") == "📈"
        assert get_icon("digital_assets") == "₿"
        assert get_icon("commodities") == "🛢️"

    def test_is_crypto(self):
        """Should detect crypto asset types."""
        assert is_crypto("crypto") is True
        assert is_crypto("digital_assets") is True
        assert is_crypto("stock") is False
        assert is_crypto("commodity") is False

    def test_is_equity(self):
        """Should detect equity asset types."""
        assert is_equity("stock") is True
        assert is_equity("shares") is True
        assert is_equity("crypto") is False
        assert is_equity("commodity") is False

    def test_is_commodity(self):
        """Should detect commodity asset types."""
        assert is_commodity("commodity") is True
        assert is_commodity("commodities") is True
        assert is_commodity("raw_materials") is True
        assert is_commodity("stock") is False
        assert is_commodity("crypto") is False


class TestConfigFiles:
    """Tests for JSON config files validity."""

    def test_assets_json_exists(self):
        """assets.json should exist."""
        config_path = Path(__file__).parent.parent / "config" / "assets.json"
        assert config_path.exists(), f"assets.json not found at {config_path}"

    def test_risk_limits_json_exists(self):
        """risk_limits.json should exist."""
        config_path = Path(__file__).parent.parent / "config" / "risk_limits.json"
        assert config_path.exists(), f"risk_limits.json not found at {config_path}"

    def test_assets_json_valid(self):
        """assets.json should be valid JSON."""
        config_path = Path(__file__).parent.parent / "config" / "assets.json"
        with open(config_path) as f:
            data = json.load(f)

        assert "asset_types" in data
        assert len(data["asset_types"]) >= 3

    def test_risk_limits_json_valid(self):
        """risk_limits.json should be valid JSON."""
        config_path = Path(__file__).parent.parent / "config" / "risk_limits.json"
        with open(config_path) as f:
            data = json.load(f)

        assert "position_limits" in data
        assert "asset_class_limits" in data

    def test_schema_validation(self):
        """Config files should validate against schemas."""
        try:
            import jsonschema
        except ImportError:
            pytest.skip("jsonschema not installed")

        config_dir = Path(__file__).parent.parent / "config"

        # Load assets config and schema
        with open(config_dir / "assets.json") as f:
            assets_config = json.load(f)
        with open(config_dir / "schemas" / "assets.schema.json") as f:
            assets_schema = json.load(f)

        # Should not raise
        jsonschema.validate(instance=assets_config, schema=assets_schema)

        # Load risk limits config and schema
        with open(config_dir / "risk_limits.json") as f:
            risk_config = json.load(f)
        with open(config_dir / "schemas" / "risk_limits.schema.json") as f:
            risk_schema = json.load(f)

        # Should not raise
        jsonschema.validate(instance=risk_config, schema=risk_schema)
