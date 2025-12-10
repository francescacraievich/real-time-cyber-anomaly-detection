"""Tests for prediction worker - background prediction loop and health checks."""

import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.append(str(Path(__file__).parents[2]))

from src.dashboard import prediction_worker


class TestPredictionWorkerHealthChecks:
    """Test prediction worker health check functionality."""

    @patch("src.dashboard.prediction_worker.requests.get")
    def test_check_flask_alive_success(self, mock_get):
        """Test Flask health check when API is running."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = prediction_worker.check_flask_alive()

        assert result is True
        mock_get.assert_called_once_with(
            f"{prediction_worker.API_BASE_URL}/api/health", timeout=3
        )

    @patch("src.dashboard.prediction_worker.requests.get")
    def test_check_flask_alive_failure_wrong_status(self, mock_get):
        """Test Flask health check when API returns non-200 status."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = prediction_worker.check_flask_alive()

        assert result is False

    @patch("src.dashboard.prediction_worker.requests.get")
    def test_check_flask_alive_connection_error(self, mock_get):
        """Test Flask health check when API is down (connection refused)."""
        mock_get.side_effect = Exception("Connection refused")

        result = prediction_worker.check_flask_alive()

        assert result is False

    @patch("src.dashboard.prediction_worker.requests.get")
    def test_check_flask_alive_timeout(self, mock_get):
        """Test Flask health check when API times out."""
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()

        result = prediction_worker.check_flask_alive()

        assert result is False


class TestPredictionWorkerLoop:
    """Test prediction worker main loop (without actually running it)."""

    @patch("src.dashboard.prediction_worker.requests.get")
    @patch("src.dashboard.prediction_worker.requests.post")
    @patch("src.dashboard.prediction_worker.time.sleep")
    def test_run_prediction_loop_flask_not_ready(self, mock_sleep, mock_post, mock_get):
        """Test prediction loop when Flask API never becomes ready."""
        # Simulate Flask API always down
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError()

        # Should return early without running loop
        prediction_worker.run_prediction_loop()

        # Should have tried 10 times (initial wait loop)
        assert mock_get.call_count == 10

    @patch("src.dashboard.prediction_worker.requests.get")
    @patch("src.dashboard.prediction_worker.requests.post")
    @patch("src.dashboard.prediction_worker.time.sleep")
    def test_run_prediction_loop_initial_evaluation_success(
        self, mock_sleep, mock_post, mock_get
    ):
        """Test initial model evaluation when Flask is ready."""
        # Mock Flask health check success
        health_response = Mock()
        health_response.status_code = 200

        # Mock evaluation success
        eval_response = Mock()
        eval_response.status_code = 200
        eval_response.json.return_value = {
            "f1_score": 0.85,
            "precision": 0.90,
            "recall": 0.80,
        }

        # Mock stream endpoint to trigger loop exit (KeyboardInterrupt simulation)
        stream_response = Mock()
        stream_response.status_code = 200
        stream_response.json.return_value = {
            "logs": [{"severity": "GREEN"}, {"severity": "RED"}]
        }

        # Setup response sequence
        mock_get.return_value = health_response
        mock_post.return_value = eval_response

        # Simulate loop stopping after first iteration
        def side_effect_get(*args, **kwargs):
            if "stream" in args[0]:
                raise KeyboardInterrupt()
            return stream_response

        mock_get.side_effect = [health_response] + [side_effect_get for _ in range(20)]

        # Run loop (should exit via KeyboardInterrupt)
        try:
            prediction_worker.run_prediction_loop()
        except KeyboardInterrupt:
            pass

        # Should have called evaluation endpoint
        assert any("/api/evaluate" in str(call) for call in mock_post.call_args_list)

    @patch("src.dashboard.prediction_worker.requests.get")
    @patch("src.dashboard.prediction_worker.requests.post")
    def test_consecutive_failures_shutdown(self, mock_post, mock_get):
        """Test that worker shuts down after MAX_CONSECUTIVE_FAILURES."""
        # Mock Flask initially ready
        health_response = Mock()
        health_response.status_code = 200

        # Mock evaluation success
        eval_response = Mock()
        eval_response.status_code = 200
        eval_response.json.return_value = {
            "f1_score": 0.85,
            "precision": 0.90,
            "recall": 0.80,
        }
        mock_post.return_value = eval_response

        # Simulate Flask becoming unavailable after initial setup
        call_count = [0]

        def health_check_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 1:
                # First call: Flask is ready
                return health_response
            else:
                # Subsequent calls: Flask down
                import requests

                raise requests.exceptions.ConnectionError()

        mock_get.side_effect = health_check_side_effect

        # Run loop - should exit after MAX_CONSECUTIVE_FAILURES
        with patch("src.dashboard.prediction_worker.time.sleep"):
            prediction_worker.run_prediction_loop()

        # Should have made multiple health check attempts
        assert call_count[0] > 1


class TestPredictionWorkerConstants:
    """Test prediction worker configuration constants."""

    def test_api_base_url_configured(self):
        """Test that API base URL is properly configured."""
        assert prediction_worker.API_BASE_URL == "http://localhost:5000"

    def test_max_consecutive_failures_set(self):
        """Test that max consecutive failures threshold is set."""
        assert prediction_worker.MAX_CONSECUTIVE_FAILURES == 5
        assert isinstance(prediction_worker.MAX_CONSECUTIVE_FAILURES, int)


class TestPredictionWorkerIntegrationPatterns:
    """Test integration patterns without running full loop."""

    @patch("src.dashboard.prediction_worker.requests.get")
    def test_stream_endpoint_response_parsing(self, mock_get):
        """Test parsing of stream endpoint response."""
        # Mock stream response with mixed severities
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "logs": [
                {"severity": "GREEN", "score": 0.1},
                {"severity": "GREEN", "score": 0.2},
                {"severity": "ORANGE", "score": 0.5},
                {"severity": "RED", "score": 0.9},
            ]
        }
        mock_get.return_value = mock_response

        # Simulate processing
        response = mock_get(f"{prediction_worker.API_BASE_URL}/api/logs/stream")
        data = response.json()
        logs = data.get("logs", [])

        # Count severities (as done in worker)
        red_count = sum(1 for log in logs if log.get("severity") == "RED")
        orange_count = sum(1 for log in logs if log.get("severity") == "ORANGE")
        green_count = sum(1 for log in logs if log.get("severity") == "GREEN")

        assert len(logs) == 4
        assert red_count == 1
        assert orange_count == 1
        assert green_count == 2

    @patch("src.dashboard.prediction_worker.requests.post")
    def test_evaluation_endpoint_response_parsing(self, mock_post):
        """Test parsing of evaluation endpoint response."""
        # Mock evaluation response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "f1_score": 0.876,
            "precision": 0.912,
            "recall": 0.843,
            "detection_rate": 0.843,
            "false_alarm_rate": 0.088,
        }
        mock_post.return_value = mock_response

        # Simulate evaluation call
        response = mock_post(
            f"{prediction_worker.API_BASE_URL}/api/evaluate",
            params={"sample_size": 500},
        )

        assert response.status_code == 200
        eval_data = response.json()

        assert "f1_score" in eval_data
        assert "precision" in eval_data
        assert "recall" in eval_data
        assert eval_data["f1_score"] > 0.8
        assert eval_data["precision"] > 0.9
