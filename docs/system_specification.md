# System Specification Document (SSD)

## Real-Time Cyber Anomaly Detection System

**Version:** 1.0
**Date:** 2025-11-29
**Authors:** Francesca Craievich, Lucas Jakin, Francesco Rumiz

---

## 1. Introduction

### 1.1 Purpose
The Real-Time Cyber Anomaly Detection System is designed to identify malicious network traffic patterns and security threats in real-time by analyzing logs from multiple honeypot sources and normal network traffic. The system leverages machine learning techniques, specifically One-Class SVM, to distinguish between benign and anomalous network behavior.

### 1.2 Scope
This document describes the functional and non-functional requirements, system architecture, data specifications, and risk analysis for the Real-Time Cyber Anomaly Detection platform. The system targets network security monitoring in enterprise environments and research contexts.

### 1.3 Definitions and Acronyms
- **SSD**: System Specification Document
- **OCSVM**: One-Class Support Vector Machine
- **IDS**: Intrusion Detection System
- **FPR**: False Positive Rate
- **TPR**: True Positive Rate (Detection Rate)
- **TPOT**: The Pitch Over Time honeypot platform
- **NFR**: Non-Functional Requirement
- **FR**: Functional Requirement

---

## 2. Problem Definition

### 2.1 Problem Statement
Network administrators and security teams face increasing challenges in detecting cyber threats in real-time. Traditional signature-based detection systems fail to identify novel attack patterns and zero-day exploits. There is a critical need for an intelligent system that can:

- Detect anomalous network behavior without predefined attack signatures
- Process high-volume network traffic streams in real-time
- Minimize false positives while maintaining high detection rates
- Provide actionable alerts for security personnel

### 2.2 Current Challenges
- **Volume**: Network traffic generates massive amounts of log data (71,679+ Suricata events)
- **Velocity**: Real-time processing requirements for timely threat detection
- **Variety**: Multiple log formats from different honeypot systems (Dionaea, Suricata, Cowrie)
- **Novelty**: Unknown attack patterns that signature-based systems cannot detect

### 2.3 Proposed Solution
A machine learning-based anomaly detection system that:
- Uses unsupervised learning (One-Class SVM) to identify outliers in network traffic
- Processes logs from multiple honeypot sources for comprehensive threat coverage
- Extracts statistical features from network traffic for model training
- Provides real-time classification of traffic as normal or anomalous

---

## 3. Data Specification

### 3.1 Data Sources

#### 3.1.1 Honeypot Logs (Malicious Traffic)
The system collects malicious traffic data from three honeypot systems:

**Dionaea**
- **Volume**: 6,287 log entries
- **Purpose**: Low-interaction honeypot for capturing malware
- **Format**: JSON
- **Location**: `data/dionaea/dionaea.json`
- **Key Attributes**: timestamp, source IP, destination port, protocol, payload

**Suricata**
- **Volume**: 71,679 log entries
- **Purpose**: Network threat detection engine
- **Format**: JSON
- **Location**: `data/suricata/log/suricata.json`
- **Key Attributes**: alert severity, signature, flow metadata, packet info

**Cowrie**
- **Volume**: Variable
- **Purpose**: SSH/Telnet honeypot for brute force attack logging
- **Format**: JSON
- **Location**: `data/cowrie/cowrie.json`
- **Key Attributes**: session ID, username attempts, commands executed

#### 3.1.2 Normal Traffic Dataset
- **Source**: Benign network traffic baseline
- **Format**: Compressed JSON (gzip)
- **Location**: `data/normal_traffic/benign_traffic_fixed.json.gz`
- **Sample Size**: Configurable (default: 10,000 samples)
- **Purpose**: Training baseline for normal behavior patterns

### 3.2 Data Collection Pipeline
1. **Extraction**: Logs collected from TPOT honeypot platform
2. **Preprocessing**: JSON parsing, invalid value replacement (NaN, Infinity → null)
3. **Sampling**: Controlled sampling using ijson for memory efficiency
4. **Storage**: Local filesystem with gzip compression for space optimization

### 3.3 Feature Engineering
Statistical features extracted from raw logs:

- **Network Features**: Protocol distribution, port frequencies, packet sizes
- **Temporal Features**: Time-based patterns, session duration, inter-arrival times
- **Behavioral Features**: Connection patterns, payload characteristics
- **Aggregated Metrics**: Per-IP statistics, per-port statistics

