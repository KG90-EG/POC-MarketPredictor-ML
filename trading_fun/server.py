from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import joblib
import os
from dotenv import load_dotenv
from .trading import features, compute_rsi, compute_macd, compute_bollinger, compute_momentum
import pandas as pd
import yfinance as yf
import hashlib
import time

# Load environment variables from .env file
load_dotenv()

try:
    from openai import OpenAI
    OPENAI_CLIENT = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
except Exception:
    OPENAI_CLIENT = None

# Simple cache for LLM responses (TTL: 5 minutes)
ANALYSIS_CACHE = {}
CACHE_TTL = 300  # seconds

app = FastAPI()

# Enable CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.environ.get('PROD_MODEL_PATH', 'models/prod_model.bin')
MODEL = None
LOADED_MODEL_PATH = None
if os.path.exists(MODEL_PATH):
    MODEL = joblib.load(MODEL_PATH)
    LOADED_MODEL_PATH = MODEL_PATH

# Optional: mount built frontend if available (expects Vite build in frontend/dist)
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist'))
if os.path.isdir(FRONTEND_DIST):
    app.mount('/', StaticFiles(directory=FRONTEND_DIST, html=True), name='frontend')


class FeaturePayload(BaseModel):
    features: Dict[str, float]


def row_from_features(feat_dict: Dict[str, Any]):
    # convert into DataFrame row with expected order
    row = {k: float(feat_dict.get(k, 0.0)) for k in features}
    return pd.DataFrame([row])


@app.get('/health')
def health():
    return {'status': 'ok', 'model_loaded': MODEL is not None}


@app.post('/predict_raw')
def predict_raw(payload: FeaturePayload):
    if MODEL is None:
        raise HTTPException(status_code=503, detail='No model available')
    row = row_from_features(payload.features)
    if hasattr(MODEL, 'predict_proba'):
        prob = MODEL.predict_proba(row.values)[0][1]
    else:
        prob = float(MODEL.predict(row.values)[0])
    return {'prob': float(prob)}


@app.get('/predict_ticker/{ticker}')
def predict_ticker(ticker: str):
    if MODEL is None:
        raise HTTPException(status_code=503, detail='No model available')
    # Get latest data and compute features
    raw = yf.download(ticker, period='300d', auto_adjust=False, progress=False)
    # Handle MultiIndex columns from yfinance
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    df = pd.DataFrame({'Adj Close': raw['Adj Close']})
    df['SMA50'] = df['Adj Close'].rolling(50).mean()
    df['SMA200'] = df['Adj Close'].rolling(200).mean()
    df['RSI'] = compute_rsi(df['Adj Close'])
    df['Volatility'] = df['Adj Close'].pct_change().rolling(30).std()
    df['Momentum_10d'] = compute_momentum(df['Adj Close'], 10)
    macd, macd_sig = compute_macd(df['Adj Close'])
    df['MACD'] = macd
    df['MACD_signal'] = macd_sig
    bb_up, bb_low = compute_bollinger(df['Adj Close'])
    df['BB_upper'] = bb_up
    df['BB_lower'] = bb_low
    df = df.dropna()
    if df.empty:
        raise HTTPException(status_code=404, detail='No recent data for ticker')
    row = df.iloc[-1:]
    prob = MODEL.predict_proba(row[features].values)[0][1]
    return {'prob': float(prob)}


@app.get('/ranking')
def ranking(tickers: str = "AAPL,MSFT,NVDA"):
    if MODEL is None:
        raise HTTPException(status_code=503, detail='No model available')
    chosen = [t.strip().upper() for t in tickers.split(',') if t.strip()]
    result = []
    for t in chosen:
        try:
            raw = yf.download(t, period='300d', auto_adjust=False, progress=False)
            # Handle MultiIndex columns from yfinance
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
        except Exception:
            continue
        if 'Adj Close' not in raw.columns:
            continue
        df = raw['Adj Close']
        if isinstance(df, pd.Series):
            df = df.to_frame(name='Adj Close')
        df['SMA50'] = df['Adj Close'].rolling(50).mean()
        df['SMA200'] = df['Adj Close'].rolling(200).mean()
        df['RSI'] = compute_rsi(df['Adj Close'])
        df['Volatility'] = df['Adj Close'].pct_change().rolling(30).std()
        df['Momentum_10d'] = compute_momentum(df['Adj Close'], 10)
        macd, macd_sig = compute_macd(df['Adj Close'])
        df['MACD'] = macd
        df['MACD_signal'] = macd_sig
        bb_up, bb_low = compute_bollinger(df['Adj Close'])
        df['BB_upper'] = bb_up
        df['BB_lower'] = bb_low
        df = df.dropna()
        if df.empty:
            continue
        row = df.iloc[-1:]
        prob = MODEL.predict_proba(row[features].values)[0][1]
        result.append({'ticker': t, 'prob': float(prob)})
    # sort result
    result.sort(key=lambda r: r['prob'], reverse=True)
    return {'ranking': result}


