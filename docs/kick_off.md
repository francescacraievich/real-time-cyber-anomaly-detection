#  Real-Time Cyber Anomaly Detection Platform
## Project Plan, Architecture & Implementation Notes

---

## 1. Obiettivo del progetto
Sviluppare una **piattaforma data-driven per il rilevamento in tempo reale di anomalie** su log di rete e di sistema.  
Funzionalità principali:
- acquisizione di log in tempo reale (Cowrie honeypot su VM);
- preprocessing, cleaning e feature engineering in streaming;
- detection di anomalie (brute-force, port-scan, traffic spikes, comportamenti insoliti) con modelli online/incrementali;
- visualizzazione in tempo reale su **Streamlit** e API REST con **Flask**.

---

## 2. Metodologia e framework
**Metodologia di progetto:** Agile (sprint settimanali, meeting quotidiani se necessario, PR/branch per ogni task).

**Framework di data science scelto:** **CRISP-DM**  
**Motivazione:** CRISP-DM è iterativo, pratico e adatto a progetti che prevedono cicli di miglioramento continui e integrazione con sistemi di produzione (deployment + monitoring). KDD è più teorico e meno orientato al ciclo di vita continuo.

CRISP-DM adattato:
1. Business Understanding
2. Data Understanding
3. Data Preparation
4. Modeling
5. Evaluation
6. Deployment
7. Monitoring & Maintenance

---

## 3. Pipeline high-level
Cowrie VM (attacker + victim)  
-> /var/log/cowrie.json  
-> Flask API (Python)  
-> Stream ingestion  
-> ML pipeline  
-> Streamlit dashboard

---

## 4. Fonti dati e come li otteniamo
- **Primary source (recommended):** *Cowrie honeypot* su VM (Oracle Cloud o VirtualBox) che scrive eventi in JSON (`/var/log/cowrie.json`). Questi log contengono login attempts, sessioni, comandi, trasferimenti di file ecc.
- **Backup / enrichment sources:** MAWI / CAIDA (trace quotidiani), feed threat-intel (Shodan, GreyNoise, AlienVault OTX, AbuseIPDB) per arricchire gli eventi.
- **Modalità di ingestione:** tail del file JSON o inotify -> Flask endpoint o producer Kafka (a seconda della scala).

---

## 5. Scelte architetturali e componenti (tools)
- **Ingestion / Collector:** Python script (tail + requests), Filebeat (per forwarding), Kafka (per throughput e resilienza).
- **API / Serving:** Flask per esporre `/predict`, `/logs`, `/health`.
- **Stream processing & Online ML:** River (online learning), scikit-multiflow (opzioni), Vowpal Wabbit (se serve performance).
- **Storage:** PostgreSQL o MongoDB per log + risultati; InfluxDB per metriche time-series.
- **Dashboard:** Streamlit (real-time UI).
- **CI/CD & Docs:** GitHub Actions (CI), MkDocs + GitHub Pages (docs).
- **Monitoring:** EvidentlyAI (data & model monitoring), Prometheus + Grafana (infrastruttura metrics).
- **Experiment tracking:** Weights & Biases o Neptune.ai.

---

## 6. Sfide previste
- **Missing values** — log incompleti o campi nulli.
- **Data bias** — honeypot attira tipologie specifiche di attacchi (non rappresentativo dell’intera rete).
- **Noise & inconsistency** — formati eterogenei, timestamp malformati.
- **Imbalanced dataset** — anomalie molto rare rispetto ai normali eventi.

---

## 7. Data Quality — metriche
Valuteremo la qualità dei dati secondo:
- **Accuracy** — correttezza dei valori (IP, port, status).
- **Completeness** — percentuale di campi presenti per evento.
- **Consistency** — uniformità di formati e valori.
- **Timeliness** — latenza tra evento e disponibilità per detection.

---

## 8. EDA (Exploratory Data Analysis)
**Scopo:** riassumere le caratteristiche del dataset, rilevare pattern e anomalie.

**Tool suggeriti:**
- `pandas`, `numpy` — manipolazione
- `matplotlib`, `seaborn` — visualizzazioni statiche
- `plotly` — grafici interattivi
- `ydata-profiling` (ex `pandas-profiling`) — report automatico
- `sweetviz` — confronto tra dataset/versioni

**Attività EDA:**
- Conteggi per src_ip, dst_ip, porta, event_type
- Serie temporali di eventi per minuto/ora
- Heatmap di correlazioni tra features
- Analisi di outlier (IQR, z-score)
- Profiling automatizzato per report velocizzati

---

## 9. Preprocessing & cleaning (dettagli operativi)
### Handling missing values:
- Se campo essenziale (es. timestamp) mancante → scartare o ricostruire.
- Numeric: imputation con median/mean (se appropriato).
- Categorical: imputation con mode o "unknown" token.

### Outlier detection & treatment:
- Z-score, IQR per valori numerici (bytes, rate).
- Robust scaler se distribuzioni pesantemente skewed.

### Noise reduction:
- Binning (temporal aggregation)
- Moving average per trend smoothing

### Consistency checks:
- Normalizzazione timestamp a UTC e formato ISO.
- Validazione IP con regex e netaddr.
- Coerenza port/protocol mapping.

---

## 10. Feature engineering — chi lo fa e come
**Responsabilità:** Data Scientist con supporto ML Engineer.

**Obiettivo:** ridurre dimensionalità, creare variabili informative (es. failed_logins_30s, unique_ports_1min, avg_bytes_5min).

**Esempi di feature:**
- temporal: hour_of_day, weekday, session_duration
- network: src_ip_freq_30s, dst_port_entropy, avg_bytes
- auth: failed_login_count_window, success_rate
- derived: ratio_failed_success, is_internal_ip

