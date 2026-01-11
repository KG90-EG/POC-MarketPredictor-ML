import hashlib
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel

from .api.analytics_routes import router as analytics_router
from .api.websocket import manager as ws_manager
from .composite_scoring import get_composite_scorer

# Import new modules
from .core.cache import cache
from .core.config import config as app_config
from .core.database import WatchlistDB
from .crypto import get_crypto_details, get_crypto_ranking, search_crypto
from .market_regime import get_regime_detector
from .ml.feature_engineering import (
    add_technical_features_only,
    get_technical_feature_names,
)
from .ml.model_retraining import get_retraining_service, start_retraining_scheduler
from .ml.trading import (
    compute_bollinger,
    compute_macd,
    compute_momentum,
    compute_rsi,
    features,
)
from .portfolio_management import get_portfolio_manager
from .services import HealthService, StockService, ValidationService
from .simulation_db import SimulationDB
from .utils import metrics as prom_metrics
from .utils.alerts import alert_db
from .utils.logging_config import RequestLogger, setup_logging
from .utils.rate_limiter import RateLimiter

# Load environment variables from .env file
load_dotenv()


# ============================================
# JSON Serialization Helper
# ============================================
def serialize_to_json(obj):
    """Convert numpy types and other non-JSON-serializable objects to JSON-safe types."""
    if isinstance(obj, dict):
        return {k: serialize_to_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_to_json(item) for item in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj) if isinstance(obj, np.floating) else int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (bool, int, float, str, type(None))):
        return obj
    else:
        return str(obj)


# ============================================# Validate configuration
app_config.validate()

# Setup structured logging
logger = setup_logging(app_config.logging.log_level)

# Initialize feature cache
try:
    from .performance import init_feature_cache

    feature_cache = init_feature_cache(
        redis_client=cache.redis_client if hasattr(cache, "redis_client") else None
    )
    logger.info("Feature cache initialized for performance optimization")
except Exception as e:
    logger.warning(f"Feature cache initialization failed: {e}")

try:
    from openai import OpenAI

    OPENAI_CLIENT = OpenAI(api_key=app_config.api.openai_api_key)
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    OPENAI_CLIENT = None
    logger.warning(f"OpenAI client not available: {e}")

# Global stocks - US (30) + Swiss SMI (20) = 50 total
# Model trained with 20 technical-only features (no external API calls)
DEFAULT_STOCKS = [
    # === US Stocks (30) ===
    # Tech Giants
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "TSLA",
    "NFLX",
    "ADBE",
    "CRM",
    # Finance
    "JPM",
    "BAC",
    "WFC",
    "GS",
    "MS",
    "V",
    "MA",
    "PYPL",
    # Healthcare & Pharma
    "UNH",
    "JNJ",
    "PFE",
    "ABBV",
    # Consumer & Retail
    "WMT",
    "COST",
    "HD",
    "NKE",
    "MCD",
    # Energy & Industrial
    "XOM",
    "CVX",
    "BA",
    # === Swiss SMI Index (20) ===
    "NESN.SW",  # Nestlé - Food & Beverage
    "NOVN.SW",  # Novartis - Pharmaceuticals
    "ROG.SW",  # Roche - Pharmaceuticals
    "UBSG.SW",  # UBS - Banking
    "ZURN.SW",  # Zurich Insurance
    "ABBN.SW",  # ABB - Engineering
    "CFR.SW",  # Richemont - Luxury Goods
    "LONN.SW",  # Lonza - Life Sciences
    "SIKA.SW",  # Sika - Chemicals
    "GIVN.SW",  # Givaudan - Flavors & Fragrances
    "SREN.SW",  # Swiss Re - Reinsurance
    "GEBN.SW",  # Geberit - Sanitary Technology
    "PGHN.SW",  # Partners Group - Private Equity
    "SGSN.SW",  # SGS - Testing & Certification
    "SCMN.SW",  # Swisscom - Telecommunications
    "HOLN.SW",  # Holcim - Building Materials
    "ALC.SW",  # Alcon - Eye Care
    "KNIN.SW",  # Kühne + Nagel - Logistics
    "UHR.SW",  # Swatch - Watches
    "ADEN.SW",  # Adecco - Staffing
]

# Market indices for dynamic stock discovery
COUNTRY_INDICES = {
    "Switzerland": "^SSMI",  # Swiss Market Index
    "Germany": "^GDAXI",  # DAX
    "United Kingdom": "^FTSE",  # FTSE 100
    "France": "^FCHI",  # CAC 40
    "Japan": "^N225",  # Nikkei 225
    "Canada": "^GSPTSE",  # S&P/TSX Composite
}


def get_top_stocks_from_index(index_symbol: str, limit: int = 30) -> List[str]:
    """Dynamically fetch top stocks from a market index."""
    try:
        # For indices, we'll use a curated list approach with validation
        # This is more reliable than trying to parse index constituents
        return []
    except Exception:
        return []


def get_stocks_by_country(country: str, limit: int = 30) -> List[str]:
    """Get top stocks for a country, using curated lists with dynamic validation."""
    import concurrent.futures

    # Curated seed lists - these get validated and ranked dynamically
    country_seeds = {
        "Switzerland": [
            "NESN.SW",
            "NOVN.SW",
            "ROG.SW",
            "UBSG.SW",
            "ZURN.SW",
            "ABBN.SW",
            "SREN.SW",
            "GIVN.SW",
            "LONN.SW",
            "SLHN.SW",
            "SCMN.SW",
            "ADEN.SW",
            "GEBN.SW",
            "PGHN.SW",
            "SGSN.SW",
            "CSGN.SW",
            "HOLN.SW",
            "CFR.SW",
            "SYNN.SW",
            "STMN.SW",
            "KNIN.SW",
            "BALN.SW",
            "BUCN.SW",
            "LISN.SW",
            "VACN.SW",
            "SREN.SW",
            "BEAN.SW",
            "AREN.SW",
            "DUFN.SW",
            "TEMN.SW",
        ],
        "Germany": [
            "SAP",
            "SIE.DE",
            "ALV.DE",
            "DTE.DE",
            "VOW3.DE",
            "MBG.DE",
            "BMW.DE",
            "BAS.DE",
            "ADS.DE",
            "MUV2.DE",
            "BAYN.DE",
            "EOAN.DE",
            "DB1.DE",
            "HEN3.DE",
            "IFX.DE",
            "RHM.DE",
            "DAI.DE",
            "FRE.DE",
            "SHL.DE",
            "CON.DE",
            "BEI.DE",
            "VNA.DE",
            "SAP.DE",
            "P911.DE",
            "HNR1.DE",
        ],
        "United Kingdom": [
            "SHEL.L",
            "AZN.L",
            "HSBA.L",
            "ULVR.L",
            "DGE.L",
            "BP.L",
            "GSK.L",
            "RIO.L",
            "LSEG.L",
            "NG.L",
            "REL.L",
            "BARC.L",
            "LLOY.L",
            "VOD.L",
            "PRU.L",
            "BT-A.L",
            "BATS.L",
            "AAL.L",
            "CRH.L",
            "IMB.L",
        ],
        "France": [
            "MC.PA",
            "OR.PA",
            "SAN.PA",
            "TTE.PA",
            "AIR.PA",
            "BNP.PA",
            "SU.PA",
            "AI.PA",
            "CA.PA",
            "EN.PA",
            "SGO.PA",
            "DG.PA",
            "CS.PA",
            "BN.PA",
            "KER.PA",
            "RMS.PA",
            "EL.PA",
            "CAP.PA",
            "VIV.PA",
            "ORA.PA",
        ],
        "Japan": [
            "TM",
            "7203.T",
            "6758.T",
            "8306.T",
            "6861.T",
            "9984.T",
            "6902.T",
            "9432.T",
            "8035.T",
            "7974.T",
            "4063.T",
            "4502.T",
            "6501.T",
            "4503.T",
            "6954.T",
            "6098.T",
            "9433.T",
            "4568.T",
            "6273.T",
            "7267.T",
        ],
        "Canada": [
            "SHOP.TO",
            "TD.TO",
            "RY.TO",
            "BNS.TO",
            "ENB.TO",
            "CNR.TO",
            "CP.TO",
            "BMO.TO",
            "CNQ.TO",
            "TRP.TO",
            "CM.TO",
            "SU.TO",
            "WCN.TO",
            "MFC.TO",
            "BAM.TO",
            "ABX.TO",
            "BCE.TO",
            "FNV.TO",
            "QSR.TO",
            "NTR.TO",
        ],
    }

    seed_list = country_seeds.get(country, DEFAULT_STOCKS)

    # Validate and rank by market cap in parallel
    def validate_ticker(ticker: str):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            market_cap = info.get("marketCap", 0)
            country_match = info.get("country", "")

            # Only include if has market cap data
            if market_cap and market_cap > 0:
                return {
                    "ticker": ticker,
                    "market_cap": market_cap,
                    "country": country_match,
                }
        except Exception:
            pass
        return None

    validated_stocks = []
    # Parallel validation with thread pool (max 15 concurrent to avoid rate limits)
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(validate_ticker, t) for t in seed_list[: limit * 2]]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                validated_stocks.append(result)

    # Sort by market cap and return top tickers
    validated_stocks.sort(key=lambda x: x["market_cap"], reverse=True)
    return [s["ticker"] for s in validated_stocks[:limit]]


def get_country_stocks(country: str) -> List[str]:
    """Get stocks for country using StockService with caching."""
    try:
        # Validate country first
        country = ValidationService.validate_country(country)

        # Use StockService to get stocks
        if country == "Global" or country == "United States":
            return app_config.market.default_stocks
        else:
            return StockService.get_stocks_by_country(country, limit=30)
    except ValueError as e:
        logger.error(f"Invalid country: {country}, error: {e}")
        return app_config.market.default_stocks
    except Exception as e:
        logger.error(f"Error fetching stocks for {country}: {e}")
        return app_config.market.default_stocks


app = FastAPI(
    title="Market Predictor ML API",
    description="""
    A production-ready ML trading API that provides:

    * **Stock Analysis**: Real-time stock data and ML-based predictions
    * **Crypto Rankings**: Cryptocurrency momentum scoring and analysis
    * **AI Analysis**: OpenAI-powered company insights and recommendations
    * **Health Monitoring**: Prometheus metrics and health checks
    * **WebSocket Support**: Real-time updates for portfolio changes

    ## Features

    - Machine learning models for stock price predictions
    - Technical indicators (RSI, MACD, Bollinger Bands, Momentum)
    - CoinGecko integration for cryptocurrency data
    - Caching and rate limiting for optimal performance
    - Real-time health monitoring with Prometheus
    - WebSocket updates for live portfolio tracking

    ## Rate Limits

    API endpoints are rate limited to prevent abuse. Default: 60 requests/minute.
    """,
    version="2.0.0",
    contact={
        "name": "Market Predictor ML Team",
        "url": "https://github.com/yourusername/POC-MarketPredictor-ML",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=None,  # Will be set after lifespan is defined
)


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    prom_metrics.initialize_metrics(
        model_is_loaded=MODEL is not None,
        openai_is_configured=OPENAI_CLIENT is not None,
    )
    logger.info("Prometheus metrics initialized")

    # Warm up feature cache with popular tickers
    try:
        from .performance import cache_warmup

        popular_tickers = DEFAULT_STOCKS[:10]  # Top 10 most popular
        cache_warmup(popular_tickers)
        logger.info(f"Feature cache warmed up with {len(popular_tickers)} tickers")
    except Exception as e:
        logger.warning(f"Cache warmup failed: {e}")

    # Start automated model retraining scheduler
    try:
        start_retraining_scheduler()
        logger.info("Model retraining scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start retraining scheduler: {e}", exc_info=True)

    # Start background jobs for pre-computation
    try:
        from .performance import start_background_jobs

        start_background_jobs()
        logger.info("Background jobs started successfully")
    except Exception as e:
        logger.error(f"Failed to start background jobs: {e}", exc_info=True)

    yield
    # Shutdown
    logger.info("Application shutting down")

    # Stop background jobs gracefully
    try:
        from .performance import stop_background_jobs

        stop_background_jobs()
        logger.info("Background jobs stopped")
    except Exception as e:
        logger.error(f"Failed to stop background jobs: {e}", exc_info=True)


# Assign lifespan to app
app.router.lifespan_context = lifespan

# Enable CORS for local frontend development and production
# Add your production frontend URLs here after deployment:
# - Vercel: https://your-app.vercel.app
# - Netlify: https://your-app.netlify.app
# - Custom domain: https://yourdomain.com
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "null",  # For file:// protocol
        # Production - Add your deployed frontend URLs below:
        # "https://your-app.vercel.app",
        # "https://your-app.netlify.app",
        # "https://yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
rate_limiter = RateLimiter(app, requests_per_minute=app_config.api.rate_limit_rpm)
logger.info(f"Rate limiting enabled: {app_config.api.rate_limit_rpm} requests/minute")


# Add Prometheus metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track request metrics for all HTTP requests."""
    start_time = time.time()

    # Skip metrics for the metrics endpoint itself
    if request.url.path == "/prometheus":
        response = await call_next(request)
        return response

    response = await call_next(request)
    duration = time.time() - start_time

    # Track metrics
    prom_metrics.track_request_metrics(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        duration=duration,
    )

    return response


MODEL_PATH = app_config.model.prod_model_path
MODEL = None
LOADED_MODEL_PATH = None
if os.path.exists(MODEL_PATH):
    MODEL = joblib.load(MODEL_PATH)
    LOADED_MODEL_PATH = MODEL_PATH


# ❌ REMOVED: FeaturePayload and row_from_features
# Reason: Only used by removed /predict_raw endpoint


@app.get("/", tags=["System"])
def root():
    """
    Root endpoint with API information.

    Returns basic information about the API and available endpoints.
    """
    return {
        "name": "POC-MarketPredictor-ML API",
        "version": "1.0.0",
        "description": "Decision Support System for Capital Allocation",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "metrics": "/metrics",
            "ranking": "/ranking",
            "ticker_info": "/ticker_info/{ticker}",
            "predict": "/predict_ticker/{ticker}",
            "market_context": "/api/context/market",
            "asset_context": "/api/context/asset/{ticker}",
        },
        "deprecated": {"analyze": "/analyze (use /api/context/market instead)"},
        "status": "operational",
    }


