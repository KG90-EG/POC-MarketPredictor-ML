"""Tests for online learning module."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.trading_engine.ml.online_learning import (
    OnlineLearner,
    create_online_ensemble,
    ensemble_predict,
)


class TestOnlineLearner:
    """Test OnlineLearner class."""

    @pytest.fixture
    def sample_data(self):
        """Generate sample binary classification data."""
        np.random.seed(42)
        n_samples = 200
        n_features = 10

        X = np.random.randn(n_samples, n_features)
        # Create separable classes
        y = (X[:, 0] + X[:, 1] > 0).astype(int)

        return X, y

    def test_sgd_learner_initialization(self):
        """Test SGD learner initialization."""
        learner = OnlineLearner(model_type="sgd", window_size=1000)

        assert learner.model_type == "sgd"
        assert learner.window_size == 1000
        assert not learner.is_fitted
        assert learner.n_updates == 0
        assert learner.total_samples == 0

    def test_partial_fit_updates_model(self, sample_data):
        """Test partial_fit updates model state."""
        X, y = sample_data
        learner = OnlineLearner(model_type="sgd")

        # First batch
        X_batch1 = X[:50]
        y_batch1 = y[:50]
        metrics = learner.partial_fit(X_batch1, y_batch1)

        assert learner.is_fitted
        assert metrics["status"] == "success"
        assert metrics["n_samples"] == 50
        assert learner.total_samples == 50
        assert learner.n_updates == 1

        # Second batch
        X_batch2 = X[50:100]
        y_batch2 = y[50:100]
        metrics = learner.partial_fit(X_batch2, y_batch2)

        assert learner.total_samples == 100
        assert learner.n_updates == 2

    def test_prediction_after_training(self, sample_data):
        """Test predictions work after training."""
        X, y = sample_data
        learner = OnlineLearner(model_type="sgd")

        # Train
        learner.partial_fit(X[:150], y[:150])

        # Predict
        X_test = X[150:]
        predictions = learner.predict(X_test)

        assert len(predictions) == len(X_test)
        assert set(predictions).issubset({0, 1})

    def test_predict_proba(self, sample_data):
        """Test probability predictions."""
        X, y = sample_data
        learner = OnlineLearner(model_type="sgd")

        learner.partial_fit(X[:150], y[:150])

        X_test = X[150:]
        probas = learner.predict_proba(X_test)

        assert probas.shape == (len(X_test), 2)
        assert np.allclose(probas.sum(axis=1), 1.0)  # Probabilities sum to 1

    def test_passive_aggressive_learner(self, sample_data):
        """Test PassiveAggressiveClassifier."""
        X, y = sample_data
        learner = OnlineLearner(model_type="passive_aggressive")

        metrics = learner.partial_fit(X[:100], y[:100])

        assert metrics["status"] == "success"
        assert learner.is_fitted

        predictions = learner.predict(X[100:])
        assert len(predictions) == 100

    def test_naive_bayes_learner(self, sample_data):
        """Test MultinomialNB learner."""
        X, y = sample_data
        learner = OnlineLearner(model_type="naive_bayes")

        # NB requires non-negative features
        metrics = learner.partial_fit(X[:100], y[:100])

        assert metrics["status"] == "success"
        predictions = learner.predict(X[100:])
        assert len(predictions) == 100

    def test_rolling_window_buffer(self, sample_data):
        """Test rolling window maintains size limit."""
        X, y = sample_data
        learner = OnlineLearner(model_type="sgd", window_size=50)

        # Add more samples than window size
        learner.partial_fit(X[:100], y[:100])

        assert len(learner.X_buffer) == 50
        assert len(learner.y_buffer) == 50

    def test_replay_buffer(self, sample_data):
        """Test buffer replay for preventing forgetting."""
        X, y = sample_data
        learner = OnlineLearner(model_type="sgd", window_size=100)

        # Initial training
        learner.partial_fit(X[:50], y[:50])
        initial_updates = learner.n_updates

        # Replay buffer
        metrics = learner.replay_buffer()

        assert metrics["status"] == "success"
        assert learner.n_updates == initial_updates + 1

    def test_save_and_load(self, sample_data):
        """Test saving and loading learner."""
        X, y = sample_data
        learner = OnlineLearner(model_type="sgd")
        learner.partial_fit(X[:100], y[:100])

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "learner.pkl"

            # Save
            learner.save(str(filepath))
            assert filepath.exists()

            # Load
            loaded_learner = OnlineLearner.load(str(filepath))

            assert loaded_learner.model_type == learner.model_type
            assert loaded_learner.is_fitted == learner.is_fitted
            assert loaded_learner.n_updates == learner.n_updates

            # Test predictions match
            X_test = X[100:]
            orig_pred = learner.predict(X_test)
            loaded_pred = loaded_learner.predict(X_test)
            assert np.array_equal(orig_pred, loaded_pred)

    def test_get_stats(self, sample_data):
        """Test get_stats returns correct info."""
        X, y = sample_data
        learner = OnlineLearner(model_type="sgd", window_size=200)
        learner.partial_fit(X[:100], y[:100])

        stats = learner.get_stats()

        assert stats["model_type"] == "sgd"
        assert stats["is_fitted"] is True
        assert stats["n_updates"] == 1
        assert stats["total_samples"] == 100
        assert stats["buffer_size"] == 100


class TestOnlineEnsemble:
    """Test online ensemble functions."""

    @pytest.fixture
    def sample_data(self):
        """Generate sample data."""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        return X, y

    def test_create_ensemble(self):
        """Test ensemble creation."""
        ensemble = create_online_ensemble(
            models=["sgd", "passive_aggressive"], window_size=1000
        )

        assert len(ensemble) == 2
        assert "sgd" in ensemble
        assert "passive_aggressive" in ensemble
        assert isinstance(ensemble["sgd"], OnlineLearner)

    def test_ensemble_voting_prediction(self, sample_data):
        """Test ensemble voting prediction."""
        X, y = sample_data
        ensemble = create_online_ensemble(models=["sgd", "passive_aggressive"])

        # Train all models
        for learner in ensemble.values():
            learner.partial_fit(X[:70], y[:70])

        # Predict with voting
        X_test = X[70:]
        predictions = ensemble_predict(ensemble, X_test, method="voting")

        assert len(predictions) == len(X_test)
        assert set(predictions).issubset({0, 1})

    def test_ensemble_average_proba_prediction(self, sample_data):
        """Test ensemble probability averaging."""
        X, y = sample_data
        ensemble = create_online_ensemble(models=["sgd", "passive_aggressive"])

        for learner in ensemble.values():
            learner.partial_fit(X[:70], y[:70])

        X_test = X[70:]
        predictions = ensemble_predict(ensemble, X_test, method="average_proba")

        assert len(predictions) == len(X_test)
        assert set(predictions).issubset({0, 1})
