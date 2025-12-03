"""
Flask API for serving network logs and anomaly predictions in real-time.
Provides endpoints for the Streamlit dashboard to consume.
"""

import sys
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from model.oneCSVM_model import OneClassSVMModel
from dashboard.geolocation_service import get_geo_service

app = Flask(__name__)
CORS(app)

# Global variables
model = None
df_logs = None
current_index = 0  # Simulates real-time log streaming


def load_resources():
    """Load the ML model and dataset on startup."""
    global model, df_logs

    print("[Flask API] Loading resources...")

    # Load the trained model
    model = OneClassSVMModel()
    if model.model_exists():
        model.load_model()
        print("[Flask API] Model loaded successfully")
    else:
        print("[Flask API] WARNING: No trained model found!")

    # Load the processed dataset
    data_path = project_root / "data" / "processed" / "combined_shuffled_dataset.csv"
    if data_path.exists():
        df_logs = pd.read_csv(data_path)
        # Shuffle for simulation variety
        df_logs = df_logs.sample(frac=1, random_state=42).reset_index(drop=True)
        print(f"[Flask API] Dataset loaded: {len(df_logs)} records")
    else:
        print("[Flask API] WARNING: Dataset not found!")
        df_logs = pd.DataFrame()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None and model.model_exists(),
        "dataset_size": len(df_logs) if df_logs is not None else 0,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/logs/stream', methods=['GET'])