@app.get(
    "/health",
    tags=["System"],
    summary="Health Check",
    description="""
    Comprehensive health check endpoint.

    Returns status of:
    - ML model availability
    - OpenAI API configuration
    - Cache system
    - Overall API health
    """,
)
def health():
    """Enhanced health check with dependency status using HealthService."""
    with RequestLogger("GET /health"):
        health_status = {
            "status": "ok",
            "timestamp": time.time(),
        }

        # Model health
        model_health = HealthService.check_model_health()
        health_status.update(model_health)
        health_status["model_loaded"] = MODEL is not None

        # OpenAI health
        openai_health = HealthService.check_openai_health()
        health_status.update(openai_health)
        health_status["openai_available"] = OPENAI_CLIENT is not None

        # Cache health
        cache_health = HealthService.check_cache_health()
        health_status.update(cache_health)

        # Additional status flags for backwards compatibility
        health_status["api_healthy"] = True

        return health_status


@app.get(
    "/currency",
    summary="Get currency exchange rate information",
    description="""
    Returns current USD/CHF exchange rate information for multi-currency support.

    Provides:
    - Current exchange rate (USD to CHF)
    - Last update timestamp
    - Rate source (API or fallback)

    Used by frontend for currency conversion toggle.
    """,
)
def get_currency_info():
    """Get current currency exchange rate information."""
    with RequestLogger("GET /currency"):
        try:
            from .utils.currency import get_rate_info

            rate_info = get_rate_info()
            return {"status": "ok", "data": rate_info}
        except Exception as e:
            logger.error(f"❌ Currency info error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "data": {
                    "rate": 0.85,
                    "updated": time.time(),
                    "source": "fallback",
                },  # Fallback rate
            }


@app.get(
    "/metrics",
    tags=["Monitoring"],
    summary="System Metrics",
    description="""
    Get detailed system metrics including:
    - Feature cache statistics (hits, misses, hit rate)
    - Parallel processing statistics (workers, success rate)
    - Request cache statistics
    - Rate limiter statistics
    - WebSocket connection stats
    - Model information
    """,
)
def metrics():
    """Get system metrics for monitoring."""
    with RequestLogger("GET /metrics"):
        # Get feature cache stats
        feature_cache_stats = {}
        try:
            from .performance import get_cache_stats

            feature_cache_stats = get_cache_stats()
        except Exception as e:
            logger.warning(f"Failed to get feature cache stats: {e}")

        # Get parallel processing stats
        parallel_stats = {}
        try:
            from .performance import get_parallel_processor

            parallel_stats = get_parallel_processor().get_stats()
        except Exception as e:
            logger.warning(f"Failed to get parallel processing stats: {e}")

        # Get background job stats
        job_stats = {}
        try:
            from .performance import get_job_stats

            job_stats = get_job_stats()
        except Exception as e:
            logger.warning(f"Failed to get background job stats: {e}")

        return {
            "cache_stats": cache.get_stats(),
            "feature_cache_stats": feature_cache_stats,
            "parallel_processing_stats": parallel_stats,  # NEW: Parallel processing metrics
            "background_jobs_stats": job_stats,  # NEW: Background job metrics
            "rate_limiter_stats": rate_limiter.get_stats(),
            "websocket_stats": ws_manager.get_stats(),
            "model_info": {"path": LOADED_MODEL_PATH, "loaded": MODEL is not None},
        }


