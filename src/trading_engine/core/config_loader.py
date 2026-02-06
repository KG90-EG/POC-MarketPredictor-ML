"""
Centralized JSON Configuration Loader with Schema Validation.

This module provides a single source of truth for all JSON-based configuration
in the MarketPredictor application, implementing NFR-011.

Features:
- Loads assets.json, risk_limits.json
- Validates against JSON Schemas
- Supports environment variable overrides
- Caches configs in memory
- Provides backward-compatible asset type mapping
"""

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    jsonschema = None

logger = logging.getLogger(__name__)

# Default paths
CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "config"
ASSETS_CONFIG_PATH = CONFIG_DIR / "assets.json"
RISK_LIMITS_CONFIG_PATH = CONFIG_DIR / "risk_limits.json"
SCHEMAS_DIR = CONFIG_DIR / "schemas"


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    pass


class ConfigLoader:
    """
    Centralized configuration loader with validation.

    Usage:
        config = ConfigLoader()
        assets = config.get_asset_types()
        limits = config.get_risk_limits("shares")
    """

    _instance: Optional["ConfigLoader"] = None
    _assets_config: Optional[Dict[str, Any]] = None
    _risk_limits_config: Optional[Dict[str, Any]] = None

    def __new__(cls) -> "ConfigLoader":
        """Singleton pattern for config loader."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_all_configs()
        return cls._instance

    def _load_all_configs(self) -> None:
        """Load and validate all configuration files."""
        self._assets_config = self._load_config(
            ASSETS_CONFIG_PATH, SCHEMAS_DIR / "assets.schema.json"
        )
        self._risk_limits_config = self._load_config(
            RISK_LIMITS_CONFIG_PATH, SCHEMAS_DIR / "risk_limits.schema.json"
        )
        logger.info("All configurations loaded and validated")

    def _load_config(self, config_path: Path, schema_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load a JSON config file with optional schema validation.

        Args:
            config_path: Path to the JSON config file
            schema_path: Optional path to JSON Schema for validation

        Returns:
            Parsed configuration dictionary

        Raises:
            ConfigValidationError: If validation fails
        """
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
            return {}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Validate against schema if available
            if schema_path and schema_path.exists() and HAS_JSONSCHEMA:
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                try:
                    jsonschema.validate(instance=config, schema=schema)
                    logger.debug(f"Config validated: {config_path.name}")
                except jsonschema.ValidationError as e:
                    raise ConfigValidationError(
                        f"Schema validation failed for {config_path.name}: {e.message}"
                    )
            elif not HAS_JSONSCHEMA:
                logger.debug("jsonschema not installed, skipping validation")

            logger.info(f"Loaded config: {config_path.name}")
            return config

        except json.JSONDecodeError as e:
            raise ConfigValidationError(f"Invalid JSON in {config_path}: {e}")

    def reload(self) -> None:
        """Reload all configurations from disk."""
        self._load_all_configs()

    # ==================== Asset Configuration ====================

    def get_asset_types(self) -> Dict[str, Any]:
        """Get all asset type configurations."""
        return self._assets_config.get("asset_types", {})

    def get_asset_type(self, asset_type: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific asset type.

        Args:
            asset_type: Asset type name (supports aliases like 'stock' -> 'shares')

        Returns:
            Asset type configuration or None
        """
        # Resolve alias if needed
        resolved = self.resolve_asset_type(asset_type)
        return self._assets_config.get("asset_types", {}).get(resolved)

    def resolve_asset_type(self, asset_type: str) -> str:
        """
        Resolve asset type alias to canonical name.

        Args:
            asset_type: Asset type name or alias

        Returns:
            Canonical asset type name
        """
        aliases = self._assets_config.get("asset_type_aliases", {})
        return aliases.get(asset_type.lower(), asset_type.lower())

    def get_enabled_asset_types(self) -> List[str]:
        """Get list of enabled asset types."""
        return [
            name for name, config in self.get_asset_types().items() if config.get("enabled", False)
        ]

    def get_popular_tickers(self, asset_type: str) -> List[str]:
        """Get popular tickers for an asset type."""
        config = self.get_asset_type(asset_type)
        if not config:
            return []

        # Handle different ticker formats
        if "popular_tickers" in config:
            return config["popular_tickers"]
        elif "popular_ids" in config:
            return config["popular_ids"]
        elif "categories" in config:
            # Commodities: extract from categories
            tickers = []
            for category in config["categories"].values():
                for item in category.get("tickers", []):
                    tickers.append(item["ticker"])
            return tickers
        return []

    def get_commodity_categories(self) -> Dict[str, Any]:
        """Get commodity categories with their tickers."""
        commodities = self.get_asset_type("commodities")
        if not commodities:
            return {}
        return commodities.get("categories", {})

    def get_commodity_tickers(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get commodity tickers, optionally filtered by category.

        Args:
            category: Optional category filter (e.g., 'precious_metals', 'energy')

        Returns:
            List of ticker dictionaries with name and unit
        """
        categories = self.get_commodity_categories()

        if category:
            cat_config = categories.get(category, {})
            return cat_config.get("tickers", [])

        # All tickers from all categories
        all_tickers = []
        for cat_config in categories.values():
            all_tickers.extend(cat_config.get("tickers", []))
        return all_tickers

    def get_cache_ttl(self, asset_type: str) -> int:
        """Get cache TTL for an asset type in seconds."""
        config = self.get_asset_type(asset_type)
        if config:
            return config.get("cache_ttl_seconds", 300)
        return 300  # Default 5 minutes

    def get_risk_multiplier(self, asset_type: str) -> float:
        """Get risk multiplier for an asset type."""
        config = self.get_asset_type(asset_type)
        if config:
            return config.get("risk_multiplier", 1.0)
        return 1.0

    def get_data_source(self, asset_type: str) -> str:
        """Get data source for an asset type."""
        config = self.get_asset_type(asset_type)
        if config:
            return config.get("data_source", "yfinance")
        return "yfinance"

    # ==================== Risk Limits Configuration ====================

    def get_position_limits(self, asset_type: Optional[str] = None) -> Dict[str, Any]:
        """Get position limits, optionally for a specific asset type."""
        limits = self._risk_limits_config.get("position_limits", {})
        if asset_type:
            resolved = self.resolve_asset_type(asset_type)
            return limits.get(resolved, {})
        return limits

    def get_max_position_pct(self, asset_type: str) -> float:
        """Get maximum position percentage for an asset type."""
        limits = self.get_position_limits(asset_type)
        return limits.get("max_position_pct", 10.0)

    def get_asset_class_limits(self, asset_type: Optional[str] = None) -> Dict[str, Any]:
        """Get asset class exposure limits."""
        limits = self._risk_limits_config.get("asset_class_limits", {})
        if asset_type:
            resolved = self.resolve_asset_type(asset_type)
            return limits.get(resolved, {})
        return limits

    def get_max_exposure_pct(self, asset_type: str) -> float:
        """Get maximum portfolio exposure for an asset type."""
        limits = self.get_asset_class_limits(asset_type)
        return limits.get("max_exposure_pct", 100.0)

    def get_regime_adjustments(self, regime: str) -> Dict[str, Any]:
        """Get risk adjustments for a market regime."""
        adjustments = self._risk_limits_config.get("regime_adjustments", {})
        return adjustments.get(regime, adjustments.get("NEUTRAL", {}))

    def get_scoring_thresholds(self) -> Dict[str, Any]:
        """Get signal scoring thresholds."""
        return self._risk_limits_config.get("scoring_thresholds", {})

    def get_diversification_rules(self) -> Dict[str, Any]:
        """Get portfolio diversification rules."""
        return self._risk_limits_config.get("diversification", {})

    # ==================== Environment Overrides ====================

    def get_with_env_override(self, key: str, default: Any = None) -> Any:
        """
        Get config value with environment variable override.

        Environment variables are checked in format: MARKET_PREDICTOR_{KEY}

        Args:
            key: Configuration key (dot notation: 'asset_types.shares.cache_ttl_seconds')
            default: Default value if not found

        Returns:
            Configuration value
        """
        env_key = f"MARKET_PREDICTOR_{key.upper().replace('.', '_')}"
        env_value = os.getenv(env_key)

        if env_value is not None:
            # Try to parse as JSON for complex types
            try:
                return json.loads(env_value)
            except json.JSONDecodeError:
                return env_value

        # Navigate nested config
        parts = key.split(".")
        value = self._assets_config
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return default

        return value if value is not None else default


# Singleton accessor
@lru_cache(maxsize=1)
def get_config_loader() -> ConfigLoader:
    """Get the singleton ConfigLoader instance."""
    return ConfigLoader()


# Convenience functions
def get_asset_config(asset_type: str) -> Optional[Dict[str, Any]]:
    """Shortcut to get asset type configuration."""
    return get_config_loader().get_asset_type(asset_type)


def resolve_asset_type(asset_type: str) -> str:
    """Shortcut to resolve asset type alias."""
    return get_config_loader().resolve_asset_type(asset_type)


def get_commodity_tickers(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Shortcut to get commodity tickers."""
    return get_config_loader().get_commodity_tickers(category)
