# Real-Time Cyber Anomaly Detection

Welcome to the documentation for the real-time network anomaly detection system.

## Project Overview

This project implements an advanced anomaly detection system for network security using **One-Class SVM** machine learning and real-time analysis. The system uses two data sources: **Suricata IDS logs** from T-Pot honeypot (malicious traffic) and **ISCX dataset** (normal traffic). It predicts potential security threats with severity classification (RED/ORANGE/GREEN).

## Key Features

- **One-Class SVM Anomaly Detection**: Trained on normal traffic to identify anomalies (90.7% TPR, 10% FPR)
- **Real-time Dashboards**: Two Streamlit dashboards for visualization and monitoring
- **Drift Detection**: ADWIN-based drift detection to monitor model performance
- **Prometheus/Grafana Monitoring**: Full ML model monitoring stack
- **Dual Data Sources**: Suricata IDS (malicious) + ISCX dataset (normal traffic)
- **Severity Classification**: Three-tier alert system (RED: critical, ORANGE: warning, GREEN: normal)

## Live Dashboards

- [Real-time Anomaly Dashboard](https://dashboard-anomalydetection.streamlit.app/) - Main visualization
- [ML Monitoring Dashboard](https://monitoring-model.streamlit.app/) - Model performance monitoring

## Project Documents

- [System Specification](system_specification.md) - Complete SSD with requirements and architecture
- [Project Proposal](project_proposal.md) - Development plan, milestones, and WBS
- [Operational Governance](operational_governance.md) - Version control, CI/CD, and monitoring

## Technical Documentation

- [Operations Guide](operations_guide.md) - Commands, formulas, and technical setup
- [Honeypot Guide](HONEYPOT_GUIDE.md) - Overview and purpose of T-Pot honeypots

## Quick Start

```bash
# Clone the repository
git clone https://github.com/francescacraievich/real-time-cyber-anomaly-detection.git
cd real-time-cyber-anomaly-detection

# Install dependencies
pip install -r requirements.txt

# Train the model (if not already trained)
python src/model/main.py

# Launch the dashboard
streamlit run src/dashboard/streamlit_app.py
```

## Project Structure

```
├── src/                    # Source code
│   ├── dashboard/          # Streamlit apps and Flask API
│   ├── model/              # ML model implementation
│   ├── monitoring/         # Prometheus metrics
│   └── feature_engineering/ # Data processing
├── tests/                  # Unit tests (116 tests)
├── data/                   # Datasets
└── docs/                   # Documentation
```

## Security

This project implements security best practices:

- **Code Scanning**: GitHub CodeQL for vulnerability detection
- **Secret Scanning**: Automatic detection of committed secrets
- **Minimal Permissions**: CI workflows run with read-only access
- **No Debug Mode**: Flask API runs securely in production

See the [Security Policy](https://github.com/francescacraievich/real-time-cyber-anomaly-detection/blob/main/SECURITY.md) for reporting vulnerabilities.

## Contributing

To contribute to this project, please check the guidelines in the GitHub repository.