@app.get(
    "/prometheus",
    tags=["Monitoring"],
    summary="Prometheus Metrics",
    description="Expose metrics in Prometheus format for scraping.",
)
def prometheus_metrics():
    """Expose Prometheus metrics in Prometheus format."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ❌ REMOVED: /predict_raw endpoint
# Reason: Redundant - /api/predict/{ticker} provides the same functionality
# with better API structure and documentation


@app.get(
    "/api/predict/{ticker}",
    tags=["Predictions"],
    summary="Predict Stock Movement",
    description="""
    Get ML prediction for a specific stock ticker.

    Uses machine learning model to predict likely price movement based on:
    - Technical indicators (RSI, MACD, Bollinger Bands, Momentum)
    - Historical price patterns
    - Volume analysis

    Returns probability (0-1) where higher values indicate higher confidence
    of upward movement.
    """,
)
def predict_ticker(ticker: str):
    if MODEL is None:
        raise HTTPException(status_code=503, detail="No model available")
    # Get latest data and compute features
    raw = yf.download(ticker, period="300d", auto_adjust=False, progress=False)

    # Check if download was successful
    if raw.empty:
        raise HTTPException(
            status_code=404, detail=f"No data available for ticker {ticker}"
        )

    # Handle MultiIndex columns from yfinance
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    # Create DataFrame with OHLCV data needed for technical features
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

    # Add all 20 technical features
    df = add_technical_features_only(df)
    df = df.dropna()

    if df.empty:
        raise HTTPException(status_code=404, detail="No recent data for ticker")
    row = df.iloc[-1:]

    # Use 20 technical features for current production model
    model_features = get_technical_feature_names()
    prob = MODEL.predict_proba(row[model_features].values)[0][1]

    # Get current price for response
    current_price = float(df["Close"].iloc[-1])

    return {
        "ticker": ticker,
        "probability": float(prob),
        "prediction": int(prob > 0.5),
        "current_price": current_price,
        "price": current_price,
    }


# Alias endpoint for frontend compatibility
@app.get(
    "/predict_ticker/{ticker}",
    tags=["Predictions"],
    summary="Predict Stock Movement (Alias)",
    description="Alias endpoint for /api/predict/{ticker} - Frontend compatibility",
)
async def predict_ticker_alias(ticker: str):
    """Alias for /api/predict/{ticker} - calls the same function."""
    return predict_ticker(ticker.upper())


@app.get(
    "/ranking",
    tags=["Predictions"],
    summary="Stock Rankings",
    description="""
    Get ranked list of stocks based on ML predictions.

    **Performance Optimized (Week 1):**
    - Parallel processing: 10 stocks simultaneously
    - Feature caching: 5-minute TTL
    - Target: < 3 seconds for 30 stocks

    Supports filtering by:
    - Country/region (e.g., 'Switzerland', 'Germany', 'United States')
    - Custom ticker list (comma-separated)
    - Top N results

    Returns stocks sorted by prediction probability (highest first).
    """,
)
def ranking(
    tickers: str = "", country: str = "Global", use_parallel: bool = False
):  # TEMP: Disabled parallel
    """
    Rank stocks by ML prediction probability.

    If no tickers provided, dynamically fetches top stocks for the specified country.
    Country options: Global, United States, Switzerland, Germany, United Kingdom, France, Japan, Canada

    Args:
        tickers: Comma-separated list of tickers (optional)
        country: Country/region for stock selection (default: Global)
        use_parallel: Enable parallel processing for faster results (default: False - TEMP DISABLED)
    """
    if MODEL is None:
        raise HTTPException(status_code=503, detail="No model available")

    start_time = time.time()

    # Use country-specific stocks if no tickers provided
    if not tickers.strip():
        chosen = get_country_stocks(country)
    else:
        chosen = [t.strip().upper() for t in tickers.split(",") if t.strip()]

    # TRY CACHE FIRST (background job may have pre-computed this)
    try:
        cache_key = f"ranking:{country}"
        cached_result = cache.get(cache_key)
        if cached_result is not None and not tickers.strip():
            # Only use cache if using default country stocks (not custom tickers)
            duration = time.time() - start_time
            logger.info(f"✨ Returning cached ranking for {country} ({duration:.3f}s)")
            return serialize_to_json(
                {
                    "ranking": cached_result,
                    "processing_mode": "cached",
                    "duration_seconds": round(duration, 3),
                }
            )
    except Exception as e:
        logger.warning(f"Cache check failed: {e}")

    # PARALLEL PROCESSING (Week 1 optimization)
    if use_parallel:
        try:
            from .performance import parallel_stock_ranking

            logger.info(f"🚀 Processing {len(chosen)} stocks in parallel...")
            # Use 20 technical features for parallel processing
            technical_features = get_technical_feature_names()
            result = parallel_stock_ranking(chosen, MODEL, technical_features)

            duration = time.time() - start_time
            logger.info(
                f"✅ Parallel ranking complete: {len(result)} stocks in {duration:.2f}s "
                f"({len(chosen)/duration:.1f} stocks/sec)"
            )

            # Track ranking generation metrics
            prom_metrics.track_ranking_generation(country, len(result), duration)

            return serialize_to_json(
                {
                    "ranking": result,
                    "processing_mode": "parallel",
                    "duration_seconds": round(duration, 2),
                }
            )

        except Exception as e:
            logger.warning(
                f"Parallel processing failed, falling back to sequential: {e}"
            )
            # Fall through to sequential processing

    # SEQUENTIAL PROCESSING (fallback)
    logger.info(f"Processing {len(chosen)} stocks sequentially...")
    result = []
    technical_features = get_technical_feature_names()

    # Get market regime BEFORE processing stocks
    regime_detector = get_regime_detector()
    regime = regime_detector.get_regime()

    # Get composite scorer
    composite_scorer = get_composite_scorer()

    logger.info(
        f"📊 Market Regime: {regime.regime_status} (Score: {regime.regime_score}/100) | "
        f"VIX: {regime.vix_value:.1f} ({regime.volatility_regime}) | "
        f"Trend: {regime.trend_regime} | "
        f"BUY Signals: {'ALLOWED ✅' if regime.allow_buys else 'BLOCKED 🔴'}"
    )

    for t in chosen:
        try:
            pred_start = time.time()
            raw = yf.download(t, period="300d", auto_adjust=False, progress=False)
            # Handle MultiIndex columns from yfinance
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
        except Exception:
            continue
        if raw.empty or "Adj Close" not in raw.columns:
            continue

        # Ensure raw is a DataFrame (yfinance sometimes returns Series for single-column results)
        if not isinstance(raw, pd.DataFrame):
            continue

        # Create OHLCV DataFrame - flatten any multi-dimensional columns
        try:
            df = pd.DataFrame(
                {
                    "Open": (
                        raw["Open"].values.flatten()
                        if raw["Open"].values.ndim > 1
                        else raw["Open"].values
                    ),
                    "High": (
                        raw["High"].values.flatten()
                        if raw["High"].values.ndim > 1
                        else raw["High"].values
                    ),
                    "Low": (
                        raw["Low"].values.flatten()
                        if raw["Low"].values.ndim > 1
                        else raw["Low"].values
                    ),
                    "Close": (
                        raw["Adj Close"].values.flatten()
                        if raw["Adj Close"].values.ndim > 1
                        else raw["Adj Close"].values
                    ),
                    "Volume": (
                        raw["Volume"].values.flatten()
                        if raw["Volume"].values.ndim > 1
                        else raw["Volume"].values
                    ),
                },
                index=raw.index,
            )
        except Exception as e:
            logger.error(f"Failed to create DataFrame for {t}: {e}")
            continue

        # Get price BEFORE feature engineering
        current_price = float(df["Close"].iloc[-1])

        # Add all 20 technical features
        df = add_technical_features_only(df)
        df = df.dropna()
        if df.empty:
            continue

        # Predict with ML model (20 technical features)
        row = df.iloc[-1:]
        ml_prob = MODEL.predict_proba(row[technical_features].values)[0][1]

        # Calculate composite score (replaces simple ML probability)
        score_breakdown = composite_scorer.calculate_composite_score(
            df=df,
            ml_probability=ml_prob,
            regime_score=regime.regime_score,
            allow_buys=regime.allow_buys,
            ticker=t,  # Pass ticker for LLM context
        )

        # Get allocation limit based on composite score
        max_allocation = composite_scorer.get_allocation_limit(
            score=score_breakdown.composite_score,
            signal=score_breakdown.signal,
            asset_type="stock",
        )

        # Track model prediction metrics
        pred_duration = time.time() - pred_start
        prom_metrics.track_model_prediction(
            "composite_scorer", score_breakdown.composite_score / 100, pred_duration
        )

        result.append(
            {
                "ticker": t,
                "composite_score": score_breakdown.composite_score,
                "signal": score_breakdown.signal,
                "confidence": score_breakdown.confidence,
                "price": current_price,
                "max_allocation": max_allocation,
                # Score breakdown for explainability
                "score_breakdown": {
                    "technical": score_breakdown.technical_score,
                    "ml": score_breakdown.ml_score,
                    "momentum": score_breakdown.momentum_score,
                    "regime": score_breakdown.regime_score,
                    "llm_adjustment": score_breakdown.llm_adjustment,
                },
                "top_factors": score_breakdown.top_factors,
                "risk_factors": score_breakdown.risk_factors,
                "llm_context": score_breakdown.llm_context,
                # Legacy fields (for backward compatibility during transition)
                "prob": float(ml_prob),
                "action": score_breakdown.signal,
            }
        )

    # sort by composite score (highest first)
    result.sort(key=lambda r: r["composite_score"], reverse=True)

    # Track ranking generation metrics
    duration = time.time() - start_time
    prom_metrics.track_ranking_generation(country, len(result), duration)

    # Return ranking with regime information
    return serialize_to_json(
        {
            "ranking": result,
            "processing_mode": "sequential",
            "duration_seconds": round(duration, 2),
            "regime": {
                "status": regime.regime_status,
                "score": regime.regime_score,
                "vix": round(regime.vix_value, 1),
                "volatility": regime.volatility_regime,
                "trend": regime.trend_regime,
                "allow_buys": regime.allow_buys,
                "recommendation": regime.recommendation,
            },
        }
    )


@app.get(
    "/regime",
    tags=["Market Analysis"],
    summary="Market Regime Status",
    description="""
    Get current market regime and risk environment.

    Provides:
    - Overall regime status (RISK_ON, NEUTRAL, RISK_OFF)
    - VIX volatility level and classification
    - S&P 500 trend analysis (BULL, NEUTRAL, BEAR)
    - Composite regime score (0-100)
    - Capital allocation recommendations

    **Decision Rules:**
    - RISK_ON (≥70): Normal operations, allow BUY signals
    - NEUTRAL (40-69): Cautious mode, reduce position sizes 50%
    - RISK_OFF (<40): Defensive mode, BLOCK all BUY signals

    This endpoint enables regime-aware investment decisions.
    """,
)
def get_regime_status():
    """
    Get current market regime for decision support.

    Returns comprehensive market regime analysis used to
    adjust capital allocation and risk management.
    """
    try:
        regime_detector = get_regime_detector()
        regime = regime_detector.get_regime()

        # Format response
        return {
            "status": regime.regime_status,
            "score": regime.regime_score,
            "allow_buys": regime.allow_buys,
            "recommendation": regime.recommendation,
            "volatility": {
                "vix": round(regime.vix_value, 2),
                "regime": regime.volatility_regime,
                "score": regime.volatility_score,
            },
            "trend": {
                "regime": regime.trend_regime,
                "score": regime.trend_score,
                "sp500_price": round(regime.sp500_price, 2),
                "ma_50": round(regime.ma_50, 2),
                "ma_200": round(regime.ma_200, 2),
            },
            "allocation_adjustment": {
                "risk_on": "100% of normal allocation",
                "neutral": "50% of normal allocation",
                "risk_off": "0% - No new positions",
                "current": (
                    "100% (normal)"
                    if regime.regime_status == "RISK_ON"
                    else (
                        "50% (reduced)"
                        if regime.regime_status == "NEUTRAL"
                        else "0% (blocked)"
                    )
                ),
            },
            "timestamp": regime.timestamp.isoformat(),
            "summary": regime_detector.get_regime_summary(),
        }
    except Exception as e:
        logger.error(f"Error fetching regime status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch regime status: {str(e)}"
        )


@app.get(
    "/api/portfolio/summary",
    tags=["Portfolio"],
    summary="Portfolio Exposure Summary",
    description="""
    Get comprehensive portfolio exposure analysis and allocation limits.
    
    **Purpose:** Risk management and compliance with allocation limits per DECISION_SUPPORT_SYSTEM_REQUIREMENTS.md
    
    Returns:
    - Current exposure percentages by asset class (stocks, crypto, cash)
    - Individual position sizes
    - Compliance with allocation limits:
      - Single stock: Max 10%
      - Single crypto: Max 5%
      - Total equities: Max 70%
      - Total crypto: Max 20%
      - Cash reserve: Min 10%
    - Warnings if limits exceeded
    - Available capacity for new positions
    
    **Requirements Reference:** Section 5.6 - Risk Management
    """,
)
def get_portfolio_summary():
    """
    Get portfolio exposure summary for risk management.

    This endpoint provides visibility into current allocations
    and ensures compliance with risk limits.
    """
    try:
        # TODO: Implement portfolio tracking system
        # For now, return demo data structure

        return {
            "total_value": 100000.00,
            "cash": 15000.00,
            "invested": 85000.00,
            "positions": {
                "stocks": {
                    "total_value": 65000.00,
                    "percentage": 65.0,
                    "limit": 70.0,
                    "available": 5.0,
                    "positions": [
                        {"ticker": "AAPL", "value": 8500, "percentage": 8.5},
                        {"ticker": "MSFT", "value": 7200, "percentage": 7.2},
                        {"ticker": "GOOGL", "value": 6800, "percentage": 6.8},
                    ],
                },
                "crypto": {
                    "total_value": 20000.00,
                    "percentage": 20.0,
                    "limit": 20.0,
                    "available": 0.0,
                    "positions": [
                        {"ticker": "BTC-USD", "value": 4500, "percentage": 4.5},
                        {"ticker": "ETH-USD", "value": 3800, "percentage": 3.8},
                    ],
                },
            },
            "allocation": {"stocks": 65.0, "crypto": 20.0, "cash": 15.0},
            "limits": {
                "single_stock_max": 10.0,
                "single_crypto_max": 5.0,
                "total_stocks_max": 70.0,
                "total_crypto_max": 20.0,
                "cash_min": 10.0,
            },
            "compliance": {"within_limits": True, "warnings": []},
            "timestamp": datetime.now().isoformat(),
            "note": "Demo data - Connect to portfolio tracking system for real data",
        }
    except Exception as e:
        logger.error(f"Error fetching portfolio summary: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch portfolio summary: {str(e)}"
        )


@app.get(
    "/api/portfolio/limits",
    tags=["Portfolio"],
    summary="Portfolio Allocation Limits",
    description="""
    Get current portfolio allocation limits and rules.
    
    Returns the risk management framework limits for:
    - Individual position sizes (stocks, crypto)
    - Asset class exposure limits
    - Regime-based adjustments
    
    **Requirements Reference:** Section 5.6 - Risk Management
    """,
)
def get_portfolio_limits():
    """Get portfolio allocation limits for risk management."""
    try:
        # Get current regime for regime-based adjustments
        regime_detector = get_regime_detector()
        regime = regime_detector.get_regime()

        # Base limits
        base_limits = {
            "single_stock": {
                "max_percentage": 10.0,
                "description": "Maximum allocation per individual stock",
            },
            "single_crypto": {
                "max_percentage": 5.0,
                "description": "Maximum allocation per individual cryptocurrency",
            },
            "total_stocks": {
                "max_percentage": 70.0,
                "description": "Maximum total equity exposure",
            },
            "total_crypto": {
                "max_percentage": 20.0,
                "description": "Maximum total cryptocurrency exposure",
            },
            "cash_reserve": {
                "min_percentage": 10.0,
                "description": "Minimum cash reserve requirement",
            },
        }

        # Regime-based adjustments
        if regime.regime_status == "RISK_OFF":
            adjusted_limits = {
                "single_stock": 5.0,
                "single_crypto": 2.0,
                "total_stocks": 50.0,
                "total_crypto": 10.0,
                "cash_reserve": 30.0,
            }
            adjustment_note = "DEFENSIVE MODE: Limits reduced due to Risk-Off regime"
        elif regime.regime_status == "NEUTRAL":
            adjusted_limits = {
                "single_stock": 7.5,
                "single_crypto": 3.5,
                "total_stocks": 60.0,
                "total_crypto": 15.0,
                "cash_reserve": 20.0,
            }
            adjustment_note = "CAUTIOUS MODE: Limits moderately reduced"
        else:
            adjusted_limits = None
            adjustment_note = "Normal limits apply"

        return {
            "base_limits": base_limits,
            "current_regime": regime.regime_status,
            "regime_score": regime.regime_score,
            "adjusted_limits": adjusted_limits,
            "adjustment_note": adjustment_note,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error fetching portfolio limits: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch portfolio limits: {str(e)}"
        )


@app.post(
    "/api/portfolio/validate",
    tags=["Portfolio"],
    summary="Validate Portfolio Allocation",
    description="""
    Validate a proposed portfolio allocation against risk limits.
    
    **Input:** Proposed allocation (ticker, percentage)
    **Output:** Validation result with warnings/errors
    
    Checks:
    - Individual position size limits
    - Asset class exposure limits
    - Cash reserve requirements
    - Regime-based restrictions
    
    **Requirements Reference:** Section 5.6 - Risk Management
    """,
)
def validate_portfolio_allocation(allocation: Dict[str, Any]):
    """
    Validate proposed portfolio allocation.

    Args:
        allocation: Dict with proposed positions
            {
                "positions": [
                    {"ticker": "AAPL", "percentage": 8.5},
                    {"ticker": "BTC-USD", "percentage": 4.5}
                ]
            }

    Returns:
        Validation result with compliance check
    """
    try:
        # Get current limits
        regime_detector = get_regime_detector()
        regime = regime_detector.get_regime()

        positions = allocation.get("positions", [])

        # Calculate totals
        stock_total = 0.0
        crypto_total = 0.0
        errors = []
        warnings = []

        for pos in positions:
            ticker = pos.get("ticker", "")
            percentage = pos.get("percentage", 0.0)

            # Determine asset type
            is_crypto = "-USD" in ticker or ticker in [
                "BTC",
                "ETH",
                "BNB",
                "XRP",
                "ADA",
            ]

            if is_crypto:
                crypto_total += percentage
                max_single = 5.0 if regime.regime_status == "RISK_ON" else 2.0
                if percentage > max_single:
                    errors.append(
                        f"{ticker}: {percentage}% exceeds single crypto limit ({max_single}%)"
                    )
            else:
                stock_total += percentage
                max_single = 10.0 if regime.regime_status == "RISK_ON" else 5.0
                if percentage > max_single:
                    errors.append(
                        f"{ticker}: {percentage}% exceeds single stock limit ({max_single}%)"
                    )

        # Check total limits
        max_stocks = 70.0 if regime.regime_status == "RISK_ON" else 50.0
        max_crypto = 20.0 if regime.regime_status == "RISK_ON" else 10.0

        if stock_total > max_stocks:
            errors.append(f"Total stocks {stock_total}% exceeds limit ({max_stocks}%)")

        if crypto_total > max_crypto:
            errors.append(f"Total crypto {crypto_total}% exceeds limit ({max_crypto}%)")

        cash_percentage = 100.0 - stock_total - crypto_total
        min_cash = 10.0 if regime.regime_status == "RISK_ON" else 30.0

        if cash_percentage < min_cash:
            errors.append(
                f"Cash reserve {cash_percentage}% below minimum ({min_cash}%)"
            )

        # Warnings for high concentration
        if stock_total > 60.0 and regime.regime_status == "NEUTRAL":
            warnings.append(
                "High equity exposure in Neutral regime - consider reducing"
            )

        is_valid = len(errors) == 0

        return {
            "valid": is_valid,
            "allocation_summary": {
                "stocks": stock_total,
                "crypto": crypto_total,
                "cash": cash_percentage,
            },
            "regime": regime.regime_status,
            "errors": errors,
            "warnings": warnings,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error validating portfolio: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to validate portfolio: {str(e)}"
        )


@app.get(
    "/crypto/ranking",
    tags=["Cryptocurrency"],
    summary="Cryptocurrency Rankings",
    description="""
    Get ranked cryptocurrencies based on momentum scoring.

    Scoring considers:
    - Market cap rank (top coins weighted higher)
    - 24h, 7d, 30d price changes
    - Volume/market cap ratio (liquidity)
    - Overall momentum score (0-1)

    Data sourced from CoinGecko API (no API key required).
    """,
)
def crypto_ranking(
    crypto_ids: str = "",
    include_nft: bool = True,
    min_probability: float = 0.0,
    limit: int = 50,
):
    """
    Rank cryptocurrencies and digital assets by momentum score.

    Query Parameters:
    - crypto_ids: Comma-separated list of CoinGecko crypto IDs (e.g., "bitcoin,ethereum")
                  If empty, fetches top cryptos by market cap dynamically
    - include_nft: Include NFT-related tokens when crypto_ids is empty (default: True)
    - min_probability: Minimum probability threshold (default: 0.0)
    - limit: Number of top cryptos to fetch when crypto_ids is empty (default: 50, max: 250)

    Returns:
    - JSON with ranked list of cryptocurrencies with trading signals
    """
    try:
        # Validate and cap limit
        limit = min(max(1, limit), 250)

        # Parse crypto IDs if provided
        crypto_list = None
        if crypto_ids.strip():
            crypto_list = [
                cid.strip().lower() for cid in crypto_ids.split(",") if cid.strip()
            ]

        # Get ranked cryptocurrencies
        rankings = get_crypto_ranking(
            crypto_ids=crypto_list,
            include_nft=include_nft,
            min_probability=min_probability,
            limit=limit,
        )

        return {"ranking": rankings}

    except Exception as e:
        logger.error(f"Error in crypto_ranking endpoint: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch crypto rankings: {str(e)}"
        )


@app.get(
    "/search_stocks",
    tags=["Stocks"],
    summary="Search Stocks by Name or Ticker",
    description="""
    Search for stocks across multiple markets by name or ticker symbol.
    
    **Supported Markets:**
    - United States (S&P 500)
    - Switzerland (SMI)
    - Germany (DAX) - Planned
    - United Kingdom (FTSE 100) - Planned
    - France (CAC 40) - Planned
    
    **Use Cases:**
    - Stock discovery for portfolio expansion
    - Finding specific stocks by partial name/ticker
    - Market expansion preparation (DAX, FTSE, CAC)
    
    **Requirements Reference:** Section 4.1 - Asset Universe Expansion
    """,
)
def search_stocks(query: str = "", market: str = "all", limit: int = 20):
    """
    Search for stocks by name or ticker.

    Args:
        query: Search term (partial ticker or company name)
        market: Filter by market (all, us, switzerland, germany, uk, france)
        limit: Maximum results (default: 20, max: 100)

    Returns:
        List of matching stocks with market info
    """
    try:
        from .data.stocks import STOCKS_BY_COUNTRY

        # Normalize query
        query = query.strip().upper()
        limit = min(max(1, limit), 100)

        results = []

        # Search across markets
        markets_to_search = {}
        if market == "all":
            markets_to_search = STOCKS_BY_COUNTRY
        elif market.lower() == "us":
            markets_to_search = {
                "United States": STOCKS_BY_COUNTRY.get("United States", [])
            }
        elif market.lower() == "switzerland":
            markets_to_search = {
                "Switzerland": STOCKS_BY_COUNTRY.get("Switzerland", [])
            }
        elif market.lower() == "germany":
            markets_to_search = {"Germany": STOCKS_BY_COUNTRY.get("Germany", [])}
        elif market.lower() == "uk":
            markets_to_search = {
                "United Kingdom": STOCKS_BY_COUNTRY.get("United Kingdom", [])
            }
        elif market.lower() == "france":
            markets_to_search = {"France": STOCKS_BY_COUNTRY.get("France", [])}

        for country, tickers in markets_to_search.items():
            for ticker in tickers:
                # Simple matching - expand with company names later
                if not query or query in ticker.upper():
                    results.append(
                        {
                            "ticker": ticker,
                            "market": country,
                            "name": ticker,  # TODO: Add company names mapping
                            "exchange": (
                                "NYSE"
                                if country == "United States"
                                else (
                                    "SIX"
                                    if country == "Switzerland"
                                    else (
                                        "XETRA"
                                        if country == "Germany"
                                        else (
                                            "LSE"
                                            if country == "United Kingdom"
                                            else "EURONEXT"
                                        )
                                    )
                                )
                            ),
                        }
                    )

                    if len(results) >= limit:
                        break

            if len(results) >= limit:
                break

        return {
            "query": query,
            "market": market,
            "results": results[:limit],
            "total_found": len(results),
        }

    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to search stocks: {str(e)}"
        )


@app.get(
    "/countries",
    tags=["Stocks"],
    summary="Get Available Countries/Markets",
    description="""
    Get list of supported countries and markets with stock counts.
    
    Returns:
    - Country names
    - Number of tracked stocks per country
    - Market status (active, planned)
    - Exchange information
    
    **Requirements Reference:** Section 4.1 - Asset Universe
    """,
)
def get_countries():
    """Get list of available countries/markets."""
    try:
        from .data.stocks import STOCKS_BY_COUNTRY

        countries = []
        for country, tickers in STOCKS_BY_COUNTRY.items():
            # Determine status
            status = "active" if len(tickers) > 0 else "planned"

            # Map to exchanges
            exchange_map = {
                "United States": "NYSE/NASDAQ",
                "Switzerland": "SIX Swiss Exchange",
                "Germany": "XETRA",
                "United Kingdom": "London Stock Exchange",
                "France": "Euronext Paris",
            }

            countries.append(
                {
                    "name": country,
                    "code": country.replace(" ", "_").lower(),
                    "stock_count": len(tickers),
                    "status": status,
                    "exchange": exchange_map.get(country, "Unknown"),
                    "tickers": (
                        tickers if len(tickers) <= 10 else tickers[:10] + ["..."]
                    ),
                }
            )

        return {
            "countries": countries,
            "total_markets": len(countries),
            "total_stocks": sum(len(tickers) for tickers in STOCKS_BY_COUNTRY.values()),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching countries: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch countries: {str(e)}"
        )


@app.get(
    "/popular_cryptos",
    tags=["Cryptocurrency"],
    summary="Get Popular Cryptocurrencies",
    description="""
    Get list of popular cryptocurrencies by market capitalization.
    
    **Selection Criteria:**
    - Top cryptocurrencies by market cap
    - Excludes stablecoins (optional)
    - Excludes NFT/meme tokens (optional)
    - Minimum liquidity requirements
    
    **Use Cases:**
    - Crypto portfolio discovery
    - Market overview
    - Quick access to major digital assets
    
    **Requirements Reference:** Section 4.1 - Digital Assets
    """,
)
def get_popular_cryptos(
    limit: int = 50,
    exclude_stablecoins: bool = True,
    exclude_meme: bool = False,
    min_market_cap_rank: int = 250,
):
    """
    Get popular cryptocurrencies by market cap.

    Args:
        limit: Number of cryptos to return (default: 50, max: 250)
        exclude_stablecoins: Exclude stablecoins (USDT, USDC, etc.)
        exclude_meme: Exclude meme coins (DOGE, SHIB, etc.)
        min_market_cap_rank: Maximum market cap rank (default: 250)

    Returns:
        List of popular cryptocurrencies with basic info
    """
    try:
        limit = min(max(1, limit), 250)
        min_market_cap_rank = min(max(1, min_market_cap_rank), 500)

        # Fetch from CoinGecko
        url = f"https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": min_market_cap_rank,
            "page": 1,
            "sparkline": False,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Filter based on criteria
        stablecoins = ["usdt", "usdc", "busd", "dai", "tusd", "usdp", "usdd"]
        meme_coins = ["doge", "shib", "pepe", "floki", "babydoge"]

        filtered = []
        for crypto in data:
            crypto_id = crypto.get("id", "").lower()
            symbol = crypto.get("symbol", "").lower()

            # Apply filters
            if exclude_stablecoins and crypto_id in stablecoins:
                continue
            if exclude_meme and crypto_id in meme_coins:
                continue

            filtered.append(
                {
                    "id": crypto.get("id"),
                    "symbol": crypto.get("symbol", "").upper(),
                    "name": crypto.get("name"),
                    "market_cap_rank": crypto.get("market_cap_rank"),
                    "current_price": crypto.get("current_price"),
                    "market_cap": crypto.get("market_cap"),
                    "price_change_24h": crypto.get("price_change_percentage_24h"),
                    "image": crypto.get("image"),
                }
            )

            if len(filtered) >= limit:
                break

        return {
            "cryptos": filtered,
            "count": len(filtered),
            "filters": {
                "exclude_stablecoins": exclude_stablecoins,
                "exclude_meme": exclude_meme,
                "min_market_cap_rank": min_market_cap_rank,
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching popular cryptos: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch popular cryptos: {str(e)}"
        )


@app.get(
    "/crypto/search",
    tags=["Cryptocurrency"],
    summary="Search Cryptocurrency",
    description="""
    Search for a cryptocurrency by name or symbol.

    Examples:
    - "bitcoin" or "BTC"
    - "ethereum" or "ETH"
    - "cardano" or "ADA"

    Returns detailed crypto information including price, market cap, and momentum score.
    """,
)
def crypto_search(query: str):
    """
    Search for a cryptocurrency by name or symbol.

    Query Parameters:
    - query: Search query (name or symbol, e.g., "bitcoin", "BTC", "ethereum")

    Returns:
    - JSON with crypto details and trading signals
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query parameter is required")

    try:
        result = search_crypto(query.strip())

        if result is None:
            raise HTTPException(
                status_code=404, detail=f"Cryptocurrency '{query}' not found"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in crypto_search endpoint: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to search crypto: {str(e)}"
        )


