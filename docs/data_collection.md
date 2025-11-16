# T-Pot Honeypot Data Collection - README

**Project:** Real-Time Anomaly Detection System
**Role:** Data Engineering
**Data Engineer:** Francesca Craievich
**Data Scientist:** Francesco Rumiz
**ML Engineer**: Lucas Jakin
**Data Collection Period:** October 2024
**Last Updated:** October 24, 2025

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Data Collection](#data-collection)
4. [Dataset Overview](#dataset-overview)
5. [Data Access](#data-access)
6. [Next Steps for Data Science](#next-steps-for-data-science)
7. [Appendices](#appendices)

---

## Executive Summary

### Project Objective
Develop a **Real-Time Anomaly Detection** system to identify cyber attacks and anomalous behaviors using data collected from a distributed honeypot network.

### What We Did (Data Engineering)

- Deployed multi-protocol honeypots on Google Cloud Platform
- Collected **148,063 real attack events**
- Coverage of **20+ protocols** (SSH, Telnet, HTTP, SMB, etc.)
- Data acquisition from **30+ specialized honeypots**
- **621 MB of logs** (296 MB compressed) ready for analysis
- Complete data structure documentation  

### Key Metrics

| Metric | Value |
|--------|-------|
| Total Events | 148,063 |
| Data Size (raw) | 621 MB |
| Data Size (compressed) | 296 MB |
| Active Honeypots | 30+ |
| Protocols Covered | 20+ |
| Collection Period | October 2024 |
| Unique Attackers | TBD (to be analyzed) |
| Countries Covered | TBD (via GeoIP) |

---

## Infrastructure Setup

### 1. Cloud Platform: Google Cloud Platform

**VM Specifications:**
- **Provider:** Google Cloud Platform (GCP)
- **Instance:** e2-standard-2 (2 vCPU, 8 GB RAM)
- **OS:** Ubuntu 24.04 LTS
- **Region:** us-central1-a
- **Public IP:** 35.225.86.61
- **Disk:** 64 GB SSD

**Estimated cost:** ~$50/month

### 2. Software: T-Pot 24.04.1

**What is T-Pot?**
T-Pot is an all-in-one honeypot platform developed by Deutsche Telekom Security. It includes:
- 30+ pre-configured honeypots
- ELK Stack (Elasticsearch, Logstash, Kibana) for logging
- Suricata IDS for network monitoring
- Pre-configured Kibana dashboards

**Installed version:** T-Pot 24.04.1
**Repository:** https://github.com/telekom-security/tpotce

### 3. Network Configuration

**Publicly exposed ports:**
- 22 (SSH - honeypot)
- 23 (Telnet - honeypot)
- 80, 443 (HTTP/HTTPS - honeypot)
- 21, 25, 110, 143 (FTP, SMTP, POP3, IMAP - honeypot)
- 445 (SMB - honeypot)
- 1433, 3306, 5432, 6379, 9200 (Database ports - honeypot)
- 5060 (SIP - honeypot)
- And many others...

**SSH management port:** 64295 (non-standard for security)
**Kibana port:** 64297 

**Firewall:** Configured on GCP to allow incoming traffic on all honeypot ports

### 4. Security

- SSH on non-standard port (64295)
- Isolated honeypot - no sensitive data on VM
- All public services are traps (honeypots)
- Active monitoring  

---

## Data Collection

### Collection Timeline

1. **October 23, 2024:** VM setup on GCP
2. **October 23, 2024:** T-Pot installation
3. **October 23-24, 2024:** Active data collection
4. **October 24, 2024:** Services stopped and data backup

**Collection duration:** ~24-48 hours of continuous Internet exposure

### Methodology

1. **Passive exposure:** Honeypots were exposed on the public Internet without any "advertising"
2. **Automatic scans:** Attackers found the services through Internet-wide scans
3. **Automatic logging:** All events were automatically recorded by T-Pot
4. **Zero intervention:** No manual interaction during collection

### Types of Attacks Captured

- **SSH Brute Force** - SSH login attempts with common credentials
- **Telnet Exploitation** - Attacks on vulnerable IoT devices
- **Malware Distribution** - Malware downloads (binaries captured)
- **SMB Exploitation** - Attacks on Windows protocol
- **Web Attacks** - SQL injection, XSS, directory traversal
- **Database Probing** - Scans on MySQL, Redis, Elasticsearch
- **VoIP Fraud** - SIP fraud attempts
- **ICS/SCADA Probing** - Attacks on industrial systems  

---

## Dataset Overview

### General Statistics

```
Total Events: 148,063
Total Size: 621 MB (raw) / 296 MB (compressed)
Format: NDJSON (Newline-Delimited JSON)
Encoding: UTF-8
```

### Honeypot Distribution 

| Honeypot | Events | % | Description |
|----------|--------|---|-------------|
| Cowrie | ~6,000 | ~4% | SSH/Telnet attacks |
| Dionaea | ~16,000 | ~11% | Malware & exploits |
| Suricata | ~80,000 | ~54% | Network IDS events |
| Others | ~46,000 | ~31% | Various honeypots |

**Note:** Numbers estimated from Kibana dashboard, exact verification to be done in analysis


**For complete schema of each honeypot, see:** `HONEYPOT_GUIDE.md`

---

## Data Access

### Backup File Path

```
C:\Users\franc\Downloads\tpot-data-backup.tar.gz
```

### Extraction

**Windows (PowerShell):**
```powershell
tar -xzf tpot-data-backup.tar.gz
```

**Linux/Mac:**
```bash
tar -xzf tpot-data-backup.tar.gz
```

### Post-Extraction Structure

```
home/
└── zach/
    └── tpotce/
        └── data/
            ├── cowrie/
            ├── dionaea/
            ├── suricata/
            └── [other honeypots]
```

### Quick Start - Exploratory Analysis

```python
import json
import pandas as pd

# Read Cowrie logs (SSH attacks)
records = []
with open('home/zach/tpotce/data/cowrie/log/cowrie.json', 'r') as f:
    for line in f:
        records.append(json.loads(line))

df = pd.DataFrame(records)

print(f"Total records: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"Unique IPs: {df['src_ip'].nunique()}")

# Top 10 attacking IPs
print(df['src_ip'].value_counts().head(10))

# Top 10 passwords tried
print(df[df['eventid'] == 'cowrie.login.failed']['password'].value_counts().head(10))
```

---

## Next Steps for Data Science

### Phase 1: Data Exploration & Cleaning

**Tasks for Francesco (Data Scientist):**

1. **Load and Explore:**
   ```python
   # Load all main logs
   df_cowrie = pd.read_json('cowrie.json', lines=True)
   df_dionaea = pd.read_json('dionaea.json', lines=True)
   df_suricata = pd.read_json('eve.json', lines=True)
   
   # EDA
   df_cowrie.info()
   df_cowrie.describe()
   df_cowrie['src_ip'].value_counts()
   ```

2. **Data Quality Check:**
   - Missing values?
   - Duplicates?
   - Timestamp parsing OK?
   - Inconsistent fields?

3. **Merge Datasets:**
   - Unify all honeypots into a single DataFrame
   - Normalized schema

### Phase 2: Feature Engineering

**Features to create:**

1. **Time-based:**
   - Hour of day
   - Day of week
   - Time since last attack (per IP)
   - Attack frequency

2. **IP-based:**
   - Country (via GeoIP)
   - ASN / Organization
   - IP reputation score (AbuseIPDB, VirusTotal)
   - Is Tor exit node?
   - Total attacks from this IP

3. **Behavioral:**
   - Session duration
   - Commands executed per session
   - Login attempts per session
   - Credential diversity (entropy)

4. **Protocol-based:**
   - Port usage patterns
   - Protocol combinations
   - Payload size distribution

5. **Sequence-based:**
   - Command n-grams (e.g., "wget http://malware.com")
   - Temporal patterns

### Phase 3: Labeling Strategy

**How do we label anomalies?**

Option 1: **Unsupervised**
- No manual labeling needed
- Use clustering (K-means, DBSCAN)
- Isolation Forest
- Autoencoder

Option 2: **Semi-supervised**
- Manually label subset (e.g., top 1000 events)
- Use transfer learning

Option 3: **Rule-based initial labels**
- Known malicious IPs → anomaly
- Rare behaviors → anomaly
- Multiple failed logins → anomaly
- Then train on these

### Phase 4: Model Selection

**Recommended algorithms:**

1. **Isolation Forest** - Excellent for anomaly detection
2. **One-Class SVM** - For single-class data
3. **Autoencoder** - Deep learning approach
4. **LSTM** - For sequence analysis (commands)
5. **Random Forest** - For classification if you have labels

### Phase 5: Real-Time Pipeline 

```
Data Source → Preprocessing → Feature Extraction → Model Prediction → Alert
    ↓              ↓                  ↓                    ↓            ↓
  T-Pot API    Normalization      Time/IP/Seq        Anomaly Score   Dashboard
```

---

## Complementary Documentation

### Files provided:

1. **`HONEYPOT_GUIDE.md`** - Complete guide to all 30+ honeypots
2. **`README.md`** - This file

### External Resources:

- **T-Pot Documentation:** https://github.com/telekom-security/tpotce
- **Cowrie Documentation:** https://github.com/cowrie/cowrie
- **Dionaea Documentation:** https://github.com/DinoTools/dionaea
- **Suricata Documentation:** https://suricata.io/
- **AbuseIPDB API:** https://www.abuseipdb.com/api
- **MaxMind GeoIP:** https://dev.maxmind.com/geoip

---

## Technical Setup (Details)

### How we deployed the infrastructure

#### Step 1: VM Creation on GCP

```bash
# Created via GCP Console
# Instance type: e2-standard-2
# OS: Ubuntu 24.04 LTS
# Disk: 64 GB SSD
# Network: Allow all ingress traffic
```

#### Step 1: T-Pot Installation

```bash
# SSH into the VM
ssh -p 22 franci.craievich2000@35.225.86.61

# Download installer
git clone https://github.com/telekom-security/tpotce
cd tpotce/iso/installer/

# Run installer
sudo ./install.sh --type=user

# Configuration:
# - Username: zach
# - Password: [set during install]
# - Installation type: HIVE (all honeypots)
```



#### Step 2: Stop and Backup

```bash
# Stop T-Pot
sudo systemctl stop tpot

# Backup data
sudo tar -czf ~/tpot-data-backup.tar.gz /home/zach/tpotce/data/

# Download to local PC
scp -P 64295 franci.craievich2000@35.225.86.61:~/tpot-data-backup.tar.gz ~/Downloads/
```

---

## Known Issues & Limitations

### Dataset Limitations

1. **Short period:** Only 24-48 hours of collection
   - **Solution:** Reactivate for continuous collection if more data needed

2. **Geographic bias:** US-based public IP
   - **Impact:** Most attacks from Asia
   - **Solution:** Multi-region deployment in the future

3. **No manual labeling:** Events are not labeled as normal/anomaly
   - **Solution:** Use unsupervised learning or rule-based labeling

4. **Timestamp timezone:** Some logs have different timezones
   - **Solution:** Normalize everything to UTC in preprocessing


---

## Lessons Learned & Best Practices

### What we learned:

- **T-Pot is production-ready** - Easy installation, very robust
- **Attacks come quickly** - First attacks in <1 hour
- **Well-structured logs** - JSON facilitates analysis
- **Excellent Kibana dashboards** - Immediate visualizations
- **Cloud is ideal** - Easy deployment, public IP, scalability

---

## Future Roadmap

### Short-term (1-2 weeks)

- [ ] Francesco: Complete EDA of dataset
- [ ] Data consolidation to Parquet format
- [ ] GeoIP enrichment
- [ ] Initial feature engineering
- [ ] Baseline model (Isolation Forest)

### Long-term (1 month)

- [ ] Real-time data pipeline (API)
- [ ] Streaming ML predictions
- [ ] Interactive Streamlit dashboard
- [ ] Model evaluation & tuning
- [ ] A/B testing different models

---

## Team & Contacts

**Data Engineer:** Francesca
- Role: Infrastructure, data collection, pipeline

**Data Scientist:** Francesco
- Role: Data analysis, formatting

**ML Engineer**: Lucas
- Role: Ml modelling

**Presentation:** Saturday [25/10/25]

---

## Saturday Meeting Notes

### Agenda

1. **Intro (5 min)**
   - Project objective
   - Team roles

2. **Infrastructure Demo (10 min)**
   - Show GCP console
   - Show Kibana dashboard
   - Explain T-Pot architecture

3. **Dataset Overview (10 min)**
   - Key numbers
   - Data structure
   - Sample records

4. **Handoff to Francesco (10 min)**
   - Where the data is
   - How to load it
   - Schema documentation
   - Next steps

5. **Q&A (5 min)**

### Materials to prepare

- [ ] README presentation
- [ ] Kibana dashboard screenshots
- [ ] Sample data (first 1000 records in CSV)


---

## Appendices


###  Python Quick Start

```python
# Install requirements
pip install pandas pyarrow fastparquet geoip2

# Load Cowrie data
import pandas as pd
df = pd.read_json('cowrie.json', lines=True)

# Parse timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Basic stats
print(df.describe())
print(df['src_ip'].value_counts().head(10))

# Export to Parquet
df.to_parquet('cowrie.parquet')
```

---

## Sign-off

**Dataset Ready:** 60%
**Documentation Complete:** Yes
**Ready for Data Science:** Yes

**Data Engineer:** Francesca Craievich
**Date:** October 24, 2025

**Data Scientist (received):** Francesco Rumiz
**Date:** October 25, 2025

---

## Support

For questions or issues:
- Email: franci.craievich2000@gmail.com
- Teams

**Last Updated:** October 24, 2025 13:30 UTC

---

*This document was generated as part of the Real-Time Anomaly Detection project using data from the T-Pot Honeypot Platform.*
