"""
Advanced Feature Engineering for ML Trading Models.

This module provides comprehensive feature engineering functions across 4 categories:
1. Technical Indicators (20 features)
2. Fundamental Features (10 features)
3. Sentiment Features (5 features)
4. Macro/Market Features (5 features)

Total: 40+ features vs original 9

Performance Optimization (Week 1):
- Feature caching with 5-minute TTL
- LRU cache for recent tickers
- Redis support for multi-instance deployments
"""

import logging
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

# Import caching decorator
try:
    from ..performance.feature_cache import cached_features

    CACHING_ENABLED = True
except ImportError:
    # Fallback if performance module not available
    CACHING_ENABLED = False

    def cached_features(func):
        return func


# ============================================================================
# Technical Indicators (20 features)
# ============================================================================


def compute_atr(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    """
    Compute Average True Range (ATR) - measures volatility.

    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: Lookback period (default: 14)

    Returns:
        ATR series
    """
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def compute_adx(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    """
    Compute Average Directional Index (ADX) - measures trend strength.

    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: Lookback period (default: 14)

    Returns:
        ADX series
    """
    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    # Calculate True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Calculate directional indicators
    plus_di = 100 * (
        plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean()
    )
    minus_di = 100 * (
        minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean()
    )

    # Calculate DX and ADX
    dx = (
        100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
    )  # Add small epsilon to avoid division by zero
    adx = dx.rolling(window=period).mean()

    return adx


def compute_stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_period: int = 14,
    d_period: int = 3,
) -> tuple:
    """
    Compute Stochastic Oscillator (%K and %D).

    Args:
        high: High price series
        low: Low price series
        close: Close price series
        k_period: %K period (default: 14)
        d_period: %D period (default: 3)

    Returns:
        Tuple of (%K, %D)
    """
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()

    k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d_percent = k_percent.rolling(window=d_period).mean()

    return k_percent, d_percent


def compute_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    Compute On-Balance Volume (OBV) - cumulative volume indicator.

    Args:
        close: Close price series
        volume: Volume series

    Returns:
        OBV series
    """
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    return obv


def compute_vwap(
    high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series
) -> pd.Series:
    """
    Compute Volume Weighted Average Price (VWAP).

    Args:
        high: High price series
        low: Low price series
        close: Close price series
        volume: Volume series

    Returns:
        VWAP series
    """
    typical_price = (high + low + close) / 3
    vwap = (typical_price * volume).cumsum() / volume.cumsum()
    return vwap


def compute_williams_r(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    """
    Compute Williams %R - momentum indicator.

    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: Lookback period (default: 14)

    Returns:
        Williams %R series
    """
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()

    williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
    return williams_r


def compute_cci(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20
) -> pd.Series:
    """
    Compute Commodity Channel Index (CCI).

    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: Lookback period (default: 20)

    Returns:
        CCI series
    """
    typical_price = (high + low + close) / 3
    sma = typical_price.rolling(window=period).mean()
    mad = typical_price.rolling(window=period).apply(
        lambda x: np.abs(x - x.mean()).mean()
    )

    cci = (typical_price - sma) / (0.015 * mad)
    return cci


def compute_parabolic_sar(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    af_start: float = 0.02,
    af_max: float = 0.2,
) -> pd.Series:
    """
    Compute Parabolic SAR (Stop and Reverse).

    Args:
        high: High price series
        low: Low price series
        close: Close price series
        af_start: Starting acceleration factor (default: 0.02)
        af_max: Maximum acceleration factor (default: 0.2)

    Returns:
        SAR series
    """
    sar = pd.Series(index=close.index, dtype=float)

    # Simplified SAR calculation
    # Full implementation would track trends and EP (Extreme Point)
    sar[0] = low.iloc[0]

    for i in range(1, len(close)):
        if close.iloc[i] > sar.iloc[i - 1]:
            sar.iloc[i] = min(low.iloc[i - 1], sar.iloc[i - 1])
        else:
            sar.iloc[i] = max(high.iloc[i - 1], sar.iloc[i - 1])

    return sar


def compute_ichimoku(
    high: pd.Series, low: pd.Series, close: pd.Series
) -> Dict[str, pd.Series]:
    """
    Compute Ichimoku Cloud components.

    Args:
        high: High price series
        low: Low price series
        close: Close price series

    Returns:
        Dictionary with conversion_line, base_line, leading_span_a, leading_span_b
    """
    # Conversion Line (9 period)
    conv_high = high.rolling(window=9).max()
    conv_low = low.rolling(window=9).min()
    conversion_line = (conv_high + conv_low) / 2

    # Base Line (26 period)
    base_high = high.rolling(window=26).max()
    base_low = low.rolling(window=26).min()
    base_line = (base_high + base_low) / 2

    # Leading Span A
    leading_span_a = ((conversion_line + base_line) / 2).shift(26)

    # Leading Span B (52 period)
    span_high = high.rolling(window=52).max()
    span_low = low.rolling(window=52).min()
    leading_span_b = ((span_high + span_low) / 2).shift(26)

    return {
        "conversion_line": conversion_line,
        "base_line": base_line,
        "leading_span_a": leading_span_a,
        "leading_span_b": leading_span_b,
    }


def compute_keltner_channels(
    close: pd.Series,
    high: pd.Series,
    low: pd.Series,
    period: int = 20,
    multiplier: float = 2.0,
) -> Dict[str, pd.Series]:
    """
    Compute Keltner Channels.

    Args:
        close: Close price series
        high: High price series
        low: Low price series
        period: EMA period (default: 20)
        multiplier: ATR multiplier (default: 2.0)

    Returns:
        Dictionary with upper, middle, lower bands
    """
    middle = close.ewm(span=period, adjust=False).mean()
    atr = compute_atr(high, low, close, period=period)

    upper = middle + (multiplier * atr)
    lower = middle - (multiplier * atr)

    return {"upper": upper, "middle": middle, "lower": lower}


# ============================================================================
# Fundamental Features (10 features)
# ============================================================================


def get_fundamental_features(ticker: str) -> Dict[str, float]:
    """
    Fetch fundamental features from yfinance.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary of fundamental metrics
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        fundamentals = {
            "pe_ratio": info.get("trailingPE", np.nan),
            "peg_ratio": info.get("pegRatio", np.nan),
            "roe": info.get("returnOnEquity", np.nan),
            "debt_to_equity": info.get("debtToEquity", np.nan),
            "profit_margin": info.get("profitMargins", np.nan),
            "operating_margin": info.get("operatingMargins", np.nan),
            "eps_growth": info.get("earningsQuarterlyGrowth", np.nan),
            "revenue_growth": info.get("revenueGrowth", np.nan),
            "free_cash_flow": info.get("freeCashflow", np.nan),
            "dividend_yield": info.get("dividendYield", np.nan),
        }

        # Normalize large values
        if fundamentals["free_cash_flow"] and not np.isnan(
            fundamentals["free_cash_flow"]
        ):
            fundamentals["free_cash_flow"] = (
                fundamentals["free_cash_flow"] / 1e9
            )  # Convert to billions

        return fundamentals

    except Exception as e:
        logger.warning(f"Failed to fetch fundamentals for {ticker}: {e}")
        return {
            "pe_ratio": np.nan,
            "peg_ratio": np.nan,
            "roe": np.nan,
            "debt_to_equity": np.nan,
            "profit_margin": np.nan,
            "operating_margin": np.nan,
            "eps_growth": np.nan,
            "revenue_growth": np.nan,
            "free_cash_flow": np.nan,
            "dividend_yield": np.nan,
        }


# ============================================================================
# Sentiment Features (5 features)
# ============================================================================


def get_sentiment_features(ticker: str) -> Dict[str, float]:
    """
    Get sentiment-related features.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary of sentiment metrics
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get recommendations
        recommendations = stock.recommendations

        sentiment = {
            "analyst_rating": 0.0,  # Placeholder - would use actual analyst data
            "institutional_ownership": info.get("heldPercentInstitutions", np.nan),
            "insider_ownership": info.get("heldPercentInsiders", np.nan),
            "short_ratio": info.get("shortRatio", np.nan),
            "news_sentiment": 0.0,  # Placeholder - would use FinBERT or similar
        }

        # Calculate analyst rating from recommendations if available
        if recommendations is not None and not recommendations.empty:
            recent_recs = recommendations.tail(10)

            # Map to scores: Strong Buy = 1, Buy = 0.5, Hold = 0, Sell = -0.5, Strong Sell = -1
            rating_map = {
                "strongBuy": 1.0,
                "buy": 0.5,
                "hold": 0.0,
                "sell": -0.5,
                "strongSell": -1.0,
            }

            # Average the ratings
            if "To Grade" in recent_recs.columns:
                grades = recent_recs["To Grade"].str.lower()
                scores = grades.map(rating_map).dropna()
                if len(scores) > 0:
                    sentiment["analyst_rating"] = scores.mean()

        return sentiment

    except Exception as e:
        logger.warning(f"Failed to fetch sentiment for {ticker}: {e}")
        return {
            "analyst_rating": 0.0,
            "institutional_ownership": np.nan,
            "insider_ownership": np.nan,
            "short_ratio": np.nan,
            "news_sentiment": 0.0,
        }


# ============================================================================
# Macro/Market Features (5 features)
# ============================================================================


def get_macro_features() -> Dict[str, float]:
    """
    Get macro/market-wide features.

    Returns:
        Dictionary of macro metrics
    """
    try:
        # VIX (Fear Index)
        vix = yf.Ticker("^VIX")
        vix_data = vix.history(period="5d")
        vix_close = vix_data["Close"].iloc[-1] if not vix_data.empty else np.nan

        # 10-Year Treasury Yield
        tnx = yf.Ticker("^TNX")
        tnx_data = tnx.history(period="5d")
        treasury_yield = tnx_data["Close"].iloc[-1] if not tnx_data.empty else np.nan

        # USD Index (DXY)
        dxy = yf.Ticker("DX-Y.NYB")
        dxy_data = dxy.history(period="5d")
        usd_index = dxy_data["Close"].iloc[-1] if not dxy_data.empty else np.nan

        # S&P 500 (for market breadth)
        sp500 = yf.Ticker("^GSPC")
        sp500_data = sp500.history(period="1mo")

        # Calculate market breadth (advance/decline)
        if not sp500_data.empty and len(sp500_data) > 1:
            advances = (sp500_data["Close"].diff() > 0).sum()
            total = len(sp500_data) - 1
            market_breadth = advances / total if total > 0 else 0.5
        else:
            market_breadth = 0.5

        # Sector performance (using SPY as proxy)
        spy = yf.Ticker("SPY")
        spy_data = spy.history(period="1mo")
        sector_performance = (
            (spy_data["Close"].iloc[-1] / spy_data["Close"].iloc[0] - 1)
            if not spy_data.empty
            else 0.0
        )

        return {
            "vix": vix_close,
            "treasury_yield": treasury_yield,
            "usd_index": usd_index,
            "market_breadth": market_breadth,
            "sector_performance": sector_performance,
        }

    except Exception as e:
        logger.warning(f"Failed to fetch macro features: {e}")
        return {
            "vix": np.nan,
            "treasury_yield": np.nan,
            "usd_index": np.nan,
            "market_breadth": 0.5,
            "sector_performance": 0.0,
        }


# ============================================================================
# Feature Engineering Pipeline
# ============================================================================


@cached_features
def add_all_features(df: pd.DataFrame, ticker: str = None) -> pd.DataFrame:
    """
    Add all 40+ features to a DataFrame with OHLCV data.

    **Performance Optimized:** This function is cached with 5-minute TTL.
    Repeated calls for the same ticker return cached results instantly.

    Args:
        df: DataFrame with Open, High, Low, Close, Volume columns
        ticker: Stock ticker symbol (for fundamentals and sentiment)

    Returns:
        DataFrame with all features added
    """
    df = df.copy()

    # Flatten multi-index columns if present (from yfinance)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Ensure required columns exist
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        return df

    # Extract OHLCV as Series (squeeze to avoid DataFrame)
    high = df["High"].squeeze() if isinstance(df["High"], pd.DataFrame) else df["High"]
    low = df["Low"].squeeze() if isinstance(df["Low"], pd.DataFrame) else df["Low"]
    close = (
        df["Close"].squeeze() if isinstance(df["Close"], pd.DataFrame) else df["Close"]
    )
    volume = (
        df["Volume"].squeeze()
        if isinstance(df["Volume"], pd.DataFrame)
        else df["Volume"]
    )

    # ========================================================================
    # Original 9 features (keep for compatibility)
    # ========================================================================
    df["SMA50"] = close.rolling(window=50).mean()
    df["SMA200"] = close.rolling(window=200).mean()

    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["Volatility"] = close.pct_change().rolling(window=30).std()
    df["Momentum_10d"] = close.pct_change(periods=10)

    # MACD
    fast_ema = close.ewm(span=12, adjust=False).mean()
    slow_ema = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = fast_ema - slow_ema
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    sma20 = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    df["BB_upper"] = sma20 + (2 * std20)
    df["BB_lower"] = sma20 - (2 * std20)

    # ========================================================================
    # New Advanced Technical Indicators (+11 features)
    # ========================================================================
    df["ATR"] = compute_atr(high, low, close)
    df["ADX"] = compute_adx(high, low, close)

    stoch_k, stoch_d = compute_stochastic(high, low, close)
    df["Stochastic_K"] = stoch_k
    df["Stochastic_D"] = stoch_d

    df["OBV"] = compute_obv(close, volume)
    df["VWAP"] = compute_vwap(high, low, close, volume)
    df["Williams_R"] = compute_williams_r(high, low, close)
    df["CCI"] = compute_cci(high, low, close)
    df["Parabolic_SAR"] = compute_parabolic_sar(high, low, close)

    # Ichimoku (use conversion line as single feature)
    ichimoku = compute_ichimoku(high, low, close)
    df["Ichimoku_Conversion"] = ichimoku["conversion_line"]

    # Keltner Channels (use middle as feature)
    keltner = compute_keltner_channels(close, high, low)
    df["Keltner_Middle"] = keltner["middle"]

    # ========================================================================
    # Fundamental Features (+10 features)
    # ========================================================================
    if ticker:
        fundamentals = get_fundamental_features(ticker)
        for key, value in fundamentals.items():
            df[key] = value
    else:
        # Add NaN placeholders if no ticker provided
        for key in [
            "pe_ratio",
            "peg_ratio",
            "roe",
            "debt_to_equity",
            "profit_margin",
            "operating_margin",
            "eps_growth",
            "revenue_growth",
            "free_cash_flow",
            "dividend_yield",
        ]:
            df[key] = np.nan

    # ========================================================================
    # Sentiment Features (+5 features)
    # ========================================================================
    if ticker:
        sentiment = get_sentiment_features(ticker)
        for key, value in sentiment.items():
            df[key] = value
    else:
        for key in [
            "analyst_rating",
            "institutional_ownership",
            "insider_ownership",
            "short_ratio",
            "news_sentiment",
        ]:
            df[key] = 0.0

    # ========================================================================
    # Macro Features (+5 features) - same for all tickers
    # ========================================================================
    macro = get_macro_features()
    for key, value in macro.items():
        df[key] = value

    return df


def add_technical_features_only(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add ONLY technical features (no external API calls).

    This is optimized for training on many stocks without rate limiting.
    Total: 20 technical features (9 original + 11 advanced)

    Args:
        df: DataFrame with Open, High, Low, Close, Volume columns

    Returns:
        DataFrame with technical features added
    """
    df = df.copy()

    # Flatten multi-index columns if present (from yfinance)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Ensure required columns exist
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        return df

    # Extract OHLCV as Series (squeeze to avoid DataFrame)
    high = df["High"].squeeze() if isinstance(df["High"], pd.DataFrame) else df["High"]
    low = df["Low"].squeeze() if isinstance(df["Low"], pd.DataFrame) else df["Low"]
    close = (
        df["Close"].squeeze() if isinstance(df["Close"], pd.DataFrame) else df["Close"]
    )
    volume = (
        df["Volume"].squeeze()
        if isinstance(df["Volume"], pd.DataFrame)
        else df["Volume"]
    )

    # ========================================================================
    # Original 9 features (keep for compatibility)
    # ========================================================================
    df["SMA50"] = close.rolling(window=50).mean()
    df["SMA200"] = close.rolling(window=200).mean()

    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["Volatility"] = close.pct_change().rolling(window=30).std()
    df["Momentum_10d"] = close.pct_change(periods=10)

    # MACD
    fast_ema = close.ewm(span=12, adjust=False).mean()
    slow_ema = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = fast_ema - slow_ema
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    sma20 = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    df["BB_upper"] = sma20 + (2 * std20)
    df["BB_lower"] = sma20 - (2 * std20)

    # ========================================================================
    # New Advanced Technical Indicators (+11 features)
    # ========================================================================
    df["ATR"] = compute_atr(high, low, close)
    df["ADX"] = compute_adx(high, low, close)

    stoch_k, stoch_d = compute_stochastic(high, low, close)
    df["Stochastic_K"] = stoch_k
    df["Stochastic_D"] = stoch_d

    df["OBV"] = compute_obv(close, volume)
    df["VWAP"] = compute_vwap(high, low, close, volume)
    df["Williams_R"] = compute_williams_r(high, low, close)
    df["CCI"] = compute_cci(high, low, close)
    df["Parabolic_SAR"] = compute_parabolic_sar(high, low, close)

    # Ichimoku (use conversion line as single feature)
    ichimoku = compute_ichimoku(high, low, close)
    df["Ichimoku_Conversion"] = ichimoku["conversion_line"]

    # Keltner Channels (use middle as feature)
    keltner = compute_keltner_channels(close, high, low)
    df["Keltner_Middle"] = keltner["middle"]

    return df


def get_technical_feature_names() -> List[str]:
    """
    Get list of technical-only feature names (20 features).
    Used by production model to avoid external API calls.

    Returns:
        List of 20 technical feature names
    """
    return [
        # Original 9
        "SMA50",
        "SMA200",
        "RSI",
        "Volatility",
        "Momentum_10d",
        "MACD",
        "MACD_signal",
        "BB_upper",
        "BB_lower",
        # Advanced Technical (11)
        "ATR",
        "ADX",
        "Stochastic_K",
        "Stochastic_D",
        "OBV",
        "VWAP",
        "Williams_R",
        "CCI",
        "Parabolic_SAR",
        "Ichimoku_Conversion",
        "Keltner_Middle",
    ]


def get_feature_names() -> List[str]:
    """
    Get list of all feature names (40+ features).
    Includes technical, fundamental, sentiment, and macro features.

    Returns:
        List of 40+ feature names
    """
    return [
        # Original 9
        "SMA50",
        "SMA200",
        "RSI",
        "Volatility",
        "Momentum_10d",
        "MACD",
        "MACD_signal",
        "BB_upper",
        "BB_lower",
        # Advanced Technical (11)
        "ATR",
        "ADX",
        "Stochastic_K",
        "Stochastic_D",
        "OBV",
        "VWAP",
        "Williams_R",
        "CCI",
        "Parabolic_SAR",
        "Ichimoku_Conversion",
        "Keltner_Middle",
        # Fundamentals (10)
        "pe_ratio",
        "peg_ratio",
        "roe",
        "debt_to_equity",
        "profit_margin",
        "operating_margin",
        "eps_growth",
        "revenue_growth",
        "free_cash_flow",
        "dividend_yield",
        # Sentiment (5)
        "analyst_rating",
        "institutional_ownership",
        "insider_ownership",
        "short_ratio",
        "news_sentiment",
        # Macro (5)
        "vix",
        "treasury_yield",
        "usd_index",
        "market_breadth",
        "sector_performance",
    ]


def select_best_features(X: pd.DataFrame, y: pd.Series, k: int = 30) -> List[str]:
    """
    Select top K features using SelectKBest with f_classif.

    Args:
        X: Feature DataFrame
        y: Target series
        k: Number of features to select (default: 30)

    Returns:
        List of selected feature names
    """
    from sklearn.feature_selection import SelectKBest, f_classif

    # Remove NaN and inf values
    X_clean = X.replace([np.inf, -np.inf], np.nan).fillna(X.median())

    selector = SelectKBest(f_classif, k=min(k, X.shape[1]))
    selector.fit(X_clean, y)

    # Get selected feature names
    selected_mask = selector.get_support()
    selected_features = X.columns[selected_mask].tolist()

    logger.info(f"Selected {len(selected_features)} best features from {X.shape[1]}")

    return selected_features