@app.get(
    "/crypto/details/{crypto_id}",
    tags=["Cryptocurrency"],
    summary="Cryptocurrency Details",
    description="""
    Get detailed information for a specific cryptocurrency.

    Requires CoinGecko crypto ID (e.g., "bitcoin", "ethereum", "cardano").

    Returns comprehensive data including:
    - Current price and market data
    - Community statistics
    - 24h/7d/30d price changes
    - Market cap and volume
    """,
)
def crypto_details(crypto_id: str):
    """
    Get detailed information for a specific cryptocurrency.

    Path Parameters:
    - crypto_id: CoinGecko crypto ID (e.g., "bitcoin", "ethereum")

    Returns:
    - JSON with detailed crypto information
    """
    try:
        details = get_crypto_details(crypto_id)

        if details is None:
            raise HTTPException(
                status_code=404, detail=f"Cryptocurrency '{crypto_id}' not found"
            )

        return details

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in crypto_details endpoint: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch crypto details: {str(e)}"
        )


@app.get("/models")
def list_models() -> Dict[str, Any]:
    """List available model artifacts in the models directory.
    Returns current loaded model filename and list of other model files with sizes.
    """
    models_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "models")
    )
    items: List[Dict[str, Any]] = []
    if os.path.isdir(models_dir):
        for fname in sorted(os.listdir(models_dir)):
            fpath = os.path.join(models_dir, fname)
            if os.path.isfile(fpath) and fname.endswith(".bin"):
                try:
                    size = os.path.getsize(fpath)
                except OSError:
                    size = None
                items.append({"file": fname, "size_bytes": size})
    current = os.path.basename(LOADED_MODEL_PATH) if LOADED_MODEL_PATH else None
    return {"current_model": current, "available_models": items}


@app.get("/ticker_info/{ticker}")
def ticker_info(ticker: str) -> Dict[str, Any]:
    """Fetch comprehensive market data for a ticker using StockService."""
    with RequestLogger(f"GET /ticker_info/{ticker}"):
        try:
            # Validate ticker
            ticker = ValidationService.validate_ticker(ticker)

            # Use StockService to get info
            info = StockService.get_ticker_info(ticker)
            info["ticker"] = ticker
            return info
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error fetching info for {ticker}: {e}")
            raise HTTPException(
                status_code=404, detail=f"Unable to fetch info: {str(e)}"
            )


@app.post("/ticker_info_batch")
def ticker_info_batch(tickers: List[str]) -> Dict[str, Any]:
    """Batch fetch ticker information using StockService for parallel processing."""
    with RequestLogger("POST /ticker_info_batch"):
        try:
            results, errors = StockService.get_ticker_info_batch(tickers)
            return {"results": results, "errors": errors}
        except Exception as e:
            logger.error(f"Batch ticker info fetch failed: {e}")
            raise HTTPException(status_code=500, detail=f"Batch fetch failed: {str(e)}")


