"""
Streamlit ML Model Monitoring Dashboard.
Provides technical monitoring of the anomaly detection model with:
- Prometheus metrics visualization
- Embedded Grafana dashboards
- Real-time model performance tracking
- Background prediction loop for continuous metrics

Automatically starts Flask API, Prometheus, Grafana, and prediction loop on launch.
"""

import streamlit as st
import subprocess
import sys
import socket
import time
import requests
import atexit
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configuration
API_BASE_URL = "http://localhost:5000"
FLASK_PORT = 5000
PROMETHEUS_PORT = 9090
GRAFANA_PORT = 3000
GRAFANA_URL = f"http://localhost:{GRAFANA_PORT}"

# Dark theme colors (matching main dashboard)
COLORS = {
    "primary": "#1BA9F5",
    "success": "#7DE2D1",
    "warning": "#F5A623",
    "danger": "#FF6B6B",
    "background": "#1D1E24",
    "surface": "#25262E",
    "text": "#DFE5EF",
    "muted": "#98A2B3",
}


def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def stop_prediction_workers():
    """Stop all running prediction worker processes."""
    try:
        import psutil

        killed = 0
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = proc.info.get("cmdline") or []
                if any("prediction_worker.py" in str(c) for c in cmdline):
                    proc.terminate()
                    killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if killed > 0:
            print(f"[Prediction Worker] Stopped {killed} worker(s)")
    except (ImportError, Exception):
        pass


# Register cleanup function to run on exit
atexit.register(stop_prediction_workers)


