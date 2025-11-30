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

# Default popular stocks for automatic ranking
DEFAULT_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B',
    'UNH', 'JNJ', 'V', 'WMT', 'JPM', 'MA', 'PG', 'XOM', 'HD', 'CVX',
    'LLY', 'ABBV', 'MRK', 'KO', 'PEP', 'COST', 'AVGO', 'TMO', 'BAC',
    'CSCO', 'MCD', 'ACN', 'AMD', 'NFLX', 'ADBE', 'DIS', 'NKE', 'INTC',
    'CRM', 'TXN', 'ORCL', 'ABT', 'CMCSA', 'VZ', 'WFC', 'PM', 'IBM',
    'QCOM', 'UPS', 'HON', 'BA', 'GE'
]

# Market indices for dynamic stock discovery
COUNTRY_INDICES = {
    'Switzerland': '^SSMI',  # Swiss Market Index
    'Germany': '^GDAXI',     # DAX
    'United Kingdom': '^FTSE',  # FTSE 100
    'France': '^FCHI',       # CAC 40
    'Japan': '^N225',        # Nikkei 225
    'Canada': '^GSPTSE'      # S&P/TSX Composite
}

def get_top_stocks_from_index(index_symbol: str, limit: int = 30) -> List[str]:
    """Dynamically fetch top stocks from a market index."""
    try:
        index = yf.Ticker(index_symbol)
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
        'Switzerland': [
            'NESN.SW', 'NOVN.SW', 'ROG.SW', 'UBSG.SW', 'ZURN.SW', 'ABBN.SW',
            'SREN.SW', 'GIVN.SW', 'LONN.SW', 'SLHN.SW', 'SCMN.SW', 'ADEN.SW',
            'GEBN.SW', 'PGHN.SW', 'SGSN.SW', 'CSGN.SW', 'HOLN.SW', 'CFR.SW',
            'SYNN.SW', 'STMN.SW', 'KNIN.SW', 'BALN.SW', 'BUCN.SW', 'LISN.SW',
            'VACN.SW', 'SREN.SW', 'BEAN.SW', 'AREN.SW', 'DUFN.SW', 'TEMN.SW'
        ],
        'Germany': [
            'SAP', 'SIE.DE', 'ALV.DE', 'DTE.DE', 'VOW3.DE', 'MBG.DE', 'BMW.DE',
            'BAS.DE', 'ADS.DE', 'MUV2.DE', 'BAYN.DE', 'EOAN.DE', 'DB1.DE',
            'HEN3.DE', 'IFX.DE', 'RHM.DE', 'DAI.DE', 'FRE.DE', 'SHL.DE', 'CON.DE',
            'BEI.DE', 'VNA.DE', 'SAP.DE', 'P911.DE', 'HNR1.DE'
        ],
        'United Kingdom': [
            'SHEL.L', 'AZN.L', 'HSBA.L', 'ULVR.L', 'DGE.L', 'BP.L', 'GSK.L',
            'RIO.L', 'LSEG.L', 'NG.L', 'REL.L', 'BARC.L', 'LLOY.L', 'VOD.L',
            'PRU.L', 'BT-A.L', 'BATS.L', 'AAL.L', 'CRH.L', 'IMB.L'
        ],
        'France': [
            'MC.PA', 'OR.PA', 'SAN.PA', 'TTE.PA', 'AIR.PA', 'BNP.PA', 'SU.PA',
            'AI.PA', 'CA.PA', 'EN.PA', 'SGO.PA', 'DG.PA', 'CS.PA', 'BN.PA',
            'KER.PA', 'RMS.PA', 'EL.PA', 'CAP.PA', 'VIV.PA', 'ORA.PA'
        ],
        'Japan': [
            'TM', '7203.T', '6758.T', '8306.T', '6861.T', '9984.T', '6902.T',
            '9432.T', '8035.T', '7974.T', '4063.T', '4502.T', '6501.T',
            '4503.T', '6954.T', '6098.T', '9433.T', '4568.T', '6273.T', '7267.T'
        ],
        'Canada': [
            'SHOP.TO', 'TD.TO', 'RY.TO', 'BNS.TO', 'ENB.TO', 'CNR.TO', 'CP.TO',
            'BMO.TO', 'CNQ.TO', 'TRP.TO', 'CM.TO', 'SU.TO', 'WCN.TO', 'MFC.TO',
            'BAM.TO', 'ABX.TO', 'BCE.TO', 'FNV.TO', 'QSR.TO', 'NTR.TO'
        ]
    }
    
    seed_list = country_seeds.get(country, DEFAULT_STOCKS)
    
    # Validate and rank by market cap in parallel
    def validate_ticker(ticker: str):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            market_cap = info.get('marketCap', 0)
            country_match = info.get('country', '')
            
            # Only include if has market cap data
            if market_cap and market_cap > 0:
                return {
                    'ticker': ticker,
                    'market_cap': market_cap,
                    'country': country_match
                }
        except Exception:
            pass
        return None
    
    validated_stocks = []
    # Parallel validation with thread pool (max 15 concurrent to avoid rate limits)
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(validate_ticker, t) for t in seed_list[:limit * 2]]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                validated_stocks.append(result)
    
    # Sort by market cap and return top tickers
    validated_stocks.sort(key=lambda x: x['market_cap'], reverse=True)
    return [s['ticker'] for s in validated_stocks[:limit]]

