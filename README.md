# Real-Time Cyber Anomaly Detection

[![Documentation](https://img.shields.io/badge/Documentation-View%20Docs-blue?style=flat-square&logo=github)](https://francescacraievich.github.io/real-time-cyber-anomaly-detection/)
&nbsp;&nbsp;
[![CI](https://github.com/francescacraievich/real-time-cyber-anomaly-detection/actions/workflows/ci.yml/badge.svg)](https://github.com/francescacraievich/real-time-cyber-anomaly-detection/actions/workflows/ci.yml)
&nbsp;&nbsp;
[![codecov](https://codecov.io/gh/francescacraievich/real-time-cyber-anomaly-detection/branch/main/graph/badge.svg)](https://codecov.io/gh/francescacraievich/real-time-cyber-anomaly-detection)
&nbsp;&nbsp;
[![Dashboard Alerts](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dashboard-alerts.streamlit.app/)
&nbsp;&nbsp;
[![ML Monitoring](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://monitoring-model.streamlit.app/)

## Overview

A machine learning-based system for detecting cyber anomalies in network traffic using **One-Class SVM**. The application analyzes Suricata IDS logs from T-Pot honeypot and predicts potential security threats in real-time with severity classification (RED/ORANGE/GREEN).

## Key Features

- **One-Class SVM Anomaly Detection**: Trained on normal traffic to identify anomalies
- **Real-time Dashboards**: Two Streamlit dashboards for visualization and monitoring
- **Drift Detection**: ADWIN-based drift detection to monitor model performance over time
- **Prometheus/Grafana Monitoring**: Full ML model monitoring stack with metrics
- **Suricata IDS Integration**: Network intrusion detection logs from T-Pot honeypot
- **Severity Classification**: Three-tier alert system (RED: critical, ORANGE: suspicious, GREEN: normal)

## Dashboards

### Real-time Anomaly Dashboard
Interactive dashboard for visualizing network traffic and anomaly predictions.

**[Open Dashboard](https://dashboard-alerts.streamlit.app/)** | Run locally: `streamlit run src/dashboard/streamlit_app.py`

**Features:**
- Live network traffic visualization
- Severity distribution charts
- Geolocation mapping of traffic sources
- Alert management with filtering

### ML Model Monitoring Dashboard
Technical monitoring dashboard for model performance and drift detection.

**[Open Monitoring](https://monitoring-model.streamlit.app/)** | Run locally: `streamlit run src/dashboard/streamlit_monitoring.py`

**Features:**
- Model performance metrics (F1, Precision, Recall)
- Drift detection status (STABLE/UNSTABLE)
- Embedded Grafana dashboards
- Auto-start for Flask API, Prometheus, and Grafana

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Data Sources  │     │  Feature Engine  │     │   ML Model      │
│  - Suricata IDS │────▶│  - Extraction    │────▶│  - One-Class    │
│    (malicious)  │     │  - Normalization │     │    SVM          │
│  - ISCX (normal)│     │  - Engineering   │     │  - Prediction   │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
┌─────────────────┐     ┌──────────────────┐              │
│   Monitoring    │◀────│  Flask API       │◀─────────────┘
│  - Prometheus   │     │  - /api/stream   │
│  - Grafana      │     │  - /metrics      │
└─────────────────┘     └──────────────────┘
```

## Project Structure

```
├── src/
│   ├── dashboard/              # Streamlit dashboards and Flask API
│   │   ├── streamlit_app.py        # Main anomaly visualization dashboard
│   │   ├── streamlit_monitoring.py # ML model monitoring dashboard
│   │   ├── flask_api.py            # REST API for predictions
│   │   └── prediction_worker.py    # Background prediction worker
│   ├── model/                  # ML model implementation
│   │   ├── oneCSVM_model.py        # One-Class SVM model
│   │   └── drift_detector.py       # ADWIN drift detection
│   ├── monitoring/             # Prometheus/Grafana stack
│   │   ├── metrics.py              # Prometheus metrics registry
│   │   ├── grafana/                # Grafana dashboards
│   │   └── prometheus/             # Prometheus configuration
│   └── feature_engineering/    # Data processing modules
├── data/                   # Raw and processed datasets
├── tests/                  # Unit tests
├── docs/                   # MkDocs documentation
└── docker-compose.yml      # Docker setup for monitoring stack
```

## Getting Started

### Prerequisites

- Python 3.11+
- Docker (for Prometheus/Grafana monitoring)

### Installation

```bash
git clone https://github.com/francescacraievich/real-time-cyber-anomaly-detection.git
cd real-time-cyber-anomaly-detection
pip install -r requirements.txt
```

### Quick Start

1. **Train the model** (if not already trained):
   ```bash
   python src/model/main.py
   ```

2. **Launch the dashboard**:
   ```bash
   streamlit run src/dashboard/streamlit_app.py
   ```

3. **Or launch the monitoring dashboard** (starts all services automatically):
   ```bash
   streamlit run src/dashboard/streamlit_monitoring.py
   ```

## Documentation

Full documentation available at [francescacraievich.github.io/real-time-cyber-anomaly-detection](https://francescacraievich.github.io/real-time-cyber-anomaly-detection/)

## License

This project is open source and available for educational and research purposes.
