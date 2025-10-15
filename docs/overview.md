# Real-Time Cyber Anomaly Detection Platform

## 1. Team and Roles
| Member | Role |
|--------|------|
| Francesca Craievich | Project Manager |
| Lucas Jakin | xxx |
| Francesco Rumiz | xxx |

---

## 2. Project Objective
Design a **data-driven** platform for real-time anomaly detection in network and system logs. The system should be able to identify:

- Sudden traffic spikes from a single IP
- Repeated failed login attempts (brute force)
- Unusual behavior from hosts or users
- Connections to unusual ports or destinations

The ultimate goal is to generate **automatic alerts** and display anomalous events in an **interactive dashboard**.

---

## 3. General Architecture

Network / System Logs -> Stream Ingestion Layer (Kafka / MQTT / Python Script) ->  Stream Processing & Anomaly Detection (ML Model + Rules) -> Storage Layer (PostgreSQL / MongoDB / InfluxDB) -> Dashboard / Alerting (Streamlit / Grafana / Web App)


## 4. Roles and Responsabilities 

| Role | Main Responsibilities |
|------|----------------------|
| 🎯 AI Product Owner | Define goals, success metrics (detection rate, false positives, latency) |
| 🗂️ Project Manager | Manage milestones, documentation, team communication |
| 📊 Data Scientist | Analyze datasets, select features, train anomaly detection models |
| 🤖 ML Engineer | Expose model as a microservice, optimize performance |
| ☁️ Data Cloud Engineer | Configure streaming pipeline and database, simulate logs |
| 💻 Software Engineer | Build interactive dashboard and real-time alerting |


