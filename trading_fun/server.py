from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Request,
    Response,
)
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import joblib
import os
from dotenv import load_dotenv
from .trading import (
    features,
    compute_rsi,
    compute_macd,
    compute_bollinger,
    compute_momentum,
)
from .crypto import (
    get_crypto_ranking,
    search_crypto,
    get_crypto_details,
)
import pandas as pd
import yfinance as yf
import hashlib
import time

# Import new modules
from .cache import cache
from .rate_limiter import RateLimiter
from .logging_config import setup_logging, RequestLogger
from .websocket import manager as ws_manager
from .config import config as app_config
from .services import StockService, ValidationService, HealthService
from . import metrics as prom_metrics
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

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


# Enable CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "null",  # For file:// protocol
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

        # Track model prediction metrics
        pred_duration = time.time() - pred_start
        prom_metrics.track_model_prediction("random_forest", float(prob), pred_duration)

        result.append({"ticker": t, "prob": float(prob)})

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


# Mount frontend static files LAST so API routes take precedence
# This must come after all route definitions to avoid catching API routes
FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
