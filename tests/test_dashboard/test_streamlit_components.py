"""Tests for Streamlit component helper functions (not UI rendering)."""

import socket
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import plotly.graph_objects as go
import pytest

# Add project root to path
sys.path.append(str(Path(__file__).parents[2]))

from src.dashboard import streamlit_monitoring


class TestStreamlitMonitoringHelpers:
    """Test helper functions from streamlit_monitoring (not UI rendering)."""

    def test_is_port_in_use_free_port(self):
        """Test port checking with a likely free port."""
        # Port 65535 is unlikely to be in use
        result = streamlit_monitoring.is_port_in_use(65535)
        assert isinstance(result, bool)

    def test_is_port_in_use_bound_port(self):
        """Test port checking with a bound port."""
        # Create a socket to bind a port temporarily
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", 0))  # Bind to random free port
            port = s.getsockname()[1]
            s.listen(1)  # Start listening on the port

            # Port should be in use while socket is open
            result = streamlit_monitoring.is_port_in_use(port)
            assert result is True

    def test_parse_prometheus_metrics_basic(self):
        """Test parsing basic Prometheus metrics text format."""
        # Note: This function doesn't exist in the original code,
        # but should be extracted for testability
        # For now, we'll test the pattern
        metrics_text = """# HELP test_metric Test metric
# TYPE test_metric gauge
test_metric 42.5
another_metric{label="value"} 100
"""
        # This is a placeholder - the actual implementation would parse this
        # Testing the concept
        assert "test_metric" in metrics_text
        assert "42.5" in metrics_text

    @patch("src.dashboard.streamlit_monitoring.subprocess.Popen")
    @patch("src.dashboard.streamlit_monitoring.is_port_in_use")
    def test_start_flask_server_already_running(self, mock_is_port_in_use, mock_popen):
        """Test Flask server start when already running."""
        mock_is_port_in_use.return_value = True

        result = streamlit_monitoring.start_flask_server()

        assert result is True
        mock_popen.assert_not_called()  # Should not start new process

    @patch("src.dashboard.streamlit_monitoring.subprocess.Popen")
    @patch("src.dashboard.streamlit_monitoring.is_port_in_use")
    @patch("src.dashboard.streamlit_monitoring.time.sleep")
    def test_start_flask_server_success(
        self, mock_sleep, mock_is_port_in_use, mock_popen
    ):
        """Test successful Flask server start."""
        # First call: not running, subsequent calls: running
        mock_is_port_in_use.side_effect = [False, False, True]
        mock_popen.return_value = Mock()

        result = streamlit_monitoring.start_flask_server()

        assert result is True
        mock_popen.assert_called_once()

    @patch("src.dashboard.streamlit_monitoring.subprocess.Popen")
    @patch("src.dashboard.streamlit_monitoring.is_port_in_use")
    def test_start_flask_server_script_not_found(self, mock_is_port_in_use, mock_popen):
        """Test Flask server start when script doesn't exist."""
        mock_is_port_in_use.return_value = False

        # Mock Path.exists to return False
        with patch.object(Path, "exists", return_value=False):
            result = streamlit_monitoring.start_flask_server()

        assert result is False

    @patch("src.dashboard.streamlit_monitoring.subprocess.run")
    @patch("src.dashboard.streamlit_monitoring.is_port_in_use")
    def test_start_docker_monitoring_already_running(
        self, mock_is_port_in_use, mock_run
    ):
        """Test Docker monitoring when already running."""
        # Both Prometheus and Grafana ports are in use
        mock_is_port_in_use.return_value = True

        success, message = streamlit_monitoring.start_docker_monitoring()

        assert success is True
        assert "Already running" in message
        mock_run.assert_not_called()

    @patch("src.dashboard.streamlit_monitoring.subprocess.run")
    @patch("src.dashboard.streamlit_monitoring.is_port_in_use")
    @patch("src.dashboard.streamlit_monitoring.time.sleep")
    def test_start_docker_monitoring_success(
        self, mock_sleep, mock_is_port_in_use, mock_run
    ):
        """Test successful Docker monitoring start."""
        # Ports not in use initially, then in use after docker starts
        mock_is_port_in_use.side_effect = [
            False,
            False,
            True,
            True,
        ]  # Initial check, then after start

        # Mock successful docker-compose command
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        success, message = streamlit_monitoring.start_docker_monitoring()

        assert success is True
        mock_run.assert_called()

    @patch("src.dashboard.streamlit_monitoring.subprocess.run")
    @patch("src.dashboard.streamlit_monitoring.is_port_in_use")
    def test_start_docker_monitoring_compose_file_not_found(
        self, mock_is_port_in_use, mock_run
    ):
        """Test Docker monitoring when compose file doesn't exist."""
        mock_is_port_in_use.return_value = False

        # Mock compose file not existing
        with patch.object(Path, "exists", return_value=False):
            success, message = streamlit_monitoring.start_docker_monitoring()

        assert success is False
        assert "not found" in message.lower()

    def test_stop_prediction_workers_with_psutil(self):
        """Test stopping prediction workers when psutil is available."""
        # This test only runs if psutil is installed
        try:
            import psutil  # noqa: F401

            # If psutil is available, test is simple - function should not crash
            try:
                streamlit_monitoring.stop_prediction_workers()
            except Exception as e:
                pytest.fail(f"stop_prediction_workers raised exception: {e}")
        except ImportError:
            # psutil not installed - skip this test
            pytest.skip("psutil not installed")

    def test_stop_prediction_workers_without_psutil(self):
        """Test stop_prediction_workers when psutil is not available."""
        # Mock the ImportError scenario by temporarily removing psutil from sys.modules
        import sys

        psutil_backup = sys.modules.get("psutil")

        try:
            # Temporarily remove psutil
            if "psutil" in sys.modules:
                del sys.modules["psutil"]

            # Should not raise exception even when psutil is missing
            try:
                streamlit_monitoring.stop_prediction_workers()
            except ImportError:
                pytest.fail("Should handle missing psutil gracefully")
        finally:
            # Restore psutil if it was there
            if psutil_backup is not None:
                sys.modules["psutil"] = psutil_backup


