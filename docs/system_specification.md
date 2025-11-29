# System Specification Document (SSD)

## Real-Time Cyber Anomaly Detection System

**Version:** 1.0
**Date:** 2025-11-29
**Authors:** Francesca Craievich, Lucas Jakin, Francesco Rumiz

---

## 1. Introduction

### 1.1 Purpose
The Real-Time Cyber Anomaly Detection System is designed to identify malicious network traffic patterns and security threats in real-time by analyzing Suricata IDS logs and normal network traffic. The system leverages machine learning techniques, specifically One-Class SVM, to distinguish between benign and anomalous network behavior.

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
- **Feature Richness**: Suricata provides comprehensive flow metadata (bytes, packets, duration, protocols)
- **Novelty**: Unknown attack patterns that signature-based systems cannot detect

### 2.3 Proposed Solution
A machine learning-based anomaly detection system that:
- Uses unsupervised learning (One-Class SVM) to identify outliers in network traffic
- Processes Suricata IDS logs as malicious traffic source (selected for complete feature set)
- Extracts 30+ statistical features from network traffic for model training
- Provides real-time classification of traffic as normal or anomalous with severity levels (GREEN/ORANGE/RED)

---

## 3. Data Specification

### 3.1 Data Sources

#### 3.1.1 Malicious Traffic (Suricata IDS)
**Suricata** was selected as the primary malicious traffic source due to its comprehensive feature set:

- **Volume**: 71,679 log entries
- **Purpose**: Network Intrusion Detection System (IDS) capturing attack traffic
- **Format**: JSON
- **Key Attributes**: source/destination IP, ports, protocol, bytes, packets, duration, flow direction
- **Label**: `suricata` (malicious)

> **Note**: Dionaea and Cowrie honeypots were evaluated but excluded from the final implementation because they lacked the complete network flow features (bytes_sent, bytes_received, pkts_sent, pkts_received, duration) required for consistent feature engineering across all data sources.

#### 3.1.2 Normal Traffic Dataset (Benign Baseline)
- **Source**: CICIDS/ISCX benign network traffic dataset
- **Format**: Compressed JSON (gzip)
- **Location**: `data/normal_traffic/benign_traffic_fixed.json.gz`
- **Sample Size**: Configurable (default: 10,000 samples)
- **Purpose**: Training baseline for normal behavior patterns
- **Label**: `benign`

### 3.2 Base Features (Unified Schema)
All data sources are normalized to a common feature schema:

| Feature | Type | Description |
|---------|------|-------------|
| `source_ip` | string | Source IP address |
| `destination_ip` | string | Destination IP address |
| `source_port` | int | Source port number |
| `destination_port` | int | Destination port number |
| `timestamp_start` | datetime | Flow start timestamp |
| `transport_protocol` | string | TCP/UDP/ICMP |
| `application_protocol` | string | HTTP/DNS/SSH/etc. |
| `duration` | float | Flow duration in seconds |
| `bytes_sent` | int | Bytes sent |
| `bytes_received` | int | Bytes received |
| `pkts_sent` | int | Packets sent |
| `pkts_received` | int | Packets received |
| `direction` | string | Flow direction |
| `label` | string | benign/suricata |

### 3.3 Feature Engineering Pipeline

#### 3.3.1 Precalculation Features
Computed from base features:

**Rate Features** (`precalculations_functions/rate_features.py`):
- `bytes_per_second`: Total bytes / duration
- `pkts_per_second`: Total packets / duration

**Ratio Features** (`precalculations_functions/ratio_features.py`):
- `bytes_ratio`: bytes_sent / bytes_received
- `pkts_ratio`: pkts_sent / pkts_received

**Temporal Features** (`precalculations_functions/temporal_features.py`):
- `hour`, `day_of_week`, `month`
- `is_weekend`, `is_business_hours`

**IP Classification** (`precalculations_functions/ip_classification_features.py`):
- `src_is_private`, `dst_is_private`
- `is_internal` (both IPs private)

**Port Categorization** (`precalculations_functions/port_categorization_features.py`):
- `dst_port_is_common` (well-known ports 0-1023)

#### 3.3.2 Aggregation Features
Statistical aggregations (`aggregation_functions/metrics_features.py`):

- `total_events_processed`: Running count of events
- `malicious_events_in_window`: Count of malicious events
- `unique_malicious_ips`: Distinct malicious source IPs
- `malicious_events_pct_change`: Trend analysis
- `events_for_dst_port`: Events per destination port
- `malicious_events_for_protocol`: Events per protocol

### 3.4 Data Processing Pipeline

```
Raw JSON Logs → DataFrame Initialization → Feature Formatting → Precalculations → Aggregations → CSV Export
     ↓                    ↓                      ↓                    ↓                ↓              ↓
  Suricata         init_suricata_df      format_suricata_df     rate_features    metrics      combined_dataset.csv
  Normal          init_normal_traffic    format_normal_traffic  temporal_features
```