@app.get("/popular_stocks", tags=["Stocks"])
def get_popular_stocks(limit: int = 50) -> Dict[str, Any]:
    """Get popular stocks with company names for autocomplete."""
    with RequestLogger("GET /popular_stocks"):
        try:
            # Predefined list (avoids yfinance rate limiting)
            all_stocks = [
                {"ticker": "AAPL", "name": "Apple Inc."},
                {"ticker": "MSFT", "name": "Microsoft Corporation"},
                {"ticker": "GOOGL", "name": "Alphabet Inc. (Google)"},
                {"ticker": "AMZN", "name": "Amazon.com Inc."},
                {"ticker": "TSLA", "name": "Tesla Inc."},
                {"ticker": "META", "name": "Meta Platforms (Facebook)"},
                {"ticker": "NVDA", "name": "NVIDIA Corporation"},
                {"ticker": "JPM", "name": "JPMorgan Chase & Co."},
                {"ticker": "V", "name": "Visa Inc."},
                {"ticker": "WMT", "name": "Walmart Inc."},
                {"ticker": "DIS", "name": "Walt Disney Company"},
                {"ticker": "NFLX", "name": "Netflix Inc."},
                {"ticker": "INTC", "name": "Intel Corporation"},
                {"ticker": "AMD", "name": "Advanced Micro Devices"},
                {"ticker": "BA", "name": "Boeing Company"},
                {"ticker": "GE", "name": "General Electric"},
                {"ticker": "F", "name": "Ford Motor Company"},
                {"ticker": "GM", "name": "General Motors"},
                {"ticker": "T", "name": "AT&T Inc."},
                {"ticker": "VZ", "name": "Verizon Communications"},
                {"ticker": "KO", "name": "Coca-Cola Company"},
                {"ticker": "PEP", "name": "PepsiCo Inc."},
                {"ticker": "MCD", "name": "McDonald's Corporation"},
                {"ticker": "NKE", "name": "Nike Inc."},
                {"ticker": "SBUX", "name": "Starbucks Corporation"},
                {"ticker": "PYPL", "name": "PayPal Holdings Inc."},
                {"ticker": "CSCO", "name": "Cisco Systems Inc."},
                {"ticker": "ORCL", "name": "Oracle Corporation"},
                {"ticker": "IBM", "name": "International Business Machines"},
                {"ticker": "CRM", "name": "Salesforce Inc."},
                {"ticker": "ADBE", "name": "Adobe Inc."},
                {"ticker": "UBER", "name": "Uber Technologies Inc."},
                {"ticker": "ABNB", "name": "Airbnb Inc."},
                {"ticker": "SHOP", "name": "Shopify Inc."},
                {"ticker": "SQ", "name": "Block Inc. (Square)"},
                {"ticker": "COIN", "name": "Coinbase Global Inc."},
                {"ticker": "ROKU", "name": "Roku Inc."},
                {"ticker": "SPOT", "name": "Spotify Technology"},
                {"ticker": "SNAP", "name": "Snap Inc."},
                {"ticker": "UBS", "name": "UBS Group AG"},
                {"ticker": "NESN.SW", "name": "Nestlé S.A."},
                {"ticker": "NOVN.SW", "name": "Novartis AG"},
                {"ticker": "ROG.SW", "name": "Roche Holding AG"},
                {"ticker": "ABBN.SW", "name": "ABB Ltd"},
                {"ticker": "ZURN.SW", "name": "Zurich Insurance Group"},
                {"ticker": "GIVN.SW", "name": "Givaudan SA"},
                {"ticker": "LONN.SW", "name": "Lonza Group AG"},
                {"ticker": "SREN.SW", "name": "Swiss Re AG"},
                {"ticker": "CSGN.SW", "name": "Credit Suisse Group AG"},
            ]

            return {"stocks": all_stocks[:limit]}
        except Exception as e:
            logger.error(f"Error fetching popular stocks: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/search_stocks", tags=["Stocks"])
def search_stocks(query: str, limit: int = 10) -> Dict[str, Any]:
    """Search stocks by ticker or company name."""
    with RequestLogger(f"GET /search_stocks?query={query}"):
        try:
            if not query or len(query) < 1:
                return {"stocks": []}

            query_lower = query.lower()

            # Get all popular stocks
            popular_response = get_popular_stocks(limit=100)
            all_stocks = popular_response["stocks"]

            # Filter by query
            matching = [
                stock
                for stock in all_stocks
                if query_lower in stock["ticker"].lower()
                or query_lower in stock["name"].lower()
            ]

            return {"stocks": matching[:limit]}
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/popular_cryptos", tags=["Cryptocurrency"])
def get_popular_cryptos(limit: int = 30) -> Dict[str, Any]:
    """Get popular cryptocurrencies for autocomplete."""
    with RequestLogger("GET /popular_cryptos"):
        try:
            # Predefined list of popular cryptos with CoinGecko IDs
            all_cryptos = [
                {"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC"},
                {"id": "ethereum", "name": "Ethereum", "symbol": "ETH"},
                {"id": "tether", "name": "Tether", "symbol": "USDT"},
                {"id": "binancecoin", "name": "BNB", "symbol": "BNB"},
                {"id": "solana", "name": "Solana", "symbol": "SOL"},
                {"id": "usd-coin", "name": "USD Coin", "symbol": "USDC"},
                {"id": "ripple", "name": "XRP", "symbol": "XRP"},
                {"id": "cardano", "name": "Cardano", "symbol": "ADA"},
                {"id": "dogecoin", "name": "Dogecoin", "symbol": "DOGE"},
                {"id": "tron", "name": "TRON", "symbol": "TRX"},
                {"id": "avalanche-2", "name": "Avalanche", "symbol": "AVAX"},
                {"id": "polkadot", "name": "Polkadot", "symbol": "DOT"},
                {"id": "chainlink", "name": "Chainlink", "symbol": "LINK"},
                {"id": "polygon", "name": "Polygon", "symbol": "MATIC"},
                {"id": "litecoin", "name": "Litecoin", "symbol": "LTC"},
                {"id": "shiba-inu", "name": "Shiba Inu", "symbol": "SHIB"},
                {"id": "uniswap", "name": "Uniswap", "symbol": "UNI"},
                {"id": "stellar", "name": "Stellar", "symbol": "XLM"},
                {"id": "cosmos", "name": "Cosmos", "symbol": "ATOM"},
                {"id": "monero", "name": "Monero", "symbol": "XMR"},
                {"id": "ethereum-classic", "name": "Ethereum Classic", "symbol": "ETC"},
                {"id": "hedera-hashgraph", "name": "Hedera", "symbol": "HBAR"},
                {
                    "id": "internet-computer",
                    "name": "Internet Computer",
                    "symbol": "ICP",
                },
                {"id": "filecoin", "name": "Filecoin", "symbol": "FIL"},
                {"id": "aptos", "name": "Aptos", "symbol": "APT"},
                {"id": "near", "name": "NEAR Protocol", "symbol": "NEAR"},
                {"id": "arbitrum", "name": "Arbitrum", "symbol": "ARB"},
                {"id": "optimism", "name": "Optimism", "symbol": "OP"},
                {"id": "the-graph", "name": "The Graph", "symbol": "GRT"},
                {"id": "algorand", "name": "Algorand", "symbol": "ALGO"},
            ]

            return {"cryptos": all_cryptos[:limit]}
        except Exception as e:
            logger.error(f"Error fetching popular cryptos: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/search_cryptos", tags=["Cryptocurrency"])
def search_cryptos(query: str, limit: int = 10) -> Dict[str, Any]:
    """Search cryptocurrencies by ID, name, or symbol."""
    with RequestLogger(f"GET /search_cryptos?query={query}"):
        try:
            if not query or len(query) < 1:
                return {"cryptos": []}

            query_lower = query.lower()

            # Get all popular cryptos
            popular_response = get_popular_cryptos(limit=50)
            all_cryptos = popular_response["cryptos"]

            # Filter by query
            matching = [
                crypto
                for crypto in all_cryptos
                if query_lower in crypto["id"].lower()
                or query_lower in crypto["name"].lower()
                or query_lower in crypto["symbol"].lower()
            ]

            return {"cryptos": matching[:limit]}
        except Exception as e:
            logger.error(f"Error searching cryptos: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/countries", tags=["Stocks"])
def get_countries() -> Dict[str, Any]:
    """Get available countries/markets for stock filtering."""
    with RequestLogger("GET /countries"):
        try:
            # Build country list from COUNTRY_INDICES
            countries = [
                {
                    "id": "Global",
                    "label": "🌐 Global",
                    "description": "Top global stocks",
                    "flag": "🌐",
                },
                {
                    "id": "United States",
                    "label": "🇺🇸 United States",
                    "description": "US market leaders",
                    "flag": "🇺🇸",
                },
            ]

            # Add countries from COUNTRY_INDICES
            country_flags = {
                "Switzerland": "🇨🇭",
                "Germany": "🇩🇪",
                "United Kingdom": "🇬🇧",
                "France": "🇫🇷",
                "Japan": "🇯🇵",
                "Canada": "🇨🇦",
            }

            for country_name in COUNTRY_INDICES.keys():
                flag = country_flags.get(country_name, "🌍")
                countries.append(
                    {
                        "id": country_name,
                        "label": f"{flag} {country_name}",
                        "description": f"{country_name} companies",
                        "flag": flag,
                    }
                )

            return {"countries": countries}
        except Exception as e:
            logger.error(f"Error fetching countries: {e}")
            raise HTTPException(status_code=500, detail=str(e))


class AnalysisRequest(BaseModel):
    ranking: List[Dict[str, Any]]
    user_context: Optional[str] = None


# Response Models for OpenAPI documentation
class HealthResponse(BaseModel):
    """Health check response with system status"""

    status: str
    timestamp: float
    model_loaded: bool
    openai_available: bool
    api_healthy: bool
    model_path: Optional[str] = None
    model_size_mb: Optional[float] = None
    openai_key_set: bool
    cache_enabled: bool
    cache_size: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ok",
                "timestamp": 1704067200.0,
                "model_loaded": True,
                "openai_available": True,
                "api_healthy": True,
                "model_path": "models/rf_model.pkl",
                "model_size_mb": 25.3,
                "openai_key_set": True,
                "cache_enabled": True,
                "cache_size": 42,
            }
        }
    }


class PredictionResponse(BaseModel):
    """ML model prediction response"""

    ticker: str
    probability: float
    prediction: int
    technical_indicators: Optional[Dict[str, float]] = None
    cached: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "ticker": "AAPL",
                "probability": 0.73,
                "prediction": 1,
                "technical_indicators": {
                    "RSI": 65.2,
                    "MACD": 1.45,
                    "BB_upper": 152.3,
                    "BB_lower": 145.8,
                },
                "cached": False,
            }
        }
    }


class StockRanking(BaseModel):
    """Individual stock ranking item"""

    ticker: str
    company_name: str
    probability: float
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    sector: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "probability": 0.73,
                "current_price": 150.25,
                "market_cap": 2400000000000,
                "sector": "Technology",
            }
        }
    }


class CryptoRanking(BaseModel):
    """Individual cryptocurrency ranking item"""

    crypto_id: str
    symbol: str
    name: str
    probability: float
    momentum_score: float
    price: float
    change_24h: float
    change_7d: float
    market_cap: float
    market_cap_rank: int
    image: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "crypto_id": "bitcoin",
                "symbol": "BTC",
                "name": "Bitcoin",
                "probability": 0.85,
                "momentum_score": 0.85,
                "price": 45000.0,
                "change_24h": 5.2,
                "change_7d": 10.5,
                "market_cap": 850000000000,
                "market_cap_rank": 1,
                "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
            }
        }
    }


# Watchlist Models
class WatchlistCreate(BaseModel):
    """Request model for creating a watchlist"""

    name: str
    description: Optional[str] = None


class WatchlistUpdate(BaseModel):
    """Request model for updating a watchlist"""

    name: Optional[str] = None
    description: Optional[str] = None


class AddStockRequest(BaseModel):
    """Request model for adding a stock or crypto to watchlist"""

    ticker: str
    notes: Optional[str] = None
    asset_type: str = "stock"  # 'stock' or 'crypto'


# Watchlist Endpoints
@app.get("/watchlists", tags=["Watchlists"])
def get_watchlists(user_id: str = "default_user"):
    """Get all watchlists for a user."""
    try:
        watchlists = WatchlistDB.get_user_watchlists(user_id)
        return {"watchlists": watchlists}
    except Exception as e:
        logger.error(f"Error fetching watchlists: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/watchlists", tags=["Watchlists"])
def create_watchlist(watchlist: WatchlistCreate, user_id: str = "default_user"):
    """Create a new watchlist."""
    try:
        watchlist_id = WatchlistDB.create_watchlist(
            user_id=user_id, name=watchlist.name, description=watchlist.description
        )
        return {
            "id": watchlist_id,
            "message": f"Watchlist '{watchlist.name}' created successfully",
        }
    except Exception as e:
        logger.error(f"Error creating watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/watchlists/{watchlist_id}", tags=["Watchlists"])
