import hashlib
import os
import time
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv
from fastapi import (
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

from . import metrics as prom_metrics
from .alerts import alert_manager

# Import new modules
from .cache import cache
from .config import config as app_config
from .crypto import get_crypto_details, get_crypto_ranking, search_crypto
from .database import WatchlistDB
from .logging_config import RequestLogger, setup_logging
from .rate_limiter import RateLimiter
from .services import HealthService, StockService, ValidationService
from .trading import (
    compute_bollinger,
    compute_macd,
    compute_momentum,
    compute_rsi,
    features,
)
from .websocket import manager as ws_manager

# Load environment variables from .env file
load_dotenv()

# Validate configuration
app_config.validate()

# Setup structured logging
logger = setup_logging(app_config.logging.log_level)

try:
    from openai import OpenAI

    OPENAI_CLIENT = OpenAI(api_key=app_config.api.openai_api_key)
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    OPENAI_CLIENT = None
    logger.warning(f"OpenAI client not available: {e}")

# Default popular stocks for automatic ranking
DEFAULT_STOCKS = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "TSLA",
    "BRK.B",
    "UNH",
    "JNJ",
    "V",
    "WMT",
    "JPM",
    "MA",
    "PG",
    "XOM",
    "HD",
    "CVX",
    "LLY",
    "ABBV",
    "MRK",
    "KO",
    "PEP",
    "COST",
    "AVGO",
    "TMO",
    "BAC",
    "CSCO",
    "MCD",
    "ACN",
    "AMD",
    "NFLX",
    "ADBE",
    "DIS",
    "NKE",
    "INTC",
    "CRM",
    "TXN",
    "ORCL",
    "ABT",
    "CMCSA",
    "VZ",
    "WFC",
    "PM",
    "IBM",
    "QCOM",
    "UPS",
    "HON",
    "BA",
    "GE",
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
)


# Initialize Prometheus metrics on startup
@app.on_event("startup")
def startup_event():
    """Initialize metrics and system state on startup."""
    prom_metrics.initialize_metrics(
        model_is_loaded=MODEL is not None,
        openai_is_configured=OPENAI_CLIENT is not None,
    )
    logger.info("Prometheus metrics initialized")


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
        status=response.status_code,
        duration=duration,
    )

    return response


MODEL_PATH = app_config.model.prod_model_path
MODEL = None
LOADED_MODEL_PATH = None
if os.path.exists(MODEL_PATH):
    MODEL = joblib.load(MODEL_PATH)
    LOADED_MODEL_PATH = MODEL_PATH


class FeaturePayload(BaseModel):
    features: Dict[str, float]


def row_from_features(feat_dict: Dict[str, Any]):
    # convert into DataFrame row with expected order
    row = {k: float(feat_dict.get(k, 0.0)) for k in features}
    return pd.DataFrame([row])