# Cache for country stocks to avoid repeated API calls
COUNTRY_STOCKS_CACHE = {}
CACHE_TIMESTAMP = {}
CACHE_DURATION = 3600  # 1 hour

def get_country_stocks(country: str) -> List[str]:
    """Get stocks for country with caching."""
    current_time = time.time()
    
    # Check cache
    if country in COUNTRY_STOCKS_CACHE:
        if current_time - CACHE_TIMESTAMP.get(country, 0) < CACHE_DURATION:
            return COUNTRY_STOCKS_CACHE[country]
    
    # Fetch and cache
    if country == 'Global' or country == 'United States':
        stocks = DEFAULT_STOCKS
    else:
        stocks = get_stocks_by_country(country, limit=30)
        if not stocks:  # Fallback to default if fetch fails
            stocks = DEFAULT_STOCKS
    
    COUNTRY_STOCKS_CACHE[country] = stocks
    CACHE_TIMESTAMP[country] = current_time
    return stocks

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
def ranking(tickers: str = "", country: str = 'Global'):
    """Rank stocks by ML prediction probability.
    If no tickers provided, dynamically fetches top stocks for the specified country.
    Country options: Global, United States, Switzerland, Germany, United Kingdom, France, Japan, Canada
    """
    if MODEL is None:
        raise HTTPException(status_code=503, detail='No model available')
    
    # Use country-specific stocks if no tickers provided
    if not tickers.strip():
        chosen = get_country_stocks(country)
    else:
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
        if raw.empty or 'Adj Close' not in raw.columns:
            continue
        
        # Ensure we have a DataFrame with proper column access
        df = pd.DataFrame()
        df['Adj Close'] = raw['Adj Close']
        
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
    """Fetch comprehensive market data for a ticker including price, volume, market cap, P/E ratio, and 52-week range."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'ticker': ticker,
            'price': info.get('currentPrice', info.get('regularMarketPrice')),
            'change': info.get('regularMarketChangePercent'),
            'volume': info.get('volume'),
            'market_cap': info.get('marketCap'),
            'name': info.get('longName', ticker),
            'pe_ratio': info.get('trailingPE'),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
            'country': info.get('country', 'Unknown')
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Unable to fetch info: {str(e)}')


@app.post('/ticker_info_batch')
def ticker_info_batch(tickers: List[str]) -> Dict[str, Any]:
    """Batch fetch ticker information for multiple stocks in parallel.
    Returns dict mapping ticker to info, with errors for failed tickers.
    """
    import concurrent.futures
    
    results = {}
    errors = {}
    
    def fetch_single(ticker: str):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return ticker, {
                'ticker': ticker,
                'price': info.get('currentPrice', info.get('regularMarketPrice')),
                'change': info.get('regularMarketChangePercent'),
                'volume': info.get('volume'),
                'market_cap': info.get('marketCap'),
                'name': info.get('longName', ticker),
                'pe_ratio': info.get('trailingPE'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'country': info.get('country', 'Unknown')
            }, None
        except Exception as e:
            return ticker, None, str(e)
    
    # Fetch in parallel with thread pool (max 10 concurrent)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_single, t) for t in tickers]
        for future in concurrent.futures.as_completed(futures):
            ticker, data, error = future.result()
            if error:
                errors[ticker] = error
            else:
                results[ticker] = data
    
    return {'results': results, 'errors': errors}


class AnalysisRequest(BaseModel):
    ranking: List[Dict[str, Any]]
    user_context: Optional[str] = None


@app.post('/analyze')
def analyze(request: AnalysisRequest) -> Dict[str, Any]:
    """Use LLM to analyze ranking and provide buy/sell recommendations."""
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

    # Fetch detailed market data for top stocks
    enriched_data = []
    for rank, r in enumerate(request.ranking[:10], 1):
        try:
            stock = yf.Ticker(r['ticker'])
            info = stock.info
            
            # Get recommendation signal
            prob = r['prob']
            if prob >= 0.65:
                signal = 'STRONG BUY'
            elif prob >= 0.55:
                signal = 'BUY'
            elif prob >= 0.45:
                signal = 'HOLD'
            elif prob >= 0.35:
                signal = 'CONSIDER SELLING'
            else:
                signal = 'SELL'
            
            enriched_data.append({
                'rank': rank,
                'ticker': r['ticker'],
                'name': info.get('longName', r['ticker']),
                'prob': prob,
                'signal': signal,
                'price': info.get('currentPrice', info.get('regularMarketPrice')),
                'change': info.get('regularMarketChangePercent'),
                'volume': info.get('volume'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow')
            })
        except Exception:
            # Fallback to basic data if fetch fails
            enriched_data.append({
                'rank': rank,
                'ticker': r['ticker'],
                'prob': r['prob'],
                'signal': 'BUY' if r['prob'] >= 0.55 else 'HOLD' if r['prob'] >= 0.45 else 'SELL'
            })

    # Build enhanced prompt with market data
    ranking_text = '\n'.join([
        f"{d['rank']}. {d['ticker']} - {d.get('name', 'N/A')}: "
        f"Probability: {d['prob']*100:.1f}% | Signal: {d['signal']} | "
        f"Price: ${d.get('price', 'N/A')} | Change: {d.get('change', 'N/A')}% | "
        f"P/E: {d.get('pe_ratio', 'N/A')}"
        for d in enriched_data
    ])

    user_ctx = request.user_context or 'General investment strategy'
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