Processing pipeline location: `feature_engineering/`

---

## 4. System Requirements

### 4.1 Functional Requirements

**FR-01: Data Ingestion**
The system shall ingest JSON log files from Dionaea, Suricata, and Cowrie honeypots.

**FR-02: Normal Traffic Processing**
The system shall process compressed (gzip) and uncompressed normal traffic datasets with configurable sample sizes.

**FR-03: Feature Extraction**
The system shall extract statistical features from raw network logs including protocol, port, IP, and temporal information.

**FR-04: Model Training**
The system shall train a One-Class SVM model using normal traffic data as the baseline.

**FR-05: Anomaly Detection**
The system shall classify incoming network traffic as normal or anomalous with probability scores.

**FR-06: Alert Generation**
The system shall generate alerts when anomalous traffic is detected above a configurable threshold.

**FR-07: Data Preprocessing**
The system shall handle invalid JSON values (NaN, Infinity, -Infinity) by replacing them with null values.

**FR-08: Memory-Efficient Processing**
The system shall use streaming JSON parsing (ijson) to handle large datasets without loading entire files into memory.

### 4.2 Non-Functional Requirements

**NFR-01: Detection Performance**
The system shall achieve a minimum True Positive Rate (TPR) of 85% with a maximum False Positive Rate (FPR) of 15%.

**NFR-02: Processing Latency**
The system shall classify a single network event within 100 milliseconds from feature extraction to prediction.

**NFR-03: Throughput**
The system shall process a minimum of 1,000 network events per second.

**NFR-04: Data Loading Time**
Feature extraction and DataFrame initialization shall complete within 5 seconds for datasets up to 10,000 samples.

**NFR-05: Model Training Time**
One-Class SVM model training shall complete within 60 seconds for datasets up to 10,000 samples.

**NFR-06: Availability**
The system shall maintain 99% uptime during operational hours.

**NFR-07: Scalability**
The system shall support horizontal scaling to handle increased traffic volumes.

**NFR-08: Data Privacy**
The system shall comply with data protection regulations by anonymizing sensitive information in logs.

**NFR-09: Resource Utilization**
The system shall operate within 4GB RAM and 2 CPU cores for baseline deployment.

**NFR-10: Model Performance Degradation**
The system shall trigger retraining alerts when detection accuracy drops below 80%.

---

## 5. System Architecture

### 5.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Collection Layer                     │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│  Dionaea    │  Suricata   │   Cowrie    │  Normal Traffic     │
│  Honeypot   │     IDS     │  Honeypot   │     Dataset         │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────────────┘
       │             │             │             │
       └─────────────┴─────────────┴─────────────┘
                         │
       ┌─────────────────▼─────────────────────────┐
       │       Feature Engineering Layer           │
       │  - JSON Parsing (ijson)                   │
       │  - Data Preprocessing                     │
       │  - Feature Extraction                     │
       │  - DataFrame Initialization               │
       └─────────────────┬─────────────────────────┘
                         │
       ┌─────────────────▼─────────────────────────┐
       │         Machine Learning Layer            │
       │  - One-Class SVM Training                 │
       │  - Model Persistence (pickle/joblib)      │
       │  - Anomaly Scoring                        │
       └─────────────────┬─────────────────────────┘
                         │
       ┌─────────────────▼─────────────────────────┐
       │          Detection & Alert Layer          │
       │  - Real-time Classification               │
       │  - Threshold-based Alerting               │
       │  - Event Logging                          │
       └───────────────────────────────────────────┘
