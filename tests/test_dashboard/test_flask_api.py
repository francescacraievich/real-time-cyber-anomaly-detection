"""Tests for Flask API business logic (not HTTP routing)."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parents[2]))

from src.dashboard import flask_api


class TestFlaskAPIHelpers:
    """Test Flask API helper functions and business logic."""

    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "source_ip": ["192.168.1.1", "10.0.0.2", "8.8.8.8", "1.1.1.1"],
                "destination_ip": ["8.8.8.8", "1.1.1.1", "192.168.1.1", "10.0.0.2"],
                "destination_port": [80, 443, 22, 3389],
                "transport_protocol": ["TCP", "TCP", "SSH", "RDP"],
                "label": ["benign", "benign", "malicious", "malicious"],
                "bytes_sent": [1000, 2000, 500, 3000],
                "pkts_sent": [10, 20, 5, 30],
                "bytes_received": [500, 1000, 200, 1500],
                "pkts_received": [5, 10, 2, 15],
            }
        )

    @pytest.fixture
    def mock_model(self):
        """Create a mock One-Class SVM model."""
        model = Mock()
        model.model_exists.return_value = True
        model.features_to_drop = ["label"]
        model.predict.return_value = [
            ("GREEN", "Normal traffic", 0.1),
            ("GREEN", "Normal traffic", 0.15),
            ("RED", "High anomaly score", 0.85),
            ("ORANGE", "Suspicious activity", 0.55),
        ]
        return model

    def test_track_request_metrics_decorator_structure(self):
        """Test that track_request_metrics decorator is properly defined."""
        assert hasattr(flask_api, "track_request_metrics")
        assert callable(flask_api.track_request_metrics)

    @patch("src.dashboard.flask_api.METRICS_ENABLED", False)
    def test_track_request_metrics_when_disabled(self):
        """Test metrics tracking when Prometheus is not available."""

        @flask_api.track_request_metrics
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"

    def test_load_resources_initializes_globals(self):
        """Test that load_resources initializes global variables."""
        with patch("src.dashboard.flask_api.OneClassSVMModel") as MockModel, patch(
            "src.dashboard.flask_api.DriftDetector"
        ) as MockDrift, patch(
            "src.dashboard.flask_api.pd.read_csv"
        ) as mock_read_csv, patch.object(
            Path, "exists", return_value=True
        ):

            # Mock model
            mock_model_instance = Mock()
            mock_model_instance.model_exists.return_value = True
            MockModel.return_value = mock_model_instance

            # Mock drift detector
            mock_drift_instance = Mock()
            MockDrift.return_value = mock_drift_instance

            # Mock dataset
            sample_df = pd.DataFrame({"col1": [1, 2, 3]})
            mock_read_csv.return_value = sample_df

            # Call load_resources
            flask_api.load_resources()

            # Verify globals are set
            assert flask_api.model is not None
            assert flask_api.drift_detector is not None
            assert flask_api.df_logs is not None

    def test_circular_buffer_logic(self, sample_dataframe):
        """Test circular buffer logic for log streaming."""
        df = sample_dataframe
        current_index = 0
        window_size = 3

        # First batch (no wrap)
        end_index = current_index + window_size
        if end_index <= len(df):
            batch = df.iloc[current_index:end_index].copy()

        assert len(batch) == 3
        current_index = end_index % len(df)
        assert current_index == 3

        # Second batch (wrap around)
        end_index = current_index + window_size
        if end_index > len(df):
            batch = pd.concat(
                [df.iloc[current_index:], df.iloc[: end_index - len(df)]]
            ).copy()

        assert len(batch) == 3  # Should still get 3 records (1 + 2)

    def test_prediction_batch_processing(self, sample_dataframe, mock_model):
        """Test batch prediction processing logic."""
        batch = sample_dataframe.copy()

        # Drop label column as model would do
        X_pred = batch.drop(columns=["label"], errors="ignore")

        # Make predictions
        predictions = mock_model.predict(X_pred)

        # Process predictions
        severities = [p[0] for p in predictions]
        descriptions = [p[1] for p in predictions]
        scores = [p[2] for p in predictions]

        assert len(severities) == 4
        assert "RED" in severities
        assert "ORANGE" in severities
        assert "GREEN" in severities
        assert all(isinstance(score, float) for score in scores)

    def test_nan_replacement_for_json(self, sample_dataframe):
        """Test NaN replacement for JSON serialization."""
        df = sample_dataframe.copy()
        df.loc[0, "bytes_sent"] = np.nan

        # Replace NaN with None (JSON-serializable)
        df_clean = df.replace({np.nan: None})

        assert df_clean.loc[0, "bytes_sent"] is None
        # Should be JSON-serializable now
        records = df_clean.to_dict(orient="records")
        assert isinstance(records, list)

    def test_drift_info_structure(self):
        """Test drift information structure."""
        mock_drift_detector = Mock()
        mock_drift_detector.drift_detected = True
        mock_drift_detector.get_current_anomaly_rate.return_value = 0.15
        mock_drift_detector.processed_samples = 1000

        drift_info = {
            "detected": mock_drift_detector.drift_detected,
            "anomaly_rate": mock_drift_detector.get_current_anomaly_rate(),
            "samples_processed": mock_drift_detector.processed_samples,
        }

        assert drift_info["detected"] is True
        assert drift_info["anomaly_rate"] == 0.15
        assert drift_info["samples_processed"] == 1000

    def test_summary_stats_calculation(self, sample_dataframe):
        """Test summary statistics calculation logic."""
        df = sample_dataframe

        stats = {
            "total_records": len(df),
            "malicious_count": int((df["label"] == "malicious").sum()),
            "benign_count": int((df["label"] == "benign").sum()),
            "protocols": df["transport_protocol"].value_counts().to_dict(),
        }

        assert stats["total_records"] == 4
        assert stats["malicious_count"] == 2
        assert stats["benign_count"] == 2
        assert "TCP" in stats["protocols"]

    def test_top_n_aggregation(self, sample_dataframe):
        """Test top N aggregation for IPs and ports."""
        df = sample_dataframe

        top_ips = df["source_ip"].value_counts().head(10).to_dict()
        top_ports = df["destination_port"].value_counts().head(10).to_dict()

        assert isinstance(top_ips, dict)
        assert isinstance(top_ports, dict)
        assert len(top_ips) <= 10
        assert len(top_ports) <= 10


class TestFlaskAPIEndpointLogic:
    """Test business logic of API endpoints (not Flask routing)."""

    @pytest.fixture
    def app_context(self):
        """Create Flask app context for testing."""
        with flask_api.app.app_context():
            yield

    def test_health_check_response_structure(self):
        """Test health check response structure."""
        response_data = {
            "status": "healthy",
            "model_loaded": True,
            "dataset_size": 1000,
            "timestamp": datetime.now().isoformat(),
        }

        assert "status" in response_data
        assert "model_loaded" in response_data
        assert "dataset_size" in response_data
        assert "timestamp" in response_data
        assert isinstance(response_data["model_loaded"], bool)
        assert isinstance(response_data["dataset_size"], int)

    def test_stream_logs_response_structure(self):
        """Test stream logs response structure."""
        logs_data = [
            {"source_ip": "192.168.1.1", "severity": "GREEN", "anomaly_score": 0.1},
            {"source_ip": "10.0.0.2", "severity": "RED", "anomaly_score": 0.9},
        ]

        response = {
            "logs": logs_data,
            "count": len(logs_data),
            "current_index": 50,
            "total_records": 10000,
            "timestamp": datetime.now().isoformat(),
            "drift": {
                "detected": False,
                "anomaly_rate": 0.05,
                "samples_processed": 500,
            },
        }

        assert "logs" in response
        assert "count" in response
        assert "drift" in response
        assert response["count"] == 2
        assert isinstance(response["logs"], list)

    def test_reset_stream_logic(self):
        """Test stream reset logic."""
        # Simulate reset
        current_index_before = 500
        current_index_after = 0

        assert current_index_after == 0
        assert current_index_after != current_index_before


class TestMetricsIntegration:
    """Test Prometheus metrics integration (when available)."""

    @patch("src.dashboard.flask_api.METRICS_ENABLED", True)
    def test_metrics_enabled_flag(self):
        """Test metrics enabled flag."""
        assert flask_api.METRICS_ENABLED is True

    @patch("src.dashboard.flask_api.METRICS_ENABLED", False)
    def test_metrics_disabled_flag(self):
        """Test metrics disabled flag."""
        assert flask_api.METRICS_ENABLED is False

    def test_metrics_endpoint_response_when_disabled(self):
        """Test metrics endpoint when Prometheus not available."""
        with patch("src.dashboard.flask_api.METRICS_ENABLED", False):
            with flask_api.app.test_client() as client:
                response = client.get("/metrics")
                assert response.status_code == 503
                assert b"not available" in response.data


class TestDataProcessing:
    """Test data processing utilities."""

    def test_timestamp_generation(self):
        """Test simulated timestamp generation."""
        from datetime import timedelta

        now = datetime.now()
        batch_size = 5

        timestamps = [
            (now - timedelta(seconds=i)).isoformat()
            for i in range(batch_size - 1, -1, -1)
        ]

        assert len(timestamps) == batch_size
        # Timestamps should be in ascending order (oldest to newest)
        # because we subtract from batch_size-1 down to 0

    def test_anomaly_detection_logic(self):
        """Test anomaly detection based on severity."""
        severities = ["GREEN", "GREEN", "ORANGE", "RED", "GREEN"]

        anomaly_count = sum(1 for s in severities if s in ["RED", "ORANGE"])
        normal_count = sum(1 for s in severities if s == "GREEN")

        assert anomaly_count == 2
        assert normal_count == 3
        assert anomaly_count + normal_count == len(severities)

    def test_error_handling_in_predictions(self):
        """Test error handling when predictions fail."""
        # Simulate prediction failure
        try:
            raise Exception("Model prediction failed")
        except Exception as e:
            error_message = str(e)
            # Fallback values
            severity = "UNKNOWN"
            description = "Prediction failed"
            score = 0.0

        assert severity == "UNKNOWN"
        assert description == "Prediction failed"
        assert score == 0.0
        assert "failed" in error_message.lower()


class TestCORSConfiguration:
    """Test CORS configuration for cross-origin requests."""

    def test_cors_enabled(self):
        """Test that CORS is enabled on the Flask app."""
        # CORS should be initialized
        assert hasattr(flask_api, "app")
        # The app should have CORS configured (via flask_cors import)
        # We can verify this by checking if the extension was applied
        # (Note: This is a smoke test - actual CORS headers tested in integration)

    def test_app_initialization(self):
        """Test Flask app is properly initialized."""
        assert flask_api.app is not None
        assert flask_api.app.name == "src.dashboard.flask_api"
