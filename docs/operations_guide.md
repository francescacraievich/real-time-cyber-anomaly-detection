# Operations Guide

## Real-Time Cyber Anomaly Detection System

**Version:** 1.0
**Date:** 2025-12-12

---

## 1. Prerequisites

**Python**: 3.11+

**Install dependencies**:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Docker** (for monitoring stack): Docker Desktop or Docker Engine

---

## 2. Project Structure

```
├── src/
│   ├── feature_engineering/
│   │   ├── initializers/           # DataFrame initialization
│   │   ├── formatters/             # Data formatting
│   │   ├── precalculation_functions/  # Feature calculations
│   │   └── aggregation_functions/  # Metrics aggregation
│   ├── model/
│   │   ├── oneCSVM_model.py        # One-Class SVM implementation
│   │   ├── drift_detector.py       # ADWIN drift detection
│   │   └── main.py                 # Training entry point
│   ├── dashboard/
│   │   ├── streamlit_app.py        # Anomaly dashboard
│   │   ├── streamlit_monitoring.py # ML monitoring dashboard
│   │   ├── flask_api.py            # REST API backend
│   │   └── geolocation_service.py  # IP geolocation
│   └── monitoring/
│       └── metrics.py              # Prometheus metrics
├── data/
│   ├── suricata/                   # Malicious traffic logs
│   └── normal_traffic/             # Benign traffic dataset
├── monitoring/
│   ├── docker-compose.yml          # Prometheus + Grafana
│   └── grafana/                    # Dashboard configs
└── tests/                          # Unit tests
```

---

## 3. Data Preparation

### 3.1 Dataset Locations

| Dataset | Location | Format |
|---------|----------|--------|
| Suricata (malicious) | `data/suricata/eve.json` | JSON |
| Normal traffic | `data/normal_traffic/benign_traffic_fixed.json.gz` | Gzip JSON |
| Combined dataset | `data/combined_dataset.csv` | CSV |

### 3.2 Building the Combined Dataset

The data pipeline processes raw logs through these stages:

```
1. Initialize DataFrames
   └── init_suricata_df() / init_normal_traffic()

2. Format columns
   └── format_suricata_df() / format_normal_traffic()

3. Calculate derived features
   └── precalculation_functions/*

4. Aggregate metrics
   └── aggregation_functions/*

5. Export to CSV
   └── combined_dataset.csv
```

### 3.3 Feature Engineering Formulas

**Rate Features**:
```
bytes_per_second = (bytes_sent + bytes_received) / duration
pkts_per_second = (pkts_sent + pkts_received) / duration
bytes_per_packet = (bytes_sent + bytes_received) / (pkts_sent + pkts_received)
```

**Ratio Features**:
```
bytes_ratio = bytes_sent / bytes_received  (if bytes_received > 0, else 0)
pkts_ratio = pkts_sent / pkts_received    (if pkts_received > 0, else 0)
```

**Temporal Features**:
```
hour = timestamp.hour                    # 0-23
day_of_week = timestamp.dayofweek        # 0=Monday, 6=Sunday
is_weekend = 1 if day_of_week >= 5 else 0
is_business_hours = 1 if 9 <= hour <= 17 and not is_weekend else 0
```

**IP Classification**:
```
src_is_private = 1 if source_ip in private_ranges else 0
dst_is_private = 1 if destination_ip in private_ranges else 0
is_internal = 1 if src_is_private and dst_is_private else 0

# Private ranges: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
```

**Port Categorization**:
```
common_ports = [20, 21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432, 8080]
dst_port_is_common = 1 if destination_port in common_ports else 0
```

---

## 4. Model Training

### 4.1 Train the Model

```bash
python src/model/main.py
```

This will:
1. Load benign traffic from `data/normal_traffic/`
2. Apply preprocessing (RobustScaler + OneHotEncoder)
3. Train One-Class SVM with RBF kernel
4. Calibrate threshold on validation set
5. Save artifacts to `src/model/`

