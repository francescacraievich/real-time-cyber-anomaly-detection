# Real-Time Cyber Anomaly Detection

## Project Overview
The goal is to monitor network flows and detect potentially malicious activity by combining **honeypot logs** from T-Pot and a **normal traffic dataset** (ISCX/IDS style). The system will simulate real-time streaming of events for demonstration purposes.

---

## Datasets

### 1. Normal Traffic Dataset (ISCX)

- 18 CSV files, total > 3.8 million rows
- Columns (21): Label, appName, destination, destinationPayloadAsBase64, destinationPayloadAsUTF, destinationPort, destinationTCPFlagsDescription, direction, generated, protocolName, source, sourcePayloadAsBase64, sourcePayloadAsUTF, sourcePort, sourceTCPFlagsDescription, startDateTime, stopDateTime, totalDestinationBytes, totalDestinationPackets, totalSourceBytes, totalSourcePackets

### 2. T-Pot Honeypot Logs (JSON)

- **Cowrie Columns:** `['eventid', 'src_ip', 'src_port', 'dst_ip', 'dst_port', 'session', 'protocol', 'message', 'sensor', 'timestamp', 'duration', 'version', 'hassh', 'hasshAlgorithms', 'kexAlgs', 'keyAlgs', 'encCS', 'macCS', 'compCS', 'langCS', 'username', 'password', 'arch', 'input', 'ttylog', 'size', 'shasum', 'duplicate', 'data', 'id']`
- **Dionea Columns:** `['connection', 'dst_ip', 'dst_port', 'src_hostname', 'src_ip', 'src_port', 'timestamp', 'ftp', 'credentials']`
- **Suricata Columns:** `['timestamp', 'flow_id', 'in_iface', 'event_type', 'src_ip', 'dest_ip', 'proto', 'icmp_type', 'icmp_code', 'pkt_src', 'alert', 'direction', 'flow', 'payload', 'payload_printable', 'stream', 'src_port', 'dest_port', 'app_proto', 'metadata', 'tls', 'tx_id', 'http', 'fileinfo', 'tcp', 'smb', 'response_icmp_type', 'response_icmp_code', 'sip', 'files', 'app_proto_tc', 'anomaly', 'ssh', 'tftp', 'tx_guessed', 'app_proto_orig', 'snmp', 'rfb', 'app_proto_ts', 'pgsql', 'smtp']`


---

## Data Formatting

### 1. Columns to Save and Rename

To unify the datasets, select only the **columns relevant for anomaly detection and visualization**, and rename them consistently:
# Column Mapping Tables

## Table 1: IDENTICAL OR DIRECTLY MAPPABLE COLUMNS

| Concept | ISCX | Cowrie | Dionaea | Suricata | Unified Name |
|---------|------|--------|---------|----------|--------------|
| Source IP | `source` | `src_ip` | `src_ip` | `src_ip` | `source_ip` |
| Source Port | `sourcePort` | `src_port` | `src_port` | `src_port` | `source_port` |
| Destination IP | `destination` | `dst_ip` | `dst_ip` | `dest_ip` | `destination_ip` |
| Destination Port | `destinationPort` | `dst_port` | `dst_port` | `dest_port` | `destination_port` |
| Timestamp | `startDateTime` | `timestamp` | `timestamp` | `timestamp` | `event_time` |
| Transport Protocol | `protocolName` | *(implicit TCP)* | `connection.transport` | `proto` | `protocol` |

## Table 2: SIMILAR COLUMNS WITH DIFFERENT REPRESENTATIONS

| Concept | ISCX | Cowrie | Dionaea | Suricata | Transformation |
|---------|------|--------|---------|----------|----------------|
| **Application Protocol** | `appName` | `protocol` | `connection.protocol` | `app_proto` | Map: HTTPWeb→HTTP, SSH→SSH, smbd→SMB |
| **Duration (seconds)** | `stopDateTime - startDateTime` | `duration` | ❌ Missing | Calculate from `flow.start` | Convert to float seconds |
| **Bytes Sent** | `totalSourceBytes` | ❌ Missing | ❌ Missing | `flow.bytes_toserver` | Use 0 for missing |
| **Bytes Received** | `totalDestinationBytes` | ❌ Missing | ❌ Missing | `flow.bytes_toclient` | Use 0 for missing |
| **Packets Sent** | `totalSourcePackets` | ❌ Missing | ❌ Missing | `flow.pkts_toserver` | Use 0 for missing |
| **Packets Received** | `totalDestinationPackets` | ❌ Missing | ❌ Missing | `flow.pkts_toclient` | Use 0 for missing |
| **Direction** | `direction` (L2R/L2L/R2R) | ❌ Missing | ❌ Missing | `direction` (to_server/to_client) | Map: L2R→outbound, L2L→internal, to_server→inbound |
| **TCP Flags** | `sourceTCPFlagsDescription` | ❌ Missing | ❌ Missing | Extract from metadata | Parse "S,A,F" → one-hot encode |
| **Payload** | `sourcePayloadAsBase64` | ❌ Missing | ❌ Missing | `payload` | Decode Base64 |
| **Label** | `Label` | Infer from `eventid` | Infer from protocol | `alert.signature` | Normalize to: Normal/Attack/{AttackType} |

