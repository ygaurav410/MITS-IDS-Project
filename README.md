# MITS-IDS-Project
This IDS system is a prototype and an initial Minimum Viable Product for the NEC of Software Development - III Sem-V (2023-2027) MITS-GWL

# Kali Linux Host-Based IDS with Suricata, MongoDB & Web Dashboard

## Overview

This project implements a functional **Host-Based Intrusion Detection System (HIDS)** utilizing open-source technologies on a **Kali Linux** platform. The system provides **real-time monitoring** of network traffic associated with the host, identifies potential security threats based on known signatures, logs these events persistently, and presents them through a **web-based dashboard**.

It demonstrates how to integrate key cybersecurity components into a cohesive, automated monitoring solution.

---

## Core Functionality

- **Real-Time Traffic Analysis:** Captures and inspects packets on the host interface.  
- **Signature-Based Detection:** Uses Suricata and the ET Open ruleset to detect known malicious patterns.  
- **Persistent Alert Storage:** Logs Suricata’s JSON alerts into MongoDB.  
- **Data Aggregation & API:** A Flask-based REST API provides both summarized statistics and raw alerts.  
- **Web Dashboard:** A lightweight HTML/JS interface displays alerts and stats, refreshing automatically.

---

## Project Structure

```
kali-ids-project/
├── backend/
│   ├── logger.py        # Reads Suricata logs and writes to MongoDB
│   └── api.py           # Flask API serving alert data to frontend
├── dashboard/
│   └── dashboard.html   # HTML/CSS/JS web dashboard
├── report/
│   └── ids_project_report.md   # Academic report
└── README.md             # Setup and usage guide
```

---

## Technology Stack Justification

| Component | Choice | Reason |
|------------|---------|--------|
| **OS** | Kali Linux | Preloaded with security tools and community familiarity |
| **IDS Engine** | Suricata | High-performance, multi-threaded, and ET ruleset compatible |
| **Ruleset** | ET Open | Free, updated community-maintained IDS rules |
| **Database** | MongoDB | Ideal for JSON-based Suricata EVE output |
| **Backend** | Python 3 + Flask + PyMongo | Lightweight REST API and database integration |
| **Frontend** | HTML + CSS (Bootstrap 5) + JavaScript | Simple, responsive dashboard without complex build steps |

---

## Setup Instructions (Run on Kali Linux)

### Prerequisites

- Kali Linux (VM or bare metal)
- Internet connectivity
- `sudo` privileges

---

### Step 1: Install Packages and Libraries

```bash
sudo apt update
sudo apt install suricata suricata-update mongodb python3-pip

pip3 install pymongo flask flask-pymongo flask-cors --break-system-packages
pip3 show pymongo flask flask-pymongo flask-cors  # optional verification
```

---

### Step 2: Configure and Start MongoDB

```bash
sudo systemctl start mongodb
sudo systemctl enable mongodb
sudo systemctl status mongodb
```
(Look for “active (running)” in green.)

---

### Step 3: Configure Suricata

**1. Download the Ruleset**
```bash
sudo suricata-update
```

**2. Identify Network Interface**
```bash
ip a
```

**3. Edit Configuration**
```bash
sudo nano /etc/suricata/suricata.yaml
```

- Set `HOME_NET` to your subnet (e.g. `[192.168.1.0/24]`).
- Under `af-packet:`, set your interface name (e.g. `eth0`).
- Enable **EVE log alerts**:
```yaml
outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: eve.json
      types:
        - alert:
```

**4. Validate Configuration**
```bash
sudo suricata -T -c /etc/suricata/suricata.yaml -v
```
(Look for “Configuration validation successful”.)

---

## Running the System

You’ll need **three terminals**:

### Terminal 1 — Start Suricata (The “Guard”)
```bash
sudo suricata -c /etc/suricata/suricata.yaml -i eth0
```

### Terminal 2 — Start Logger (The “Pipeline”)
```bash
cd backend/
python3 logger.py
```

### Terminal 3 — Start API Server (The “Waiter”)
```bash
cd backend/
python3 api.py
```
(Flask typically runs on `http://127.0.0.1:5000`.)

---

## Step 4: Open the Dashboard

- Navigate to `kali-ids-project/dashboard/`
- Open `dashboard.html` in your browser
- It will load and auto-refresh every 10 seconds

---

## Step 5: Test the IDS

Open a **fourth terminal** and run:

```bash
curl http://testmynids.org/uid/index.html
```

Expected sequence:
1. Terminal outputs `uid=0(root) gid=0(root)...`
2. Logger terminal logs:
   ```
   ALERT Logged: GPL ATTACK_RESPONSE id check returned root
   ```
3. Dashboard updates on the next refresh, showing the new alert.

---

## Troubleshooting Guide

| Issue | Possible Cause | Fix |
|--------|----------------|-----|
| `ModuleNotFoundError` | Missing Python packages | Re-run pip3 install commands |
| `Error connecting to MongoDB` | Service stopped | `sudo systemctl start mongodb` |
| `Log file not found` | Suricata not running | Ensure `/var/log/suricata/eve.json` exists |
| Dashboard stuck on “Loading...” | API not reachable | Ensure Flask API is running on port 5000 |
| No alerts detected | Incorrect interface or disabled `alert` type | Check `suricata.yaml` and Suricata logs |
| Test alert missing | Rule disabled | Verify with `grep 2100498 /var/lib/suricata/rules/suricata.rules` |

---

## Summary

We’ve now built and deployed a **complete host-based intrusion detection setup** on Kali Linux integrating:

- **Suricata** for packet analysis  
- **MongoDB** for structured alert storage  
- **Flask API** for data delivery  
- **Web Dashboard** for visualization  

This project demonstrates the essential components of a modern, modular security monitoring pipeline suitable for both academic and practical applications.

---