@app.get('/models')
def list_models() -> Dict[str, Any]:
    """List available model artifacts in the models directory.
    Returns current loaded model filename and list of other model files with sizes.
    """
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
    items: List[Dict[str, Any]] = []
    if os.path.isdir(models_dir):
        for fname in sorted(os.listdir(models_dir)):
            fpath = os.path.join(models_dir, fname)
            if os.path.isfile(fpath) and fname.endswith('.bin'):
                try:
                    size = os.path.getsize(fpath)
                except OSError:
                    size = None
                items.append({'file': fname, 'size_bytes': size})
    current = os.path.basename(LOADED_MODEL_PATH) if LOADED_MODEL_PATH else None
    return {'current_model': current, 'available_models': items}


@app.get('/ticker_info/{ticker}')
def ticker_info(ticker: str) -> Dict[str, Any]:
    """Fetch current price, change, volume, and market cap for a ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'ticker': ticker,
            'price': info.get('currentPrice', info.get('regularMarketPrice')),
            'change': info.get('regularMarketChangePercent'),
            'volume': info.get('volume'),
            'market_cap': info.get('marketCap'),
            'name': info.get('longName', ticker)
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Unable to fetch info: {str(e)}')


class AnalysisRequest(BaseModel):
    ranking: List[Dict[str, Any]]
    user_context: Optional[str] = None


@app.post('/analyze')
def analyze(request: AnalysisRequest) -> Dict[str, Any]:
    """Use LLM to analyze ranking and provide recommendations."""
    if not OPENAI_CLIENT:
        raise HTTPException(status_code=503, detail='LLM not configured (set OPENAI_API_KEY)')

    # Create cache key from ranking + context
    cache_key = hashlib.md5(
        f"{[r['ticker'] for r in request.ranking[:10]]}{request.user_context}".encode()
    ).hexdigest()

    # Check cache
    if cache_key in ANALYSIS_CACHE:
        cached_data, timestamp = ANALYSIS_CACHE[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            cached_data['cached'] = True
            return cached_data

    # Build prompt
    ranking_text = '\n'.join(
        [f"{i+1}. {r['ticker']}: {r['prob']*100:.2f}% probability"
         for i, r in enumerate(request.ranking[:10])]
    )

    user_ctx = request.user_context or 'No additional context provided'
    prompt = (
        f"You are a financial analysis assistant. Analyze the following "
        f"stock ranking based on ML model predictions:\\n\\n{ranking_text}\\n\\n"
        f"User context: {user_ctx}\\n\\n"
        "Provide:\\n"
        "1. A brief summary of the top opportunities\\n"
        "2. Key considerations and risks\\n"
        "3. Actionable recommendations\\n\\n"
        "Keep your response concise (200-300 words)."
    )

    try:
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                response = OPENAI_CLIENT.chat.completions.create(
                    model=os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
                    messages=[{'role': 'user', 'content': prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                analysis = response.choices[0].message.content
                result = {'analysis': analysis, 'model': response.model, 'cached': False}

                # Cache the result
                ANALYSIS_CACHE[cache_key] = (result, time.time())

                return result
            except Exception as e:
                error_str = str(e)
                # Check if it's a rate limit error
                if '429' in error_str or 'rate_limit' in error_str.lower():
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        raise HTTPException(
                            status_code=429,
                            detail='OpenAI rate limit exceeded. '
                                   'Please wait a moment and try again.'
                        )
                else:
                    raise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'LLM analysis failed: {str(e)}')
