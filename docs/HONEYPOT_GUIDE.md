# T-Pot Honeypot - Complete Log Guide

## Overview
This document describes all honeypots present in T-Pot and the data they collect.

**Total Events Collected:** 148,063
**Data Size:** 621 MB (296 MB compressed)
**Collection Period:** October 2025

---

### 1. **COWRIE**
**Type:** SSH & Telnet Honeypot
**Port:** 22 (SSH), 23 (Telnet)
**Description:** Simulates a vulnerable Linux system to capture SSH/Telnet attacks

**Collected data:**
- Login attempts (username/password)
- Commands executed by attackers
- Downloaded/uploaded files
- Complete attacker sessions
- Client fingerprinting (HASSH)

**Log file:** `cowrie/log/cowrie.json`

**Key fields:**
```json
{
  "eventid": "cowrie.login.failed",
  "username": "root",
  "password": "admin123",
  "src_ip": "103.177.227.135",
  "dst_port": 22,
  "timestamp": "2025-10-24T13:10:32.397585Z",
  "session": "98551c342a64",
  "protocol": "ssh"
}
```

**ML Use Cases:**
- Attack pattern analysis
- Credential stuffing detection
- Attacker behavioral analysis
- Command sequence analysis

---

### 2. **DIONAEA**
**Type:** Multi-protocol Honeypot (malware capture)
**Ports:** 21 (FTP), 42 (WINS), 135 (MSRPC), 443/445 (SMB), 1433 (MSSQL), 3306 (MySQL)
**Description:** Captures malware and exploits on Windows/database protocols

**Collected data:**
- Malware binaries (with MD5/SHA512 hashes)
- Exploit attempts
- Network connections
- Protocol-specific attacks

**Log file:** `dionaea/log/dionaea.json`

**Key fields:**
```json
{
  "src_ip": "181.115.193.18",
  "dst_port": 445,
  "md5": "a1b2c3d4...",
  "sha512": "f5e6d7...",
  "connection_protocol": "smbd",
  "timestamp": "2025-10-24T13:11:24.404497"
}
```

**ML Use Cases:**
- Malware detection
- Zero-day exploit identification
- Attack vector analysis

---

### 3. **SURICATA**
**Type:** Network Intrusion Detection System (IDS)
**Description:** Analyzes all network traffic and detects suspicious patterns

**Collected data:**
- Network flows
- Protocol analysis
- Signature-based alerts
- Traffic anomalies

**Log file:** `suricata/log/eve.json`

**Key fields:**
```json
{
  "event_type": "alert",
  "src_ip": "x.x.x.x",
  "dest_ip": "y.y.y.y",
  "proto": "TCP",
  "alert": {
    "signature": "ET SCAN Potential SSH Scan",
    "category": "Attempted Information Leak"
  }
}
```

**ML Use Cases:**
- Network anomaly detection
- Traffic pattern analysis
- Protocol abuse detection

---

### 4. **TANNER**
**Type:** Web Application Honeypot
**Port:** 80, 8080
**Description:** Simulates vulnerable web applications

**Collected data:**
- HTTP requests
- SQL injection attempts
- XSS attempts
- Path traversal attacks
- Web shells

**Log file:** `tanner/log/`

**ML Use Cases:**
- Web attack classification
- OWASP Top 10 detection
- Bot detection

---

### 5. **CONPOT**
**Type:** Industrial Control Systems (ICS/SCADA) Honeypot
**Ports:** 102 (S7), 502 (Modbus), 161 (SNMP)
**Description:** Simulates industrial systems (PLC, SCADA)

**Collected data:**
- ICS protocol attacks
- SCADA probing
- Industrial system reconnaissance

**ML Use Cases:**
- Critical infrastructure threat detection
- ICS-specific attack patterns

---

### 6. **ELASTICPOT**
**Type:** Elasticsearch Honeypot
**Port:** 9200
**Description:** Simulates a vulnerable Elasticsearch cluster

**Collected data:**
- Elasticsearch query attempts
- Data exfiltration attempts
- Cluster enumeration

---

### 7. **HONEYTRAP**
**Type:** Network security tool
**Description:** Captures connections on non-standard ports

**Collected data:**
- Unknown protocol connections
- Port scanning
- Service enumeration

---

### 8. **NGINX**
**Type:** Web server honeypot
**Port:** 80, 443
**Description:** Simulates a web server with known vulnerabilities

---

### 9. **SENTRYPEER**
**Type:** VoIP/SIP Honeypot
**Port:** 5060
**Description:** Captures VoIP attacks and fraud

**Collected data:**
- SIP registration attempts
- VoIP toll fraud attempts
- Caller enumeration

---

## SPECIALIZED HONEYPOTS

### 10. **MAILONEY**
**Type:** SMTP Honeypot
**Port:** 25
**Description:** Simulates a mail server to capture spam/phishing

---

### 11. **REDISHONEYPOT**
**Type:** Redis Honeypot
**Port:** 6379
**Description:** Simulates an unauthenticated Redis database

