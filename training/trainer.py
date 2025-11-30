"""Trainer script that can be used by CI/CD or a scheduled job to retrain and save models."""
import os
import sys
from datetime import datetime
from trading_fun.trading import build_dataset, train_model
import mlflow
import os

# Setup mlflow tracking if env var set
MLFLOW_TRACKING_URI = os.environ.get('MLFLOW_TRACKING_URI', 'file:./mlruns')
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

def main():
    tickers = ['AAPL', 'MSFT', 'NVDA']
    data = build_dataset(tickers, period='1y')
    model_path = os.path.abspath(os.path.join('models', f'model_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.bin'))
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    # Use mlflow to track the training run
    with mlflow.start_run():
        model, metrics = train_model(data, model_type='rf', save_path=model_path)
        mlflow.log_param('tickers', ','.join(tickers))
        for k, v in metrics.items():
            if v is not None:
                mlflow.log_metric(k, v)
        mlflow.sklearn.log_model(model, 'model')
        print('Model saved to', model_path, 'metrics=', metrics)

if __name__ == '__main__':
    main()
