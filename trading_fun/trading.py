import argparse
import logging
import shutil
import sys
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
try:
    from xgboost import XGBClassifier
    _USE_XGB = True
except Exception as e:
    XGBClassifier = None
    _USE_XGB = False
    _xgboost_import_error = e

# default tickers
tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "V", "MA", "PG", "KO"]
features = ["SMA50", "SMA200", "RSI", "Volatility"]

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def load_data(ticker, period="5y"):
    try:
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=False)
    except Exception as e:
        logging.warning("Failed to download data for %s: %s", ticker, e)
        return None
    if df.empty:
        return None
    df["Returns_90d"] = df["Adj Close"].pct_change(90).shift(-90)
    df["Outperform"] = (df["Returns_90d"] > 0.05).astype(int)
    df["SMA50"] = df["Adj Close"].rolling(50).mean()
    df["SMA200"] = df["Adj Close"].rolling(200).mean()
    df["RSI"] = compute_rsi(df["Adj Close"])
    df["Volatility"] = df["Adj Close"].pct_change().rolling(30).std()
    df["Ticker"] = ticker
    return df.dropna()

def check_xgboost_and_openmp():
    if _USE_XGB:
        return True
    try:
        err_msg = str(_xgboost_import_error)
    except NameError:
        err_msg = ""
    if "libomp" in err_msg or "OpenMP" in err_msg or "libxgboost" in err_msg:
        try:
            import ctypes.util
            found = ctypes.util.find_library('omp') or ctypes.util.find_library('libomp')
        except Exception:
            found = None
        if found:
            logging.warning("xgboost import failed but libomp appears present (%s).", found)
        else:
            if shutil.which('brew'):
                logging.warning("xgboost import failed due to missing OpenMP runtime (libomp). Install with brew install libomp")
            else:
                logging.warning("xgboost import failed due to missing OpenMP runtime (libomp). Install via your package manager.")
    else:
        logging.warning("xgboost import failed (%s). Falling back to RandomForestClassifier.", err_msg)
    return False

def build_dataset(tickers_list, period="5y"):
    dfs = []
    for t in tickers_list:
        df = load_data(t, period=period)
        if df is not None:
            dfs.append(df)
    if not dfs:
        raise RuntimeError("No data could be loaded for the given tickers.")
    return pd.concat(dfs)

def parse_args():
    parser = argparse.ArgumentParser(description="Simple AI-driven buy list generator")
    parser.add_argument("--tickers", type=str, default=','.join(tickers), help="Comma-separated list of tickers")
    parser.add_argument("--period", type=str, default="5y", help="History period for yfinance downloads (e.g., 1y, 5y)")
    parser.add_argument("--top-n", type=int, default=10, help="Number of top tickers to print")
    parser.add_argument("--rank-period", type=str, default="300d", help="History period for ranking calculation (e.g., 300d)")
    parser.add_argument("--use-xgb", action="store_true", help="Prefer XGBoost if available")
    parser.add_argument("--quiet", action="store_true", help="Reduce logging verbosity")
    return parser.parse_args()

def train_model(data, model_type='rf', save_path=None):
    X = data[features]
    y = data['Outperform']
    if y.nunique() < 2:
        raise ValueError("Target `y` must contain at least two classes.")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    if model_type == 'xgb' and _USE_XGB:
        model = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, subsample=0.9, eval_metric='logloss', use_label_encoder=False, random_state=42)
    else:
        model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train.values, y_train.values)
    # Save model
    if save_path:
        import joblib
        joblib.dump(model, save_path)
    # MLFlow tracking if available
    try:
        import mlflow
        mlflow.log_metric('accuracy', float(acc))
    except Exception:
        pass
    # Evaluate
    from sklearn.metrics import accuracy_score
    preds = model.predict(X_test.values)
    acc = accuracy_score(y_test.values, preds)
    return model, acc

def main(args=None):
    if args is None:
        args = parse_args()
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    else:
        logging.getLogger().setLevel(logging.INFO)
    chosen_tickers = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
    data = build_dataset(chosen_tickers, period=args.period)
    model, acc = train_model(data, model_type='rf')
    logging.info('Model trained, acc=%.3f', acc)
    # Ranking
    ranking = {}
    for t in chosen_tickers:
        try:
            latest = yf.download(t, period=args.rank_period, auto_adjust=False)['Adj Close']
        except Exception:
            logging.warning('Failed to download latest for %s', t)
            continue
        df = pd.DataFrame()
        df['SMA50'] = latest.rolling(50).mean()
        df['SMA200'] = latest.rolling(200).mean()
        df['RSI'] = compute_rsi(latest)
        df['Volatility'] = latest.pct_change().rolling(30).std()
        df = df.dropna()
        if df.empty:
            logging.warning('No recent data for %s', t)
            continue
        row = df.iloc[-1:]
        prob = model.predict_proba(row.values)[0][1]
        ranking[t] = prob
    ranking = dict(sorted(ranking.items(), key=lambda x: x[1], reverse=True))
    for i, (k, v) in enumerate(ranking.items()):
        if i >= args.top_n:
            break
        print(f"{k}: {v:.2f}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    args = parse_args()
    main(args)
