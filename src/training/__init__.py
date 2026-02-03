"""
ML Training Pipeline Module (FR-004).

This module provides automated model training, validation, and deployment.

Components:
    - hyperparams: Hyperparameter search spaces and defaults
    - Training scripts in scripts/
"""

from src.training.hyperparams import (
    DEFAULT_HYPERPARAMS,
    OPTIMIZATION_CONFIG,
    get_default_params,
    get_search_space,
    sample_params,
)

__all__ = [
    "get_search_space",
    "sample_params",
    "get_default_params",
    "DEFAULT_HYPERPARAMS",
    "OPTIMIZATION_CONFIG",
]