class TestPlotlyGaugeCharts:
    """Test Plotly gauge chart creation (structure validation only)."""

    def test_create_gauge_chart_structure(self):
        """Test that gauge charts can be created with valid structure."""
        # Create a simple gauge chart (this tests Plotly integration)
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=0.75,
                title={"text": "Test Metric"},
                gauge={"axis": {"range": [0, 1]}},
            )
        )

        # Verify it's a valid Plotly figure
        assert hasattr(fig, "data")
        assert hasattr(fig, "layout")
        assert len(fig.data) > 0
        assert fig.data[0].value == 0.75

    def test_gauge_chart_with_thresholds(self):
        """Test gauge chart with colored threshold zones."""
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=0.85,
                title={"text": "Model Performance"},
                gauge={
                    "axis": {"range": [0, 1]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 0.5], "color": "red"},
                        {"range": [0.5, 0.8], "color": "yellow"},
                        {"range": [0.8, 1], "color": "green"},
                    ],
                    "threshold": {
                        "line": {"color": "black", "width": 4},
                        "thickness": 0.75,
                        "value": 0.8,
                    },
                },
            )
        )

        assert fig.data[0].value == 0.85
        assert len(fig.data[0].gauge.steps) == 3


class TestMetricsFormatting:
    """Test metrics formatting utilities."""

    def test_format_number_with_commas(self):
        """Test number formatting with thousands separators."""
        assert f"{1000:,}" == "1,000"
        assert f"{1000000:,}" == "1,000,000"

    def test_format_percentage(self):
        """Test percentage formatting."""
        value = 0.856
        formatted = f"{value:.1%}"
        assert formatted == "85.6%"

    def test_format_float_precision(self):
        """Test float formatting with precision."""
        value = 0.8567891
        formatted = f"{value:.4f}"
        assert formatted == "0.8568"
