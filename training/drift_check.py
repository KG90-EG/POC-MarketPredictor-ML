import argparse
import numpy as np
from market_predictor.trading import load_data
from scipy.stats import ks_2samp


def compute_baseline(tickers, period="1y"):
    arrs = []
    for t in tickers:
        df = load_data(t, period=period)
        if df is None or df.empty:
            continue
        arrs.append(df["Adj Close"].values)
    if not arrs:
        raise RuntimeError("No data")
    return np.concatenate(arrs)


def check_drift(baseline, current, threshold=0.05):
    stat, p = ks_2samp(baseline, current)
    # If p < threshold, the distributions are different => drift
    return p < threshold, stat, p


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", default="AAPL,MSFT,NVDA")
    parser.add_argument("--period", default="30d")
    parser.add_argument("--baseline-period", default="1y")
    parser.add_argument("--threshold", type=float, default=0.05)
    args = parser.parse_args()
    tickers = [t.strip().upper() for t in args.tickers.split(",")]
    baseline = compute_baseline(tickers, period=args.baseline_period)
    # Current period: compute aggregated adj close
    curr = compute_baseline(tickers, period=args.period)
    drift, stat, p = check_drift(baseline, curr, threshold=args.threshold)
    print("drift", drift, "stat", stat, "p", p)
    if drift:
        print("Drift detected")
        exit(2)
    else:
        print("No drift")
        exit(0)


if __name__ == "__main__":
    main()