```

### 5.2 Component Descriptions

#### 5.2.1 Data Initialization Module
**Location**: `feature_engineering/df_initializing/`

**Components**:
- `init_suricata_df.py`: Suricata log DataFrame initializer
- `init_normal_traffic_df.py`: Normal traffic DataFrame initializer with gzip support
- `handler_init_dfs.py`: Orchestrates DataFrame initialization for all sources

**Responsibilities**:
- Parse JSON logs using streaming approach (ijson)
- Handle compressed and uncompressed files
- Preprocess invalid numeric values
- Initialize pandas DataFrames for downstream processing

#### 5.2.2 Feature Engineering Module
**Location**: `feature_engineering/df_formatting/`

**Components**:
- `format_suricata_df.py`: Suricata-specific feature extraction
- `format_normal_traffic.py`: Normal traffic feature extraction
- `handler_df_formatter.py`: Coordinates formatting across all data sources
- `aggregation_functions.py`: Statistical aggregation utilities
- `precalculations_functions.py`: Pre-computed feature calculations

**Responsibilities**:
- Extract statistical features from raw logs
- Normalize and standardize features
- Handle missing values and outliers
- Create feature vectors for ML models

#### 5.2.3 Model Training & Inference Module
**Location**: `model/`

**Components**:
- `oneCSVM_model.py`: One-Class SVM implementation
- Model persistence (pickle/joblib)
- Hyperparameter configuration

**Responsibilities**:
- Train One-Class SVM on normal traffic baseline
- Serialize trained models for deployment
- Perform anomaly detection inference
- Calculate anomaly scores and decision functions

#### 5.2.4 Utility Functions
**Location**: `util_functions/`

**Responsibilities**:
- Common data processing utilities
- Logging and monitoring helpers
- Configuration management

### 5.3 Data Flow

1. **Ingestion**: Raw JSON logs from honeypots and normal traffic sources
2. **Parsing**: Streaming JSON parsing with ijson for memory efficiency
3. **Preprocessing**: Invalid value replacement, data cleaning
4. **Feature Extraction**: Statistical feature computation
5. **Model Training**: One-Class SVM training on normal traffic baseline
6. **Inference**: Real-time anomaly detection on new traffic
7. **Alert Generation**: Threshold-based alert triggering

### 5.4 Technology Stack

**Programming Language**: Python 3.11+

**Core Libraries**:
- `pandas==2.3.3`: Data manipulation and analysis
- `numpy==2.3.5`: Numerical computing
- `scikit-learn`: Machine learning (One-Class SVM)
- `ijson==3.4.0.post0`: Streaming JSON parser

**Development Tools**:
- `pytest==9.0.1`: Unit testing framework
- `mkdocs==1.6.1`: Documentation generation
- `mkdocs-material==9.7.0`: Documentation theme

**CI/CD**:
- GitHub Actions for automated testing and documentation deployment

**Version Control**: Git with GitHub

---

## 6. Model Specification

### 6.1 Algorithm Selection
**One-Class Support Vector Machine (OCSVM)**

**Rationale**:
- Unsupervised anomaly detection approach
- Effective for high-dimensional feature spaces
- Does not require labeled malicious traffic for training
- Learns decision boundary around normal behavior
- Robust to outliers in training data

### 6.2 Training Strategy
- **Training Data**: Normal traffic baseline only
- **Validation**: Holdout set from honeypot logs
- **Hyperparameters**: Kernel (RBF), nu (outlier fraction), gamma (kernel coefficient)

### 6.3 Performance Metrics
- **True Positive Rate (TPR)**: Percentage of correctly detected anomalies
- **False Positive Rate (FPR)**: Percentage of normal traffic misclassified as anomalous
- **F1-Score**: Harmonic mean of precision and recall
- **ROC-AUC**: Area under the receiver operating characteristic curve

### 6.4 Current Performance
Based on existing implementation (`model/oneCSVM_model.py`):
- **Detection Rate**: 90.7%
- **False Alarm Rate**: 10%
- **F1-Score**: 0.885

---

## 7. Risk Analysis

### 7.1 Technical Risks

**RISK-01: Model Drift**
- **Description**: Model performance degrades over time as attack patterns evolve
- **Impact**: High - Reduced detection accuracy
- **Probability**: High
- **Mitigation**:
  - Implement continuous model monitoring
  - Schedule periodic retraining (monthly)
  - Track performance metrics in production
  - Trigger automatic retraining when accuracy drops below 80%

**RISK-02: High False Positive Rate**
- **Description**: Excessive false alarms cause alert fatigue
- **Impact**: Medium - Reduced trust in system
- **Probability**: Medium
- **Mitigation**:
  - Tune decision threshold based on operational requirements
  - Implement multi-stage alert validation
  - Collect feedback loop for false positive analysis
  - Adjust model hyperparameters (nu parameter)

**RISK-03: Data Quality Issues**
- **Description**: Corrupted or incomplete logs affect model training
- **Impact**: High - Poor model performance
- **Probability**: Medium
- **Mitigation**:
  - Implement robust data validation pipelines
  - Handle missing values and invalid JSON gracefully
  - Monitor data quality metrics (completeness, consistency)
  - Reject datasets below quality thresholds

**RISK-04: Scalability Bottlenecks**
- **Description**: System cannot handle peak traffic volumes
- **Impact**: High - Missed threat detection
- **Probability**: Medium
- **Mitigation**:
  - Design for horizontal scaling
  - Implement load balancing and queueing
  - Use streaming processing for large datasets
  - Optimize feature extraction performance

**RISK-05: Novel Attack Patterns**
- **Description**: Zero-day attacks not represented in training data
- **Impact**: High - Undetected threats
- **Probability**: High
- **Mitigation**:
  - Combine ML-based detection with rule-based systems
  - Implement ensemble methods
  - Regular model updates with new threat intelligence
  - Human-in-the-loop validation for edge cases

### 7.2 Operational Risks

**RISK-06: Honeypot Detection**
- **Description**: Attackers identify and avoid honeypots
- **Impact**: Medium - Reduced data collection
- **Probability**: Medium
- **Mitigation**:
  - Use diverse honeypot configurations
  - Regularly update honeypot signatures
  - Deploy decoy services alongside production systems

**RISK-07: Resource Exhaustion**
- **Description**: DDoS attacks overwhelm processing capacity
- **Impact**: Medium - System unavailability
- **Probability**: Low
- **Mitigation**:
  - Implement rate limiting
  - Deploy auto-scaling infrastructure
  - Set resource quotas and circuit breakers

**RISK-08: Model Poisoning**
- **Description**: Malicious data injected into training pipeline
- **Impact**: High - Compromised detection capability
- **Probability**: Low
- **Mitigation**:
  - Validate training data sources
  - Implement data provenance tracking
  - Use secure data collection pipelines
  - Regular audit of training datasets

---

## 8. Quality Attributes

### 8.1 Maintainability
- Modular architecture with clear separation of concerns
- Comprehensive documentation using MkDocs
- Unit tests with pytest framework
- CI/CD pipeline for automated testing

### 8.2 Reliability
- Robust error handling for malformed logs
- Graceful degradation under high load
- Automated health checks and monitoring

### 8.3 Performance
- Streaming JSON parsing for memory efficiency
- Optimized feature extraction algorithms
- Model inference within 100ms latency target

### 8.4 Security
- No storage of sensitive user data
- Anonymization of IP addresses where required
- Secure model artifact storage

---

## 9. Constraints and Assumptions

### 9.1 Constraints
- System operates on local filesystem (no cloud deployment in v1.0)
- Limited to Python-based implementation
- Requires pre-collected log data (no live network capture)
- Single-node deployment in initial version

### 9.2 Assumptions
- Honeypot logs represent realistic attack patterns
- Normal traffic dataset is free from malicious activity
- Attack patterns remain relatively stable over short periods (weeks)
- System operates in controlled environment with known data sources

---

## 10. Future Enhancements

### 10.1 Planned Features
- **Real-time Stream Processing**: Integration with Apache Kafka or MQTT
- **Interactive Dashboard**: Streamlit or Grafana visualization
- **Multi-model Ensemble**: Combine OCSVM with Isolation Forest, Autoencoders
- **Automated Retraining Pipeline**: Continuous learning from new data
- **Alert Notification System**: Email, Slack, webhook integrations
- **Explainable AI**: SHAP/LIME for anomaly explanation

### 10.2 Scalability Roadmap
- Distributed processing with Apache Spark
- Cloud deployment (AWS, Azure, GCP)
- Kubernetes orchestration for auto-scaling
- Time-series database integration (InfluxDB)

---

## 11. References

### 11.1 External Resources
- TPOT Honeypot Platform: https://github.com/telekom-security/tpotce
- Suricata IDS Documentation: https://suricata.io/
- One-Class SVM: Schölkopf et al., "Support Vector Method for Novelty Detection"

### 11.2 Related Documentation
- [Project Overview](overview.md)
- [Data Collection Guide](data_collection.md)
- [Feature Engineering](feature_engineering.md)
- [Honeypot Guide](HONEYPOT_GUIDE.md)

---

**Document Version History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-29 | F. Craievich, L. Jakin, F. Rumiz | Initial SSD creation |
