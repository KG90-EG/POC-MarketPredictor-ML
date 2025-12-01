"""Small online learning prototype using `river` to simulate streaming updates."""

try:
    from river.linear_model import LogisticRegression
    from river.preprocessing import StandardScaler
    from river.compose import ColumnTransformer
except Exception:
    LogisticRegression = None
    StandardScaler = None
    ColumnTransformer = None

from trading_fun.trading import build_dataset
import numpy as np


def run_online_training(tickers=["AAPL", "MSFT", "NVDA"], n_iter=1000):
    if LogisticRegression is None:
        raise RuntimeError("river not installed; install `river` to run online trainer")
    data = build_dataset(tickers, period="1y")
    X = data[["SMA50", "SMA200", "RSI", "Volatility"]]
    y = data["Outperform"]
    # Prepare a simple preprocessor and classifier
    model = LogisticRegression()
    # Online training loop
    for xi, yi in zip(X.values, y.values):
        xdict = {f"feat_{i}": float(xi[i]) for i in range(len(xi))}
        model.learn_one(xdict, int(yi))
    # Return model for demonstration
    return model


if __name__ == "__main__":
    try:
        model = run_online_training()
        print("Online training finished, model:", model)
    except RuntimeError as e:
        print("Skipping online trainer:", e)