**Dimension reduction:** useremo **PCA** inizialmente per features numeriche dense.
- **Motivazione PCA:** riduce dimensionalità preservando varianza, diminuisce overfitting e costo computazionale. Utile se dopo encoding (one-hot / embeddings) lo spazio diventa molto grande.
- **Quando non usarlo:** se serve alta interpretabilità per ogni singola feature — in tal caso preferire selezione feature per importanza.

**Altre opzioni future:** Autoencoders (per rappresentazioni non-lineari), LDA solo per text-topic extraction.

---

## 11. Modelli e strategia di modellazione
**Tipo di apprendimento:** principalmente **unsupervised / semi-supervised / online** (anomaly detection).

**Algoritmi candidati:**
- **Streaming / online:** Hoeffding Tree (VFDT), Online Bagging/Boosting (River)
- **Anomaly detection:** Isolation Forest (batch), One-Class SVM (batch), Autoencoders (deep), LOF
- **Detection drift:** ADWIN, DDM (per trigger retraining/adattamento)

**Scelta iniziale:** River + Hoeffding Tree per classificazione online / ADWIN per drift detection; Isolation Forest come baseline offline per confronto.

**RICE framework:** lo useremo come guida concettuale:
- **Representation:** feature + PCA
- **Information:** feature selection & importance
- **Computation:** algoritmi streaming (River)
- **Evaluation:** metriche in streaming (precision/recall/latency)

---

## 12. Model adaptation & drift handling
- **Sudden drift:** Rilevamento rapido con ADWIN -> possibile retraining o switch a modello alternativo.
- **Incremental drift:** aggiornamento continuo (online learning).
- **Recurring drift:** mantenere pool di modelli con strategie di ensemble e rotazione.

---

## 13. Continuous learning — tecniche e librerie
- **Online learning libs:** River, Vowpal Wabbit.
- **Window-based updates:** aggiornamento su finestre temporali (sliding windows).
- **Streaming ensembles:** combinazione di modelli aggiornati localmente.
- **Metriche streaming:** precision@k, recall, F1 on sliding window, detection delay.

---

## 14. Ingestion / streaming infra (opzioni)
- **Semplice (dev):** Flask endpoint che riceve eventi JSON e li processa subito.
- **Scalabile (prod/test):** Filebeat -> Kafka -> stream processors -> model consumers.
- **Processing engines:** Apache Flink (complesso), Kafka Streams, o semplici Python consumers.

---

## 15. Deployment (serving) & dashboard
- **Model serving:** Flask microservice che carica il modello (pickle o joblib) e espone `/predict` e `/update`.
- **Dashboard:** Streamlit che chiama la Flask API o legge DB per ultimi eventi e anomalie.
- **Storage:** PostgreSQL / MongoDB (log & anomalies), InfluxDB per metriche.
- **Containerization:** Docker per Flask, Streamlit, worker, Kafka (dev compose).

---

## 16. CI/CD & Documentazione
- **CI:** GitHub Actions per lint (flake8), test (pytest), build Docker images, e deploy staging.
- **Docs:** MkDocs (Material) + GitHub Pages — pipeline automatica su merge a `main`.
- **Branching:** `feature/*` per ogni task; PR -> `develop` -> merge in `main` dopo review e CI passata.

---

## 17. Monitoring & Model Observability
- **Data drift & model monitoring:** EvidentlyAI (reports), Prometheus + Grafana (metrics).
- **Alerting:** webhook su slack/email quando drift o drop di metriche.
- **Retraining trigger:** soglia su metriche (precision, recall) o su drift detection.

---

## 18. Specific tasks: Who does what (sprint 1 example)
- **Francesca (PM):** repo, docs, sprint plan, kickoff, PR review.
- **Francesco (Data Cloud Engineer):** set up Cowrie VM, ingestion script, Kafka dev.
- **Lucas (ML Engineer):** baseline model (Isolation Forest), River setup, Flask API skeleton.
- **All:** create `docs/`, initial Streamlit skeleton, run EDA on collected logs.

---

## 19. Quick start / week 1 checklist
1. Create repo with suggested structure.  
2. Setup Cowrie on VM (or Docker) and confirm `cowrie.json` generation.  
3. Implement a simple Flask endpoint to ingest and store events.  
4. Implement a tail-to-db or tail-to-kafka producer script.  
5. Build a minimal Streamlit app that shows last N events (polls DB or API).  
6. Add CI workflow (lint + tests) to `.github/workflows/ci.yml`.  
7. Create MkDocs skeleton in `docs/` and configure GitHub Pages.

---

## 20. Files & templates to add 
- `docs/project_plan.md` (this file)  
- `.github/workflows/ci.yml` (CI template)  
- `mkdocs.yml` + `docs/index.md` (docs skeleton)  
- `src/api/flask_app.py` (Flask skeleton)  
- `src/ingestion/producer_replay.py` (replay/inject script)  
- `src/dashboard/streamlit_app.py` (basic UI)

---

## 21. Note finali e raccomandazioni
- **PCA**: utile come primo strumento di riduzione dimensionale. Sperimentare e valutare trade-off interpretabilità vs performance.  
- **Cowrie vs feed MAWI/CAIDA**: Cowrie = eventi reali e variabili (consigliato, ma richiede isolamento); MAWI/CAIDA = ottimo come base storica e per replay giornaliero.  
- **Immediate demo:** usa ingestion file->Flask->DB->Streamlit con dati di replay (1 msg/s) + injection casuale di anomalie per dimostrare la pipeline il primo giorno.

---