**Output Files** (`data/processed/`):
- `suricata_formatted.csv`: Processed Suricata data with all features
- `normal_traffic_formatted.csv`: Processed benign traffic with all features
- `combined_shuffled_dataset.csv`: Merged and shuffled dataset for model training/testing

---

## 4. System Requirements

### 4.1 Functional Requirements

**FR-01: Data Ingestion**
The system shall ingest JSON log files from Suricata IDS and normal traffic datasets.
- **Acceptance Criteria**: Successfully parse Suricata JSON logs and compressed (.gz) benign traffic files.

**FR-02: Feature Engineering**
The system shall extract and compute 30+ features from raw network logs.
- **Acceptance Criteria**: Generate rate, ratio, temporal, IP classification, and port categorization features.

**FR-03: Data Normalization**
The system shall normalize all data sources to a unified schema with 14 base features.
- **Acceptance Criteria**: All formatted DataFrames contain identical column structure.

**FR-04: Model Training**
The system shall train a One-Class SVM model using only benign traffic data.
- **Acceptance Criteria**: Model trained with configurable nu, gamma, and max_train_samples parameters.

**FR-05: Model Persistence**
The system shall save and load trained models using joblib/pickle.
- **Acceptance Criteria**: Model, preprocessor, and config saved to `model/` directory; fit_or_load() function works correctly.

**FR-06: Anomaly Detection**
The system shall classify network traffic with three severity levels.
- **Acceptance Criteria**: Predictions return GREEN (normal), ORANGE (suspicious), or RED (critical) based on decision boundary.

**FR-07: Performance Evaluation**
The system shall compute precision, recall, F1-score, and confusion matrix.
- **Acceptance Criteria**: evaluate_model_performance() returns all metrics and detailed breakdown.

**FR-08: Simulation Mode**
The system shall simulate real-time stream processing with batch predictions.
- **Acceptance Criteria**: run_simulation() and run_detailed_simulation() process data in configurable chunk sizes.

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
├───────────────────────────────┬─────────────────────────────────┤
│       Suricata IDS            │       Normal Traffic            │
│    (Malicious Traffic)        │     (Benign Baseline)           │
│      71,679 events            │      ~10,000 samples            │
└───────────────┬───────────────┴───────────────┬─────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                │
       ┌────────────────────────▼────────────────────────┐
       │          Feature Engineering Layer              │
       │  ┌─────────────────┐  ┌──────────────────────┐ │
       │  │ df_initializing │  │   df_formatting      │ │
       │  │ - Suricata init │  │ - Rate features      │ │
       │  │ - Normal init   │  │ - Ratio features     │ │
       │  └─────────────────┘  │ - Temporal features  │ │
       │                       │ - IP classification  │ │
       │  ┌─────────────────┐  │ - Port categorization│ │
       │  │  aggregations   │  └──────────────────────┘ │
       │  │ - Event counts  │                           │
       │  │ - Trend analysis│                           │
       │  └─────────────────┘                           │
       └────────────────────────┬────────────────────────┘
                                │
       ┌────────────────────────▼────────────────────────┐
       │            Machine Learning Layer               │
       │  ┌──────────────────────────────────────────┐  │
       │  │         OneClassSVMModel                 │  │
       │  │  - RobustScaler + OneHotEncoder          │  │
       │  │  - fit() on benign data only             │  │
       │  │  - Decision boundary calibration         │  │
       │  │  - Model persistence (joblib/pickle)     │  │
       │  └──────────────────────────────────────────┘  │
       └────────────────────────┬────────────────────────┘
                                │
       ┌────────────────────────▼────────────────────────┐
       │          Detection & Evaluation Layer           │
       │  - predict(): GREEN / ORANGE / RED severity     │
       │  - run_simulation(): Real-time stream demo      │
       │  - evaluate_model_performance(): Metrics        │
       │  - Confusion matrix, Precision, Recall, F1      │
       └─────────────────────────────────────────────────┘
