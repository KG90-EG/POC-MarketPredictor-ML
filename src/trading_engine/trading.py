import argparse
import logging
import shutil
from typing import Optional, Tuple

import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from .ml.feature_engineering import add_all_features  # noqa: F401 - re-exported
from .ml.feature_engineering import get_feature_names, select_best_features

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
# Original 9 features (kept for backward compatibility)
features_legacy = [
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

# All 40+ features from feature engineering
features = get_feature_names()

# Use all features by default (can be reduced via feature selection)
USE_ALL_FEATURES = True

# Use all features by default (can be reduced via feature selection)
USE_ALL_FEATURES = True


def compute_macd(
    series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> Tuple[pd.Series, pd.Series]:
    """Compute MACD (Moving Average Convergence Divergence) indicator.

    Args:
        series: Price series to compute MACD on
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)

    Returns:
        Tuple of (MACD line, Signal line)
    """
    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd = fast_ema - slow_ema
    sig = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig


def compute_bollinger(series: pd.Series, window: int = 20) -> Tuple[pd.Series, pd.Series]:
    """Compute Bollinger Bands.

    Args:
        series: Price series to compute bands on
        window: Rolling window size (default: 20)

    Returns:
        Tuple of (upper band, lower band)
    """
    sma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = sma + (std * 2)
    lower = sma - (std * 2)
    return upper, lower


def compute_momentum(series: pd.Series, period: int = 10) -> pd.Series:
    """Compute momentum as percentage change over period.

    Args:
        series: Price series
        period: Number of periods to look back (default: 10)

    Returns:
        Momentum series
    """
    return series.pct_change(period)


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Compute RSI (Relative Strength Index).

    Args:
        series: Price series
        period: RSI period (default: 14)

    Returns:
        RSI series (0-100)
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))


def load_data(
    ticker: str, period: str = "5y", use_advanced_features: bool = True
) -> Optional[pd.DataFrame]:
    """Load historical price data for a ticker with features.

    Args:
        ticker: Stock ticker symbol
        period: Time period (e.g., "5y", "1y", "6mo")
        use_advanced_features: Use 20 technical features if True, else 9 legacy features

    Returns:
        DataFrame with features and target, or None if failed
    """
    try:
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=False, progress=False)
    except Exception as e:
        logging.warning("Failed to download data for %s: %s", ticker, e)
        return None
    if df.empty:
        return None

    # Calculate target variable (outperformance)
    df["Returns_90d"] = df["Adj Close"].pct_change(90).shift(-90)
    df["Outperform"] = (df["Returns_90d"] > 0.05).astype(int)

    if use_advanced_features and USE_ALL_FEATURES:
        # Use ONLY technical features (no external API calls to avoid rate limiting)
        logging.info(f"Adding 20 technical features for {ticker}")
        from .ml.feature_engineering import add_technical_features_only

        df = add_technical_features_only(df)
    else:
        # Legacy: compute 9 original features only
        df["SMA50"] = df["Adj Close"].rolling(50).mean()
        df["SMA200"] = df["Adj Close"].rolling(200).mean()
        df["RSI"] = compute_rsi(df["Adj Close"])
        df["Volatility"] = df["Adj Close"].pct_change().rolling(30).std()
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

            found = ctypes.util.find_library("omp") or ctypes.util.find_library("libomp")
        except Exception:
            found = None
        if found:
            logging.warning("xgboost import failed but libomp appears present (%s).", found)
        else:
            if shutil.which("brew"):
                logging.warning(
                    "xgboost import failed due to missing OpenMP runtime (libomp). "
                    "Install with brew install libomp"
                )
            else:
                logging.warning(
                    "xgboost import failed due to missing OpenMP runtime (libomp). "
                    "Install via your package manager."
                )
    else:
        logging.warning(
            "xgboost import failed (%s). Falling back to RandomForestClassifier.",
            err_msg,
        )
    return False


