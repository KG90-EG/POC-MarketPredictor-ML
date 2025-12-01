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
    # xgboost is not usable (e.g., missing OpenMP runtime on macOS). Fall back to RandomForest
    XGBClassifier = None
    _USE_XGB = False
    _xgboost_import_error = e

# ----------------------------------
# 1. Aktienliste definieren
# ----------------------------------
tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "V", "MA", "PG", "KO"]

# Features/Label
features = ["SMA50", "SMA200", "RSI", "Volatility"]

# ----------------------------------
# 2. Daten laden und Features berechnen
# ----------------------------------
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
    """Try to import xgboost and detect common problems (like missing libomp on macOS)."""
    if _USE_XGB:
        # Already successfully imported
        return True
    # If import failed, check known error messages
    try:
        # If _xgboost_import_error exists, check message
        err_msg = str(_xgboost_import_error)
    except NameError:
        err_msg = ""  # import not attempted earlier
    if "libomp" in err_msg or "OpenMP" in err_msg or "libxgboost" in err_msg:
        # check for libomp presence
        try:
            import ctypes.util
            found = ctypes.util.find_library('omp') or ctypes.util.find_library('libomp')
        except Exception:
            found = None
        if found:
            logging.warning("xgboost import failed but libomp appears to be present (%s). The issue may be related to mismatched installations. Consider reinstalling xgboost or ensuring libomp is in the library path.", found)
        else:
            if shutil.which('brew'):
                logging.warning("xgboost import failed due to missing OpenMP runtime (libomp). On macOS, install with: brew install libomp")
            else:
                logging.warning("xgboost import failed due to missing OpenMP runtime (libomp). Install libomp via your platform package manager or build from source.")
    else:
        logging.warning("xgboost import failed (%s). Falling back to RandomForestClassifier.", err_msg)
    return False

# Dataset erstellen
def build_dataset(tickers_list, period="5y"):
    dfs = []
    for t in tickers_list:
        df = load_data(t, period=period)
        if df is not None:
            dfs.append(df)
    if not dfs:
        raise RuntimeError("No data could be loaded for the given tickers.")
    return pd.concat(dfs)

# (no global dataset; main builds dataset based on args)


def parse_args():
    parser = argparse.ArgumentParser(description="Simple AI-driven buy list generator")
    parser.add_argument("--tickers", type=str, default=','.join(tickers), help="Comma-separated list of tickers")
    parser.add_argument("--period", type=str, default="5y", help="History period for yfinance downloads (e.g., 1y, 5y)")
    parser.add_argument("--top-n", type=int, default=10, help="Number of top tickers to print")
    parser.add_argument("--rank-period", type=str, default="300d", help="History period for ranking calculation (e.g., 300d)")
    parser.add_argument("--use-xgb", action="store_true", help="Prefer XGBoost if available")
    parser.add_argument("--quiet", action="store_true", help="Reduce logging verbosity")
    return parser.parse_args()


def main(args=None):
    if args is None:
        args = parse_args()
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    else:
        logging.getLogger().setLevel(logging.INFO)

    chosen_tickers = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
    logging.info("Loading data for tickers: %s", chosen_tickers)
    data = build_dataset(chosen_tickers, period=args.period)

    # Build features/labels
    X = data[features]
    y = data["Outperform"]

    if y.nunique() < 2:
        raise ValueError("Target `y` must contain at least two classes. Check your label generation and data quantity.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Model selection
    if args.use_xgb and _USE_XGB and XGBClassifier is not None:
        logging.info("Using XGBoost classifier")
        model = XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            eval_metric="logloss",
            use_label_encoder=False,
            random_state=42,
        )
    else:
        if args.use_xgb and not _USE_XGB:
            check_xgboost_and_openmp()
        logging.info("Using RandomForest classifier as fallback")
        model = RandomForestClassifier(n_estimators=200, random_state=42)

    model.fit(X_train.values, y_train.values)

    # Ranking
    ranking = {}
    for t in chosen_tickers:
        try:
            latest = yf.download(t, period=args.rank_period, auto_adjust=False)["Adj Close"]
        except Exception as e:
            logging.warning("Failed to download latest data for %s: %s", t, e)
            continue
        df = pd.DataFrame()
        df["SMA50"] = latest.rolling(50).mean()
        df["SMA200"] = latest.rolling(200).mean()
        df["RSI"] = compute_rsi(latest)
        df["Volatility"] = latest.pct_change().rolling(30).std()
        df = df.dropna()
        if df.empty:
            logging.warning("No recent data for %s, skipping", t)
            continue
        row = df.iloc[-1:]
        prob = model.predict_proba(row.values)[0][1]
        ranking[t] = prob

    ranking = dict(sorted(ranking.items(), key=lambda x: x[1], reverse=True))
    logging.info("\n🔥 BUY-LIST — AI-Wahrscheinlichkeit der Outperformance:\n")
    for i, (k, v) in enumerate(ranking.items()):
        if i >= args.top_n:
            break
        print(f"{k}: {v:.2f}")


def quick_test():
    # Quick sanity check: run main with three tickers and quiet output
    test_args = argparse.Namespace(tickers='AAPL,MSFT,NVDA', period='1y', top_n=3, use_xgb=False, quiet=True, rank_period='300d')
    main(test_args)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    try:
        args = parse_args()
        main(args)
    except Exception as e:
        logging.exception("Error running Trading_Test2: %s", e)
        sys.exit(1)