---

### 12. **WORDPOT**
**Type:** WordPress Honeypot
**Description:** Simulates a vulnerable WordPress site

---

### 13. **HERALDING**
**Type:** Credential catching honeypot
**Multiple ports:** FTP, Telnet, SSH, HTTP, POP3, IMAP, SMTP, VNC
**Description:** Captures credentials across multiple protocols

---

### 14. **GLUTTON**
**Type:** All-eating honeypot
**Description:** Accepts connections on all ports and protocols

---

### 15. **CISCOASA**
**Type:** Cisco ASA Honeypot
**Description:** Simulates a Cisco ASA firewall

---

### 16. **DDOSPOT**
**Type:** DDoS detection
**Description:** Detects DDoS attack attempts

---

### 17. **DICOMPOT**
**Type:** Medical imaging honeypot
**Port:** 11112
**Description:** Simulates DICOM systems (medical imaging)

---

### 18. **HONEYPOTS** (generic)
Generic configuration for custom honeypots

---

### 19. **IPPHONEY**
**Type:** IP Phone Honeypot
**Description:** Simulates IP phones

---

### 20. **MEDPOT**
**Type:** Healthcare systems honeypot
**Description:** Simulates healthcare systems

---

### 21. **LOG4POT**
**Type:** Log4Shell vulnerability honeypot
**Description:** Captures Log4Shell exploits (CVE-2021-44228)

---

### 22. **P0F**
**Type:** Passive OS fingerprinting
**Description:** Identifies operating systems from network traffic

---

### 23. **HELLPOT**
**Type:** Aggressive honeypot
**Description:** Responds aggressively to scanners

---

### Other honeypots present:
- **ADBHONEY**: Android Debug Bridge
- **BEELZEBUB**: Multi-protocol honeypot
- **BLACKHOLE**: Traffic black hole
- **CITRIXHONEYPOT**: Citrix vulnerabilities
- **ENDLESSH**: SSH tarpit
- **EWS**: Early Warning System
- **FATT**: Fingerprint All The Things
- **GALAH**: Web honeypot
- **GO-POT**: Golang-based honeypot
- **HONEYML**: ML-based honeypot
- **HONEYSAP**: SAP systems
- **H0NEYTR4P**: Custom trap
- **MINIPRINT**: Printer honeypot
- **SPIDERFOOT**: OSINT tool integration
- **TPOT**: T-Pot metadati
- **UUID**: System UUID

---

## File System Structure

```
/home/zach/tpotce/data/
├── cowrie/
│   └── log/
│       └── cowrie.json           ← PRIORITY 1
├── dionaea/
│   ├── log/
│   │   └── dionaea.json          ← PRIORITY 2
│   └── bistreams/                
├── suricata/
│   └── log/
│       └── eve.json              ← PRIORITY 3
├── tanner/
│   └── log/                      ← Web attacks
├── conpot/
│   └── log/                      ← ICS/SCADA
├── elasticpot/
├── honeytrap/
├── nginx/
├── sentrypeer/
└── elk/                          
    └── data/
```

---

## Machine Learning Priority

**High Priority:**
1. Cowrie (SSH/Telnet) - behavioral analysis
2. Dionaea (Malware) - threat intelligence
3. Suricata (Network) - anomaly detection

**Medium Priority:**
4. Tanner (Web attacks)
5. Conpot (ICS/SCADA)
6. Elasticpot, Honeytrap

**Low Priority:**
- Specialized honeypots for specific use cases

---

## Dataset Statistics

- **Total Events:** 148,063
- **Format:** NDJSON (newline-delimited JSON)
- **Original size:** 621 MB
- **Compressed size:** 296 MB
- **Active honeypots:** 30+
- **Covered protocols:** 20+ (SSH, Telnet, HTTP, SMB, FTP, MySQL, etc.)

---

## Common Fields Across All Logs

Most logs share these fields:
```json
{
  "timestamp": "ISO 8601 format",
  "src_ip": "Attacker IP",
  "dst_ip": "Honeypot IP",
  "dst_port": "Target port",
  "sensor": "Honeypot ID",
  "session": "Session ID",
  "eventid": "Event type identifier"
}
```

---

## Data Science Recommendations

1. **Start with Cowrie** - has the richest and most structured data
2. **Enrich with GeoIP** - add geographic information to IPs
3. **Normalize timestamps** - convert all to UTC
4. **Create feature engineering**:
   - Time-based features (hour, day, week)
   - IP reputation scores
   - Attack frequency per IP
   - Session duration
   - Command sequences (n-grams)

5. **Cross-honeypot joins** - correlate attacks from the same IP across different honeypots

---

## References

- T-Pot Documentation: https://github.com/telekom-security/tpotce
- Cowrie: https://github.com/cowrie/cowrie
- Dionaea: https://github.com/DinoTools/dionaea
- Suricata: https://suricata.io/