def build_dataset(tickers_list, period="5y", use_advanced_features=None):
    """Build dataset from multiple tickers.

    Args:
        tickers_list: List of ticker symbols
        period: Historical data period (default: "5y")
        use_advanced_features: Use 20 technical features if True, else 9 legacy features.
                              If None, uses global USE_ALL_FEATURES setting.

    Returns:
        Concatenated DataFrame with all tickers
    """
    # Use global setting if not explicitly specified
    if use_advanced_features is None:
        use_advanced_features = USE_ALL_FEATURES

    import time

    dfs = []
    failed_tickers = []

    for i, t in enumerate(tickers_list):
        # Add delay to avoid rate limiting (0.5s between requests)
        if i > 0:
            time.sleep(0.5)

        try:
            df = load_data(t, period=period, use_advanced_features=use_advanced_features)
            if df is not None:
                dfs.append(df)
                logging.info(f"✓ Loaded {t}: {len(df)} samples")
            else:
                failed_tickers.append(t)
                logging.warning(f"✗ Failed to load {t}: empty data")
        except Exception as e:
            failed_tickers.append(t)
            logging.warning(f"✗ Failed to load {t}: {str(e)[:100]}")
            # If rate limited, wait longer
            if "Rate limit" in str(e) or "Too Many Requests" in str(e):
                logging.warning("Rate limited! Waiting 10 seconds...")
                time.sleep(10)

    if failed_tickers:
        logging.warning(
            f"Failed to load {len(failed_tickers)} tickers: {', '.join(failed_tickers[:5])}..."
        )

    if not dfs:
        raise RuntimeError("No data could be loaded for the given tickers.")

    logging.info(f"Successfully loaded {len(dfs)}/{len(tickers_list)} tickers")
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
    parser.add_argument("--top-n", type=int, default=10, help="Number of top tickers to print")
    parser.add_argument(
        "--rank-period",
        type=str,
        default="300d",
        help="History period for ranking calculation (e.g., 300d)",
    )
    parser.add_argument("--use-xgb", action="store_true", help="Prefer XGBoost if available")
    parser.add_argument("--quiet", action="store_true", help="Reduce logging verbosity")
    return parser.parse_args()


