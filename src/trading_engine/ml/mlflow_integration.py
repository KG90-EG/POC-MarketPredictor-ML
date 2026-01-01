"""
MLflow Integration for Experiment Tracking and Model Registry.

Week 4 Implementation - Track all training runs, parameters, and metrics.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow.tracking import MlflowClient

logger = logging.getLogger(__name__)


class MLflowTracker:
    """
    MLflow experiment tracking and model registry integration.

    Tracks:
    - Training parameters
    - Performance metrics
    - Model artifacts
    - Feature importance
    - Training data statistics
    """

    def __init__(
        self,
        experiment_name: str = "trading_model_experiments",
        tracking_uri: Optional[str] = None,
        artifact_location: Optional[str] = None,
    ):
        """
        Initialize MLflow tracker.

        Args:
            experiment_name: Name of MLflow experiment
            tracking_uri: MLflow tracking server URI (None = local file://mlruns)
            artifact_location: Where to store artifacts (None = default)
        """
        self.experiment_name = experiment_name

        # Set tracking URI
        if tracking_uri is None:
            # Default to local mlruns directory
            mlruns_path = Path("mlruns").absolute()
            tracking_uri = f"file://{mlruns_path}"

        mlflow.set_tracking_uri(tracking_uri)
        logger.info(f"MLflow tracking URI: {tracking_uri}")

        # Create or get experiment
        try:
            self.experiment_id = mlflow.create_experiment(experiment_name, artifact_location=artifact_location)
            logger.info(f"Created new experiment: {experiment_name}")
        except Exception:
            # Experiment already exists
            experiment = mlflow.get_experiment_by_name(experiment_name)
            self.experiment_id = experiment.experiment_id
            logger.info(f"Using existing experiment: {experiment_name}")

        mlflow.set_experiment(experiment_name)

        # MLflow client for advanced operations
        self.client = MlflowClient()

        # Current run ID
        self.current_run_id: Optional[str] = None

    def start_run(self, run_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> str:
        """
        Start a new MLflow run.

        Args:
            run_name: Name for this run
            tags: Dictionary of tags

        Returns:
            Run ID
        """
        run = mlflow.start_run(run_name=run_name, tags=tags)
        self.current_run_id = run.info.run_id
        logger.info(f"Started MLflow run: {self.current_run_id}")

        return self.current_run_id

    def log_params(self, params: Dict[str, Any]) -> None:
        """
        Log parameters to current run.

        Args:
            params: Dictionary of parameters
        """
        if not mlflow.active_run():
            raise RuntimeError("No active MLflow run. Call start_run() first.")

        mlflow.log_params(params)
        logger.debug(f"Logged {len(params)} parameters")

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        """
        Log metrics to current run.

        Args:
            metrics: Dictionary of metrics
            step: Optional step number for time series metrics
        """
        if not mlflow.active_run():
            raise RuntimeError("No active MLflow run. Call start_run() first.")

        mlflow.log_metrics(metrics, step=step)
        logger.debug(f"Logged {len(metrics)} metrics")

    def log_model(
        self,
        model,
        artifact_path: str = "model",
        registered_model_name: Optional[str] = None,
        signature=None,
        input_example=None,
    ) -> None:
        """
        Log model to MLflow.

        Args:
            model: Trained model
            artifact_path: Path within run's artifact directory
            registered_model_name: Register model to Model Registry
            signature: Model signature (input/output schema)
            input_example: Example input data
        """
        if not mlflow.active_run():
            raise RuntimeError("No active MLflow run. Call start_run() first.")

        mlflow.sklearn.log_model(
            model,
            artifact_path=artifact_path,
            registered_model_name=registered_model_name,
            signature=signature,
            input_example=input_example,
        )

        logger.info(f"Model logged to artifact path: {artifact_path}")

        if registered_model_name:
            logger.info(f"Model registered as: {registered_model_name}")

    def log_feature_importance(self, feature_names: List[str], importances: np.ndarray) -> None:
        """
        Log feature importance as artifact.

        Args:
            feature_names: Names of features
            importances: Importance values
        """
        if not mlflow.active_run():
            raise RuntimeError("No active MLflow run. Call start_run() first.")

        # Create DataFrame
        importance_df = pd.DataFrame({"feature": feature_names, "importance": importances})
        importance_df = importance_df.sort_values("importance", ascending=False)

        # Save as artifact
        artifact_path = "feature_importance.csv"
        importance_df.to_csv(artifact_path, index=False)
        mlflow.log_artifact(artifact_path)

        # Clean up local file
        os.remove(artifact_path)

        logger.info("Feature importance logged")

    def log_confusion_matrix(self, y_true, y_pred, labels: Optional[List[str]] = None) -> None:
        """
        Log confusion matrix as artifact.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            labels: Label names
        """
        if not mlflow.active_run():
            raise RuntimeError("No active MLflow run. Call start_run() first.")

        import matplotlib.pyplot as plt
        import seaborn as sns
        from sklearn.metrics import confusion_matrix

        cm = confusion_matrix(y_true, y_pred)

        # Plot
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
        plt.ylabel("True Label")
        plt.xlabel("Predicted Label")
        plt.title("Confusion Matrix")

        # Save
        artifact_path = "confusion_matrix.png"
        plt.savefig(artifact_path, bbox_inches="tight", dpi=150)
        plt.close()

        mlflow.log_artifact(artifact_path)
        os.remove(artifact_path)

        logger.info("Confusion matrix logged")

    def log_dataset_stats(self, X, y, prefix: str = "train") -> None:
        """
        Log dataset statistics.

        Args:
            X: Features
            y: Labels
            prefix: Prefix for metric names ('train', 'test', etc.)
        """
        if not mlflow.active_run():
            raise RuntimeError("No active MLflow run. Call start_run() first.")

        stats = {
            f"{prefix}_samples": len(X),
            f"{prefix}_features": X.shape[1] if hasattr(X, "shape") else len(X[0]),
            f"{prefix}_class_0": int(np.sum(y == 0)),
            f"{prefix}_class_1": int(np.sum(y == 1)),
            f"{prefix}_class_balance": float(np.mean(y)),
        }

        mlflow.log_metrics(stats)
        logger.debug(f"Logged {prefix} dataset statistics")

    def end_run(self, status: str = "FINISHED") -> None:
        """
        End current MLflow run.

        Args:
            status: Run status ('FINISHED', 'FAILED', 'KILLED')
        """
        if mlflow.active_run():
            mlflow.end_run(status=status)
            logger.info(f"Ended MLflow run with status: {status}")
            self.current_run_id = None

    def get_best_run(self, metric: str = "f1_score", ascending: bool = False) -> Optional[mlflow.entities.Run]:
        """
        Get best run from experiment based on metric.

        Args:
            metric: Metric to optimize
            ascending: True if lower is better

        Returns:
            Best run object or None
        """
        runs = mlflow.search_runs(
            experiment_ids=[self.experiment_id],
            order_by=[f"metrics.{metric} {'ASC' if ascending else 'DESC'}"],
            max_results=1,
        )

        if len(runs) == 0:
            logger.warning("No runs found in experiment")
            return None

        best_run_id = runs.iloc[0]["run_id"]
        best_run = self.client.get_run(best_run_id)

        logger.info(f"Best run: {best_run_id}, {metric}={runs.iloc[0][f'metrics.{metric}']:.4f}")

        return best_run

    def compare_runs(self, run_ids: List[str], metrics: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Compare multiple runs.

        Args:
            run_ids: List of run IDs to compare
            metrics: Metrics to include (None = all)

        Returns:
            DataFrame with comparison
        """
        runs_data = []

        for run_id in run_ids:
            run = self.client.get_run(run_id)

            run_info = {
                "run_id": run_id,
                "run_name": run.info.run_name,
                "start_time": run.info.start_time,
                "status": run.info.status,
            }

            # Add metrics
            if metrics:
                for metric in metrics:
                    run_info[metric] = run.data.metrics.get(metric, None)
            else:
                run_info.update(run.data.metrics)

            runs_data.append(run_info)

        comparison_df = pd.DataFrame(runs_data)
        logger.info(f"Compared {len(run_ids)} runs")

        return comparison_df

    def load_model(self, run_id: str, artifact_path: str = "model"):
        """
        Load model from MLflow run.

        Args:
            run_id: Run ID
            artifact_path: Artifact path within run

        Returns:
            Loaded model
        """
        model_uri = f"runs:/{run_id}/{artifact_path}"
        model = mlflow.sklearn.load_model(model_uri)

        logger.info(f"Loaded model from run: {run_id}")

        return model

    def register_model(self, run_id: str, model_name: str, artifact_path: str = "model") -> str:
        """
        Register model to Model Registry.

        Args:
            run_id: Run ID containing the model
            model_name: Name for registered model
            artifact_path: Artifact path within run

        Returns:
            Model version
        """
        model_uri = f"runs:/{run_id}/{artifact_path}"

        model_version = mlflow.register_model(model_uri, model_name)

        logger.info(f"Registered model: {model_name}, version: {model_version.version}")

        return model_version.version

    def transition_model_stage(self, model_name: str, version: str, stage: str) -> None:
        """
        Transition model to different stage in Model Registry.

        Args:
            model_name: Name of registered model
            version: Model version
            stage: Target stage ('Staging', 'Production', 'Archived')
        """
        self.client.transition_model_version_stage(name=model_name, version=version, stage=stage)

        logger.info(f"Transitioned {model_name} v{version} to {stage}")

    def get_production_model(self, model_name: str):
        """
        Load production model from Model Registry.

        Args:
            model_name: Name of registered model

        Returns:
            Production model
        """
        model_uri = f"models:/{model_name}/Production"
        model = mlflow.sklearn.load_model(model_uri)

        logger.info(f"Loaded production model: {model_name}")

        return model


def track_training_run(
    tracker: MLflowTracker,
    model,
    params: Dict[str, Any],
    metrics: Dict[str, float],
    X_train,
    y_train,
    X_test,
    y_test,
    run_name: Optional[str] = None,
    feature_names: Optional[List[str]] = None,
    register_model_name: Optional[str] = None,
) -> str:
    """
    Convenience function to track a complete training run.

    Args:
        tracker: MLflowTracker instance
        model: Trained model
        params: Training parameters
        metrics: Performance metrics
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        run_name: Name for run
        feature_names: Feature names for importance logging
        register_model_name: Register model to Model Registry

    Returns:
        Run ID
    """
    # Start run
    run_id = tracker.start_run(run_name=run_name)

    try:
        # Log parameters
        tracker.log_params(params)

        # Log metrics
        tracker.log_metrics(metrics)

        # Log dataset stats
        tracker.log_dataset_stats(X_train, y_train, prefix="train")
        tracker.log_dataset_stats(X_test, y_test, prefix="test")

        # Log model
        tracker.log_model(model, artifact_path="model", registered_model_name=register_model_name)

        # Log feature importance if available
        if feature_names and hasattr(model, "feature_importances_"):
            tracker.log_feature_importance(feature_names, model.feature_importances_)

        # Log confusion matrix
        y_pred = model.predict(X_test)
        tracker.log_confusion_matrix(y_test, y_pred, labels=["Down", "Up"])

        # End run successfully
        tracker.end_run(status="FINISHED")

        logger.info(f"✅ Training run tracked successfully: {run_id}")

    except Exception as e:
        logger.error(f"Error tracking run: {e}")
        tracker.end_run(status="FAILED")
        raise

    return run_id
