# ML Model & Dashboard Integration

## Real-Time Cyber Anomaly Detection System

**Version:** 1.0
**Date:** 2025-12-11
**Authors:** Francesca Craievich, Lucas Jakin, Francesco Rumiz

---

## 1. Overview

This document describes the machine learning model implementation and its integration with the Streamlit dashboards for real-time cyber anomaly detection.

### 1.1 Live Dashboards

- **[Real-time Anomaly Dashboard](https://dashboard-alerts.streamlit.app/)** - Main visualization
- **[ML Monitoring Dashboard](https://monitoring-model.streamlit.app/)** - Model performance monitoring

---

## 2. One-Class SVM Model

### 2.1 Model Architecture

The system uses a **One-Class Support Vector Machine (OCSVM)** for anomaly detection. This unsupervised learning approach is ideal for cyber security because:

- Trains only on "normal" (benign) traffic
- Identifies anomalies as deviations from learned normal behavior
- Detects zero-day attacks without requiring labeled malicious samples
- Uses RBF kernel to capture non-linear patterns

**Location**: `src/model/oneCSVM_model.py`

### 2.2 Model Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `kernel` | `rbf` | Radial Basis Function for non-linear boundaries |
| `nu` | `0.5` | Upper bound on training errors (controls sensitivity) |
| `gamma` | `scale` | Kernel coefficient (auto-scaled based on features) |

### 2.3 Preprocessing Pipeline

```
Raw Data → Feature Selection → ColumnTransformer → Trained Model
                                    │
                      ┌─────────────┴─────────────┐
                      │                           │
              RobustScaler              OneHotEncoder
           (numerical features)      (categorical features)
```

**Numerical Features** (scaled with RobustScaler):
- `source_port`, `destination_port`, `duration`
- `bytes_sent`, `bytes_received`, `pkts_sent`, `pkts_received`
- `bytes_per_second`, `pkts_per_second`, `bytes_per_packet`
- `bytes_ratio`, `pkts_ratio`, `hour`
- `events_in_window`, `events_pct_change`, `burst_indicator`
- `events_for_protocol`

**Categorical Features** (encoded with OneHotEncoder):
- `transport_protocol`, `direction`, `day_of_week`
- `is_weekend`, `is_business_hours`
- `src_is_private`, `dst_is_private`, `is_internal`, `dst_port_is_common`

**Dropped Features** (not used for prediction):
- `source_ip`, `destination_ip` (high cardinality)
- `timestamp_start` (temporal features extracted separately)
- `label` (would cause data leakage)
- Malicious-related aggregations (leak label information)

### 2.4 Training Process

```python
# 1. Load benign traffic data
df_benign = load_data()

# 2. Configure feature pipeline
model._configure_features(df_benign)

# 3. Split data (80/20)
X_train, X_val = train_test_split(df_benign, test_size=0.2)

# 4. Fit preprocessor and transform
preprocessor.fit(X_train)
X_train_processed = preprocessor.transform(X_train)

# 5. Train One-Class SVM
model.fit(X_train_processed)

# 6. Calibrate threshold on validation set
scores = model.decision_function(X_val_processed)
threshold = np.percentile(scores, contamination * 100)
```

### 2.5 Severity Classification

The model classifies traffic into three severity levels based on the decision function score:

| Severity | Condition | Description |
|----------|-----------|-------------|
| **RED** | `score < threshold - 0.5` | CRITICAL: Far outside normal boundary |
| **ORANGE** | `threshold - 0.5 ≤ score < threshold` | SUSPICIOUS: Just outside boundary |
| **GREEN** | `score ≥ threshold` | NORMAL: Within expected behavior |

### 2.6 Model Performance

Based on evaluation with `nu=0.2`, `contamination=0.1`, `max_train_samples=10,000`:

| Metric | Value |
|--------|-------|
| Detection Rate (Recall) | 90.7% |
| False Alarm Rate | 10% |
| F1-Score | 0.885 |
| Precision | ~85% |

### 2.7 Model Persistence

Model artifacts are saved to `src/model/`:

| File | Content |
|------|---------|
| `oneclass_svm_model.pkl` | Trained SVM model (joblib) |
| `oneclass_svm_preprocessor.pkl` | ColumnTransformer pipeline |
| `oneclass_svm_config.pkl` | Threshold, features, hyperparameters |

---

## 3. Drift Detection

### 3.1 ADWIN Algorithm

**Location**: `src/model/drift_detector.py`

The system uses **ADWIN (Adaptive Windowing)** to detect concept drift:

```python
from river import drift

class DriftDetector:
    def __init__(self, threshold=0.002, window_size=100, change_threshold=0.08):
        self.adwin = drift.ADWIN(delta=threshold)
        self.history = deque(maxlen=window_size)
        self.change_threshold = change_threshold  # 8% change triggers drift
```

### 3.2 Drift Detection Methods

1. **ADWIN Detection**: Statistical test for distribution changes
2. **Threshold-based Detection**: Triggers when anomaly rate changes by >8%

### 3.3 Drift Status

| Status | Condition | Action |
|--------|-----------|--------|
| **STABLE** | No significant distribution change | Continue normal operation |
| **UNSTABLE** | Drift detected | Alert user, consider retraining |

### 3.4 Auto-Retraining

When drift is detected and the retrain buffer has >1000 samples:

```python
def retrain(self):
    if len(self.retrain_buffer) < 1000:
        return False

    df_recent = pd.DataFrame(self.retrain_buffer)
    self.fit(df_recent, max_train_samples=len(df_recent))
    return True
```

---

## 4. Real-time Anomaly Dashboard

### 4.1 Overview

**Location**: `src/dashboard/streamlit_app.py`

The main dashboard provides a Kibana-style interface for real-time anomaly visualization.

### 4.2 Features

#### Alert Summary Cards
- **Critical Alerts (RED)**: Count of high-severity anomalies
- **Suspicious (ORANGE)**: Count of medium-severity events
- **Normal (GREEN)**: Count of benign traffic
- **Total Analyzed**: Total events processed

#### Live Alerts Tab
- Filterable alerts table with color-coded severity
- Anomaly score distribution histogram
- Real-time updates with configurable refresh interval

#### Attack Map Tab
- Geographic visualization of traffic sources
- Country-based attack statistics
- Interactive map with Plotly

#### Traffic Analysis Tab
- Protocol distribution (donut chart)
- Top destination ports
- Traffic metrics (bytes/sec, packets/sec, duration)
- Internal vs external traffic ratio

#### Temporal Patterns Tab
- Today's live activity (15-minute intervals)
- Historical distribution by hour
- Business hours traffic percentage

### 4.3 Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Streamlit App  │────▶│    Flask API     │────▶│   ML Model      │
│  (Frontend)     │◀────│   (Backend)      │◀────│   (Inference)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                      │
         │              ┌───────┴───────┐
         │              │  Prometheus   │
         │              │   Metrics     │
         │              └───────────────┘
         │
    ┌────┴────┐
    │ Plotly  │
    │ Charts  │
    └─────────┘
```

### 4.4 API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `/api/health` | Service status and model info |
| `/api/alerts/recent` | Recent predictions with severity |
| `/api/stats/geolocation` | IP geolocation data |
| `/api/stats/temporal` | Time-based statistics |
| `/api/stats/traffic` | Traffic metrics |
| `/api/stats/summary` | Protocol and port statistics |

### 4.5 Auto-Start Behavior

When the dashboard launches, it automatically:
1. Checks if Flask API is running on port 5000
2. Starts Flask server if not running
3. Waits for API to be ready before loading data

---

## 5. ML Monitoring Dashboard

### 5.1 Overview

**Location**: `src/dashboard/streamlit_monitoring.py`

Technical dashboard for monitoring model performance and system health.

### 5.2 Features

#### Service Status Panel
- Flask API status (port 5000)
- Prometheus status (port 9090)
- Grafana status (port 3000)
- Prediction Worker status
- Overall system health

#### Model Performance Gauges
- **F1-Score**: Harmonic mean of precision and recall
- **Precision**: Accuracy of positive predictions
- **Recall**: Detection rate of actual anomalies
- **Detection Rate**: Percentage of anomalies caught
- **False Alarm Rate**: Percentage of false positives

#### Drift Detection Panel
- Current drift status (STABLE/UNSTABLE)
- Real-time anomaly rate
- Total drift events detected
- Samples processed since last reset

#### Embedded Grafana Dashboard
- Pre-configured ML monitoring dashboards
- Real-time metrics visualization
- Historical trend analysis

### 5.3 Auto-Start Services

The "Start All Services" button launches:

1. **Flask API**: REST backend for predictions
2. **Docker Monitoring Stack**: Prometheus + Grafana containers
3. **Prediction Worker**: Background process for continuous predictions

### 5.4 Prometheus Metrics

The system exposes these metrics at `/metrics`:

| Metric | Type | Description |
|--------|------|-------------|
| `anomaly_detection_predictions_total` | Counter | Total predictions by severity |
| `anomaly_detection_samples_processed_total` | Counter | Total samples processed |
| `anomaly_detection_anomalies_detected_total` | Counter | Total anomalies detected |
| `anomaly_detection_prediction_latency` | Histogram | Prediction time distribution |
| `anomaly_detection_decision_score` | Histogram | Decision function scores |
| `anomaly_detection_f1_score` | Gauge | Current F1 score |
| `anomaly_detection_precision` | Gauge | Current precision |
| `anomaly_detection_recall` | Gauge | Current recall |
| `anomaly_detection_drift_status` | Gauge | Drift detected (1) or stable (0) |
| `anomaly_detection_anomaly_rate` | Gauge | Current window anomaly rate |

---

## 6. Flask API

### 6.1 Overview

**Location**: `src/dashboard/flask_api.py`

REST API backend that serves predictions and statistics to the dashboards.

### 6.2 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check and model status |
| GET | `/api/alerts/recent` | Recent predictions with severity |
| GET | `/api/stats/summary` | Dataset summary statistics |
| GET | `/api/stats/temporal` | Time-based analysis |
| GET | `/api/stats/traffic` | Traffic metrics |
| GET | `/api/stats/geolocation` | IP geolocation data |
| GET | `/api/stream` | Server-sent events for real-time data |
| GET | `/metrics` | Prometheus metrics endpoint |
| POST | `/api/logs/reset` | Reset data stream to beginning |

### 6.3 Geolocation Service

**Location**: `src/dashboard/geolocation_service.py`

Provides IP geolocation lookup for attack source mapping:

```python
def get_location(ip: str) -> dict:
    return {
        "ip": ip,
        "lat": latitude,
        "lon": longitude,
        "country": country_name,
        "city": city_name
    }
```

---

## 7. Quick Start

### 7.1 Train the Model

```bash
python src/model/main.py
```

### 7.2 Launch Real-time Dashboard

```bash
streamlit run src/dashboard/streamlit_app.py
```

The dashboard will:
- Automatically start Flask API
- Load the trained model
- Begin displaying predictions

### 7.3 Launch Monitoring Dashboard

```bash
streamlit run src/dashboard/streamlit_monitoring.py
```

Click "Start All Services" to launch:
- Flask API
- Prometheus (port 9090)
- Grafana (port 3000)
- Prediction Worker

### 7.4 Access Grafana

1. Open http://localhost:3000
2. Login: admin/admin
3. Navigate to "Cyber Anomaly Detection" dashboard

---

## 8. Configuration

### 8.1 Model Parameters

Edit `src/model/oneCSVM_model.py`:

```python
self.model = OneClassSVM(
    kernel="rbf",      # Kernel type
    nu=0.5,            # Sensitivity (0-1)
    gamma="scale",     # Kernel coefficient
)
```

### 8.2 Drift Detection

Edit `src/model/drift_detector.py`:

```python
DriftDetector(
    threshold=0.002,       # ADWIN delta
    window_size=100,       # Sliding window size
    change_threshold=0.08  # 8% change triggers drift
)
```

### 8.3 Dashboard Settings

Edit `src/dashboard/streamlit_app.py`:

```python
API_BASE_URL = "http://localhost:5000/api"
FLASK_PORT = 5000
```

---

## 9. Troubleshooting

### 9.1 Model Not Loading

```bash
# Check if model files exist
ls src/model/*.pkl

# Retrain if missing
python src/model/main.py
```

### 9.2 Flask API Not Starting

```bash
# Check if port is in use
netstat -an | grep 5000

# Start manually
python src/dashboard/flask_api.py
```

### 9.3 Docker Services Not Starting

```bash
# Check Docker status
docker ps

# Start monitoring stack manually
cd monitoring/
docker-compose up -d
```

### 9.4 Grafana Not Loading

1. Ensure Docker is running
2. Check Grafana container: `docker logs grafana`
3. Default credentials: admin/admin

---

**Document Version History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-11 | F. Craievich, L. Jakin, F. Rumiz | Initial document |
