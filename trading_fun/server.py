from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import joblib
import os
from .trading import features, compute_rsi, compute_macd, compute_bollinger, compute_momentum
import pandas as pd
import yfinance as yf

app = FastAPI()

# Enable CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.environ.get('PROD_MODEL_PATH', 'models/prod_model.bin')
MODEL = None
if os.path.exists(MODEL_PATH):
    MODEL = joblib.load(MODEL_PATH)

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
    prob = MODEL.predict_proba(row.values)[0][1] if hasattr(MODEL, 'predict_proba') else float(MODEL.predict(row.values)[0])
    return {'prob': float(prob)}


@app.get('/predict_ticker/{ticker}')
def predict_ticker(ticker: str):
    if MODEL is None:
        raise HTTPException(status_code=503, detail='No model available')
    # Get latest data and compute features
    df = yf.download(ticker, period='300d', auto_adjust=False)['Adj Close']
    df = pd.DataFrame({'Adj Close': df})
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
        df = yf.download(t, period='300d', auto_adjust=False)['Adj Close']
        df = pd.DataFrame({'Adj Close': df})
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
