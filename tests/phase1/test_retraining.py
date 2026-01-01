#!/usr/bin/env python3
"""
Test script for the model retraining system.

Usage:
    python test_retraining.py              # Check status
    python test_retraining.py --trigger    # Trigger manual retrain
    python test_retraining.py --rollback   # Rollback to backup
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.trading_engine.ml.model_retraining import get_retraining_service


def main():
    parser = argparse.ArgumentParser(description="Test model retraining system")
    parser.add_argument("--trigger", action="store_true", help="Trigger manual retraining")
    parser.add_argument("--rollback", action="store_true", help="Rollback to backup model")
    parser.add_argument("--force", action="store_true", help="Force deployment (skip validation)")
    args = parser.parse_args()

    service = get_retraining_service()

    if args.trigger:
        print("🚀 Triggering manual retraining...")
        print("⏳ This may take 1-2 minutes...")
        success = service.retrain_model(force=args.force)
        if success:
            print("✅ Retraining completed successfully!")
        else:
            print("❌ Retraining failed or model didn't pass validation")
        return

    if args.rollback:
        print("🔄 Rolling back to backup model...")
        try:
            service.rollback_model()
            print("✅ Rollback successful!")
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
        return

    # Default: show status
    print("📊 Model Retraining System Status\n")
    status = service.get_status()

    print(f"Running: {'✅ Yes' if status['running'] else '❌ No'}")
    print(f"Next Retraining: {status['next_retraining']}")
    print()

    print("Current Model Performance:")
    metrics = status["current_metrics"]
    print(f"  F1 Score:  {metrics.get('f1_score', 0):.3f}")
    print(f"  Accuracy:  {metrics.get('accuracy', 0):.3f}")
    print(f"  Precision: {metrics.get('precision', 0):.3f}")
    print(f"  Recall:    {metrics.get('recall', 0):.3f}")
    print()

    print(f"Model Path:  {status['model_path']}")
    print(f"Backup Path: {status['backup_path']}")
    print()

    if status["scheduled_jobs"]:
        print("Scheduled Jobs:")
        for job in status["scheduled_jobs"]:
            print(f"  - {job['name']}: {job['next_run']}")
    else:
        print("⚠️ No scheduled jobs found (scheduler may not be running)")


if __name__ == "__main__":
    main()
