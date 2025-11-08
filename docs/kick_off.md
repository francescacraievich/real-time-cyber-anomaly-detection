#  Real-Time Cyber Anomaly Detection Platform
## Project Plan, Architecture & Implementation Notes

---

## 1. Project Objective
Develop a **data-driven platform for real-time anomaly detection** on network and system logs.
Main features:
- Real-time log acquisition (Cowrie honeypot on VM);
- Streaming preprocessing, cleaning, and feature engineering;
- Anomaly detection (brute-force, port-scan, traffic spikes, unusual behaviors) with online/incremental models;
- Real-time visualization on **Streamlit** and REST API with **Flask**.

---

## 2. Methodology and Framework
**Project methodology:** Agile (weekly sprints, daily meetings if needed, PR/branch for each task).

**Data science framework chosen:** **CRISP-DM**
**Rationale:** CRISP-DM is iterative, practical, and suitable for projects that involve continuous improvement cycles and integration with production systems (deployment + monitoring). KDD is more theoretical and less oriented toward continuous lifecycle.

Adapted CRISP-DM:
1. Business Understanding
2. Data Understanding
3. Data Preparation
4. Modeling
5. Evaluation
6. Deployment
7. Monitoring & Maintenance

---

## 3. High-Level Pipeline
Cowrie VM (attacker + victim)
-> /var/log/cowrie.json
-> Flask API (Python)
-> Stream ingestion
-> ML pipeline
-> Streamlit dashboard

---

## 4. Data Sources and Acquisition Methods
- **Primary source (recommended):** *Cowrie honeypot* on VM (Oracle Cloud or VirtualBox) writing events in JSON (`/var/log/cowrie.json`). These logs contain login attempts, sessions, commands, file transfers, etc.
- **Backup / enrichment sources:** MAWI / CAIDA (daily traces), threat-intel feeds (Shodan, GreyNoise, AlienVault OTX, AbuseIPDB) to enrich events.
- **Ingestion method:** JSON file tail or inotify -> Flask endpoint or Kafka producer (depending on scale).

---

## 5. Architectural Choices and Components (tools)
- **Ingestion / Collector:** Python script (tail + requests), Filebeat (for forwarding), Kafka (for throughput and resilience).
- **API / Serving:** Flask to expose `/predict`, `/logs`, `/health`.
- **Stream processing & Online ML:** River (online learning), scikit-multiflow (options), Vowpal Wabbit (if performance needed).
- **Storage:** PostgreSQL or MongoDB for logs + results; InfluxDB for time-series metrics.
- **Dashboard:** Streamlit (real-time UI).
- **CI/CD & Docs:** GitHub Actions (CI), MkDocs + GitHub Pages (docs).
- **Monitoring:** EvidentlyAI (data & model monitoring), Prometheus + Grafana (infrastructure metrics).
- **Experiment tracking:** Weights & Biases or Neptune.ai.

---

## 6. Expected Challenges
- **Missing values** — incomplete logs or null fields.
- **Data bias** — honeypot attracts specific types of attacks (not representative of entire network).
- **Noise & inconsistency** — heterogeneous formats, malformed timestamps.
- **Imbalanced dataset** — anomalies very rare compared to normal events.

---

## 7. Data Quality — Metrics
We will evaluate data quality according to:
- **Accuracy** — correctness of values (IP, port, status).
- **Completeness** — percentage of fields present per event.
- **Consistency** — uniformity of formats and values.
- **Timeliness** — latency between event and availability for detection.

---

## 8. EDA (Exploratory Data Analysis)
**Purpose:** summarize dataset characteristics, detect patterns and anomalies.

**Suggested tools:**
- `pandas`, `numpy` — manipulation
- `matplotlib`, `seaborn` — static visualizations
- `plotly` — interactive charts
- `ydata-profiling` (formerly `pandas-profiling`) — automated report
- `sweetviz` — comparison between datasets/versions

**EDA activities:**
- Counts by src_ip, dst_ip, port, event_type
- Time series of events per minute/hour
- Correlation heatmap between features
- Outlier analysis (IQR, z-score)
- Automated profiling for fast reports

---

## 9. Preprocessing & Cleaning (operational details)
### Handling missing values:
- If essential field (e.g., timestamp) is missing → discard or reconstruct.
- Numeric: imputation with median/mean (if appropriate).
- Categorical: imputation with mode or "unknown" token.

### Outlier detection & treatment:
- Z-score, IQR for numeric values (bytes, rate).
- Robust scaler if distributions heavily skewed.

### Noise reduction:
- Binning (temporal aggregation)
- Moving average for trend smoothing

### Consistency checks:
- Timestamp normalization to UTC and ISO format.
- IP validation with regex and netaddr.
- Port/protocol mapping consistency.

---

## 10. Feature Engineering — Who Does What and How
**Responsibility:** Data Scientist with ML Engineer support.

**Objective:** reduce dimensionality, create informative variables (e.g., failed_logins_30s, unique_ports_1min, avg_bytes_5min).

**Feature examples:**
- temporal: hour_of_day, weekday, session_duration
- network: src_ip_freq_30s, dst_port_entropy, avg_bytes
- auth: failed_login_count_window, success_rate
- derived: ratio_failed_success, is_internal_ip

