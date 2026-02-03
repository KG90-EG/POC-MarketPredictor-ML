"""Performance optimization subpackage."""

from .background_jobs import (get_job_stats, start_background_jobs,
                              stop_background_jobs, trigger_job_now)
from .feature_cache import (cache_warmup, cached_features, clear_feature_cache,
                            get_cache_stats, get_feature_cache,
                            init_feature_cache)
from .parallel import get_parallel_processor, parallel_stock_ranking

__all__ = [
    "init_feature_cache",
    "get_feature_cache",
    "cached_features",
    "cache_warmup",
    "clear_feature_cache",
    "get_cache_stats",
    "get_parallel_processor",
    "parallel_stock_ranking",
    "start_background_jobs",
    "stop_background_jobs",
    "get_job_stats",
    "trigger_job_now",
]