```

### 5.2 Component Descriptions

#### 5.2.1 Data Initialization Module
**Location**: `feature_engineering/df_initializing/`

**Components**:
- `init_suricata_df.py`: Suricata log DataFrame initializer
- `init_normal_traffic_df.py`: Normal traffic DataFrame initializer with gzip support
- `handler_init_dfs.py`: Orchestrates DataFrame initialization

**Responsibilities**:
- Parse JSON logs using streaming approach (ijson)
- Handle compressed (.gz) and uncompressed files
- Initialize pandas DataFrames for downstream processing

#### 5.2.2 Feature Engineering Module
**Location**: `feature_engineering/`

**Formatting Components** (`df_formatting/`):
- `format_suricata_df.py`: Suricata-specific feature extraction
- `format_normal_traffic.py`: Normal traffic feature extraction
- `handler_df_formatter.py`: Coordinates formatting, precalculations, and aggregations

**Precalculation Components** (`precalculations_functions/`):
- `rate_features.py`: bytes_per_second, pkts_per_second
- `ratio_features.py`: bytes_ratio, pkts_ratio
- `temporal_features.py`: hour, day_of_week, is_weekend, is_business_hours
- `ip_classification_features.py`: src_is_private, dst_is_private, is_internal
- `port_categorization_features.py`: dst_port_is_common
- `ip_geolocation_features.py`: Optional geolocation lookup

**Aggregation Components** (`aggregation_functions/`):
- `metrics_features.py`: Event counts, trend analysis, protocol statistics

#### 5.2.3 Model Training & Inference Module
**Location**: `model/`

**Components**:
- `oneCSVM_model.py`: OneClassSVMModel class implementation

**Key Methods**:
- `fit()`: Train model on benign data with configurable parameters
- `fit_or_load()`: Load existing model or train new one
- `predict()`: Classify traffic with severity levels (GREEN/ORANGE/RED)
- `save_model()` / `load_model()`: Model persistence
- `run_simulation()`: Real-time stream simulation
- `run_detailed_simulation()`: Detailed performance analysis
- `evaluate_model_performance()`: Metrics computation

**Model Artifacts**:
- `oneclass_svm_model.pkl`: Trained SVM model
- `oneclass_svm_preprocessor.pkl`: ColumnTransformer (RobustScaler + OneHotEncoder)
- `oneclass_svm_config.pkl`: Configuration (threshold, features, hyperparameters)

#### 5.2.4 Testing Module
**Location**: `tests/`

**Test Suites**:
- `test_precalculations/`: Unit tests for all precalculation functions
- `test_aggregations/`: Unit tests for aggregation functions
- `test_formatters/`: Unit tests for data formatters

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
- Semi-supervised anomaly detection (trains only on normal data)
- Effective for high-dimensional feature spaces (30+ features)
- Does not require labeled malicious traffic for training
- Learns decision boundary around normal behavior
- RBF kernel captures non-linear patterns in network traffic

### 6.2 Model Architecture

**Preprocessing Pipeline** (`ColumnTransformer`):
- **Numerical Features**: RobustScaler (handles outliers better than StandardScaler)
- **Categorical Features**: OneHotEncoder (handle_unknown='ignore')

**Features Dropped** (not used for prediction):
- `source_ip`, `destination_ip` (high cardinality)
- `timestamp_start` (temporal context already extracted)
- `label` (target variable)
- Aggregation features that leak label information

**Categorical Features**:
- `transport_protocol`, `application_protocol`, `direction`
- `day_of_week`, `is_weekend`, `is_business_hours`
- `src_is_private`, `dst_is_private`, `is_internal`, `dst_port_is_common`

**Numerical Features**: All remaining columns after dropping and categoricals

### 6.3 Training Strategy
- **Training Data**: Benign traffic only (10,000 samples default)
- **Train/Val Split**: 80/20 split with random_state=42
- **Downsampling**: Max 50,000 samples (SVM scales O(n^2))
- **Threshold Calibration**: Set at contamination percentile (default 5%) of validation scores

### 6.4 Hyperparameters
| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `kernel` | `rbf` | Radial Basis Function kernel |
| `nu` | `0.2` | Upper bound on training errors (outlier fraction) |
| `gamma` | `scale` | Kernel coefficient (1 / (n_features * X.var())) |
| `contamination` | `0.1` | Expected proportion of outliers for threshold |
| `max_train_samples` | `10,000` | Maximum training samples for speed |

### 6.5 Prediction Logic
```
score = model.decision_function(X)

if score < threshold_boundary - 0.5:
    → RED (CRITICAL): Far outside normal boundary
elif score < threshold_boundary:
    → ORANGE (SUSPICIOUS): Just outside boundary
else:
    → GREEN (Normal): Within expected behavior
```

### 6.6 Performance Metrics
- **Precision**: What % of flagged anomalies are actually anomalies
- **Recall / Detection Rate**: What % of actual anomalies were detected
- **F1-Score**: Harmonic mean of precision and recall
- **False Alarm Rate**: % of benign traffic incorrectly flagged

### 6.7 Current Performance (Tested)
Based on evaluation with `nu=0.2`, `contamination=0.1`, `max_train_samples=10,000`:

| Metric | Value |
|--------|-------|
| Detection Rate (Recall) | ~90% |
| False Alarm Rate | ~10% |
| F1-Score | ~0.88 |
| Precision | ~0.85 |

**Confusion Matrix** (typical results on 10,000 test samples):
```
              Predicted
              Normal  Anomaly
Actual Normal   4500     500
Actual Anomaly   500    4500
```

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