def stream_logs():
    """
    Simulate real-time log streaming.
    Returns a batch of logs as if they were arriving in real-time.
    """
    global current_index

    # Get parameters
    window_size = request.args.get('window_size', default=50, type=int)

    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    # Get next batch of logs (circular buffer)
    end_index = current_index + window_size

    if end_index <= len(df_logs):
        batch = df_logs.iloc[current_index:end_index].copy()
    else:
        # Wrap around to beginning
        batch = pd.concat([
            df_logs.iloc[current_index:],
            df_logs.iloc[:end_index - len(df_logs)]
        ]).copy()

    # Update index for next request
    current_index = end_index % len(df_logs)

    # Add simulated real-time timestamp
    now = datetime.now()
    batch['simulated_timestamp'] = [
        (now - timedelta(seconds=i)).isoformat()
        for i in range(len(batch) - 1, -1, -1)
    ]

    # Make predictions if model is available
    if model is not None and model.model_exists():
        try:
            # Prepare data for prediction
            X_pred = batch.drop(columns=model.features_to_drop, errors='ignore')
            predictions = model.predict(X_pred)

            batch['severity'] = [p[0] for p in predictions]
            batch['description'] = [p[1] for p in predictions]
            batch['anomaly_score'] = [p[2] for p in predictions]
        except Exception as e:
            print(f"[Flask API] Prediction error: {e}")
            batch['severity'] = 'UNKNOWN'
            batch['description'] = 'Prediction failed'
            batch['anomaly_score'] = 0.0

    # Convert to JSON-serializable format
    batch = batch.replace({np.nan: None})

    return jsonify({
        "logs": batch.to_dict(orient='records'),
        "count": len(batch),
        "current_index": current_index,
        "total_records": len(df_logs),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/logs/reset', methods=['POST'])
def reset_stream():
    """Reset the log stream to the beginning."""
    global current_index
    current_index = 0
    return jsonify({"message": "Stream reset", "current_index": current_index})


@app.route('/api/stats/summary', methods=['GET'])
def get_summary_stats():
    """Get summary statistics of the current dataset."""
    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    stats = {
        "total_records": len(df_logs),
        "malicious_count": int((df_logs['label'] == 'malicious').sum()) if 'label' in df_logs.columns else 0,
        "benign_count": int((df_logs['label'] == 'benign').sum()) if 'label' in df_logs.columns else 0,
        "protocols": df_logs['transport_protocol'].value_counts().to_dict() if 'transport_protocol' in df_logs.columns else {},
        "top_source_ips": df_logs['source_ip'].value_counts().head(10).to_dict() if 'source_ip' in df_logs.columns else {},
        "top_destination_ports": df_logs['destination_port'].value_counts().head(10).to_dict() if 'destination_port' in df_logs.columns else {},
    }

    return jsonify(stats)


@app.route('/api/stats/network', methods=['GET'])
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
        "direction_stats": {}
    }

    # Internal vs External traffic analysis
    if all(col in df_logs.columns for col in ['src_is_private', 'dst_is_private']):
        internal_internal = int(((df_logs['src_is_private'] == 1) & (df_logs['dst_is_private'] == 1)).sum())
        internal_external = int(((df_logs['src_is_private'] == 1) & (df_logs['dst_is_private'] == 0)).sum())
        external_internal = int(((df_logs['src_is_private'] == 0) & (df_logs['dst_is_private'] == 1)).sum())
        external_external = int(((df_logs['src_is_private'] == 0) & (df_logs['dst_is_private'] == 0)).sum())

        network_data["internal_external"] = {
            "Internal → Internal": internal_internal,
            "Internal → External": internal_external,
            "External → Internal": external_internal,
            "External → External": external_external
        }

    # Top source IPs
    if 'source_ip' in df_logs.columns:
        network_data["top_source_ips"] = df_logs['source_ip'].value_counts().head(10).to_dict()

    # Top destination IPs
    if 'destination_ip' in df_logs.columns:
        network_data["top_dest_ips"] = df_logs['destination_ip'].value_counts().head(10).to_dict()

    # Top destination ports
    if 'destination_port' in df_logs.columns:
        port_counts = df_logs['destination_port'].value_counts().head(15)
        network_data["top_dest_ports"] = {str(int(k)): int(v) for k, v in port_counts.items()}

    # Common port ratio
    if 'dst_port_is_common' in df_logs.columns:
        network_data["common_port_ratio"] = float(df_logs['dst_port_is_common'].mean())

    # Burst indicator analysis
    if 'burst_indicator' in df_logs.columns:
        network_data["burst_events"] = int(df_logs['burst_indicator'].sum())
        network_data["burst_ratio"] = float(df_logs['burst_indicator'].mean())

    # Direction statistics
    if 'direction' in df_logs.columns:
        network_data["direction_stats"] = df_logs['direction'].value_counts().to_dict()

    return jsonify(network_data)


@app.route('/api/stats/geolocation', methods=['GET'])
def get_geolocation_stats():
    """Get geolocation statistics using GeoIP service."""
    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    geo_service = get_geo_service()

    # Get unique source IPs (limit for performance)
    unique_ips = df_logs['source_ip'].dropna().unique()[:200]

    geo_points = []
    country_counts = {}

    for ip in unique_ips:
        location = geo_service.get_location(str(ip))
        if location and location.get('latitude') and location.get('longitude'):
            # Get label for this IP (malicious if any record is malicious)
            ip_records = df_logs[df_logs['source_ip'] == ip]
            label = 'malicious' if (ip_records['label'] == 'malicious').any() else 'benign'

            geo_points.append({
                "ip": str(ip),
                "lat": location['latitude'],
                "lon": location['longitude'],
                "country": location['country'],
                "city": location.get('city', 'Unknown'),
                "label": label
            })

            # Count by country
            country = location['country']
            if country and country != 'Private':
                country_counts[country] = country_counts.get(country, 0) + 1

    return jsonify({
        "geo_points": geo_points,
        "country_stats": dict(sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:20]),
        "cached_ips": geo_service.get_cached_count()
    })


