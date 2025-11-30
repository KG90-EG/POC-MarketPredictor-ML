import argparse
import joblib
import os
from trading_fun.trading import build_dataset
from sklearn.metrics import accuracy_score
try:
    import boto3  # optional
except ImportError:  # pragma: no cover
    boto3 = None

def evaluate_model(model_path, tickers, period='1y'):
    model = joblib.load(model_path)
    data = build_dataset(tickers, period=period)
    X = data[['SMA50', 'SMA200', 'RSI', 'Volatility']]
    y = data['Outperform']
    preds = model.predict(X.values)
    acc = accuracy_score(y.values, preds)
    return acc

def promote_if_better(new_model, prod_model, tickers):
    new_acc = evaluate_model(new_model, tickers)
    prod_acc = evaluate_model(prod_model, tickers) if os.path.exists(prod_model) else -1
    print(f'New model acc: {new_acc:.4f}; Prod acc: {prod_acc:.4f}')
    if new_acc > prod_acc:
        print('Promoting model...')
        os.makedirs(os.path.dirname(prod_model) or '.', exist_ok=True)
        import shutil
        shutil.copyfile(new_model, prod_model)
        # After promotion, save latest baseline data for drift detection
        try:
            import numpy as np
            data = build_dataset(tickers, period='1y')
            arr = np.concatenate([d['Adj Close'].values for _, d in data.groupby('Ticker')])
            os.makedirs('models', exist_ok=True)
            np.save('models/baseline.npy', arr)
        except Exception:  # pragma: no cover
            pass
        # Optional S3 upload of promoted model
        bucket = os.environ.get('S3_BUCKET')
        if bucket and boto3:
            try:
                s3 = boto3.client('s3')
                key = f"models/{os.path.basename(prod_model)}"
                s3.upload_file(prod_model, bucket, key)
                print(f'Uploaded promoted model to s3://{bucket}/{key}')
            except Exception as e:  # pragma: no cover
                print('S3 upload failed:', e)
        elif bucket and not boto3:
            print('boto3 not installed; skipping S3 upload')
        print('Promoted new model')
        return True, new_acc, prod_acc
    return False, new_acc, prod_acc

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--new-model', required=True)
    parser.add_argument('--prod-model', default='models/prod_model.bin')
    parser.add_argument('--tickers', default='AAPL,MSFT,NVDA')
    parser.add_argument('--period', default='1y')
    args = parser.parse_args()
    tickers = [t.strip().upper() for t in args.tickers.split(',')]
    promoted, new_acc, prod_acc = promote_if_better(args.new_model, args.prod_model, tickers)
    if promoted:
        print('Promoted successfully')
    else:
        print('No promotion done')

if __name__ == '__main__':
    main()
