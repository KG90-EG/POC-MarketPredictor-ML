import argparse
import logging
import shutil
import yfinance as yf
import pandas as pd
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
tickers = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL",
    "META",
    "TSLA",
    "V",
    "MA",
    "PG",
    "KO",
]
features = [
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


def compute_macd(series, fast=12, slow=26, signal=9):
    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd = fast_ema - slow_ema
    sig = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig


def compute_bollinger(series, window=20):
    sma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = sma + (std * 2)
    lower = sma - (std * 2)
    return upper, lower


def compute_momentum(series, period=10):
    return series.pct_change(period)


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
    # extra features
    df["Momentum_10d"] = compute_momentum(df["Adj Close"], period=10)
    macd, macd_sig = compute_macd(df["Adj Close"])
    df["MACD"] = macd
    df["MACD_signal"] = macd_sig
    bb_up, bb_low = compute_bollinger(df["Adj Close"], window=20)
    df["BB_upper"] = bb_up
    df["BB_lower"] = bb_low
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

            found = ctypes.util.find_library("omp") or ctypes.util.find_library(
                "libomp"
            )
        except Exception:
            found = None
        if found:
            logging.warning(
                "xgboost import failed but libomp appears present (%s).", found
            )
        else:
            if shutil.which("brew"):
                logging.warning(
                    "xgboost import failed due to missing OpenMP runtime (libomp). Install with brew install libomp"
                )
            else:
                logging.warning(
                    "xgboost import failed due to missing OpenMP runtime (libomp). Install via your package manager."
                )
    else:
        logging.warning(
            "xgboost import failed (%s). Falling back to RandomForestClassifier.",
            err_msg,
        )
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
    parser.add_argument(
        "--tickers",
        type=str,
        default=",".join(tickers),
        help="Comma-separated list of tickers",
    )
    parser.add_argument(
        "--period",
        type=str,
        default="5y",
        help="History period for yfinance downloads (e.g., 1y, 5y)",
    )
    parser.add_argument(
        "--top-n", type=int, default=10, help="Number of top tickers to print"
    )
    parser.add_argument(
        "--rank-period",
        type=str,
        default="300d",
        help="History period for ranking calculation (e.g., 300d)",
    )
    parser.add_argument(
        "--use-xgb", action="store_true", help="Prefer XGBoost if available"
    )
    parser.add_argument("--quiet", action="store_true", help="Reduce logging verbosity")
    return parser.parse_args()


def train_model(data, model_type="rf", save_path=None):
    X = data[features]
    y = data["Outperform"]
    if y.nunique() < 2:
        raise ValueError("Target `y` must contain at least two classes.")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    if model_type == "xgb" and _USE_XGB:
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
        model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train.values, y_train.values)
    # Save model
    if save_path:
        import joblib

        joblib.dump(model, save_path)
    # MLFlow tracking if available
    # Evaluate
    from sklearn.metrics import (
        accuracy_score,
        precision_score,
        recall_score,
        f1_score,
        roc_auc_score,
    )

    preds = model.predict(X_test.values)
    proba = (
        model.predict_proba(X_test.values)[:, 1]
        if hasattr(model, "predict_proba")
        else None
    )
    acc = accuracy_score(y_test.values, preds)
    prec = precision_score(y_test.values, preds, zero_division=0)
    rec = recall_score(y_test.values, preds, zero_division=0)
    f1 = f1_score(y_test.values, preds, zero_division=0)
    roc = roc_auc_score(y_test.values, proba) if proba is not None else None

    # Cross-validation: time-series split
    from sklearn.model_selection import TimeSeriesSplit, cross_val_score

    tscv = TimeSeriesSplit(n_splits=5)
    cv_scores = cross_val_score(
        model,
        X.values,
        y.values,
        cv=tscv,
        scoring="roc_auc" if roc is not None else "accuracy",
    )

    metrics = {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "roc_auc": float(roc) if roc is not None else None,
        "cv_mean": float(cv_scores.mean()),
        "cv_std": float(cv_scores.std()),
    }
    # MLFlow tracking if available
    try:
        import mlflow

        for k, v in metrics.items():
            if v is not None:
                mlflow.log_metric(k, v)
    except Exception:
        pass
    return model, metrics


def main(args=None):
    if args is None:
        args = parse_args()
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    else:
        logging.getLogger().setLevel(logging.INFO)
    chosen_tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    data = build_dataset(chosen_tickers, period=args.period)
    model, metrics = train_model(data, model_type="rf")
    logging.info("Model trained, metrics=%s", metrics)
    # Ranking
    ranking = {}
    for t in chosen_tickers:
        try:
            latest = yf.download(t, period=args.rank_period, auto_adjust=False)[
                "Adj Close"
            ]
        except Exception:
            logging.warning("Failed to download latest for %s", t)
            continue
        df = pd.DataFrame()
        df["SMA50"] = latest.rolling(50).mean()
        df["SMA200"] = latest.rolling(200).mean()
        df["RSI"] = compute_rsi(latest)
        df["Volatility"] = latest.pct_change().rolling(30).std()
        df = df.dropna()
        if df.empty:
            logging.warning("No recent data for %s", t)
            continue
        row = df.iloc[-1:]
        prob = model.predict_proba(row.values)[0][1]
        ranking[t] = prob
    ranking = dict(sorted(ranking.items(), key=lambda x: x[1], reverse=True))
    for i, (k, v) in enumerate(ranking.items()):
        if i >= args.top_n:
            break
        print(f"{k}: {v:.2f}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    args = parse_args()
    main(args)
