import argparse
import joblib
import os
from trading_fun.trading import build_dataset
from sklearn.metrics import accuracy_score

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
                    from trading_fun.trading import build_dataset
                    import numpy as np
                    tickers_list = tickers
                    data = build_dataset(tickers_list, period='1y')
                    arr = np.concatenate([d['Adj Close'].values for _, d in data.groupby('Ticker')])
                    np.save('models/baseline.npy', arr)
                except Exception:
                    pass
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