def start_flask_server():
    """Start Flask server in background if not already running."""
    if is_port_in_use(FLASK_PORT):
        return True

    dashboard_dir = Path(__file__).parent
    flask_script = dashboard_dir / "flask_api.py"

    if not flask_script.exists():
        return False

    try:
        if sys.platform == "win32":
            subprocess.Popen(
                [sys.executable, str(flask_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            subprocess.Popen(
                [sys.executable, str(flask_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

        for _ in range(10):
            time.sleep(0.5)
            if is_port_in_use(FLASK_PORT):
                return True
        return False
    except Exception:
        return False


def start_docker_monitoring():
    """Start Prometheus and Grafana via Docker Compose."""
    project_root = Path(__file__).resolve().parent.parent.parent
    compose_file = (project_root / "docker-compose.yml").resolve()
    monitoring_dir = (project_root / "src" / "monitoring").resolve()

    if not compose_file.exists():
        return False, f"docker-compose.yml not found at {compose_file}"

    # Check if already running
    if is_port_in_use(PROMETHEUS_PORT) and is_port_in_use(GRAFANA_PORT):
        return True, "Already running"

    try:
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            # Try docker compose (newer syntax)
            result = subprocess.run(
                ["docker", "compose", "up", "-d"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=60,
            )

        if result.returncode == 0:
            # Wait for services to start
            for _ in range(20):
                time.sleep(1)
                if is_port_in_use(PROMETHEUS_PORT) and is_port_in_use(GRAFANA_PORT):
                    return True, "Started successfully"
            return False, "Timeout waiting for services"
        else:
            return False, result.stderr

    except FileNotFoundError:
        return False, "Docker not found. Please install Docker Desktop."
    except subprocess.TimeoutExpired:
        return False, "Timeout starting Docker services"
    except Exception as e:
        return False, str(e)


def is_prediction_worker_running():
    """Check if the prediction worker process is running."""
    try:
        import psutil

        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = proc.info.get("cmdline") or []
                cmdline_str = " ".join(str(c) for c in cmdline)
                if (
                    "python" in cmdline_str.lower()
                    and "prediction_worker.py" in cmdline_str
                ):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except ImportError:
        pass
    return False


def start_prediction_worker():
    """Start the prediction worker as a separate process."""
    dashboard_dir = Path(__file__).resolve().parent
    worker_script = (dashboard_dir / "prediction_worker.py").resolve()
    project_root = dashboard_dir.parent.parent

    if not worker_script.exists():
        return False, f"prediction_worker.py not found at {worker_script}"

    try:
        if sys.platform == "win32":
            subprocess.Popen(
                [sys.executable, str(worker_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                | subprocess.DETACHED_PROCESS,
                cwd=str(project_root),
            )
        else:
            subprocess.Popen(
                [sys.executable, str(worker_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                cwd=str(project_root),
            )

        time.sleep(3)

        if is_prediction_worker_running():
            return True, "Started"
        else:
            return False, "Failed to start"

    except Exception as e:
        return False, str(e)


def fetch_prometheus_metrics():
    """Fetch metrics from Flask /metrics endpoint and parse them."""
    try:
        response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
        if response.status_code == 200:
            return parse_prometheus_metrics(response.text)
        return {}
    except Exception:
        return {}


def parse_prometheus_metrics(text):
    """Parse Prometheus text format into a dictionary."""
    metrics = {}
    for line in text.split("\n"):
        if line and not line.startswith("#"):
            try:
                # Handle metrics with labels
                if "{" in line:
                    name = line.split("{")[0]
                    value = float(line.split()[-1])
                    if name not in metrics:
                        metrics[name] = []
                    metrics[name].append(
                        {"labels": line.split("{")[1].split("}")[0], "value": value}
                    )
                else:
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        value = float(parts[1])
                        metrics[name] = value
            except (ValueError, IndexError):
                continue
    return metrics


def create_gauge_chart(value, title, max_val=1.0, thresholds=None):
    """Create a gauge chart for metrics."""
    if thresholds is None:
        thresholds = [0.5, 0.7]

    color = COLORS["danger"]
    if value >= thresholds[1]:
        color = COLORS["success"]
    elif value >= thresholds[0]:
        color = COLORS["warning"]

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": title, "font": {"size": 14, "color": COLORS["text"]}},
            number={
                "font": {"size": 28, "color": COLORS["text"]},
                "suffix": "" if max_val == 1 else "",
            },
            gauge={
                "axis": {"range": [0, max_val], "tickcolor": COLORS["muted"]},
                "bar": {"color": color},
                "bgcolor": COLORS["surface"],
                "borderwidth": 0,
                "steps": [
                    {
                        "range": [0, thresholds[0] * max_val],
                        "color": "rgba(255,107,107,0.2)",
                    },
                    {
                        "range": [thresholds[0] * max_val, thresholds[1] * max_val],
                        "color": "rgba(245,166,35,0.2)",
                    },
                    {
                        "range": [thresholds[1] * max_val, max_val],
                        "color": "rgba(125,226,209,0.2)",
                    },
                ],
                "threshold": {
                    "line": {"color": COLORS["text"], "width": 2},
                    "thickness": 0.75,
                    "value": value,
                },
            },
        )
    )

    fig.update_layout(
        paper_bgcolor=COLORS["surface"],
        font={"color": COLORS["text"]},
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


def render_service_status():
    """Render service status indicators."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        flask_status = is_port_in_use(FLASK_PORT)
        status_color = COLORS["success"] if flask_status else COLORS["danger"]
        status_text = "Running" if flask_status else "Stopped"
        st.markdown(
            f"""
        <div style="background-color: {COLORS['surface']}; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid {status_color};">
            <div style="color: {COLORS['muted']}; font-size: 12px;">Flask API</div>
            <div style="color: {status_color}; font-size: 18px; font-weight: bold;">{status_text}</div>
            <div style="color: {COLORS['muted']}; font-size: 11px;">Port {FLASK_PORT}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        prometheus_status = is_port_in_use(PROMETHEUS_PORT)
        status_color = COLORS["success"] if prometheus_status else COLORS["danger"]
        status_text = "Running" if prometheus_status else "Stopped"
        st.markdown(
            f"""
        <div style="background-color: {COLORS['surface']}; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid {status_color};">
            <div style="color: {COLORS['muted']}; font-size: 12px;">Prometheus</div>
            <div style="color: {status_color}; font-size: 18px; font-weight: bold;">{status_text}</div>
            <div style="color: {COLORS['muted']}; font-size: 11px;">Port {PROMETHEUS_PORT}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        grafana_status = is_port_in_use(GRAFANA_PORT)
        status_color = COLORS["success"] if grafana_status else COLORS["danger"]
        status_text = "Running" if grafana_status else "Stopped"
        st.markdown(
            f"""
        <div style="background-color: {COLORS['surface']}; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid {status_color};">
            <div style="color: {COLORS['muted']}; font-size: 12px;">Grafana</div>
            <div style="color: {status_color}; font-size: 18px; font-weight: bold;">{status_text}</div>
            <div style="color: {COLORS['muted']}; font-size: 11px;">Port {GRAFANA_PORT}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        # Check if worker is running by looking at metrics activity
        metrics = fetch_prometheus_metrics()
        samples = metrics.get("anomaly_detection_samples_processed_total", 0)
        pred_status = samples > 0
        status_color = COLORS["success"] if pred_status else COLORS["danger"]
        status_text = "Active" if pred_status else "Inactive"
        st.markdown(
            f"""
        <div style="background-color: {COLORS['surface']}; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid {status_color};">
            <div style="color: {COLORS['muted']}; font-size: 12px;">Prediction Worker</div>
            <div style="color: {status_color}; font-size: 18px; font-weight: bold;">{status_text}</div>
            <div style="color: {COLORS['muted']}; font-size: 11px;">{int(samples):,} samples</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col5:
        flask_ok = is_port_in_use(FLASK_PORT)
        prom_ok = is_port_in_use(PROMETHEUS_PORT)
        graf_ok = is_port_in_use(GRAFANA_PORT)
        all_running = flask_ok and prom_ok and graf_ok and pred_status
        status_color = COLORS["success"] if all_running else COLORS["warning"]
        status_text = "All Systems Go" if all_running else "Partial"
        st.markdown(
            f"""
        <div style="background-color: {COLORS['surface']}; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid {status_color};">
            <div style="color: {COLORS['muted']}; font-size: 12px;">Overall Status</div>
            <div style="color: {status_color}; font-size: 18px; font-weight: bold;">{status_text}</div>
            <div style="color: {COLORS['muted']}; font-size: 11px;">&nbsp;</div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_model_performance(metrics):
    """Render model performance gauges."""
    st.subheader("Model Performance")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        f1 = metrics.get("anomaly_detection_f1_score", 0)
        fig = create_gauge_chart(f1, "F1-Score", thresholds=[0.5, 0.7])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        precision = metrics.get("anomaly_detection_precision", 0)
        fig = create_gauge_chart(precision, "Precision", thresholds=[0.6, 0.8])
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        recall = metrics.get("anomaly_detection_recall", 0)
        fig = create_gauge_chart(recall, "Recall", thresholds=[0.6, 0.8])
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        det_rate = metrics.get("anomaly_detection_detection_rate", 0)
        fig = create_gauge_chart(det_rate, "Detection Rate", thresholds=[0.7, 0.8])
        st.plotly_chart(fig, use_container_width=True)

    with col5:
        far = metrics.get("anomaly_detection_false_alarm_rate", 0)
        # Invert thresholds for false alarm (lower is better)
        fig = create_gauge_chart(far, "False Alarm Rate", thresholds=[0.1, 0.05])
        st.plotly_chart(fig, use_container_width=True)


def render_drift_status(metrics):
    """Render drift detection status."""
    st.subheader("Drift Detection")

    col1, col2, col3, col4 = st.columns(4)

    drift_detected = metrics.get("anomaly_detection_drift_status", 0)
    anomaly_rate = metrics.get("anomaly_detection_anomaly_rate", 0)
    drift_total = metrics.get("anomaly_detection_drift_detected_total", 0)
    samples_since = metrics.get("anomaly_detection_samples_since_drift", 0)

    with col1:
        status_color = COLORS["danger"] if drift_detected else COLORS["success"]
        status_text = "DRIFT DETECTED!" if drift_detected else "STABLE"
        st.markdown(
            f"""
        <div style="background-color: {status_color}; padding: 30px; border-radius: 8px; text-align: center;">
            <div style="color: white; font-size: 14px; opacity: 0.9;">Drift Status</div>
            <div style="color: white; font-size: 28px; font-weight: bold;">{status_text}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.metric("Anomaly Rate", f"{anomaly_rate:.1%}")

    with col3:
        st.metric("Total Drift Events", int(drift_total))

    with col4:
        st.metric("Samples Since Reset", int(samples_since))


def render_system_metrics(metrics):
    """Render system metrics."""
    st.subheader("System Metrics")

    col1, col2, col3 = st.columns(3)

    retrains = metrics.get("anomaly_detection_model_retrain_total", 0)
    samples = metrics.get("anomaly_detection_samples_processed_total", 0)
    threshold = metrics.get("anomaly_detection_threshold_boundary", 0)

    with col1:
        st.metric("Model Retrains", int(retrains))

    with col2:
        st.metric("Samples Processed", f"{int(samples):,}")

    with col3:
        st.metric("Decision Threshold", f"{threshold:.4f}")


def render_grafana_embed():
    """Render embedded Grafana dashboard."""
    st.subheader("Grafana Dashboard")

    if is_port_in_use(GRAFANA_PORT):
        # Grafana embed URL with anonymous access
        dashboard_url = f"{GRAFANA_URL}/d/anomaly-detection-overview/cyber-anomaly-detection-ml-model-monitoring?orgId=1&refresh=10s&kiosk"

        st.markdown(
            f"""
        <iframe src="{dashboard_url}"
                width="100%"
                height="800"
                frameborder="0"
                style="border-radius: 8px; background-color: {COLORS['surface']};">
        </iframe>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
        <div style="text-align: center; margin-top: 10px;">
            <a href="{GRAFANA_URL}" target="_blank" style="color: {COLORS['primary']};">
                Open Grafana in new tab (admin/admin)
            </a>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("Grafana is not running. Click 'Start All Services' to launch.")


def main():
    """Main application."""
    st.set_page_config(
        page_title="ML Model Monitoring",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Dark theme CSS
    st.markdown(
        f"""
    <style>
        .stApp {{
            background-color: {COLORS['background']};
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {COLORS['text']} !important;
        }}
        p, span, label {{
            color: {COLORS['text']} !important;
        }}
        [data-testid="stMetricValue"] {{
            color: {COLORS['text']} !important;
            font-size: 2rem !important;
        }}
        [data-testid="stMetricLabel"] {{
            color: {COLORS['muted']} !important;
        }}
        .stButton > button {{
            background-color: {COLORS['primary']};
            color: white;
            border: none;
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("ML Model Monitoring Dashboard")
    st.markdown("---")

    # Service control buttons (narrow columns to keep buttons close)
    col1, col2, col3, _ = st.columns([1, 1, 1, 5])

    with col1:
        if st.button("Start All Services", type="primary"):
            with st.spinner("Starting services..."):
                # Start Flask
                flask_ok = start_flask_server()
                if flask_ok:
                    st.success("Flask API started")
                else:
                    st.error("Failed to start Flask API")

                # Start Docker monitoring stack
                docker_ok, msg = start_docker_monitoring()
                if docker_ok:
                    st.success(f"Monitoring stack: {msg}")
                else:
                    st.error(f"Monitoring stack: {msg}")

                # Start prediction worker
                time.sleep(2)  # Wait for Flask to be ready
                pred_ok, pred_msg = start_prediction_worker()
                if pred_ok:
                    st.success(f"Prediction worker: {pred_msg}")
                else:
                    st.error(f"Prediction worker: {pred_msg}")

            time.sleep(3)
            st.rerun()

    with col2:
        if st.button("Refresh"):
            st.rerun()

    with col3:
        if st.button("Reset Stream"):
            # Reset the data stream to the beginning
            try:
                response = requests.post(f"{API_BASE_URL}/api/logs/reset", timeout=5)
                if response.status_code == 200:
                    st.success("Stream reset to beginning!")
                else:
                    st.error("Failed to reset stream")
            except requests.exceptions.ConnectionError:
                st.error("Flask API not running")
            except Exception as e:
                st.error(f"Error: {e}")
            time.sleep(1)
            st.rerun()

    # Service status
    st.markdown("### Service Status")
    render_service_status()
    st.markdown("---")

    # Fetch metrics from Prometheus endpoint
    metrics = fetch_prometheus_metrics()

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Model Metrics", "Grafana Dashboard", "Raw Metrics"])

    with tab1:
        if metrics:
            render_model_performance(metrics)
            st.markdown("---")
            render_drift_status(metrics)
            st.markdown("---")
            render_system_metrics(metrics)
        else:
            st.info(
                "No metrics available. Click 'Start All Services' to begin monitoring."
            )

            # Show placeholder gauges with zero values
            render_model_performance({})
            st.markdown("---")
            render_drift_status({})

    with tab2:
        render_grafana_embed()

    with tab3:
        st.subheader("Prometheus Metrics Overview")
        if metrics:
            # Filter to show only anomaly_detection metrics
            ad_metrics = {
                k: v for k, v in metrics.items() if k.startswith("anomaly_detection")
            }

            # Group metrics by category
            categories = {
                "Model Performance": [
                    "precision",
                    "recall",
                    "f1_score",
                    "detection_rate",
                    "false_alarm_rate",
                ],
                "Predictions": [
                    "samples_processed",
                    "predictions_red",
                    "predictions_orange",
                    "predictions_green",
                ],
                "Drift Detection": [
                    "drift_status",
                    "drift_detected_total",
                    "samples_since_drift",
                    "anomaly_rate",
                ],
                "System": ["model_loaded", "dataset_size"],
            }

            for category, keywords in categories.items():
                category_metrics = {
                    k: v
                    for k, v in ad_metrics.items()
                    if any(kw in k for kw in keywords)
                }
                if category_metrics:
                    st.markdown(f"**{category}**")
                    cols = st.columns(min(len(category_metrics), 4))
                    for i, (metric_name, value) in enumerate(category_metrics.items()):
                        with cols[i % 4]:
                            # Clean up metric name for display
                            display_name = (
                                metric_name.replace("anomaly_detection_", "")
                                .replace("_", " ")
                                .title()
                            )
                            # Format value
                            if isinstance(value, float):
                                if value < 1 and value > 0:
                                    display_value = f"{value:.3f}"
                                else:
                                    display_value = f"{value:,.0f}"
                            else:
                                display_value = (
                                    f"{value:,}"
                                    if isinstance(value, (int, float))
                                    else str(value)
                                )

                            st.metric(label=display_name, value=display_value)
                    st.markdown("---")

        else:
            st.info("No metrics available. Start the services to see metrics.")

    # Auto-refresh option
    st.sidebar.markdown("### Settings")
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh interval (sec)", 5, 60, 10)

    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: {COLORS['muted']};'>"
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f"</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
