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
        self,
        items: List[Any],
        process_func: Callable,
        timeout: Optional[float] = None
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
            future_to_item = {
                executor.submit(process_func, item): item
                for item in items
            }
            
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
            "max_workers": self.max_workers
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


def parallel_stock_ranking(
    tickers: List[str],
    model: Any,
    features_list: List[str]
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
    import pandas as pd
    import yfinance as yf
    from ..ml.trading import compute_rsi, compute_momentum, compute_macd, compute_bollinger
    
    # Use only legacy 9 features for now (until full feature engineering is integrated)
    features_legacy = [
        "SMA50",
        "SMA200",
        "RSI",
        "Volatility",
        "Momentum_10d",
        "MACD",
        "MACD_signal",
        "BB_upper",
        "BB_lower",
    ]
    
    def process_ticker(ticker: str) -> Optional[Dict[str, Any]]:
        """Process single ticker - will run in parallel."""
        try:
            # Download data
            raw = yf.download(ticker, period="300d", auto_adjust=False, progress=False)
            
            # Handle MultiIndex columns
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            
            if raw.empty or "Adj Close" not in raw.columns:
                return None
            
            # Build features DataFrame
            df = pd.DataFrame()
            adj_close = raw["Adj Close"]
            if isinstance(adj_close, pd.DataFrame):
                adj_close = adj_close.iloc[:, 0]
            df["Adj Close"] = adj_close
            
            # Compute technical indicators (9 legacy features)
            df["SMA50"] = df["Adj Close"].rolling(50).mean()
            df["SMA200"] = df["Adj Close"].rolling(200).mean()
            df["RSI"] = compute_rsi(df["Adj Close"])
            df["Volatility"] = df["Adj Close"].pct_change().rolling(30).std()
            df["Momentum_10d"] = compute_momentum(df["Adj Close"], 10)
            
            macd, macd_sig = compute_macd(df["Adj Close"])
            df["MACD"] = macd
            df["MACD_signal"] = macd_sig
            
            bb_up, bb_low = compute_bollinger(df["Adj Close"])
            df["BB_upper"] = bb_up
            df["BB_lower"] = bb_low
            
            df = df.dropna()
            if df.empty:
                return None
            
            # Make prediction using legacy features
            row = df.iloc[-1:]
            prob = model.predict_proba(row[features_legacy].values)[0][1]
            
            # Determine action based on probability
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
                "price": float(df["Adj Close"].iloc[-1])
            }
            
        except Exception as e:
            logger.debug(f"Error processing {ticker}: {e}")
            return None
    
    # Process all tickers in parallel
    processor = get_parallel_processor()
    results = processor.process_batch(tickers, process_ticker)
    
    # Sort by probability (highest first)
    results.sort(key=lambda x: x["prob"], reverse=True)
    
    return results


def parallel_predictions(
    tickers: List[str],
    predict_func: Callable[[str], Dict[str, Any]]
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