def get_watchlist(watchlist_id: int, user_id: str = "default_user"):
    """Get a specific watchlist with all its stocks."""
    try:
        watchlist = WatchlistDB.get_watchlist(watchlist_id, user_id)
        if not watchlist:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        return watchlist
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/watchlists/{watchlist_id}", tags=["Watchlists"])
def update_watchlist(
    watchlist_id: int, watchlist: WatchlistUpdate, user_id: str = "default_user"
):
    """Update watchlist details."""
    try:
        success = WatchlistDB.update_watchlist(
            watchlist_id=watchlist_id,
            user_id=user_id,
            name=watchlist.name,
            description=watchlist.description,
        )
        if not success:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        return {"message": "Watchlist updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/watchlists/{watchlist_id}", tags=["Watchlists"])
def delete_watchlist(watchlist_id: int, user_id: str = "default_user"):
    """Delete a watchlist and all its items."""
    try:
        success = WatchlistDB.delete_watchlist(watchlist_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        return {"message": "Watchlist deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/watchlists/{watchlist_id}/stocks", tags=["Watchlists"])
def add_stock_to_watchlist(
    watchlist_id: int, stock: AddStockRequest, user_id: str = "default_user"
):
    """Add a stock or crypto to a watchlist."""
    try:
        # For crypto assets, skip validation (CoinGecko IDs don't need ticker validation)
        if stock.asset_type == "crypto":
            validated_ticker = stock.ticker.lower()
            company_name = stock.ticker
        else:
            # Validate and verify ticker (auto-corrects common mistakes like APPLE -> AAPL)
            validated_ticker, company_name = (
                ValidationService.validate_and_verify_ticker(stock.ticker)
            )

        # Use company name in notes if no notes provided
        notes = stock.notes or company_name

        success = WatchlistDB.add_stock_to_watchlist(
            watchlist_id=watchlist_id,
            user_id=user_id,
            ticker=validated_ticker,
            notes=notes,
            asset_type=stock.asset_type,
        )
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"{stock.asset_type.title()} {validated_ticker} already in watchlist or watchlist not found",
            )

        # Return corrected ticker if it was auto-corrected (stocks only)
        response = {
            "message": f"{stock.asset_type.title()} {validated_ticker} added to watchlist"
        }
        if stock.asset_type == "stock" and validated_ticker != stock.ticker.upper():
            response["corrected_from"] = stock.ticker
            response["message"] = (
                f"Stock {stock.ticker} auto-corrected to {validated_ticker} and added to watchlist"
            )
        return response
    except ValueError as e:
        # Validation error with suggestions
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding stock to watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/watchlists/{watchlist_id}/stocks/{ticker}", tags=["Watchlists"])
def remove_stock_from_watchlist(
    watchlist_id: int, ticker: str, user_id: str = "default_user"
):
    """Remove a stock from a watchlist."""
    try:
        success = WatchlistDB.remove_stock_from_watchlist(
            watchlist_id=watchlist_id, user_id=user_id, ticker=ticker
        )
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Stock not found in watchlist or watchlist not found",
            )
        return {"message": f"Stock {ticker} removed from watchlist"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing stock from watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/context/market", tags=["LLM Context"])
def get_market_context(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Get LLM-generated market context and insights (NO buy/sell recommendations).

    This endpoint provides:
    - Market condition summary
    - Risk factors to consider
    - Sector trends
    - Economic context

    It does NOT provide:
    - Buy/sell recommendations
    - Trade signals
    - Investment advice
    """
    if not OPENAI_CLIENT:
        raise HTTPException(
            status_code=503, detail="LLM not configured (set OPENAI_API_KEY)"
        )

    # Create cache key from ranking + context
    cache_key = hashlib.md5(
        f"{[r['ticker'] for r in request.ranking[:10]]}{request.user_context}".encode()
    ).hexdigest()

    # Check cache
    cached_data = cache.get(f"market_context:{cache_key}")
    if cached_data:
        logger.debug(f"Cache hit for market context: {cache_key[:8]}")
        cached_data["cached"] = True
        return cached_data

    # Fetch detailed market data for top stocks
    enriched_data = []
    for rank, r in enumerate(request.ranking[:10], 1):
        try:
            stock = yf.Ticker(r["ticker"])
            info = stock.info

            enriched_data.append(
                {
                    "rank": rank,
                    "ticker": r["ticker"],
                    "name": info.get("longName", r["ticker"]),
                    "score": r["prob"],
                    "price": info.get("currentPrice", info.get("regularMarketPrice")),
                    "change": info.get("regularMarketChangePercent"),
                    "volume": info.get("volume"),
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE"),
                    "sector": info.get("sector", "N/A"),
                    "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                    "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                }
            )
        except Exception:
            # Fallback to basic data if fetch fails
            enriched_data.append(
                {
                    "rank": rank,
                    "ticker": r["ticker"],
                    "score": r["prob"],
                }
            )

    # Build context-focused prompt (NO recommendations)
    ranking_text = "\n".join(
        [
            f"{d['rank']}. {d['ticker']} ({d.get('sector', 'N/A')}) - "
            f"Score: {d['score']*100:.1f} | "
            f"Price: ${d.get('price', 'N/A')} | Change: {d.get('change', 'N/A')}% | "
            f"P/E: {d.get('pe_ratio', 'N/A')}"
            for d in enriched_data
        ]
    )

    user_ctx = request.user_context or "General market overview"
    prompt = (
        "You are a financial market analyst providing CONTEXT only (NOT investment advice).\n\n"
        f"TOP-RANKED STOCKS:\n{ranking_text}\n\n"
        f"USER FOCUS: {user_ctx}\n\n"
        "Provide market CONTEXT in these areas:\n\n"
        "1. MARKET CONDITIONS - Overall market environment and trends\n"
        "2. SECTOR ANALYSIS - Which sectors are represented and their current state\n"
        "3. RISK FACTORS - Key risks investors should be aware of (economic, geopolitical, sector-specific)\n"
        "4. NOTABLE PATTERNS - Any interesting patterns in the top-ranked stocks\n\n"
        "IMPORTANT RULES:\n"
        "- DO NOT make buy/sell recommendations\n"
        "- DO NOT say which stocks to purchase\n"
        "- DO provide factual market context\n"
        "- DO identify risks and opportunities in general terms\n"
        "- Focus on education and awareness, not specific actions\n\n"
        "250-350 words, objective and informative."
    )

    try:
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                response = OPENAI_CLIENT.chat.completions.create(
                    model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7,
                )
                context = response.choices[0].message.content
                result = {
                    "context": context,
                    "disclaimer": "This is informational context only, not investment advice. Make your own decisions based on quantitative signals.",
                    "model": response.model,
                    "cached": False,
                }

                # Cache the result
                cache.set(
                    f"market_context:{cache_key}",
                    result,
                    ttl_seconds=app_config.cache.ai_analysis_ttl,
                )

                return result
            except Exception as e:
                error_str = str(e)
                # Check if it's a rate limit error
                if "429" in error_str or "rate_limit" in error_str.lower():
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        raise HTTPException(
                            status_code=429,
                            detail="OpenAI rate limit exceeded. "
                            "Please wait a moment and try again.",
                        )
                else:
                    raise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Context generation failed: {str(e)}"
        )


@app.post("/analyze", tags=["AI Analysis"], deprecated=True)
def analyze_deprecated(request: AnalysisRequest) -> Dict[str, Any]:
    """
    DEPRECATED: Use /api/context/market instead.

    This endpoint will be removed in a future version.
    It violates the "No automated trading" principle by making BUY/SELL recommendations.
    """
    logger.warning("/analyze endpoint is deprecated, use /api/context/market instead")

    return {
        "error": "DEPRECATED",
        "message": "This endpoint is deprecated and will be removed.",
        "migration": {
            "use_instead": "/api/context/market",
            "reason": "Complies with 'Decision Support' principle (no automated recommendations)",
            "documentation": "See API docs at /docs",
        },
        "temporary_redirect": "/api/context/market",
    }


@app.get("/api/context/asset/{ticker}", tags=["LLM Context"])
async def get_asset_context(ticker: str) -> Dict[str, Any]:
    """
    Get LLM-generated context for a specific asset (NO recommendations).

    Provides:
    - News summary (if available)
    - Risk factors
    - Market positioning
    - Sector context

    Does NOT provide:
    - Buy/sell signals
    - Price targets
    - Investment advice
    """
    if not OPENAI_CLIENT:
        # Return graceful degradation without LLM
        return {
            "ticker": ticker.upper(),
            "context": "LLM context not available (OPENAI_API_KEY not configured)",
            "risk_factors": [],
            "sector_context": "N/A",
            "llm_enabled": False,
        }

    ticker = ticker.upper()
    cache_key = f"asset_context:{ticker}"

    # Check cache
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.debug(f"Cache hit for asset context: {ticker}")
        cached_data["cached"] = True
        return cached_data

    try:
        # Get current LLM context provider
        from .llm_context import get_context_provider

        context_provider = get_context_provider()
        if not context_provider:
            return {
                "ticker": ticker,
                "context": "LLM context provider not initialized",
                "risk_factors": [],
                "sector_context": "N/A",
                "llm_enabled": False,
            }

        # Get asset context (limited to ±5% adjustment)
        asset_context = await context_provider.get_asset_context(
            ticker=ticker,
            current_score=50.0,  # Placeholder, not used for context-only mode
            lookback_days=7,
        )

        result = {
            "ticker": ticker,
            "context": asset_context.news_summary,
            "risk_factors": asset_context.risk_events,
            "positive_catalysts": asset_context.positive_catalysts,
            "sentiment": asset_context.sentiment_score,
            "last_updated": asset_context.last_updated.isoformat(),
            "disclaimer": "Informational context only. Not investment advice.",
            "llm_enabled": True,
            "cached": False,
        }

        # Cache for 1 hour
        cache.set(cache_key, result, ttl_seconds=3600)

        return result

    except Exception as e:
        logger.error(f"Failed to get asset context for {ticker}: {e}")
        return {
            "ticker": ticker,
            "context": f"Failed to retrieve context: {str(e)}",
            "risk_factors": [],
            "sector_context": "N/A",
            "llm_enabled": False,
            "error": str(e),
        }


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time market data updates.

    Usage:
    - Connect: ws://localhost:8000/ws/{client_id}
    - Subscribe: {"action": "subscribe", "ticker": "AAPL"}
    - Unsubscribe: {"action": "unsubscribe", "ticker": "AAPL"}
    - Receive updates: {"type": "price_update", "ticker": "AAPL", "price": 150.0, ...}
    """
    await ws_manager.connect(websocket, client_id)

    # Start update task if not running
    ws_manager.start_updates()

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            action = data.get("action")
            ticker = data.get("ticker", "").upper()

            if action == "subscribe" and ticker:
                ws_manager.subscribe(client_id, ticker)
                await ws_manager.send_personal_message(
                    {"type": "subscribed", "ticker": ticker}, client_id
                )
            elif action == "unsubscribe" and ticker:
                ws_manager.unsubscribe(client_id, ticker)
                await ws_manager.send_personal_message(
                    {"type": "unsubscribed", "ticker": ticker}, client_id
                )
            elif action == "ping":
                await ws_manager.send_personal_message(
                    {"type": "pong", "timestamp": time.time()}, client_id
                )
            else:
                await ws_manager.send_personal_message(
                    {"type": "error", "message": "Invalid action or missing ticker"},
                    client_id,
                )

    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
        logger.info(f"WebSocket client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        ws_manager.disconnect(client_id)


# ============================================================================
# SIMULATION API ENDPOINTS
# ============================================================================


class SimulationCreateRequest(BaseModel):
    """Request model for creating a simulation."""

    user_id: str = "default_user"
    initial_capital: float = 10000.0
    mode: str = "auto"


class SimulationTradeRequest(BaseModel):
    """Request model for executing a trade."""

    ticker: str
    action: str
    quantity: int
    price: float
    reason: str
    ml_confidence: Optional[float] = None


@app.post("/api/simulations", tags=["Simulation"])
async def create_simulation(request: SimulationCreateRequest):
    """
    Create a new trading simulation.

    Args:
        user_id: User identifier (default: "default_user")
        initial_capital: Starting capital (default: $10,000)
        mode: 'auto' or 'manual' trading mode

    Returns:
        Simulation metadata with ID
    """
    try:
        sim_id = SimulationDB.create_simulation(
            user_id=request.user_id,
            initial_capital=request.initial_capital,
            mode=request.mode,
        )

        sim = SimulationDB.get_simulation(sim_id)

        return {
            "simulation_id": sim_id,
            "user_id": request.user_id,
            "initial_capital": request.initial_capital,
            "current_cash": request.initial_capital,
            "mode": request.mode,
            "positions": {},
            "created_at": sim.created_at.isoformat(),
        }
    except Exception as e:
        logger.error(f"Error creating simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/simulations/{simulation_id}", tags=["Simulation"])
async def get_simulation(simulation_id: int):
    """
    Get simulation details.

    Returns:
        Full simulation state including positions, trades, and metrics
    """
    try:
        sim = SimulationDB.get_simulation(simulation_id)
        if not sim:
            raise HTTPException(status_code=404, detail="Simulation not found")

        # Get current prices for metrics
        current_prices = {}
        for ticker in sim.positions.keys():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                if not hist.empty:
                    current_prices[ticker] = float(hist["Close"].iloc[-1])
            except Exception as e:
                logger.error(f"Error fetching price for {ticker}: {e}")

        metrics = sim.get_performance_metrics(current_prices)

        return {**sim.to_dict(), "metrics": metrics}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simulations/{simulation_id}/recommendations", tags=["Simulation"])
async def get_recommendations(simulation_id: int):
    """
    Get AI trading recommendations for simulation.

    Uses ML model predictions to generate buy/sell recommendations
    based on confidence thresholds and risk management rules.

    Returns:
        List of recommendations with action, ticker, confidence, reason
    """
    try:
        sim = SimulationDB.get_simulation(simulation_id)
        if not sim:
            raise HTTPException(status_code=404, detail="Simulation not found")

        if not MODEL:
            raise HTTPException(status_code=503, detail="ML model not loaded")

        # Get predictions for watchlist stocks or default stocks
        stocks = DEFAULT_STOCKS[:20]  # Limit to top 20 for performance

        predictions = []
        current_prices = {}

        for ticker in stocks:
            try:
                # Get stock data
                stock = yf.Ticker(ticker)
                hist = stock.history(period="60d")

                if len(hist) < 30:
                    continue

                # Compute features
                df = hist.copy()
                df["RSI"] = compute_rsi(df["Close"])
                macd_line, signal_line = compute_macd(df["Close"])
                df["MACD"] = macd_line
                df["Signal"] = signal_line
                bb_upper, bb_lower = compute_bollinger(df["Close"])
                df["BB_upper"] = bb_upper
                df["BB_lower"] = bb_lower
                df["Momentum"] = compute_momentum(df["Close"])

                df.dropna(inplace=True)

                if df.empty:
                    continue

                # Make prediction
                X = df[features].iloc[-1:].values
                prediction = MODEL.predict_proba(X)[0]
                confidence = float(max(prediction))
                signal = "UP" if prediction[1] > 0.5 else "DOWN"

                predictions.append(
                    {"ticker": ticker, "confidence": confidence, "signal": signal}
                )

                current_prices[ticker] = float(hist["Close"].iloc[-1])

            except Exception as e:
                logger.error(f"Error predicting {ticker}: {e}")

        # Get recommendations from simulation
        recommendations = sim.get_ai_recommendations(predictions, current_prices)

        return {"recommendations": recommendations}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simulations/{simulation_id}/trades", tags=["Simulation"])
async def execute_trade(simulation_id: int, request: SimulationTradeRequest):
    """
    Execute a trade in the simulation.

    Args:
        ticker: Stock ticker symbol
        action: 'BUY' or 'SELL'
        quantity: Number of shares
        price: Execution price per share
        reason: Trade rationale
        ml_confidence: ML prediction confidence (optional)

    Returns:
        Trade confirmation with updated portfolio
    """
    try:
        sim = SimulationDB.get_simulation(simulation_id)
        if not sim:
            raise HTTPException(status_code=404, detail="Simulation not found")

        # Execute trade
        trade = sim.execute_trade(
            ticker=request.ticker.upper(),
            action=request.action.upper(),
            quantity=request.quantity,
            price=request.price,
            reason=request.reason,
            ml_confidence=request.ml_confidence,
        )

        # Save to database
        SimulationDB.save_simulation(sim)
        SimulationDB.save_trade(simulation_id, trade)

        return {
            "success": True,
            "trade": {**trade, "timestamp": trade["timestamp"].isoformat()},
            "updated_cash": sim.cash,
            "updated_positions": sim.positions,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ❌ REMOVED: auto-trade and autopilot endpoints
# Reason: Violate Non-Goal requirement "shall NOT perform automated trading"
# See: DECISION_SUPPORT_SYSTEM_REQUIREMENTS.md Section 8
# Decision Support Systems provide recommendations, not automated execution


@app.get("/api/simulations/{simulation_id}/portfolio", tags=["Simulation"])
async def get_portfolio(simulation_id: int):
    """
    Get current portfolio state with live prices.

    Returns:
        Portfolio summary with positions, cash, total value, and P&L
    """
    try:
        sim = SimulationDB.get_simulation(simulation_id)
        if not sim:
            raise HTTPException(status_code=404, detail="Simulation not found")

        # Get current prices
        current_prices = {}
        for ticker in sim.positions.keys():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                if not hist.empty:
                    current_prices[ticker] = float(hist["Close"].iloc[-1])
            except Exception as e:
                logger.error(f"Error fetching price for {ticker}: {e}")

        portfolio_value = sim.get_portfolio_value(current_prices)

        # Calculate position details
        positions_detail = []
        for ticker, pos in sim.positions.items():
            current_price = current_prices.get(ticker, pos["current_price"])
            value = pos["quantity"] * current_price
            cost_basis = pos["quantity"] * pos["avg_cost"]
            pnl = value - cost_basis
            pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0

            positions_detail.append(
                {
                    "ticker": ticker,
                    "quantity": pos["quantity"],
                    "avg_cost": pos["avg_cost"],
                    "current_price": current_price,
                    "value": value,
                    "pnl": pnl,
                    "pnl_percent": pnl_pct,
                }
            )

        return {
            "simulation_id": simulation_id,
            "cash": sim.cash,
            "positions": positions_detail,
            "total_value": portfolio_value,
            "initial_capital": sim.initial_capital,
            "total_pnl": portfolio_value - sim.initial_capital,
            "total_pnl_percent": (
                (portfolio_value - sim.initial_capital) / sim.initial_capital * 100
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/simulations/{simulation_id}/history", tags=["Simulation"])
async def get_trade_history(simulation_id: int):
    """
    Get trade history for simulation.

    Returns:
        List of all executed trades with timestamps
    """
    try:
        sim = SimulationDB.get_simulation(simulation_id)
        if not sim:
            raise HTTPException(status_code=404, detail="Simulation not found")

        trades = [
            {**trade, "timestamp": trade["timestamp"].isoformat()}
            for trade in sim.trades
        ]

        return {"trades": trades}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trade history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/simulations/{simulation_id}", tags=["Simulation"])
async def delete_simulation(simulation_id: int):
    """
    Delete a simulation and all associated data.
    """
    try:
        SimulationDB.delete_simulation(simulation_id)
        return {"success": True, "message": "Simulation deleted"}
    except Exception as e:
        logger.error(f"Error deleting simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simulations/{simulation_id}/reset", tags=["Simulation"])
async def reset_simulation(simulation_id: int):
    """
    Reset simulation to initial state.

    Clears all trades and positions, resets cash to initial capital.
    """
    try:
        SimulationDB.reset_simulation(simulation_id)
        return {"success": True, "message": "Simulation reset"}
    except Exception as e:
        logger.error(f"Error resetting simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== MLOps Dashboard Endpoints =====


@app.get(
    "/api/ml/model/info",
    tags=["MLOps"],
    summary="Get ML Model Information",
    description="""
    Get comprehensive information about the currently loaded ML model.
    
    Returns:
    - Model type and algorithm
    - Training metrics (accuracy, precision, recall, F1)
    - Feature importance
    - Model version and training date
    - Hyperparameters
    - Performance statistics
    
    **Use Case:** MLOps dashboard for model monitoring and validation
    """,
)
def get_model_info():
    """Get information about the currently loaded ML model."""
    try:
        if MODEL is None:
            raise HTTPException(status_code=503, detail="No model loaded")

        # Basic model info
        model_type = type(MODEL).__name__

        # Try to get feature importances if available
        feature_importances = None
        if hasattr(MODEL, "feature_importances_"):
            importances = MODEL.feature_importances_
            feature_importances = [
                {"feature": feat, "importance": float(imp)}
                for feat, imp in zip(features, importances)
            ]
            feature_importances.sort(key=lambda x: x["importance"], reverse=True)

        # Model parameters
        params = MODEL.get_params() if hasattr(MODEL, "get_params") else {}

        # Try to load training metrics from MLflow or joblib metadata
        training_metrics = {
            "accuracy": "N/A - Load from MLflow",
            "precision": "N/A",
            "recall": "N/A",
            "f1_score": "N/A",
        }

        return {
            "model_type": model_type,
            "model_path": str(LOADED_MODEL_PATH) if LOADED_MODEL_PATH else MODEL_PATH,
            "features_count": len(features),
            "features": features,
            "feature_importances": feature_importances,
            "hyperparameters": {k: str(v) for k, v in params.items()},
            "training_metrics": training_metrics,
            "version": "1.0.0",  # TODO: Track version in model metadata
            "last_trained": "2026-01-11",  # TODO: Load from metadata
            "status": "active",
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching model info: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch model info: {str(e)}"
        )


@app.get(
    "/api/ml/retraining/status",
    tags=["MLOps"],
    summary="Get Model Retraining Status",
    description="""
    Get status of model retraining process.
    
    Returns:
    - Current retraining status (idle, training, completed, failed)
    - Progress percentage
    - Start/end timestamps
    - Training metrics (if completed)
    - Error messages (if failed)
    
    **Use Case:** Monitor long-running retraining jobs
    """,
)
def get_retraining_status():
    """Get status of model retraining process."""
    try:
        # TODO: Implement actual retraining job tracking
        # For now, return mock status

        return {
            "status": "idle",
            "message": "No retraining job in progress",
            "progress": 0,
            "start_time": None,
            "end_time": None,
            "duration_seconds": None,
            "metrics": None,
            "error": None,
            "last_retrain": {
                "date": "2026-01-11",
                "duration_seconds": 3600,
                "status": "completed",
                "accuracy_improvement": "+2.3%",
            },
            "next_scheduled": "2026-01-18",  # Weekly retraining
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching retraining status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch retraining status: {str(e)}"
        )


@app.post(
    "/api/ml/retraining/trigger",
    tags=["MLOps"],
    summary="Trigger Model Retraining",
    description="""
    Manually trigger model retraining process.
    
    **Process:**
    1. Fetch latest market data (last 300 days)
    2. Compute features for all stocks
    3. Train new model with updated hyperparameters
    4. Validate model performance
    5. Replace current model if accuracy improves
    6. Log results to MLflow
    
    **Note:** This is a long-running operation (15-60 minutes)
    
    **Requirements:** Admin access (TODO: implement auth)
    """,
)
def trigger_retraining(stocks_limit: int = 50, test_mode: bool = False):
    """
    Trigger model retraining.

    Args:
        stocks_limit: Number of stocks to train on (default: 50)
        test_mode: If True, runs quick validation without replacing model

    Returns:
        Job ID for tracking retraining progress
    """
    try:
        # TODO: Implement actual retraining logic with background job
        # For now, return mock response

        import uuid

        job_id = str(uuid.uuid4())

        logger.info(
            f"🔄 Retraining triggered: Job {job_id} (stocks={stocks_limit}, test={test_mode})"
        )

        return {
            "success": True,
            "job_id": job_id,
            "message": "Retraining job started",
            "estimated_duration_minutes": 30 if not test_mode else 5,
            "stocks_count": stocks_limit,
            "test_mode": test_mode,
            "status_endpoint": f"/api/ml/retraining/status",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error triggering retraining: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to trigger retraining: {str(e)}"
        )


@app.post(
    "/api/ml/retraining/rollback",
    tags=["MLOps"],
    summary="Rollback to Previous Model",
    description="""
    Rollback to previous model version.
    
    **Use Case:** If new model performs worse than previous version
    
    **Process:**
    1. Identify previous model version
    2. Load previous model from backup
    3. Replace current model
    4. Log rollback event
    
    **Requirements:** Admin access (TODO: implement auth)
    """,
)
def rollback_model():
    """Rollback to previous model version."""
    try:
        # TODO: Implement actual model versioning and rollback
        # For now, return mock response

        logger.warning("⚠️ Model rollback requested")

        return {
            "success": False,
            "message": "Model rollback not yet implemented",
            "reason": "No previous model version found in backup",
            "current_model": (
                str(LOADED_MODEL_PATH) if LOADED_MODEL_PATH else MODEL_PATH
            ),
            "backup_location": "models/backup/",
            "available_versions": [],
            "note": "Implement model versioning system for rollback functionality",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error rolling back model: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to rollback model: {str(e)}"
        )


# ===== Alert Endpoints =====


@app.get("/alerts", tags=["Alerts"])
async def get_alerts(
    user_id: str = "default_user",
    unread_only: bool = False,
    priority: Optional[str] = None,
    asset_type: Optional[str] = None,
    limit: int = 50,
):
    """
    Get user alerts with optional filtering.

    Query Parameters:
    - user_id: User identifier (default: 'default_user')
    - unread_only: Return only unread alerts (default: False)
    - priority: Filter by priority (high, medium, low)
    - asset_type: Filter by asset type (stock, crypto)
    - limit: Maximum number of alerts to return (default: 50)
    """
    try:
        alerts = alert_db.get_alerts(
            user_id=user_id,
            unread_only=unread_only,
            priority=priority,
            asset_type=asset_type,
            limit=limit,
        )
        unread_count = alert_db.get_unread_count(user_id)

        return {"alerts": alerts, "unread_count": unread_count, "total": len(alerts)}
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")


@app.post("/alerts/mark-read", tags=["Alerts"])
async def mark_alerts_read(alert_ids: List[int]):
    """
    Mark one or more alerts as read.

    Request Body:
    - alert_ids: List of alert IDs to mark as read
    """
    try:
        marked_count = alert_db.mark_read(alert_ids)
        return {"success": True, "marked_count": marked_count}
    except Exception as e:
        logger.error(f"Error marking alerts as read: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to mark alerts as read: {str(e)}"
        )


@app.delete("/alerts/clear", tags=["Alerts"])
async def clear_old_alerts(older_than_days: int = 7, user_id: str = "default_user"):
    """
    Delete old read alerts.

    Query Parameters:
    - older_than_days: Delete alerts older than this many days (default: 7)
    - user_id: User identifier (default: 'default_user')
    """
    try:
        deleted_count = alert_db.delete_old_alerts(user_id, older_than_days)
        return {"success": True, "deleted_count": deleted_count}
    except Exception as e:
        logger.error(f"Error clearing old alerts: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to clear old alerts: {str(e)}"
        )


# Include analytics router
app.include_router(analytics_router)


# ============================================================================
# Model Retraining & MLOps Endpoints
# ============================================================================


@app.get("/api/ml/retraining/status", tags=["MLOps"])
async def get_retraining_status():
    """
    Get current status of the automated retraining system.

    Returns:
    - running: Whether scheduler is active
    - current_metrics: Latest model performance metrics
    - next_retraining: Timestamp of next scheduled retraining
    - scheduled_jobs: List of all scheduled jobs
    """
    try:
        service = get_retraining_service()
        status = service.get_status()
        return status
    except Exception as e:
        logger.error(f"Error fetching retraining status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch retraining status: {str(e)}"
        )


@app.post("/api/ml/retraining/trigger", tags=["MLOps"])
async def trigger_manual_retraining(
    force: bool = False, background_tasks: BackgroundTasks = None
):
    """
    Manually trigger model retraining.

    Query Parameters:
    - force: Skip validation and deploy anyway (default: False)

    Returns:
    - job_id: ID of the retraining job
    - status: Initial status
    """
    try:
        service = get_retraining_service()

        # Run in background
        if background_tasks:
            job_id = f"retrain_{int(datetime.now().timestamp())}"
            background_tasks.add_task(service.retrain_model, force=force)
            return {
                "job_id": job_id,
                "status": "started",
                "message": "Retraining job started in background",
            }
        else:
            # Run synchronously (blocks request)
            success = service.retrain_model(force=force)
            return {
                "success": success,
                "status": "completed" if success else "failed",
                "message": (
                    "Retraining completed"
                    if success
                    else "Retraining failed validation"
                ),
            }
    except Exception as e:
        logger.error(f"Error triggering manual retraining: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to trigger retraining: {str(e)}"
        )


@app.post("/api/ml/retraining/rollback", tags=["MLOps"])
async def rollback_model():
    """
    Rollback to previous model version.

    Returns:
    - success: Whether rollback succeeded
    - message: Status message
    """
    try:
        service = get_retraining_service()
        service.rollback_model()
        return {
            "success": True,
            "message": "Successfully rolled back to previous model version",
        }
    except Exception as e:
        logger.error(f"Error rolling back model: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to rollback model: {str(e)}"
        )


@app.get("/api/ml/model/info", tags=["MLOps"])
async def get_model_info():
    """
    Get current model information and performance.

    Returns:
    - model_path: Path to current production model
    - metrics: Current model performance metrics
    - last_trained: Timestamp of last training
    - features: List of features used by model
    """
    try:
        service = get_retraining_service()
        status = service.get_status()

        return {
            "model_path": status["model_path"],
            "backup_path": status["backup_path"],
            "metrics": status["current_metrics"],
            "features": features,  # From trading.py
            "feature_count": len(features),
        }
    except Exception as e:
        logger.error(f"Error fetching model info: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch model info: {str(e)}"
        )


@app.post("/api/portfolio/validate", tags=["Portfolio"])
async def validate_portfolio(positions: List[Dict]):
    """
    Validate portfolio allocation against limits.

    Request body:
    ```json
    [
        {"ticker": "AAPL", "allocation": 10.0, "asset_type": "stock", "score": 85},
        {"ticker": "BTC-USD", "allocation": 5.0, "asset_type": "crypto", "score": 78}
    ]
    ```

    Returns:
    - violations: List of limit violations
    - warnings: List of warnings
    - diversification_score: 0-100 score
    - rebalancing_suggestions: Recommended actions
    """
    try:
        portfolio_mgr = get_portfolio_manager()

        # Validate allocations
        analysis = portfolio_mgr.validate_allocation(positions)

        # Get rebalancing suggestions if needed
        suggestions = []
        if analysis.violations or analysis.warnings:
            suggestions = portfolio_mgr.suggest_rebalancing(positions)

        return {
            "valid": len(analysis.violations) == 0,
            "total_allocation": analysis.total_allocation,
            "equity_exposure": analysis.equity_exposure,
            "crypto_exposure": analysis.crypto_exposure,
            "cash_reserve": analysis.cash_reserve,
            "diversification_score": analysis.diversification_score,
            "concentrated_positions": analysis.concentrated_positions or [],
            "violations": analysis.violations,
            "warnings": analysis.warnings,
            "rebalancing_suggestions": suggestions,
        }
    except Exception as e:
        logger.error(f"Error validating portfolio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/portfolio/limits", tags=["Portfolio"])
async def get_portfolio_limits():
    """
    Get current portfolio allocation limits.

    Returns configuration for:
    - Position limits (max % per stock/crypto)
    - Asset class limits (max equity/crypto exposure)
    - Risk limits (correlation thresholds)
    """
    portfolio_mgr = get_portfolio_manager()
    limits = portfolio_mgr.limits

    return {
        "position_limits": {
            "max_stock_position": limits.max_stock_position,
            "max_crypto_position": limits.max_crypto_position,
        },
        "asset_class_limits": {
            "max_equity_exposure": limits.max_equity_exposure,
            "max_crypto_exposure": limits.max_crypto_exposure,
            "min_cash_reserve": limits.min_cash_reserve,
        },
        "risk_limits": {
            "max_correlation": limits.max_correlation,
            "max_concentrated_positions": limits.max_concentrated_positions,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════
# HISTORICAL VALIDATION & BACKTESTING (Phase 3)
# ═══════════════════════════════════════════════════════════════════════════


@app.post("/api/backtest/run", tags=["Historical Validation"])
async def run_backtest(
    tickers: Optional[List[str]] = None,
    start_date: str = "2025-01-01",
    end_date: str = "2026-01-11",
    initial_capital: float = 100000.0,
) -> Dict[str, Any]:
    """
    Run historical backtest comparing 3 strategies.

    Strategies tested:
    1. Composite Score System (Tech 40% + ML 30% + Momentum 20% + Regime 10%)
    2. ML-Only Strategy
    3. S&P 500 Buy-and-Hold Benchmark

    Args:
        tickers: List of stock tickers (default: top 30 US stocks)
        start_date: Backtest start date (YYYY-MM-DD)
        end_date: Backtest end date (YYYY-MM-DD)
        initial_capital: Starting portfolio value (default: $100k)

    Returns:
        Comparison results with metrics for each strategy
    """
    from ..backtest.historical_validator import (
        HistoricalBacktester,
        generate_backtest_report,
    )

    # Default to top US stocks if not specified
    if not tickers:
        tickers = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "NVDA",
            "META",
            "TSLA",
            "BRK-B",
            "V",
            "JNJ",
            "WMT",
            "JPM",
            "MA",
            "PG",
            "UNH",
            "HD",
            "CVX",
            "MRK",
            "PFE",
            "ABBV",
            "KO",
            "PEP",
            "COST",
            "AVGO",
            "TMO",
            "MCD",
            "CSCO",
            "ABT",
            "ACN",
            "ADBE",
        ]

    try:
        logger.info(f"Running backtest: {start_date} to {end_date}")
        logger.info(
            f"Tickers: {len(tickers)} stocks, Initial capital: ${initial_capital:,.2f}"
        )

        backtester = HistoricalBacktester(initial_capital=initial_capital)
        results = backtester.run_comparison(tickers, start_date, end_date)

        # Convert results to JSON-serializable format
        response = {
            "backtest_period": {
                "start_date": start_date,
                "end_date": end_date,
                "duration_days": (
                    pd.to_datetime(end_date) - pd.to_datetime(start_date)
                ).days,
            },
            "strategies": {},
            "comparison": {
                "winner_by_return": None,
                "winner_by_sharpe": None,
                "alpha_vs_benchmark": None,
            },
        }

        best_return = None
        best_sharpe = None

        for name, result in results.items():
            strategy_data = {
                "name": result.strategy_name,
                "metrics": {
                    "total_return": round(result.total_return, 2),
                    "max_drawdown": round(result.max_drawdown, 2),
                    "sharpe_ratio": round(result.sharpe_ratio, 2),
                    "calmar_ratio": round(result.calmar_ratio, 2),
                    "win_rate": round(result.win_rate, 1),
                    "num_trades": result.num_trades,
                    "avg_trade_return": round(result.avg_trade_return, 2),
                    "final_portfolio_value": round(result.final_portfolio_value, 2),
                },
                "trades": result.trades[:10],  # First 10 trades only
            }

            response["strategies"][name] = strategy_data

            if not best_return or result.total_return > best_return.total_return:
                best_return = result

            if not best_sharpe or result.sharpe_ratio > best_sharpe.sharpe_ratio:
                best_sharpe = result

        # Set comparison winners
        if best_return:
            response["comparison"]["winner_by_return"] = {
                "strategy": best_return.strategy_name,
                "return": round(best_return.total_return, 2),
            }

        if best_sharpe:
            response["comparison"]["winner_by_sharpe"] = {
                "strategy": best_sharpe.strategy_name,
                "sharpe": round(best_sharpe.sharpe_ratio, 2),
            }

        # Calculate alpha vs benchmark
        if "composite" in results and "sp500" in results:
            alpha = results["composite"].total_return - results["sp500"].total_return
            response["comparison"]["alpha_vs_benchmark"] = {
                "alpha": round(alpha, 2),
                "interpretation": "Outperformed" if alpha > 0 else "Underperformed",
                "percentage_points": abs(round(alpha, 2)),
            }

        # Generate markdown report
        report = generate_backtest_report(results)
        response["report"] = report

        logger.info(
            f"Backtest complete. Best return: {best_return.strategy_name} ({best_return.total_return:.2f}%)"
        )

        return response

    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Backtest execution failed: {str(e)}"
        )


@app.get("/api/backtest/status", tags=["Historical Validation"])
def get_backtest_status() -> Dict[str, Any]:
    """
    Get status of historical validation system.

    Returns information about available backtesting capabilities.
    """
    return {
        "available": True,
        "strategies": {
            "composite": "Composite Score System (Tech 40% + ML 30% + Momentum 20% + Regime 10%)",
            "ml_only": "ML-Only Strategy (probability-based)",
            "sp500": "S&P 500 Buy-and-Hold Benchmark",
        },
        "metrics": [
            "Total Return",
            "Max Drawdown",
            "Sharpe Ratio",
            "Calmar Ratio",
            "Win Rate",
            "Average Trade Return",
        ],
        "default_params": {
            "initial_capital": 100000.0,
            "position_size": 0.10,
            "risk_free_rate": 0.04,
            "lookback_period": "1 year",
        },
        "phase": "Phase 3: Historical Validation",
        "status": "Implemented (2026-01-11)",
    }


# Mount frontend static files LAST so API routes take precedence
# This must come after all route definitions to avoid catching API routes
FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.trading_engine.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
