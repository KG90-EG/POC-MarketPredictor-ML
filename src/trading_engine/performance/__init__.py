"""Performance optimization subpackage."""

from .feature_cache import (
    cache_warmup,
    cached_features,
    clear_feature_cache,
    get_cache_stats,
    get_feature_cache,
    init_feature_cache,
)

__all__ = [
    "init_feature_cache",
    "get_feature_cache",
    "cached_features",
    "cache_warmup",
    "clear_feature_cache",
    "get_cache_stats",
]
