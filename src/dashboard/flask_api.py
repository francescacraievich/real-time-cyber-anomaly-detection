"""
Flask API for serving network logs and anomaly predictions in real-time.
Provides endpoints for the Streamlit dashboard to consume.
Also exposes Prometheus metrics endpoint for Grafana monitoring.
"""

import sys
import time
from functools import wraps
from pathlib import Path
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.model.oneCSVM_model import OneClassSVMModel
from src.model.drift_detector import DriftDetector
from src.dashboard.geolocation_service import get_geo_service

# Prometheus metrics (optional - graceful fallback if not available)
try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from src.monitoring.metrics import (
        api_request_duration,
        api_requests_total,
        model_loaded_gauge,
        dataset_size_gauge,
        anomaly_rate_gauge,
        drift_detected_total,
        drift_detected_flag,
        samples_since_drift,
    )

    METRICS_ENABLED = True
except ImportError:
    METRICS_ENABLED = False

app = Flask(__name__)
CORS(app)

# Global variables
model = None
df_logs = None
drift_detector = None
current_index = 0  # Simulates real-time log streaming


def track_request_metrics(f):
    """Decorator to track API request metrics for Prometheus."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not METRICS_ENABLED:
            return f(*args, **kwargs)

        start_time = time.time()
        endpoint = request.endpoint or "unknown"
        method = request.method

        try:
            response = f(*args, **kwargs)
            status = "success"
            return response
        except Exception as e:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            api_request_duration.labels(endpoint=endpoint, method=method).observe(
                duration
            )
            api_requests_total.labels(endpoint=endpoint, status=status).inc()

    return decorated_function


def load_resources():
    """Load the ML model and dataset on startup."""
    global model, df_logs, drift_detector

    # Initialize drift detector (lower threshold = more sensitive)
    drift_detector = DriftDetector(threshold=0.002, window_size=100)

    # Load the trained model
    model = OneClassSVMModel()
    if model.model_exists():
        model.load_model()
        if METRICS_ENABLED:
            model_loaded_gauge.set(1)
    else:
        if METRICS_ENABLED:
            model_loaded_gauge.set(0)

    # Load the processed dataset
    data_path = project_root / "data" / "processed" / "combined_shuffled_dataset.csv"
    if data_path.exists():
        df_logs = pd.read_csv(data_path)
        # Shuffle for simulation variety
        df_logs = df_logs.sample(frac=1, random_state=42).reset_index(drop=True)
        if METRICS_ENABLED:
            dataset_size_gauge.set(len(df_logs))
    else:
        df_logs = pd.DataFrame()
        if METRICS_ENABLED:
            dataset_size_gauge.set(0)


@app.route("/metrics", methods=["GET"])
def prometheus_metrics():
    """Prometheus metrics endpoint for Grafana monitoring."""
    if METRICS_ENABLED:
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
    else:
        return Response(
            "Metrics not available - prometheus_client not installed", status=503
        )


@app.route("/api/health", methods=["GET"])
@track_request_metrics
def health_check():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "model_loaded": model is not None and model.model_exists(),
            "dataset_size": len(df_logs) if df_logs is not None else 0,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/logs/stream", methods=["GET"])
@track_request_metrics
def stream_logs():
    """
    Simulate real-time log streaming.
    Returns a batch of logs as if they were arriving in real-time.
    """
    global current_index

    # Get parameters
    window_size = request.args.get("window_size", default=50, type=int)

    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    # Get next batch of logs (circular buffer)
    end_index = current_index + window_size

    if end_index <= len(df_logs):
        batch = df_logs.iloc[current_index:end_index].copy()
    else:
        # Wrap around to beginning
        batch = pd.concat(
            [df_logs.iloc[current_index:], df_logs.iloc[: end_index - len(df_logs)]]
        ).copy()

    # Update index for next request
    current_index = end_index % len(df_logs)

    # Add simulated real-time timestamp
    now = datetime.now()
    batch["simulated_timestamp"] = [
        (now - timedelta(seconds=i)).isoformat() for i in range(len(batch) - 1, -1, -1)
    ]

    # Make predictions if model is available
    if model is not None and model.model_exists():
        try:
            # Prepare data for prediction
            X_pred = batch.drop(columns=model.features_to_drop, errors="ignore")
            predictions = model.predict(X_pred)

            batch["severity"] = [p[0] for p in predictions]
            batch["description"] = [p[1] for p in predictions]
            batch["anomaly_score"] = [p[2] for p in predictions]

            # Update drift detector with each prediction
            # The drift detector handles all Prometheus metrics internally
            if drift_detector is not None:
                for severity in batch["severity"]:
                    is_anomaly = severity in ["RED", "ORANGE"]
                    drift_detector.update(is_anomaly)
        except Exception:
            batch["severity"] = "UNKNOWN"
            batch["description"] = "Prediction failed"
            batch["anomaly_score"] = 0.0

    # Convert to JSON-serializable format
    batch = batch.replace({np.nan: None})

    # Get drift status
    drift_info = {
        "detected": drift_detector.drift_detected if drift_detector else False,
        "anomaly_rate": (
            drift_detector.get_current_anomaly_rate() if drift_detector else 0.0
        ),
        "samples_processed": drift_detector.processed_samples if drift_detector else 0,
    }

    return jsonify(
        {
            "logs": batch.to_dict(orient="records"),
            "count": len(batch),
            "current_index": current_index,
            "total_records": len(df_logs),
            "timestamp": datetime.now().isoformat(),
            "drift": drift_info,
        }
    )


@app.route("/api/logs/reset", methods=["POST"])
def reset_stream():
    """Reset the log stream and drift detector to the beginning."""
    global current_index, drift_detector
    current_index = 0

    # Also reset the drift detector for a fresh start
    if drift_detector is not None:
        drift_detector.reset()

    return jsonify(
        {"message": "Stream reset", "current_index": current_index, "drift_reset": True}
    )


@app.route("/api/stats/summary", methods=["GET"])
def get_summary_stats():
    """Get summary statistics of the current dataset."""
    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    stats = {
        "total_records": len(df_logs),
        "malicious_count": (
            int((df_logs["label"] == "malicious").sum())
            if "label" in df_logs.columns
            else 0
        ),
        "benign_count": (
            int((df_logs["label"] == "benign").sum())
            if "label" in df_logs.columns
            else 0
        ),
        "protocols": (
            df_logs["transport_protocol"].value_counts().to_dict()
            if "transport_protocol" in df_logs.columns
            else {}
        ),
        "top_source_ips": (
            df_logs["source_ip"].value_counts().head(10).to_dict()
            if "source_ip" in df_logs.columns
            else {}
        ),
        "top_destination_ports": (
            df_logs["destination_port"].value_counts().head(10).to_dict()
            if "destination_port" in df_logs.columns
            else {}
        ),
    }

    return jsonify(stats)


@app.route("/api/stats/network", methods=["GET"])
def get_network_stats():
    """Get network analysis statistics (internal/external, ports, bursts)."""
    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    network_data = {
        "internal_external": {},
        "top_source_ips": {},
        "top_dest_ips": {},
        "top_dest_ports": {},
        "common_port_ratio": 0,
        "burst_events": 0,
        "burst_ratio": 0,
        "direction_stats": {},
    }

    # Internal vs External traffic analysis
    if all(col in df_logs.columns for col in ["src_is_private", "dst_is_private"]):
        internal_internal = int(
            ((df_logs["src_is_private"] == 1) & (df_logs["dst_is_private"] == 1)).sum()
        )
        internal_external = int(
            ((df_logs["src_is_private"] == 1) & (df_logs["dst_is_private"] == 0)).sum()
        )
        external_internal = int(
            ((df_logs["src_is_private"] == 0) & (df_logs["dst_is_private"] == 1)).sum()
        )
        external_external = int(
            ((df_logs["src_is_private"] == 0) & (df_logs["dst_is_private"] == 0)).sum()
        )

        network_data["internal_external"] = {
            "Internal → Internal": internal_internal,
            "Internal → External": internal_external,
            "External → Internal": external_internal,
            "External → External": external_external,
        }

    # Top source IPs
    if "source_ip" in df_logs.columns:
        network_data["top_source_ips"] = (
            df_logs["source_ip"].value_counts().head(10).to_dict()
        )

    # Top destination IPs
    if "destination_ip" in df_logs.columns:
        network_data["top_dest_ips"] = (
            df_logs["destination_ip"].value_counts().head(10).to_dict()
        )

    # Top destination ports
    if "destination_port" in df_logs.columns:
        port_counts = df_logs["destination_port"].value_counts().head(15)
        network_data["top_dest_ports"] = {
            str(int(k)): int(v) for k, v in port_counts.items()
        }

    # Common port ratio
    if "dst_port_is_common" in df_logs.columns:
        network_data["common_port_ratio"] = float(df_logs["dst_port_is_common"].mean())

    # Burst indicator analysis
    if "burst_indicator" in df_logs.columns:
        network_data["burst_events"] = int(df_logs["burst_indicator"].sum())
        network_data["burst_ratio"] = float(df_logs["burst_indicator"].mean())

    # Direction statistics
    if "direction" in df_logs.columns:
        network_data["direction_stats"] = df_logs["direction"].value_counts().to_dict()

    return jsonify(network_data)


@app.route("/api/stats/geolocation", methods=["GET"])
def get_geolocation_stats():
    """Get geolocation statistics using GeoIP service."""
    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    geo_service = get_geo_service()

    # Get unique source IPs (limit for performance)
    unique_ips = df_logs["source_ip"].dropna().unique()[:200]

    geo_points = []
    country_counts = {}

    for ip in unique_ips:
        location = geo_service.get_location(str(ip))
        if location and location.get("latitude") and location.get("longitude"):
            # Get label for this IP (malicious if any record is malicious)
            ip_records = df_logs[df_logs["source_ip"] == ip]
            label = (
                "malicious" if (ip_records["label"] == "malicious").any() else "benign"
            )

            geo_points.append(
                {
                    "ip": str(ip),
                    "lat": location["latitude"],
                    "lon": location["longitude"],
                    "country": location["country"],
                    "city": location.get("city", "Unknown"),
                    "label": label,
                }
            )

            # Count by country
            country = location["country"]
            if country and country != "Private":
                country_counts[country] = country_counts.get(country, 0) + 1

    return jsonify(
        {
            "geo_points": geo_points,
            "country_stats": dict(
                sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            ),
            "cached_ips": geo_service.get_cached_count(),
        }
    )


@app.route("/api/stats/temporal", methods=["GET"])
def get_temporal_stats():
    """Get temporal statistics for time-based visualizations."""
    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    temporal_data = {
        "by_hour": {},
        "by_day_of_week": {},
        "business_hours_ratio": 0,
        "weekend_ratio": 0,
    }

    if "hour" in df_logs.columns:
        temporal_data["by_hour"] = df_logs["hour"].value_counts().sort_index().to_dict()

    if "day_of_week" in df_logs.columns:
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_counts = df_logs["day_of_week"].value_counts().sort_index()
        temporal_data["by_day_of_week"] = {
            day_names[i]: int(count) for i, count in day_counts.items()
        }

    if "is_business_hours" in df_logs.columns:
        temporal_data["business_hours_ratio"] = float(
            df_logs["is_business_hours"].mean()
        )

    if "is_weekend" in df_logs.columns:
        temporal_data["weekend_ratio"] = float(df_logs["is_weekend"].mean())

    return jsonify(temporal_data)


@app.route("/api/stats/traffic", methods=["GET"])
def get_traffic_stats():
    """Get traffic statistics (bytes, packets, rates)."""
    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    traffic_data = {
        "avg_bytes_per_second": 0,
        "avg_packets_per_second": 0,
        "avg_duration": 0,
        "bytes_sent_ratio_avg": 0,
        "internal_traffic_ratio": 0,
    }

    if "bytes_per_second" in df_logs.columns:
        traffic_data["avg_bytes_per_second"] = float(df_logs["bytes_per_second"].mean())

    if "packets_per_second" in df_logs.columns:
        traffic_data["avg_packets_per_second"] = float(
            df_logs["packets_per_second"].mean()
        )

    if "duration" in df_logs.columns:
        traffic_data["avg_duration"] = float(df_logs["duration"].mean())

    if "bytes_sent_ratio" in df_logs.columns:
        traffic_data["bytes_sent_ratio_avg"] = float(df_logs["bytes_sent_ratio"].mean())

    if "is_internal" in df_logs.columns:
        traffic_data["internal_traffic_ratio"] = float(df_logs["is_internal"].mean())

    return jsonify(traffic_data)


@app.route("/api/alerts/recent", methods=["GET"])
@track_request_metrics
def get_recent_alerts():
    """Get recent alerts (predictions) from the last batch."""
    window_size = request.args.get("window_size", default=100, type=int)
    severity_filter = request.args.get("severity", default=None, type=str)

    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    # Get a sample of logs
    sample = df_logs.sample(n=min(window_size, len(df_logs)), random_state=None).copy()

    # Make predictions
    alerts = []
    if model is not None and model.model_exists():
        try:
            X_pred = sample.drop(columns=model.features_to_drop, errors="ignore")
            predictions = model.predict(X_pred)

            for i, (row_idx, row) in enumerate(sample.iterrows()):
                severity, desc, score = predictions[i]

                # Apply severity filter
                if severity_filter and severity != severity_filter:
                    continue

                alerts.append(
                    {
                        "id": int(row_idx),
                        "timestamp": datetime.now().isoformat(),
                        "source_ip": row.get("source_ip", "N/A"),
                        "destination_ip": row.get("destination_ip", "N/A"),
                        "destination_port": int(row.get("destination_port", 0)),
                        "protocol": row.get("transport_protocol", "N/A"),
                        "severity": severity,
                        "description": desc,
                        "anomaly_score": float(score),
                        "label": row.get("label", "unknown"),
                        "bytes_sent": int(row.get("bytes_sent", 0)),
                        "packets_sent": int(row.get("pkts_sent", 0)),
                        "country": row.get("src_country", "Unknown"),
                    }
                )
        except Exception:
            pass

    # Sort by severity (RED first)
    severity_order = {"RED": 0, "ORANGE": 1, "GREEN": 2, "UNKNOWN": 3}
    alerts.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return jsonify(
        {
            "alerts": alerts,
            "total_count": len(alerts),
            "red_count": sum(1 for a in alerts if a["severity"] == "RED"),
            "orange_count": sum(1 for a in alerts if a["severity"] == "ORANGE"),
            "green_count": sum(1 for a in alerts if a["severity"] == "GREEN"),
        }
    )


@app.route("/api/evaluate", methods=["POST"])
@track_request_metrics
def evaluate_model():
    """
    Run model evaluation on a sample of data to calculate F1, precision, recall.
    This updates the Prometheus metrics for model performance.
    """
    from sklearn.metrics import (
        precision_score,
        recall_score,
        f1_score,
        confusion_matrix as sk_confusion_matrix,
    )

    sample_size = request.args.get("sample_size", default=500, type=int)

    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    if model is None or not model.model_exists():
        return jsonify({"error": "Model not loaded"}), 500

    try:
        # Get a sample with labels
        sample = df_logs.sample(
            n=min(sample_size, len(df_logs)), random_state=None
        ).copy()

        # Get true labels (1 = malicious/anomaly, 0 = benign/normal)
        y_true = (sample["label"] == "malicious").astype(int).values

        # Make predictions
        X_pred = sample.drop(columns=model.features_to_drop, errors="ignore")
        predictions = model.predict(X_pred)

        # Convert predictions to binary (RED/ORANGE = anomaly = 1, GREEN = normal = 0)
        y_pred = [1 if p[0] in ["RED", "ORANGE"] else 0 for p in predictions]

        # Calculate metrics
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        # Confusion matrix
        cm = sk_confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

        # Detection rate and false alarm rate
        det_rate = tp / (tp + fn) if (tp + fn) > 0 else 0
        far = fp / (fp + tn) if (fp + tn) > 0 else 0

        # Update Prometheus metrics
        if METRICS_ENABLED:
            from src.monitoring.metrics import (
                model_precision,
                model_recall,
                model_f1_score,
                detection_rate as dr_metric,
                false_alarm_rate as far_metric,
                confusion_matrix as cm_metric,
            )

            model_precision.set(precision)
            model_recall.set(recall)
            model_f1_score.set(f1)
            dr_metric.set(det_rate)
            far_metric.set(far)

            # Update confusion matrix
            cm_metric.labels(actual="normal", predicted="normal").set(tn)
            cm_metric.labels(actual="normal", predicted="anomaly").set(fp)
            cm_metric.labels(actual="anomaly", predicted="normal").set(fn)
            cm_metric.labels(actual="anomaly", predicted="anomaly").set(tp)

        return jsonify(
            {
                "precision": float(precision),
                "recall": float(recall),
                "f1_score": float(f1),
                "detection_rate": float(det_rate),
                "false_alarm_rate": float(far),
                "confusion_matrix": {
                    "tn": int(tn),
                    "fp": int(fp),
                    "fn": int(fn),
                    "tp": int(tp),
                },
                "sample_size": int(len(sample)),
                "anomaly_count": int(sum(y_pred)),
                "malicious_count": int(sum(y_true)),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Initialize resources on startup
load_resources()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
