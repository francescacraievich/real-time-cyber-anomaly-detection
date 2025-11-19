# Real-Time Cyber Anomaly Detection

[![Documentation](https://img.shields.io/badge/Documentation-View%20Docs-blue?style=flat-square&logo=github)](https://francescacraievich.github.io/real-time-cyber-anomaly-detection/)
&nbsp;&nbsp;
[![CI](https://img.shields.io/github/actions/workflow/status/francescacraievich/real-time-cyber-anomaly-detection/ci.yml?label=CI&logo=github&style=flat-square)](https://github.com/francescacraievich/real-time-cyber-anomaly-detection/actions/workflows/ci.yml)

## Overview

A machine learning-based system for detecting cyber anomalies in network traffic through statistical analysis. This application analyzes network traffic patterns from multiple honeypot sources and predicts potential security threats in real-time.

## What It Does

The application monitors and analyzes network traffic to identify anomalous behavior that could indicate:
- Malicious attacks
- Unusual traffic patterns
- Security breaches
- Potential threats

By processing logs from honeypots (Dionaea, Suricata, Cowrie) and normal traffic data, the system uses statistical features to train machine learning models that can distinguish between benign and malicious network activity.

## Key Features

- **Multi-source Data Processing**: Handles logs from multiple honeypot systems (Dionaea, Suricata, Cowrie)
- **Feature Engineering**: Extracts and processes statistical features from network traffic
- **Anomaly Detection**: Uses machine learning to identify abnormal traffic patterns
- **Real-time Analysis**: Designed for real-time threat detection
- **Automated Data Pipeline**: Streamlined data collection, processing, and analysis

## Data Sources

The system processes network traffic data from:
- **Dionaea** (6,287 log entries): Low-interaction honeypot for capturing malware
- **Suricata** (71,679 log entries): Network threat detection engine
- **Cowrie**: SSH/Telnet honeypot for logging brute force attacks
- **Normal Traffic**: Benign network traffic for baseline comparison

## Architecture

```
Data Collection → Feature Engineering → Model Training → Anomaly Detection
     ↓                    ↓                   ↓                ↓
  Honeypots      Extract Features      ML Models      Predict Threats
```

## Documentation

Full documentation is available at [francescacraievich.github.io/real-time-cyber-anomaly-detection](https://francescacraievich.github.io/real-time-cyber-anomaly-detection/)

## Project Structure

- [`data/`](data/) - Raw honeypot logs and network traffic data
- [`feature_engineering/`](feature_engineering/) - Data processing and feature extraction modules
- [`docs/`](docs/) - Project documentation
- [`useful_scripts/`](useful_scripts/) - Utility scripts for data handling

## Getting Started

### Prerequisites

- Python 3.x
- Required libraries: pandas, numpy, scikit-learn (see requirements)

### Installation

```bash
git clone https://github.com/francescacraievich/real-time-cyber-anomaly-detection.git
cd real-time-cyber-anomaly-detection
pip install -r requirements.txt
```

## License

This project is open source and available for educational and research purposes.
