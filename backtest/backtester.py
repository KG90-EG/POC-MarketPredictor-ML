import pandas as pd
import numpy as np
from typing import Iterable


def simulate_strategy(
    df: pd.DataFrame,
    prob_col: str = "prob",
    price_col: str = "Adj Close",
    threshold: float = 0.5,
):
    """Simple long-only strategy: buy if prob >= threshold, hold for 90 days (or until end).
    Returns a DataFrame with positions and PnL.
    """
    df = df.copy()
    df["signal"] = (df[prob_col] >= threshold).astype(int)
    df["position"] = 0
    df["pnl"] = 0.0
    # naive approach: if signal -> buy one share and hold for 90 days
    for i in range(len(df)):
        if df["signal"].iat[i] == 1:
            buy_price = df[price_col].iat[i]
            sell_idx = min(i + 90, len(df) - 1)
            sell_price = df[price_col].iat[sell_idx]
            pnl = sell_price - buy_price
            df.at[df.index[i], "pnl"] = pnl
            df.at[df.index[i], "position"] = 1
    df["cum_pnl"] = df["pnl"].cumsum()
    return df


def evaluate_backtest(df: pd.DataFrame):
    # Compute simple metrics
    total_pnl = float(df["pnl"].sum())
    num_trades = int(df["position"].sum())
    ave_pnl = float(df["pnl"].mean()) if num_trades > 0 else 0.0
    max_dd = (df["cum_pnl"].cummax() - df["cum_pnl"]).max()
    return {
        "total_pnl": total_pnl,
        "num_trades": num_trades,
        "ave_pnl": ave_pnl,
        "max_drawdown": float(max_dd),
    }


def from_predictions(preds: Iterable, prices: Iterable, threshold: float = 0.5):
    df = pd.DataFrame({"prob": list(preds), "Adj Close": list(prices)})
    df = simulate_strategy(
        df, prob_col="prob", price_col="Adj Close", threshold=threshold
    )
    metrics = evaluate_backtest(df)
    return df, metrics


if __name__ == "__main__":
    # small example
    prices = np.linspace(10, 20, 500)
    probs = np.random.rand(500)
    df, metrics = from_predictions(probs, prices, threshold=0.9)
    print(metrics)