## Feature Engineering - Pre-calculate Offline
```python
# Rate features
bytes_per_second = total_bytes / duration
packets_per_second = total_packets / duration
bytes_per_packet = total_bytes / total_packets

# Ratio features  
bytes_ratio = bytes_sent / (bytes_sent + bytes_recv)
packets_ratio = packets_sent / (packets_sent + packets_recv)

# Temporal features
hour = timestamp.hour  # 0-23
day_of_week = timestamp.dayofweek  # 0-6
is_weekend = day_of_week in [5, 6]
is_business_hours = (9 <= hour <= 17) and not is_weekend

# TCP flags (one-hot)
flag_syn, flag_ack, flag_fin, flag_rst, flag_psh = parse_tcp_flags()

# IP classification
src_is_private = is_rfc1918(src_ip)
dst_is_private = is_rfc1918(dst_ip)
is_internal = src_is_private and dst_is_private

# Port categorization
dst_port_is_common = dst_port in [80, 443, 22, 21, 25, 53, 3389]
```

>Note: Eliminate columns with >50% NaN values 

## Feature Engineering

Based on your intended Streamlit visualization, derive **features/aggregations** for each metric:

### 1. Overall Status Metrics
- **Total events processed:** count of rows per time window (e.g., last hour)
- **Anomalous events:** count of rows with `label == ATTACK` or `is_anomaly == 1` (if using Isolation Forest)
- **Unique IPs attacking:** count unique `src_ip` in anomalous events
- **Trend indicators:** compare current time window vs previous (delta) to detect bursts

### 2. Alerts Table (Prioritization)
- Compute **anomaly score** per event (Isolation Forest, One-Class SVM, or other unsupervised method)
- Include the following columns in the alert table:
  - `timestamp`, `src_ip`, `dst_ip`, `dst_port`, `protocol`, `anomaly_score`
- Color-code severity: high score → red, medium → orange, low → yellow
- Sort by score descending to show most critical alerts first

### 3. Time-Series Analysis
- Aggregate anomalies by time windows (e.g., 5 or 10 minutes):
  - Count of anomalies per window
  - Average anomaly score per window
- These aggregates will feed line charts to visualize bursts of suspicious activity

### 4. Geolocation Features
- Use **`geolite2` or `geoip2`** to map `src_ip` to:
  - `country`
  - `latitude` / `longitude`
- Aggregations:
  - Number of anomalies per country
  - Coordinates for plotting heatmaps / scatter geo maps

### 5. Ports and Protocols
- Count number of anomalous events per `dst_port` to detect targeted services
- Count anomalies per `protocol` to understand attack vectors
- These can be visualized as bar charts

### 6. Flow-Based Features
- Compute derived features for anomaly detection:
  - Flow duration = `stopDateTime - startDateTime` or use `duration` if available
  - Total bytes and packets per flow (`bytes_src + bytes_dst`, `packets_src + packets_dst`)
  - Direction encoded numerically
  - TCP flags one-hot encoded for model input

### 7. Aggregation for Real-Time Simulation
- Group events into small batches for streaming (e.g., 1000 rows at a time)
- Maintain rolling metrics for Streamlit (last hour or last N minutes)
- Update all KPI metrics, alert table, time-series, and map plots with each batch

---

## Streamlit Dashboard Design

The application will answer four main questions:

1. **"Is everything okay or is there something that requires attention?"**
   - Display top metrics and trend indicators

2. **"If something is unusual, where should I look first?"**
   - Show prioritized alerts table with anomaly score, source IP, destination port, and severity

3. **"What is happening over time?"**
   - Time-series graph of anomaly scores, highlighting bursts of activity

4. **"Who is attacking and what are they targeting?"**
   - World map of attack origins and bar charts for most attacked ports/protocols

---

## Real-Time Simulation

- Replay historical logs using original timestamps or accelerated time
- Stream small batches to the backend (Flask API)
- Update metrics, alerts, time-series graphs, and maps in real-time
