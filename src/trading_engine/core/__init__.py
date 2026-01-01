"""Core Module - Configuration, caching, database."""

from .cache import cache
from .config import config

__all__ = ["config", "cache"]