**Dimension reduction:** we will use **PCA** initially for dense numeric features.
- **PCA rationale:** reduces dimensionality while preserving variance, decreases overfitting and computational cost. Useful if space becomes very large after encoding (one-hot / embeddings).
- **When not to use it:** if high interpretability is needed for each individual feature — in that case prefer feature selection by importance.

**Other future options:** Autoencoders (for non-linear representations), LDA only for text-topic extraction.

---

## 11. Models and Modeling Strategy
**Learning type:** mainly **unsupervised / semi-supervised / online** (anomaly detection).

**Candidate algorithms:**
- **Streaming / online:** Hoeffding Tree (VFDT), Online Bagging/Boosting (River)
- **Anomaly detection:** Isolation Forest (batch), One-Class SVM (batch), Autoencoders (deep), LOF
- **Drift detection:** ADWIN, DDM (to trigger retraining/adaptation)

**Initial choice:** River + Hoeffding Tree for online classification / ADWIN for drift detection; Isolation Forest as offline baseline for comparison.

**RICE framework:** we will use it as conceptual guide:
- **Representation:** features + PCA
- **Information:** feature selection & importance
- **Computation:** streaming algorithms (River)
- **Evaluation:** streaming metrics (precision/recall/latency)

---

## 12. Model Adaptation & Drift Handling
- **Sudden drift:** Rapid detection with ADWIN -> possible retraining or switch to alternative model.
- **Incremental drift:** continuous update (online learning).
- **Recurring drift:** maintain model pool with ensemble strategies and rotation.

---

## 13. Continuous Learning — Techniques and Libraries
- **Online learning libs:** River, Vowpal Wabbit.
- **Window-based updates:** updates on temporal windows (sliding windows).
- **Streaming ensembles:** combination of locally updated models.
- **Streaming metrics:** precision@k, recall, F1 on sliding window, detection delay.

---

## 14. Ingestion / Streaming Infrastructure (options)
- **Simple (dev):** Flask endpoint that receives JSON events and processes them immediately.
- **Scalable (prod/test):** Filebeat -> Kafka -> stream processors -> model consumers.
- **Processing engines:** Apache Flink (complex), Kafka Streams, or simple Python consumers.

---

## 15. Deployment (serving) & Dashboard
- **Model serving:** Flask microservice that loads the model (pickle or joblib) and exposes `/predict` and `/update`.
- **Dashboard:** Streamlit that calls the Flask API or reads DB for latest events and anomalies.
- **Storage:** PostgreSQL / MongoDB (logs & anomalies), InfluxDB for metrics.
- **Containerization:** Docker for Flask, Streamlit, worker, Kafka (dev compose).

---

## 16. CI/CD & Documentation
- **CI:** GitHub Actions for lint (flake8), tests (pytest), Docker image build, and staging deploy.
- **Docs:** MkDocs (Material) + GitHub Pages — automated pipeline on merge to `main`.
- **Branching:** `feature/*` for each task; PR -> `develop` -> merge to `main` after review and CI passes.

---

## 17. Monitoring & Model Observability
- **Data drift & model monitoring:** EvidentlyAI (reports), Prometheus + Grafana (metrics).
- **Alerting:** webhook to Slack/email when drift or metrics drop.
- **Retraining trigger:** threshold on metrics (precision, recall) or drift detection.

---

## 18. Specific Tasks: Who Does What (sprint 1 example)
- **Francesca (PM):** repo, docs, sprint plan, kickoff, PR review.
- **Francesco (Data Cloud Engineer):** set up Cowrie VM, ingestion script, Kafka dev.
- **Lucas (ML Engineer):** baseline model (Isolation Forest), River setup, Flask API skeleton.
- **All:** create `docs/`, initial Streamlit skeleton, run EDA on collected logs.

---

## 19. Quick Start / Week 1 Checklist
1. Create repo with suggested structure.
2. Setup Cowrie on VM (or Docker) and confirm `cowrie.json` generation.
3. Implement a simple Flask endpoint to ingest and store events.
4. Implement a tail-to-db or tail-to-kafka producer script.
5. Build a minimal Streamlit app that shows last N events (polls DB or API).
6. Add CI workflow (lint + tests) to `.github/workflows/ci.yml`.
7. Create MkDocs skeleton in `docs/` and configure GitHub Pages.

---

## 20. Files & Templates to Add
- `docs/project_plan.md` (this file)
- `.github/workflows/ci.yml` (CI template)
- `mkdocs.yml` + `docs/index.md` (docs skeleton)
- `src/api/flask_app.py` (Flask skeleton)
- `src/ingestion/producer_replay.py` (replay/inject script)
- `src/dashboard/streamlit_app.py` (basic UI)

---

## 21. Final Notes and Recommendations
- **PCA**: useful as first dimensionality reduction tool. Experiment and evaluate interpretability vs performance trade-off.
- **Cowrie vs MAWI/CAIDA feeds**: Cowrie = real and variable events (recommended, but requires isolation); MAWI/CAIDA = excellent as historical base and for daily replay.
- **Immediate demo:** use file ingestion->Flask->DB->Streamlit with replay data (1 msg/s) + random anomaly injection to demonstrate pipeline on day one.

---


