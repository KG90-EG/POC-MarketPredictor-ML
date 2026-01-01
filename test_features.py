#!/usr/bin/env python3
"""
Test script for Week 2: Feature Expansion

Tests the new 40+ feature engineering system and compares performance
against the legacy 9-feature baseline.
"""

import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.trading_engine.feature_engineering import get_feature_names
from src.trading_engine.trading import build_dataset, train_model, USE_ALL_FEATURES

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_feature_count():
    """Test that we have 40+ features."""
    features = get_feature_names()
    print(f"\n📊 Feature Count Test")
    print(f"=" * 60)
    print(f"Total Features: {len(features)}")
    print(f"Expected: 40+")
    print(f"Status: {'✅ PASS' if len(features) >= 40 else '❌ FAIL'}")
    
    print(f"\n📋 Feature Categories:")
    print(f"  • Original Technical (9): SMA50, SMA200, RSI, ...")
    print(f"  • Advanced Technical (11): ATR, ADX, Stochastic, ...")
    print(f"  • Fundamentals (10): P/E, ROE, Debt/Equity, ...")
    print(f"  • Sentiment (5): Analyst Ratings, Ownership, ...")
    print(f"  • Macro (5): VIX, Treasury Yield, USD Index, ...")
    
    return len(features) >= 40


def test_feature_engineering():
    """Test feature engineering on sample data."""
    print(f"\n⚙️  Feature Engineering Test")
    print(f"=" * 60)
    
    tickers = ["AAPL", "MSFT", "GOOGL"]
    print(f"Testing with tickers: {tickers}")
    
    try:
        # Build dataset with advanced features
        print("\n🔄 Building dataset with 40+ features...")
        data = build_dataset(tickers, period="1y")
        
        print(f"✅ Dataset built: {len(data)} samples")
        print(f"✅ Columns: {data.shape[1]}")
        
        # Check if advanced features are present
        features = get_feature_names()
        present_features = [f for f in features if f in data.columns]
        
        print(f"\n📈 Features Present: {len(present_features)}/{len(features)}")
        
        # Show sample features
        sample_features = present_features[:15]
        print(f"\nSample features:")
        for i, feat in enumerate(sample_features, 1):
            value = data[feat].iloc[-1] if feat in data.columns else "N/A"
            print(f"  {i:2d}. {feat:25s} = {value}")
        
        return len(present_features) >= 30  # At least 30 features should be present
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_training():
    """Test model training with feature selection."""
    print(f"\n🤖 Model Training Test")
    print(f"=" * 60)
    
    tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "META"]
    print(f"Training with tickers: {tickers}")
    
    try:
        # Build dataset
        print("\n🔄 Building training dataset...")
        data = build_dataset(tickers, period="2y")
        print(f"✅ Dataset: {len(data)} samples")
        
        # Train with feature selection (40+ → 30 best features)
        print(f"\n🧠 Training model with feature selection...")
        print(f"  Input: {len(get_feature_names())} features")
        print(f"  Feature selection: → 30 best features")
        
        model, metrics = train_model(
            data, 
            model_type="xgb",
            use_feature_selection=True,
            n_features=30
        )
        
        print(f"\n📊 Model Performance:")
        print(f"  F1 Score:  {metrics['f1']:.3f}")
        print(f"  Accuracy:  {metrics['accuracy']:.3f}")
        print(f"  Precision: {metrics['precision']:.3f}")
        print(f"  Recall:    {metrics['recall']:.3f}")
        print(f"  ROC AUC:   {metrics.get('roc_auc', 0):.3f}")
        print(f"  CV Mean:   {metrics['cv_mean']:.3f} ± {metrics['cv_std']:.3f}")
        
        # Success if F1 > 0.65
        success = metrics['f1'] > 0.65
        print(f"\n{'✅ PASS' if success else '❌ FAIL'}: F1 Score {'>' if success else '<='} 0.65")
        
        return success
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_feature_comparison():
    """Compare 9 legacy features vs 40+ new features."""
    print(f"\n🔬 Feature Comparison Test")
    print(f"=" * 60)
    print(f"Comparing 9 legacy features vs 40+ advanced features")
    
    tickers = ["AAPL", "MSFT", "NVDA"]
    
    try:
        # Test 1: Legacy 9 features
        print(f"\n📉 Test 1: Legacy 9 Features")
        print(f"-" * 60)
        
        import src.trading_engine.trading as trading_module
        original_flag = trading_module.USE_ALL_FEATURES
        trading_module.USE_ALL_FEATURES = False
        
        data_legacy = build_dataset(tickers, period="1y")
        print(f"  Samples: {len(data_legacy)}")
        print(f"  Features: {len([c for c in data_legacy.columns if c in trading_module.features_legacy])}")
        
        # Test 2: Advanced 40+ features
        print(f"\n📈 Test 2: Advanced 40+ Features")
        print(f"-" * 60)
        
        trading_module.USE_ALL_FEATURES = True
        data_advanced = build_dataset(tickers, period="1y")
        print(f"  Samples: {len(data_advanced)}")
        
        features = get_feature_names()
        present = [f for f in features if f in data_advanced.columns]
        print(f"  Features: {len(present)}")
        
        # Restore original
        trading_module.USE_ALL_FEATURES = original_flag
        
        print(f"\n✅ Comparison successful!")
        print(f"  Legacy:   9 features")
        print(f"  Advanced: {len(present)} features")
        print(f"  Increase: +{len(present) - 9} features ({((len(present) - 9) / 9 * 100):.0f}%)")
        
        return len(present) > 30
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  Week 2: Feature Expansion - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Feature Count", test_feature_count),
        ("Feature Engineering", test_feature_engineering),
        ("Model Training", test_model_training),
        ("Feature Comparison", test_feature_comparison),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {name}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    
    print("\n" + "=" * 60)
    print(f"Results: {passed_count}/{total} tests passed ({passed_count/total*100:.0f}%)")
    print("=" * 60)
    
    return 0 if passed_count == total else 1


if __name__ == "__main__":
    sys.exit(main())
