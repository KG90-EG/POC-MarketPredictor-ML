import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

# ----------------------------------
# 1. Aktienliste definieren
# ----------------------------------
tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "V", "MA", "PG", "KO"]

# ----------------------------------
# 2. Daten laden
# ----------------------------------
def load_data(ticker):
    df = yf.download(ticker, period="3y")
    df["Returns_90d"] = df["Adj Close"].pct_change(90).shift(-90)

    # Label: outperform = 1, sonst 0
    df["Outperform"] = (df["Returns_90d"] > 0.05).astype(int)

    # Technische Features
    df["SMA50"] = df["Adj Close"].rolling(50).mean()
    df["SMA200"] = df["Adj Close"].rolling(200).mean()
    df["RSI"] = 100 - (100 / (1 + df["Adj Close"].pct_change().rolling(14).mean()))
    df["Volatility"] = df["Adj Close"].pct_change().rolling(30).std()

    df["Ticker"] = ticker
    return df.dropna()

# Build dataset
dfs = [load_data(t) for t in tickers]
data = pd.concat(dfs)

# Features & Label
features = ["SMA50", "SMA200", "RSI", "Volatility"]
X = data[features]
y = data["Outperform"]

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# ----------------------------------
# 3. AI-Modell (XGBoost)
# ----------------------------------
model = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
)
model.fit(X_train, y_train)

# ----------------------------------
# 4. Ranking erstellen
# ----------------------------------
ranking = {}

for t in tickers:
    latest = yf.download(t, period="200d")["Adj Close"]
    df = pd.DataFrame()
    df["SMA50"] = latest.rolling(50).mean()
    df["SMA200"] = latest.rolling(200).mean()
    df["RSI"] = 100 - (100 / (1 + latest.pct_change().rolling(14).mean()))
    df["Volatility"] = latest.pct_change().rolling(30).std()
    
    row = df.dropna().iloc[-1:]  # letzte Zeile
    prob = model.predict_proba(row)[0][1]

    ranking[t] = prob

# Sortieren
ranking = dict(sorted(ranking.items(), key=lambda x: x[1], reverse=True))

print("\n🔥 BUY-LIST — AI-Wahrscheinlichkeit der Outperformance:\n")
for k, v in ranking.items():
    print(f"{k}: {v:.2f}")