def train_model(
    data,
    model_type="rf",
    save_path=None,
    use_feature_selection=True,
    n_features=30,
    use_ensemble=False,
    optimize_hyperparams=False,
    n_trials=50,
    track_with_mlflow=False,
    run_name=None,
):
    """Train ML model with optional feature selection, ensemble, and hyperparameter tuning.

    Args:
        data: Training data DataFrame
        model_type: 'rf', 'xgb', 'voting', 'stacking' (default: 'rf')
        save_path: Path to save trained model
        use_feature_selection: Apply feature selection if True (default: True)
        n_features: Number of features to select (default: 30)
        use_ensemble: Use ensemble methods if True (default: False)
        optimize_hyperparams: Run hyperparameter optimization if True (default: False)
        n_trials: Number of Optuna trials for optimization (default: 50)
        track_with_mlflow: Track run with MLflow if True (default: False)
        run_name: Name for MLflow run (default: None)

    Returns:
        Tuple of (model, metrics_dict)
    """
    # Import ensemble if needed
    if use_ensemble or model_type in ["voting", "stacking"]:
        from .ensemble_models import create_ensemble

    # Import optimization/tracking if needed
    mlflow_tracker = None
    if track_with_mlflow:
        from .mlflow_integration import MLflowTracker

        mlflow_tracker = MLflowTracker()
        mlflow_tracker.start_run(run_name=run_name)

    # Prepare features and target
    available_features = [f for f in features if f in data.columns]

    if len(available_features) == 0:
        raise ValueError(f"No features found in data. Expected: {features[:5]}...")

    X = data[available_features]
    y = data["Outperform"]

    if y.nunique() < 2:
        raise ValueError("Target `y` must contain at least two classes.")

    # Feature selection
    selected_features = available_features
    if use_feature_selection and USE_ALL_FEATURES and len(available_features) > n_features:
        logging.info(
            f"Applying feature selection: {len(available_features)} → {n_features} features"
        )
        selected_features = select_best_features(X, y, k=n_features)
        X = X[selected_features]
        logging.info(f"Selected features: {selected_features[:10]}...")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Hyperparameter optimization
    optimized_params = {}
    if optimize_hyperparams and model_type not in ["voting", "stacking"]:
        from .hyperparameter_tuning import HyperparameterTuner

        logging.info(f"Starting hyperparameter optimization for {model_type} ({n_trials} trials)")

        # Map model_type to optimization name
        optim_type_map = {
            "rf": "random_forest",
            "xgb": "xgboost",
            "gb": "gradient_boosting",
            "lgbm": "lightgbm",
        }

        if model_type in optim_type_map:
            tuner = HyperparameterTuner(n_trials=n_trials, cv_folds=5, n_jobs=-1)
            optimized_params = tuner.optimize_model(
                optim_type_map[model_type], X_train, y_train, show_progress=True
            )
            logging.info(f"✅ Optimization complete. Best params: {optimized_params}")
        else:
            logging.warning(f"Hyperparameter optimization not supported for {model_type}")

    # Model selection
    if model_type == "voting":
        logging.info("Creating voting ensemble (XGB + RF + GB + LGBM)")
        model = create_ensemble("voting", voting="soft")
    elif model_type == "stacking":
        logging.info("Creating stacking ensemble with meta-learner")
        model = create_ensemble("stacking", cv=5)
    elif model_type == "xgb" and _USE_XGB:
        # Use optimized params if available
        params = (
            optimized_params
            if optimized_params
            else {
                "n_estimators": 200,
                "max_depth": 4,
                "learning_rate": 0.05,
                "subsample": 0.9,
                "random_state": 42,
            }
        )
        params.update({"eval_metric": "logloss", "use_label_encoder": False})
        model = XGBClassifier(**params)
    else:
        # RandomForest with optimized params if available
        params = (
            optimized_params
            if optimized_params
            else {
                "n_estimators": 200,
                "random_state": 42,
            }
        )
        model = RandomForestClassifier(**params)

    # Train model
    logging.info(f"Training {model_type} model...")
    model.fit(X_train.values, y_train.values)

    # Save model (and selected features)
    if save_path:
        import joblib

        joblib.dump(model, save_path)

        # Save selected features list
        features_path = save_path.replace(".bin", "_features.txt")
        with open(features_path, "w") as f:
            f.write("\n".join(selected_features))
        logging.info(f"Saved model to {save_path} with {len(selected_features)} features")

    # Evaluate
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    preds = model.predict(X_test.values)
    proba = model.predict_proba(X_test.values)[:, 1] if hasattr(model, "predict_proba") else None
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

    # MLflow tracking
    if track_with_mlflow and mlflow_tracker:
        try:
            # Log parameters
            params_to_log = {
                "model_type": model_type,
                "n_features": len(selected_features),
                "use_feature_selection": use_feature_selection,
                "use_ensemble": use_ensemble,
                "optimize_hyperparams": optimize_hyperparams,
            }
            if optimized_params:
                params_to_log.update({f"hp_{k}": v for k, v in optimized_params.items()})

            mlflow_tracker.log_params(params_to_log)

            # Log metrics
            mlflow_tracker.log_metrics(metrics)

            # Log dataset stats
            mlflow_tracker.log_dataset_stats(X_train, y_train, prefix="train")
            mlflow_tracker.log_dataset_stats(X_test, y_test, prefix="test")

            # Log model
            if save_path:
                mlflow_tracker.log_model(model, artifact_path="model")

            # Log feature importance
            if hasattr(model, "feature_importances_"):
                mlflow_tracker.log_feature_importance(selected_features, model.feature_importances_)

            # Log confusion matrix
            mlflow_tracker.log_confusion_matrix(y_test, preds, labels=["Down", "Up"])

            mlflow_tracker.end_run(status="FINISHED")
            logging.info("✅ MLflow tracking complete")

        except Exception as e:
            logging.warning(f"MLflow tracking failed: {e}")
            if mlflow_tracker:
                mlflow_tracker.end_run(status="FAILED")

    # Legacy MLFlow tracking (deprecated)
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
            latest = yf.download(t, period=args.rank_period, auto_adjust=False)["Adj Close"]
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
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args()
    main(args)
