"""Trainer script that can be used by CI/CD or a scheduled job to retrain and save models."""

import os
from datetime import datetime
from trading_fun.trading import build_dataset, train_model
import mlflow

try:
    import boto3  # optional
except ImportError:  # pragma: no cover
    boto3 = None

# Setup mlflow tracking if env var set
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "file:./mlruns")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


def main():
    tickers = ["AAPL", "MSFT", "NVDA"]
    print(f"Building dataset for {tickers}...")
    try:
        # Use 2y period to have enough data after dropna (SMA200 needs 200 days + 90 days look-ahead)
        data = build_dataset(tickers, period="2y")
        if data.empty:
            print("ERROR: Dataset is empty, cannot train model")
            return
        print(f"Dataset shape: {data.shape}")
    except Exception as e:
        print(f"ERROR: Failed to build dataset: {e}")
        return
    
    model_path = os.path.abspath(
        os.path.join(
            "models", f'model_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.bin'
        )
    )
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    # Use mlflow to track the training run
    try:
        with mlflow.start_run():
            model, metrics = train_model(data, model_type="rf", save_path=model_path)
            mlflow.log_param("tickers", ",".join(tickers))
            for k, v in metrics.items():
                if v is not None:
                    mlflow.log_metric(k, v)
            mlflow.sklearn.log_model(model, "model")
            print("Model saved to", model_path, "metrics=", metrics)
    except ValueError as e:
        print(f"ERROR: Training failed - {e}")
        print("This may be due to insufficient data or all same class labels")
        return
    except Exception as e:
        print(f"ERROR: Unexpected training error - {e}")
        return

    # Optional S3 upload
    bucket = os.environ.get("S3_BUCKET")
    if bucket and boto3:
        try:
            s3 = boto3.client("s3")
            key = f"models/{os.path.basename(model_path)}"
            s3.upload_file(model_path, bucket, key)
            print(f"Uploaded model to s3://{bucket}/{key}")
        except Exception as e:  # pragma: no cover
            print("S3 upload failed:", e)
    elif bucket and not boto3:
        print("boto3 not installed; skipping S3 upload")


if __name__ == "__main__":
    main()
