"""
Asset Type Mapper for Backward Compatibility.

This module provides mapping between legacy asset type names and the new
canonical names introduced in NFR-011.

Mappings:
- 'stock' -> 'shares'
- 'crypto' -> 'digital_assets'
- 'commodity' -> 'commodities'
"""

from typing import Optional

# Canonical asset type names
ASSET_TYPE_SHARES = "shares"
ASSET_TYPE_DIGITAL_ASSETS = "digital_assets"
ASSET_TYPE_COMMODITIES = "commodities"

# Legacy to canonical mapping
ASSET_TYPE_MAP = {
    # Legacy names -> Canonical names
    "stock": ASSET_TYPE_SHARES,
    "stocks": ASSET_TYPE_SHARES,
    "equity": ASSET_TYPE_SHARES,
    "equities": ASSET_TYPE_SHARES,
    "crypto": ASSET_TYPE_DIGITAL_ASSETS,
    "cryptocurrency": ASSET_TYPE_DIGITAL_ASSETS,
    "cryptocurrencies": ASSET_TYPE_DIGITAL_ASSETS,
    "digital_asset": ASSET_TYPE_DIGITAL_ASSETS,
    "commodity": ASSET_TYPE_COMMODITIES,
    "raw_material": ASSET_TYPE_COMMODITIES,
    "raw_materials": ASSET_TYPE_COMMODITIES,
    # Canonical names (identity mapping)
    ASSET_TYPE_SHARES: ASSET_TYPE_SHARES,
    ASSET_TYPE_DIGITAL_ASSETS: ASSET_TYPE_DIGITAL_ASSETS,
    ASSET_TYPE_COMMODITIES: ASSET_TYPE_COMMODITIES,
}

# Reverse mapping (canonical -> legacy for API compatibility)
LEGACY_ASSET_TYPE_MAP = {
    ASSET_TYPE_SHARES: "stock",
    ASSET_TYPE_DIGITAL_ASSETS: "crypto",
    ASSET_TYPE_COMMODITIES: "commodity",
}

# All valid canonical asset types
VALID_ASSET_TYPES = {
    ASSET_TYPE_SHARES,
    ASSET_TYPE_DIGITAL_ASSETS,
    ASSET_TYPE_COMMODITIES,
}


def resolve_asset_type(asset_type: str) -> str:
    """
    Resolve an asset type name to its canonical form.

    Args:
        asset_type: Asset type name (can be legacy or canonical)

    Returns:
        Canonical asset type name

    Examples:
        >>> resolve_asset_type("stock")
        'shares'
        >>> resolve_asset_type("crypto")
        'digital_assets'
        >>> resolve_asset_type("shares")
        'shares'
    """
    normalized = asset_type.lower().strip()
    return ASSET_TYPE_MAP.get(normalized, normalized)


def get_legacy_name(asset_type: str) -> str:
    """
    Get the legacy name for a canonical asset type.
    Useful for backward-compatible API responses.

    Args:
        asset_type: Canonical or legacy asset type name

    Returns:
        Legacy asset type name

    Examples:
        >>> get_legacy_name("shares")
        'stock'
        >>> get_legacy_name("digital_assets")
        'crypto'
    """
    canonical = resolve_asset_type(asset_type)
    return LEGACY_ASSET_TYPE_MAP.get(canonical, asset_type)


def is_valid_asset_type(asset_type: str) -> bool:
    """
    Check if an asset type is valid (after resolving).

    Args:
        asset_type: Asset type name to validate

    Returns:
        True if valid, False otherwise
    """
    resolved = resolve_asset_type(asset_type)
    return resolved in VALID_ASSET_TYPES


def get_all_asset_types() -> list:
    """Get list of all canonical asset types."""
    return list(VALID_ASSET_TYPES)


def get_display_name(asset_type: str, language: str = "en") -> str:
    """
    Get display name for an asset type.

    Args:
        asset_type: Asset type name
        language: Language code ('en' or 'de')

    Returns:
        Human-readable display name
    """
    canonical = resolve_asset_type(asset_type)

    display_names = {
        ASSET_TYPE_SHARES: {"en": "Shares", "de": "Aktien"},
        ASSET_TYPE_DIGITAL_ASSETS: {"en": "Digital Assets", "de": "Kryptowährungen"},
        ASSET_TYPE_COMMODITIES: {"en": "Commodities", "de": "Rohstoffe"},
    }

    names = display_names.get(canonical, {"en": asset_type.title(), "de": asset_type.title()})
    return names.get(language, names["en"])


def get_icon(asset_type: str) -> str:
    """Get emoji icon for an asset type."""
    canonical = resolve_asset_type(asset_type)

    icons = {
        ASSET_TYPE_SHARES: "📈",
        ASSET_TYPE_DIGITAL_ASSETS: "₿",
        ASSET_TYPE_COMMODITIES: "🛢️",
    }

    return icons.get(canonical, "📊")


def is_crypto(asset_type: str) -> bool:
    """Check if asset type is cryptocurrency/digital asset."""
    return resolve_asset_type(asset_type) == ASSET_TYPE_DIGITAL_ASSETS


def is_equity(asset_type: str) -> bool:
    """Check if asset type is equity/shares."""
    return resolve_asset_type(asset_type) == ASSET_TYPE_SHARES


def is_commodity(asset_type: str) -> bool:
    """Check if asset type is commodity."""
    return resolve_asset_type(asset_type) == ASSET_TYPE_COMMODITIES