### 4.2 Model Hyperparameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `kernel` | `rbf` | Radial Basis Function |
| `nu` | `0.2` | Upper bound on training errors |
| `gamma` | `scale` | Kernel coefficient: `1 / (n_features * X.var())` |
| `contamination` | `0.1` | Expected outlier proportion for threshold |
| `max_train_samples` | `10000` | Max samples (SVM scales O(n²)) |

### 4.3 Model Artifacts

| File | Content |
|------|---------|
| `oneclass_svm_model.pkl` | Trained SVM model |
| `oneclass_svm_preprocessor.pkl` | ColumnTransformer (scaler + encoder) |
| `oneclass_svm_config.pkl` | Threshold, feature names, hyperparameters |

### 4.4 Severity Classification

```
decision_score = model.decision_function(X)

if score < threshold - 0.5:
    severity = "RED"      # Critical anomaly
elif score < threshold:
    severity = "ORANGE"   # Suspicious
else:
    severity = "GREEN"    # Normal
```

---

## 5. Running the Dashboards

### 5.1 Real-time Anomaly Dashboard

```bash
streamlit run src/dashboard/streamlit_app.py
```

- **URL**: http://localhost:8501
- **Live**: https://dashboard-anomalydetection.streamlit.app/

The dashboard auto-starts Flask API on port 5000.

### 5.2 ML Monitoring Dashboard

```bash
streamlit run src/dashboard/streamlit_monitoring.py
```

- **URL**: http://localhost:8502
- **Live**: https://monitoring-model.streamlit.app/

### 5.3 Flask API Only

```bash
python src/dashboard/flask_api.py
```

- **URL**: http://localhost:5000
- **Metrics**: http://localhost:5000/metrics

---

## 6. Monitoring Stack (Docker)

### 6.1 Start Prometheus & Grafana

```bash
cd monitoring/
docker-compose up -d
```

### 6.2 Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin / admin |

### 6.3 Stop Services

```bash
cd monitoring/
docker-compose down
```

---

## 7. Drift Detection Configuration

### 7.1 ADWIN Parameters

```python
DriftDetector(
    threshold=0.002,       # ADWIN delta (sensitivity)
    window_size=100,       # Sliding window for anomaly rate
    change_threshold=0.08  # 8% change triggers drift
)
```

### 7.2 Auto-Retraining

Retraining triggers when:
- Drift detected (ADWIN or threshold-based)
- Retrain buffer has >1000 samples

---

## 8. Running Tests

```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=term

# Specific suite
pytest tests/test_model/
pytest tests/test_precalculations/
pytest tests/test_dashboard/
```

---

## 9. Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint
flake8 src/ tests/

# All checks (as in CI)
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
```

---

## 10. Troubleshooting

### Model Not Loading

```bash
# Check if model files exist
ls src/model/*.pkl

# Retrain if missing
python src/model/main.py
```

### Flask API Not Starting

```bash
# Check if port is in use
netstat -an | findstr 5000   # Windows
netstat -an | grep 5000      # Linux/Mac

# Kill process on port
taskkill /F /PID <pid>       # Windows
kill -9 <pid>                # Linux/Mac

# Start manually
python src/dashboard/flask_api.py
```

### Docker Services Not Starting

```bash
# Check Docker status
docker ps

# View logs
docker logs prometheus
docker logs grafana

# Restart
cd monitoring/
docker-compose down
docker-compose up -d
```

### Grafana Not Accessible

1. Ensure Docker is running
2. Check container: `docker logs grafana`
3. Default login: admin / admin
4. Reset password if needed via Grafana UI

---

## 11. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_PORT` | `5000` | Flask API port |
| `PROMETHEUS_PORT` | `9090` | Prometheus port |
| `GRAFANA_PORT` | `3000` | Grafana port |

---

## 12. API Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/alerts/recent` | GET | Recent predictions |
| `/api/stats/summary` | GET | Protocol/port stats |
| `/api/stats/temporal` | GET | Time-based analysis |
| `/api/stats/traffic` | GET | Traffic metrics |
| `/api/stats/geolocation` | GET | IP geolocation |
| `/api/stream` | GET | SSE real-time stream |
| `/metrics` | GET | Prometheus metrics |
| `/api/logs/reset` | POST | Reset data stream |
