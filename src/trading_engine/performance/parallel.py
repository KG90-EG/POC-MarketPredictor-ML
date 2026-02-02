"""
Parallel processing utilities for performance optimization.

Week 1 - Task 4: Parallel Processing
- Process multiple stocks simultaneously
- ThreadPoolExecutor for I/O-bound tasks (Yahoo Finance API)
- ProcessPoolExecutor for CPU-bound tasks (feature computation)
- Target: 10x speedup for /ranking endpoint
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ParallelProcessor:
    """
    Parallel processing for stock predictions.

    Uses ThreadPoolExecutor for I/O-bound operations:
    - Fetching data from Yahoo Finance
    - API calls

    Automatically batches and tracks progress.
    """

    def __init__(self, max_workers: int = 10):
        """
        Initialize parallel processor.

        Args:
            max_workers: Maximum number of concurrent threads (default: 10)
        """
        self.max_workers = max_workers
        self.total_processed = 0
        self.total_errors = 0

        logger.info(f"Parallel processor initialized with {max_workers} workers")

    def process_batch(
        self, items: List[Any], process_func: Callable, timeout: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of items in parallel.

        Args:
            items: List of items to process
            process_func: Function to apply to each item
            timeout: Timeout per item in seconds (optional)

        Returns:
            List of results (successful only)
        """
        results = []
        start_time = time.time()

        logger.info(f"Processing {len(items)} items with {self.max_workers} workers...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {executor.submit(process_func, item): item for item in items}

            # Collect results as they complete
            for future in as_completed(future_to_item, timeout=timeout):
                item = future_to_item[future]
                try:
                    result = future.result(timeout=5.0)  # 5s per task
                    if result is not None:
                        results.append(result)
                        self.total_processed += 1
                except Exception as e:
                    self.total_errors += 1
                    logger.warning(f"Failed to process {item}: {e}")

        duration = time.time() - start_time
        success_rate = len(results) / len(items) * 100 if items else 0

        logger.info(
            f"Batch complete: {len(results)}/{len(items)} successful "
            f"({success_rate:.1f}%) in {duration:.2f}s "
            f"({len(items)/duration:.1f} items/sec)"
        )

        return results

    def get_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics.

        Returns:
            Dict with total processed, errors, success rate
        """
        total = self.total_processed + self.total_errors
        success_rate = (self.total_processed / total * 100) if total > 0 else 0

        return {
            "total_processed": self.total_processed,
            "total_errors": self.total_errors,
            "success_rate_pct": round(success_rate, 2),
            "max_workers": self.max_workers,
        }


# Global parallel processor instance
_parallel_processor: Optional[ParallelProcessor] = None


def get_parallel_processor() -> ParallelProcessor:
    """
    Get global parallel processor instance.

    Returns:
        ParallelProcessor instance
    """
    global _parallel_processor
    if _parallel_processor is None:
        _parallel_processor = ParallelProcessor(max_workers=10)
    return _parallel_processor


# MODULE-LEVEL FUNCTION for proper thread isolation
def _process_single_ticker(args: tuple) -> Optional[Dict[str, Any]]:
    """
    Process single ticker - MUST be module-level for thread safety.

    Args:
        args: Tuple of (ticker, model_pickle)

    Returns:
        Dict with ticker, prob, action, confidence, price OR None
    """
    import pickle

    import pandas as pd
    import yfinance as yf

    from ..ml.feature_engineering import (
        add_technical_features_only,
        get_technical_feature_names,
    )

    ticker, model_pickle = args

    try:
        # Each thread deserializes its own model copy
        model = pickle.loads(model_pickle)

        # Download fresh data with unique session to avoid cache pollution
        import yfinance as yfin

        stock = yfin.Ticker(ticker)
        raw = stock.history(period="300d", auto_adjust=False)

        # Handle MultiIndex
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        if raw.empty or "Adj Close" not in raw.columns:
            return None

        # CRITICAL: Extract price FIRST from raw data
        current_price = float(raw["Adj Close"].iloc[-1])

        # Create OHLCV DataFrame with .values to break any references
        df = pd.DataFrame(
            {
                "Open": raw["Open"].values,
                "High": raw["High"].values,
                "Low": raw["Low"].values,
                "Close": raw["Adj Close"].values,
                "Volume": raw["Volume"].values,
            },
            index=raw.index,
        )

        # Add features
        df = add_technical_features_only(df)
        df = df.dropna()

        if df.empty:
            return None

        # Get features
        technical_features = get_technical_feature_names()

        # Predict
        row = df.iloc[-1:]
        prob = model.predict_proba(row[technical_features].values)[0][1]

        # Action
        if prob >= 0.6:
            action = "BUY"
        elif prob <= 0.4:
            action = "SELL"
        else:
            action = "HOLD"

        return {
            "ticker": ticker,
            "prob": float(prob),
            "action": action,
            "confidence": float(prob * 100),
            "price": current_price,  # Use price from raw data BEFORE processing
        }

    except Exception as e:
        logger.debug(f"Error processing {ticker}: {e}")
        return None


def parallel_stock_ranking(
    tickers: List[str], model: Any, features_list: List[str]
) -> List[Dict[str, Any]]:
    """
    Rank stocks in parallel using ML model.

    This is the optimized version of the /ranking endpoint logic.
    Processes multiple stocks simultaneously instead of sequentially.

    Args:
        tickers: List of stock ticker symbols
        model: Trained ML model
        features_list: List of feature names to use

    Returns:
        List of dicts with {ticker, prob, action, confidence}
    """
    import pickle

    # Serialize model once - each thread will deserialize its own copy
    model_pickle = pickle.dumps(model)

    # Create args: (ticker, model_pickle) for each ticker
    args_list = [(ticker, model_pickle) for ticker in tickers]

    # Process using module-level function (ensures thread safety)
    processor = get_parallel_processor()
    results = processor.process_batch(args_list, _process_single_ticker)

    # Sort by probability
    results.sort(key=lambda x: x["prob"], reverse=True)

    return results


def parallel_predictions(
    tickers: List[str], predict_func: Callable[[str], Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generic parallel prediction function.

    Args:
        tickers: List of ticker symbols
        predict_func: Function that takes ticker and returns prediction dict

    Returns:
        List of prediction results
    """
    processor = get_parallel_processor()
    return processor.process_batch(tickers, predict_func)