@app.route('/api/stats/temporal', methods=['GET'])
def get_temporal_stats():
    """Get temporal statistics for time-based visualizations."""
    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    temporal_data = {
        "by_hour": {},
        "by_day_of_week": {},
        "business_hours_ratio": 0,
        "weekend_ratio": 0
    }

    if 'hour' in df_logs.columns:
        temporal_data['by_hour'] = df_logs['hour'].value_counts().sort_index().to_dict()

    if 'day_of_week' in df_logs.columns:
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_counts = df_logs['day_of_week'].value_counts().sort_index()
        temporal_data['by_day_of_week'] = {day_names[i]: int(count) for i, count in day_counts.items()}

    if 'is_business_hours' in df_logs.columns:
        temporal_data['business_hours_ratio'] = float(df_logs['is_business_hours'].mean())

    if 'is_weekend' in df_logs.columns:
        temporal_data['weekend_ratio'] = float(df_logs['is_weekend'].mean())

    return jsonify(temporal_data)


@app.route('/api/stats/traffic', methods=['GET'])
def get_traffic_stats():
    """Get traffic statistics (bytes, packets, rates)."""
    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    traffic_data = {
        "avg_bytes_per_second": 0,
        "avg_packets_per_second": 0,
        "avg_duration": 0,
        "bytes_sent_ratio_avg": 0,
        "internal_traffic_ratio": 0
    }

    if 'bytes_per_second' in df_logs.columns:
        traffic_data['avg_bytes_per_second'] = float(df_logs['bytes_per_second'].mean())

    if 'packets_per_second' in df_logs.columns:
        traffic_data['avg_packets_per_second'] = float(df_logs['packets_per_second'].mean())

    if 'duration' in df_logs.columns:
        traffic_data['avg_duration'] = float(df_logs['duration'].mean())

    if 'bytes_sent_ratio' in df_logs.columns:
        traffic_data['bytes_sent_ratio_avg'] = float(df_logs['bytes_sent_ratio'].mean())

    if 'is_internal' in df_logs.columns:
        traffic_data['internal_traffic_ratio'] = float(df_logs['is_internal'].mean())

    return jsonify(traffic_data)


@app.route('/api/alerts/recent', methods=['GET'])
def get_recent_alerts():
    """Get recent alerts (predictions) from the last batch."""
    window_size = request.args.get('window_size', default=100, type=int)
    severity_filter = request.args.get('severity', default=None, type=str)

    if df_logs is None or df_logs.empty:
        return jsonify({"error": "No data available"}), 500

    # Get a sample of logs
    sample = df_logs.sample(n=min(window_size, len(df_logs)), random_state=None).copy()

    # Make predictions
    alerts = []
    if model is not None and model.model_exists():
        try:
            X_pred = sample.drop(columns=model.features_to_drop, errors='ignore')
            predictions = model.predict(X_pred)

            for i, (row_idx, row) in enumerate(sample.iterrows()):
                severity, desc, score = predictions[i]

                # Apply severity filter
                if severity_filter and severity != severity_filter:
                    continue

                alerts.append({
                    "id": int(row_idx),
                    "timestamp": datetime.now().isoformat(),
                    "source_ip": row.get('source_ip', 'N/A'),
                    "destination_ip": row.get('destination_ip', 'N/A'),
                    "destination_port": int(row.get('destination_port', 0)),
                    "protocol": row.get('transport_protocol', 'N/A'),
                    "severity": severity,
                    "description": desc,
                    "anomaly_score": float(score),
                    "label": row.get('label', 'unknown'),
                    "bytes_sent": int(row.get('bytes_sent', 0)),
                    "packets_sent": int(row.get('pkts_sent', 0)),
                    "country": row.get('src_country', 'Unknown')
                })
        except Exception as e:
            print(f"[Flask API] Alert generation error: {e}")

    # Sort by severity (RED first)
    severity_order = {'RED': 0, 'ORANGE': 1, 'GREEN': 2, 'UNKNOWN': 3}
    alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))

    return jsonify({
        "alerts": alerts,
        "total_count": len(alerts),
        "red_count": sum(1 for a in alerts if a['severity'] == 'RED'),
        "orange_count": sum(1 for a in alerts if a['severity'] == 'ORANGE'),
        "green_count": sum(1 for a in alerts if a['severity'] == 'GREEN')
    })


# Initialize resources on startup
load_resources()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