@app.get("/", tags=["System"])
def root():
    """
    Root endpoint with API information.

    Returns basic information about the API and available endpoints.
    """
    return {
        "name": "POC-MarketPredictor-ML API",
        "version": "1.0.0",
        "description": "Machine Learning powered stock ranking and analysis",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "metrics": "/metrics",
            "ranking": "/ranking",
            "ticker_info": "/ticker_info/{ticker}",
            "predict": "/predict_ticker/{ticker}",
            "analyze": "/analyze",
        },
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
    "/metrics",
    tags=["Monitoring"],
    summary="System Metrics",
    description="""
    Get detailed system metrics including:
    - Cache statistics (hits, misses, size)
    - Rate limiter statistics
    - WebSocket connection stats
    - Model information
    """,
)
def metrics():
    """Get system metrics for monitoring."""
    with RequestLogger("GET /metrics"):
        return {
            "cache_stats": cache.get_stats(),
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


@app.post("/predict_raw")
def predict_raw(payload: FeaturePayload):
    if MODEL is None:
        raise HTTPException(status_code=503, detail="No model available")
    row = row_from_features(payload.features)
    if hasattr(MODEL, "predict_proba"):
        prob = MODEL.predict_proba(row.values)[0][1]
    else:
        prob = float(MODEL.predict(row.values)[0])
    return {"prob": float(prob)}


@app.get(
    "/predict_ticker/{ticker}",
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
    # Handle MultiIndex columns from yfinance
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    df = pd.DataFrame({"Adj Close": raw["Adj Close"]})
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
        raise HTTPException(status_code=404, detail="No recent data for ticker")
    row = df.iloc[-1:]
    prob = MODEL.predict_proba(row[features].values)[0][1]
    return {"prob": float(prob)}


@app.get(
    "/ranking",
    tags=["Predictions"],
    summary="Stock Rankings",
    description="""
    Get ranked list of stocks based on ML predictions.

    Supports filtering by:
    - Country/region (e.g., 'Switzerland', 'Germany', 'United States')
    - Custom ticker list (comma-separated)
    - Top N results

    Returns stocks sorted by prediction probability (highest first).
    """,
)
def ranking(tickers: str = "", country: str = "Global"):
    """Rank stocks by ML prediction probability.
    If no tickers provided, dynamically fetches top stocks for the specified country.
    Country options: Global, United States, Switzerland, Germany, United Kingdom, France, Japan, Canada
    """
    if MODEL is None:
        raise HTTPException(status_code=503, detail="No model available")

    start_time = time.time()

    # Use country-specific stocks if no tickers provided
    if not tickers.strip():
        chosen = get_country_stocks(country)
    else:
        chosen = [t.strip().upper() for t in tickers.split(",") if t.strip()]

    result = []
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

        # Ensure we have a DataFrame with proper column access
        df = pd.DataFrame()
        # Extract as Series to avoid MultiIndex issues
        adj_close = raw["Adj Close"]
        if isinstance(adj_close, pd.DataFrame):
            adj_close = adj_close.iloc[:, 0]  # Take first column if DataFrame
        df["Adj Close"] = adj_close

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
            continue
        row = df.iloc[-1:]
        prob = MODEL.predict_proba(row[features].values)[0][1]

        # Get current price
        current_price = float(df["Adj Close"].iloc[-1])

        # Track model prediction metrics
        pred_duration = time.time() - pred_start
        prom_metrics.track_model_prediction("random_forest", float(prob), pred_duration)

        result.append(
            {"ticker": t, "prob": float(prob), "current_price": current_price}
        )

    # sort result
    result.sort(key=lambda r: r["prob"], reverse=True)

    # Track ranking generation metrics
    duration = time.time() - start_time
    prom_metrics.track_ranking_generation(country, len(result), duration)

    return {"ranking": result}


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
                {"ticker": "HOLN.SW", "name": "Holcim Ltd"},
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
    """Search stocks by ticker or company name with yfinance fallback."""
    with RequestLogger(f"GET /search_stocks?query={query}"):
        try:
            if not query or len(query) < 1:
                return {"stocks": []}

            query_lower = query.lower()
            query_upper = query.upper()

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

            # If no matches in popular list, try yfinance search and lookup
            if len(matching) == 0:
                try:
                    # First try yfinance search API (finds by company name like "Amazon")
                    import yfinance as yf_module

                    search_results = yf_module.Search(query, max_results=5)

                    if (
                        search_results
                        and hasattr(search_results, "quotes")
                        and search_results.quotes
                    ):
                        for result in search_results.quotes:
                            try:
                                ticker = result.get("symbol", "")
                                if not ticker:
                                    continue
                                name = result.get(
                                    "longname", result.get("shortname", "")
                                )
                                if ticker and name:
                                    matching.append({"ticker": ticker, "name": name})
                            except Exception as search_error:
                                logger.debug(
                                    f"Error processing search result: {search_error}"
                                )
                                continue

                    # If search didn't work, try as direct ticker
                    if len(matching) == 0:
                        ticker_obj = yf.Ticker(query_upper)
                        info = ticker_obj.info

                        # Check if ticker is valid (has longName or shortName)
                        if info and (info.get("longName") or info.get("shortName")):
                            matching.append(
                                {
                                    "ticker": query_upper,
                                    "name": info.get("longName")
                                    or info.get("shortName", query_upper),
                                }
                            )
                        else:
                            # Try with common suffixes for Swiss stocks
                            for suffix in [".SW", ".DE", ".L", ".PA"]:
                                ticker_with_suffix = query_upper + suffix
                                ticker_obj = yf.Ticker(ticker_with_suffix)
                                info = ticker_obj.info
                                if info and (
                                    info.get("longName") or info.get("shortName")
                                ):
                                    matching.append(
                                        {
                                            "ticker": ticker_with_suffix,
                                            "name": info.get("longName")
                                            or info.get(
                                                "shortName", ticker_with_suffix
                                            ),
                                        }
                                    )
                                    break
                except Exception as yf_error:
                    logger.debug(f"YFinance lookup failed for {query}: {yf_error}")

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

    class Config:
        json_schema_extra = {
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


class PredictionResponse(BaseModel):
    """ML model prediction response"""

    ticker: str
    probability: float
    prediction: int
    technical_indicators: Optional[Dict[str, float]] = None
    cached: bool = False

    class Config:
        json_schema_extra = {
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


class StockRanking(BaseModel):
    """Individual stock ranking item"""

    ticker: str
    company_name: str
    probability: float
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    sector: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "probability": 0.73,
                "current_price": 150.25,
                "market_cap": 2400000000000,
                "sector": "Technology",
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

    class Config:
        json_schema_extra = {
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


@app.get("/watchlist/prediction/{ticker}", tags=["Watchlists", "Predictions"])
def get_watchlist_prediction(ticker: str, asset_type: str = "stock"):
    """Get buy/sell/hold prediction for a watchlist item (stock or crypto).

    Returns:
    - signal: BUY, SELL, or HOLD
    - confidence: 0-100 percentage
    - reasoning: Brief explanation
    """
    try:
        if asset_type == "crypto":
            # Crypto prediction based on momentum and trends
            try:
                response = requests.get(
                    f"https://api.coingecko.com/api/v3/coins/{ticker.lower()}",
                    params={
                        "localization": "false",
                        "tickers": "false",
                        "community_data": "false",
                        "developer_data": "false",
                    },
                    timeout=10,
                )

                if response.status_code != 200:
                    return {
                        "signal": "HOLD",
                        "confidence": 50,
                        "reasoning": "Unable to fetch market data",
                    }

                data = response.json()
                market_data = data.get("market_data", {})

                # Extract key metrics
                price_change_24h = market_data.get("price_change_percentage_24h", 0)
                price_change_7d = market_data.get("price_change_percentage_7d", 0)
                price_change_30d = market_data.get("price_change_percentage_30d", 0)
                market_cap_rank = data.get("market_cap_rank", 999)

                # Calculate momentum score
                momentum = (
                    price_change_24h * 0.5
                    + price_change_7d * 0.3
                    + price_change_30d * 0.2
                )

                # Determine signal - Very aggressive thresholds for maximum opportunities
                if momentum > 5 and price_change_24h > 1 and market_cap_rank <= 150:
                    signal = "BUY"
                    confidence = min(85, 60 + abs(momentum))
                    reasoning = (
                        f"Strong upward momentum ({momentum:.1f}%), top-150 crypto"
                    )
                elif momentum > 0 and price_change_7d > -2:
                    signal = "BUY"
                    confidence = min(75, 50 + abs(momentum))
                    reasoning = f"Positive trend ({price_change_7d:.1f}% weekly)"
                elif momentum > -2 and price_change_24h > -1:
                    signal = "BUY"
                    confidence = min(60, 48 + abs(momentum))
                    reasoning = f"Mild positive momentum ({momentum:.1f}%)"
                elif momentum < -5 or price_change_24h < -3:
                    signal = "SELL"
                    confidence = min(80, 60 + abs(momentum))
                    reasoning = f"Negative momentum ({momentum:.1f}%)"
                else:
                    signal = "HOLD"
                    confidence = 50 + abs(momentum) / 2
                    reasoning = f"Neutral trend ({momentum:.1f}%)"

                result = {
                    "signal": signal,
                    "confidence": round(confidence, 1),
                    "reasoning": reasoning,
                    "metrics": {
                        "price_change_24h": round(price_change_24h, 2),
                        "price_change_7d": round(price_change_7d, 2),
                        "momentum": round(momentum, 2),
                    },
                }

                # Check for alerts (crypto)
                crypto_name = data.get("name", ticker)
                current_price = (
                    data.get("market_data", {}).get("current_price", {}).get("usd")
                )
                alert_manager.check_and_create_alerts(
                    symbol=ticker,
                    name=crypto_name,
                    asset_type="crypto",
                    prediction=result,
                    current_price=current_price,
                )

                return result

            except Exception as e:
                logger.error(f"Crypto prediction error: {e}")
                return {
                    "signal": "HOLD",
                    "confidence": 50,
                    "reasoning": "Prediction unavailable",
                }

        else:
            # Stock prediction using ML model
            if MODEL is None:
                return {
                    "signal": "HOLD",
                    "confidence": 50,
                    "reasoning": "ML model not loaded",
                }

            try:
                # Get latest data and compute features
                raw = yf.download(
                    ticker, period="300d", auto_adjust=False, progress=False
                )

                if raw.empty:
                    return {
                        "signal": "HOLD",
                        "confidence": 50,
                        "reasoning": "No market data available",
                    }

                # Handle MultiIndex columns
                if isinstance(raw.columns, pd.MultiIndex):
                    raw.columns = raw.columns.get_level_values(0)

                df = pd.DataFrame({"Adj Close": raw["Adj Close"]})
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
                    return {
                        "signal": "HOLD",
                        "confidence": 50,
                        "reasoning": "Insufficient data for prediction",
                    }

                row = df.iloc[-1:]
                prob = MODEL.predict_proba(row[features].values)[0][1]

                # Determine signal based on probability
                # Very aggressive thresholds for maximum opportunities: BUY > 0.40, SELL < 0.35
                if prob >= 0.60:
                    signal = "BUY"
                    confidence = round(prob * 100, 1)
                    reasoning = (
                        f"Strong bullish signal from ML model (prob: {prob:.2f})"
                    )
                elif prob >= 0.40:
                    signal = "BUY"
                    confidence = round(prob * 100, 1)
                    reasoning = f"Moderate bullish signal (prob: {prob:.2f})"
                elif prob <= 0.20:
                    signal = "SELL"
                    confidence = round((1 - prob) * 100, 1)
                    reasoning = f"Strong bearish signal (prob: {prob:.2f})"
                elif prob <= 0.35:
                    signal = "SELL"
                    confidence = round((1 - prob) * 100, 1)
                    reasoning = f"Weak bearish signal (prob: {prob:.2f})"
                else:
                    signal = "HOLD"
                    confidence = 50 + abs(prob - 0.5) * 20
                    reasoning = f"Neutral - no clear direction (prob: {prob:.2f})"

                return {
                    "signal": signal,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "metrics": {
                        "probability": round(prob, 3),
                        "rsi": (
                            round(float(df.iloc[-1]["RSI"]), 2)
                            if pd.notna(df.iloc[-1]["RSI"])
                            else None
                        ),
                        "momentum": (
                            round(float(df.iloc[-1]["Momentum_10d"]), 4)
                            if pd.notna(df.iloc[-1]["Momentum_10d"])
                            else None
                        ),
                    },
                }

                # Check for alerts (stock)
                current_price = float(df["Adj Close"].iloc[-1])
                alert_manager.check_and_create_alerts(
                    symbol=ticker,
                    name=ticker,  # Could fetch company name from yfinance
                    asset_type="stock",
                    prediction=result,
                    current_price=current_price,
                )

                return result

            except Exception as e:
                logger.error(f"Stock prediction error for {ticker}: {e}")
                return {
                    "signal": "HOLD",
                    "confidence": 50,
                    "reasoning": "Prediction error - insufficient data",
                }

    except Exception as e:
        logger.error(f"Prediction error: {e}")
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


@app.post("/analyze", tags=["AI Analysis"])
def analyze(request: AnalysisRequest) -> Dict[str, Any]:
    """Use LLM to analyze ranking and provide buy/sell recommendations."""
    if not OPENAI_CLIENT:
        raise HTTPException(
            status_code=503, detail="LLM not configured (set OPENAI_API_KEY)"
        )

    # Create cache key from ranking + context
    cache_key = hashlib.md5(
        f"{[r['ticker'] for r in request.ranking[:10]]}{request.user_context}".encode()
    ).hexdigest()

    # Check cache
    cached_data = cache.get(f"analysis:{cache_key}")
    if cached_data:
        logger.debug(f"Cache hit for analysis: {cache_key[:8]}")
        cached_data["cached"] = True
        return cached_data

    # Fetch detailed market data for top stocks
    enriched_data = []
    for rank, r in enumerate(request.ranking[:10], 1):
        try:
            stock = yf.Ticker(r["ticker"])
            info = stock.info

            # Get recommendation signal
            prob = r["prob"]
            if prob >= 0.65:
                signal = "STRONG BUY"
            elif prob >= 0.55:
                signal = "BUY"
            elif prob >= 0.45:
                signal = "HOLD"
            elif prob >= 0.35:
                signal = "CONSIDER SELLING"
            else:
                signal = "SELL"

            enriched_data.append(
                {
                    "rank": rank,
                    "ticker": r["ticker"],
                    "name": info.get("longName", r["ticker"]),
                    "prob": prob,
                    "signal": signal,
                    "price": info.get("currentPrice", info.get("regularMarketPrice")),
                    "change": info.get("regularMarketChangePercent"),
                    "volume": info.get("volume"),
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE"),
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
                    "prob": r["prob"],
                    "signal": (
                        "BUY"
                        if r["prob"] >= 0.55
                        else "HOLD" if r["prob"] >= 0.45 else "SELL"
                    ),
                }
            )

    # Build enhanced prompt with market data
    ranking_text = "\n".join(
        [
            f"{d['rank']}. {d['ticker']} - {d.get('name', 'N/A')}: "
            f"Probability: {d['prob']*100:.1f}% | Signal: {d['signal']} | "
            f"Price: ${d.get('price', 'N/A')} | Change: {d.get('change', 'N/A')}% | "
            f"P/E: {d.get('pe_ratio', 'N/A')}"
            for d in enriched_data
        ]
    )

    user_ctx = request.user_context or "General investment strategy"
    prompt = (
        "You are an expert trading analyst. Based on ML model predictions and market data, "
        "provide actionable BUY/SELL recommendations.\n\n"
        f"RANKED STOCKS (Top 10):\n{ranking_text}\n\n"
        f"USER CONTEXT: {user_ctx}\n\n"
        "Provide:\n"
        "1. TOP 3 BUY RECOMMENDATIONS - Which stocks to buy NOW and why\n"
        "2. SELL/AVOID - Any stocks to sell or avoid and why\n"
        "3. KEY RISKS - Important market risks to watch\n"
        "4. ACTION PLAN - Clear next steps for the investor\n\n"
        "Be specific, direct, and actionable. Focus on concrete buy/sell decisions. "
        "Use the Signal column (STRONG BUY, BUY, HOLD, SELL) as guidance. 250-350 words."
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
                analysis = response.choices[0].message.content
                result = {
                    "analysis": analysis,
                    "model": response.model,
                    "cached": False,
                }

                # Cache the result
                cache.set(
                    f"analysis:{cache_key}",
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
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")


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


# Alert Management Endpoints
@app.get("/alerts", tags=["Alerts"])
def get_alerts(
    unread_only: bool = False,
    priority: Optional[str] = None,
    asset_type: Optional[str] = None,
    limit: int = 50,
):
    """
    Get alerts with optional filters.

    Query Parameters:
    - unread_only: Only return unread alerts (default: False)
    - priority: Filter by priority (low, medium, high, critical)
    - asset_type: Filter by asset type (stock, crypto)
    - limit: Maximum number of alerts to return (default: 50)
    """
    try:
        from .alerts import AlertPriority

        priority_enum = None
        if priority:
            try:
                priority_enum = AlertPriority[priority.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid priority: {priority}"
                )

        alerts = alert_manager.get_alerts(
            unread_only=unread_only,
            priority=priority_enum,
            asset_type=asset_type,
            limit=limit,
        )

        unread_count = alert_manager.get_unread_count()

        return {
            "alerts": alerts,
            "unread_count": unread_count,
            "total_count": len(alert_manager.alerts),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/mark-read", tags=["Alerts"])
def mark_alerts_read(alert_ids: List[str]):
    """
    Mark alerts as read.

    Body:
    - alert_ids: List of alert IDs to mark as read
    """
    try:
        marked = alert_manager.mark_as_read(alert_ids)
        return {"message": f"Marked {marked} alerts as read", "marked_count": marked}
    except Exception as e:
        logger.error(f"Error marking alerts as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/alerts/clear", tags=["Alerts"])
def clear_old_alerts(older_than_days: int = 7):
    """
    Clear old alerts.

    Query Parameters:
    - older_than_days: Remove alerts older than this many days (default: 7)
    """
    try:
        removed = alert_manager.clear_alerts(older_than_days)
        return {"message": f"Cleared {removed} old alerts", "removed_count": removed}
    except Exception as e:
        logger.error(f"Error clearing alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Mount frontend static files LAST so API routes take precedence
# This must come after all route definitions to avoid catching API routes
FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
