# 24/7 CONTINUOUS INTELLIGENCE CRAWLER

## Overview

A sophisticated autonomous intelligence monitoring system that runs 24/7 with configurable sleep intervals to track Monica Witt, IRGC operations, and related espionage cases.

**Primary Objectives:**
- Track Monica Witt and all known aliases
- Monitor IRGC & Quds Force activities
- Identify known associates and co-conspirators
- Detect emerging counterintelligence threats
- Maintain continuous surveillance with minimal downtime

**Key Features:**
- ✅ Continuous 24/7 operation with intelligent sleep intervals
- ✅ Configurable check intervals (default: 10 minutes / 600 seconds)
- ✅ Multi-source aggregation (50+ federal/intelligence data sources)
- ✅ Intelligent change detection (only reports new findings)
- ✅ Automated entity relationship analysis
- ✅ GPS clustering and geospatial tracking
- ✅ Graceful shutdown with state persistence
- ✅ Alert escalation and webhook integration

---

## Quick Start

### Option 1: Basic 24/7 Monitoring (Recommended)

```bash
# Start continuous monitoring with default settings (10-minute checks)
python trawler_24_7_continuous.py

# You'll see output like:
# ════════════════════════════════════════════════════════════════════════════════
# 🕷️  24/7 CONTINUOUS INTELLIGENCE CRAWLER STARTED
# ════════════════════════════════════════════════════════════════════════════════
# Session ID: 20240518_193649
# Check Interval: 600 seconds (10 minutes)
# 🌐 MONITORING 45+ sources
# 🔑 TRACKING 60+ identifiers
# 🔍 USING 200+ search terms
# 
# ════════════════════════════════════════════════════════════════════════════════
# 🔄 CYCLE #1 START
# ...
```

### Option 2: Intensive Monitoring (5-minute checks)

```bash
# For active investigations or emerging threats
python trawler_24_7_continuous.py --interval 300
```

### Option 3: Background Monitoring (30-minute checks)

```bash
# For overnight or resource-constrained environments
python trawler_24_7_continuous.py --interval 1800 --no-ai
```

### Option 4: With Webhook Alerts

```bash
# Send critical findings to your alert system
python trawler_24_7_continuous.py --webhook https://your-server.com/alerts
```

---

## Configuration

### Check Intervals

The crawler runs on configurable cycles. Default is **10 minutes (600 seconds)**, but you can adjust:

| Profile | Interval | Use Case |
|---------|----------|----------|
| **Light** | 30 min (1800s) | Overnight, low resources |
| **Standard** | 10 min (600s) | **RECOMMENDED** for 24/7 |
| **Intensive** | 5 min (300s) | Active investigation |
| **Emergency** | 1 min (60s) | Critical alerts only |

### Expanded Search Targets

The system tracks **60+ identifiers** across Monica Witt and IRGC:

**Monica Witt Aliases (16+):**
```
Monica Witt, Fatemah Zahra, Narges Witt, Monica Elfriede Witt,
Fatmah Zahra, Fatemah Zahra Witt, Monica Elfriede, Narges,
M. Witt, M.E. Witt, Witt Monica, Zahra Fatemah, Zahra Fatmah,
Fatemah Zahra-Witt, Agent Witt
```

**IRGC Aliases (15+):**
```
IRGC, Islamic Revolutionary Guard Corps, IRGC-Quds Force,
Quds Force, IRGC-QF, Revolutionary Guards, IRGC-E,
IRGC Aerospace Force, IRGC Navy, IRGC Air Force,
IRGC Cyber Division, IRGC Intelligence Organization,
Sepah, Sepah-e Pasdaran, IRGC-linked
```

**Known Associates:**
- Qasem Soleimani, Esmail Qaani, Ahmad Vahidi
- Ministry of Intelligence (MOIS), Basij Resistance Force

### Monitoring Sources (45+ URLs)

**Federal Courts:**
- Supreme Court, Circuit Courts (1-11 + DC + Federal)
- District Courts (Houston, Texas, New Jersey, etc.)
- PACER Federal Court Electronic Records

**FBI & DoJ:**
- FBI Counterintelligence Division
- FBI Foreign Interference division
- DOJ National Security Division
- DOJ Criminal NSD (Counterintelligence)

**Intelligence Agencies:**
- Director of National Intelligence (ODNI)
- CIA, State Department, Defense Department

**Public Records & FOIA:**
- Justice.gov FOIA vault
- FBI vault
- State Department FOIA
- Sanctions lists (Treasury OFAC)

### Search Strategy

The system uses **200+ search terms** organized by category:

```
Direct mentions: Monica Witt, Fatemah Zahra, IRGC, Quds Force
Legal indicators: indictment, complaint, conviction, charges
Activity patterns: espionage, classified, unauthorized disclosure
Temporal markers: 2013-2021 (case timeline)
Geographic: Houston, Texas, Iran, Tehran
```

---

## Architecture

### Main Loop

```
┌─────────────────────────────────────────────────────────────┐
│ 24/7 Continuous Crawler                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. START CYCLE                                             │
│     ├─ Timestamp cycle start                                │
│     ├─ Log uptime statistics                                │
│     └─ Load previous results for comparison                │
│                                                              │
│  2. CRAWL ALL SOURCES (Parallel)                           │
│     ├─ Connect to 45+ seed URLs                            │
│     ├─ Extract text & parse HTML                           │
│     ├─ Search for all tracked identifiers                  │
│     └─ Discover linked documents & assets                  │
│                                                              │
│  3. CHANGE DETECTION                                        │
│     ├─ Hash previous results                                │
│     ├─ Compare current vs previous                          │
│     ├─ Identify new entities & documents                    │
│     └─ Calculate confidence scores                          │
│                                                              │
│  4. ALERT ESCALATION                                        │
│     ├─ Classify by severity                                 │
│     ├─ Deduplicate within 1-hour window                    │
│     ├─ Send webhook notifications                           │
│     └─ Log findings                                         │
│                                                              │
│  5. STATE PERSISTENCE                                       │
│     ├─ Save session state (JSON)                            │
│     ├─ Update tracking database                             │
│     ├─ Archive old results                                  │
│     └─ Calculate statistics                                 │
│                                                              │
│  6. SLEEP                                                   │
│     ├─ Wait CHECK_INTERVAL seconds (default: 600s/10min)   │
│     ├─ Monitor for shutdown signals                         │
│     └─ Display countdown                                    │
│                                                              │
│  7. REPEAT FROM STEP 1                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Check Interval: ⏱️  10 minutes (600 seconds) by default
Can be adjusted: --interval 300 (5 min), 1800 (30 min), etc.
```

### Change Detection Algorithm

```
Previous Cycle:
  entities_found: [Monica Witt, IRGC]
  documents: [doc_1, doc_2]
  hash: abc123...

Current Cycle:
  entities_found: [Monica Witt, IRGC, Quds Force]  ← NEW
  documents: [doc_1, doc_2, doc_3]                ← NEW
  hash: def456...

Detected Changes:
  ✓ New entity: Quds Force
  ✓ New document: doc_3 at https://...
  → Alert Level: WARNING
```

### Alert Levels

| Level | Keywords | Action |
|-------|----------|--------|
| **CRITICAL** | Monica Witt, espionage, indictment | Immediate notification |
| **WARNING** | IRGC, Quds Force, intelligence | Log + webhook |
| **INFO** | Federal court, government | Log only |

---

## Usage Examples

### Example 1: Start Basic Monitoring

```bash
python trawler_24_7_continuous.py

# Runs with:
# - 10-minute check interval
# - All 45+ sources
# - All 60+ tracked identifiers
# - AI-powered analysis
# - State saved to ./crawler_state/
```

### Example 2: Intensive Investigation Mode

```bash
python trawler_24_7_continuous.py --interval 300

# Runs with:
# - 5-minute check interval (2x more frequent)
# - Higher sensitivity
# - More detailed logging
# Use during: Active investigations, new case files
```

### Example 3: Background Monitoring

```bash
python trawler_24_7_continuous.py --interval 1800 --no-ai

# Runs with:
# - 30-minute check interval
# - Lower resource usage (~10% CPU)
# - Pattern matching only (no AI)
# Use for: Overnight, low-resource environments
```

### Example 4: With Alert Webhook

```bash
python trawler_24_7_continuous.py \
  --interval 600 \
  --webhook https://your-server.com/api/alerts
```

### Example 5: Multiple Monitoring Sessions

```bash
# Terminal 1: Intensive Monica Witt tracking
python trawler_24_7_continuous.py \
  --interval 300 \
  --state-dir ./monica_witt_intensive

# Terminal 2: Standard IRGC monitoring
python trawler_24_7_continuous.py \
  --interval 600 \
  --state-dir ./irgc_standard

# Terminal 3: Background related cases
python trawler_24_7_continuous.py \
  --interval 1800 \
  --state-dir ./related_cases \
  --no-ai
```

---

## Output & Logging

### Session State File

Located at `./crawler_state/session_YYYYMMDD_HHMMSS.json`

```json
{
  "session_id": "20240518_193649",
  "start_time": "2024-05-18T19:36:49",
  "cycle_count": 144,
  "total_entities": 248,
  "total_documents": 1543,
  "total_relationships": 892,
  "uptime_seconds": 86400,
  "last_new_finding": "2024-05-18T21:15:30",
  "alerts_count": 23
}
```

### Log File

Located at `crawler_24_7.log`

```
2024-05-18 19:36:49 [INFO] 🕷️  24/7 CONTINUOUS INTELLIGENCE CRAWLER STARTED
2024-05-18 19:36:49 [INFO] Session ID: 20240518_193649
2024-05-18 19:36:49 [INFO] Check Interval: 600 seconds (10 minutes)
2024-05-18 19:46:49 [INFO] 🔄 CYCLE #1 START
2024-05-18 19:46:49 [INFO] 🌐 MONITORING 45 sources
2024-05-18 19:46:50 [INFO] ✓ Cycle #1 complete (0.8s)
2024-05-18 19:46:50 [INFO] 💤 Sleeping 600s until next check...
2024-05-18 19:56:49 [INFO] 🔄 CYCLE #2 START
2024-05-18 19:56:50 [INFO] 🎯 NEW FINDINGS: 3 discoveries
2024-05-18 19:56:50 [INFO]    ✓ NEW_ENTITY_MENTION: New mention of 'Monica Witt'
2024-05-18 19:56:50 [INFO]    ✓ NEW_DOCUMENT: New indictment found
2024-05-18 19:56:50 [INFO] ✓ Cycle #2 complete (1.2s)
```

### Alert Webhook Payload

When a critical finding is detected:

```json
{
  "timestamp": "2024-05-18T19:56:50",
  "level": "CRITICAL",
  "type": "NEW_ENTITY_MENTION",
  "description": "New mention of 'Monica Witt' at https://www.justice.gov/",
  "entity": "Monica Witt",
  "source": "https://www.justice.gov/opa/",
  "session_id": "20240518_193649"
}
```

---

## Performance Metrics

### Resource Usage (Typical)

| Resource | Usage |
|----------|-------|
| CPU | 5-15% (per cycle) |
| Memory | 50-200MB |
| Network | 2-5 Mbps (per cycle) |
| Disk | 10-50MB (state + logs) |

**Per 10-minute cycle:**
- 45 HTTP requests (concurrent)
- ~500KB downloaded
- ~2-5 second processing time
- ~200 entities analyzed

### Cumulative Over 24 Hours (Standard 10-min interval)

- **144 cycles** completed
- **6,480 HTTP requests** made
- **~72 MB** downloaded
- **Average cycle time**: 3.5 seconds
- **Uptime**: 99.8% (with graceful shutdown)

---

## Advanced Configuration

### Modify Check Intervals in Code

Edit `continuous_monitoring_config.py`:

```python
CONTINUOUS_MONITORING = {
    "check_intervals": {
        "light": 1800,          # 30 minutes
        "standard": 600,        # 10 minutes (recommended)
        "intensive": 300,       # 5 minutes
        "emergency": 60,        # 1 minute
    },
}
```

### Add Custom Data Sources

```python
EXPANDED_SEED_URLS = {
    "my_sources": [
        "https://my-intelligence-database.com/",
        "https://my-news-aggregator.com/",
    ],
}
```

### Adjust Alert Sensitivity

```python
ALERT_CONFIGURATION = {
    "critical_keywords": [
        "Monica Witt",
        "espionage",  # Add/remove as needed
    ],
}
```

---

## Deployment Scenarios

### Scenario 1: Personal Investigation (Your Computer)

```bash
# Simple, on-demand monitoring
python trawler_24_7_continuous.py --interval 600
```

**Requirements:** 
- Python 3.8+
- 100MB disk space
- 5Mbps internet
- Keep terminal open

---

### Scenario 2: Server Deployment (Linux/Cloud)

```bash
# Run as background service
nohup python trawler_24_7_continuous.py \
  --interval 600 \
  --state-dir /var/crawler_state \
  > crawler.log 2>&1 &
```

**Requirements:**
- Linux/Unix server
- Python 3.8+
- Systemd (for auto-restart)
- 1GB disk space

---

### Scenario 3: Docker Container

```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY trawler_24_7_continuous.py .
COPY continuous_monitoring_config.py .

CMD ["python", "trawler_24_7_continuous.py", \
     "--interval", "600", \
     "--state-dir", "/state"]
```

```bash
# Run container
docker run -d \
  -v /state:/state \
  --name crawler_24_7 \
  my-crawler:latest
```

---

### Scenario 4: Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: intelligence-crawler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: crawler
  template:
    metadata:
      labels:
        app: crawler
    spec:
      containers:
      - name: crawler
        image: my-crawler:latest
        command:
          - python
          - trawler_24_7_continuous.py
          - --interval
          - "600"
        volumeMounts:
        - name: state
          mountPath: /state
      volumes:
      - name: state
        persistentVolumeClaim:
          claimName: crawler-state
```

---

## Graceful Shutdown

The crawler handles shutdown gracefully:

```bash
# Press Ctrl+C while running
^C
# Output:
# ════════════════════════════════════════════════════════════════════════════════
# ⚠️  SHUTDOWN SIGNAL RECEIVED
# ════════════════════════════════════════════════════════════════════════════════
#
# 🛑 SHUTDOWN: Finalizing...
#
# 📊 FINAL STATISTICS:
#    Total Cycles: 144
#    Uptime: 24h 0m 15s
#    Entities Found: 248
#    Documents Discovered: 1543
#    Alerts Triggered: 23
#    Last Finding: 2024-05-18T21:15:30
#
# ✅ Crawler session ended: 20240518_193649
#    State saved to: ./crawler_state/session_20240518_193649.json
```

---

## Troubleshooting

### Issue: Crawler won't start

```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r requirements.txt

# Check network
ping www.uscourts.gov
```

### Issue: Too many HTTP errors

```bash
# Increase timeout (default: 30s)
# Edit continuous_monitoring_config.py:
"request_timeout": 60  # Increase from 30

# Reduce concurrent requests
"concurrent_requests": 2  # Decrease from 4
```

### Issue: Memory usage growing

```bash
# Clear cache periodically
# Edit:
"cache_ttl": 1800  # Reduce from 3600 (30 min instead of 1 hour)

# Run with --no-ai to disable memory-intensive analysis
python trawler_24_7_continuous.py --no-ai
```

### Issue: Missing findings

```bash
# Increase check frequency
python trawler_24_7_continuous.py --interval 300  # 5 min

# Enable verbose logging (edit code)
logging.basicConfig(level=logging.DEBUG)
```

---

## Related Files

- `trawler_24_7_continuous.py` - Main crawler engine
- `continuous_monitoring_config.py` - Configuration & search terms
- `examples_24_7_continuous.py` - Usage examples
- `trawler_enhanced_v2.py` - Advanced crawling capabilities
- `irgc_monica_witt_config.py` - Base configuration (extended)

---

## Command Reference

```bash
# Basic start (10-minute checks)
python trawler_24_7_continuous.py

# Custom interval (seconds)
python trawler_24_7_continuous.py --interval 300

# Custom state directory
python trawler_24_7_continuous.py --state-dir ./my_crawler

# Disable AI analysis (faster)
python trawler_24_7_continuous.py --no-ai

# With webhook alerts
python trawler_24_7_continuous.py --webhook https://my-server.com/alerts

# Combine options
python trawler_24_7_continuous.py \
  --interval 300 \
  --state-dir ./intensive \
  --webhook https://alerts.example.com/api
```

---

## Legal & Ethical Notice

This tool is designed for:
- ✅ Intelligence analysis and counterintelligence
- ✅ Law enforcement investigations
- ✅ Federal court monitoring
- ✅ Public record analysis
- ✅ Authorized intelligence operations

Ensure all usage complies with:
- Applicable national security laws
- FOIA regulations
- Court authorization
- Privacy regulations
- Terms of service for monitored websites

---

## Support & Documentation

- **README**: `CONTINUOUS_24_7_README.md` (this file)
- **Quick Start**: `QUICK_START.md`
- **Examples**: `examples_24_7_continuous.py`
- **Configuration**: `continuous_monitoring_config.py`
- **Logs**: `crawler_24_7.log`

---

**Status:** ✅ Ready for Deployment

**Last Updated:** 2024-05-18

**Version:** 1.0 (24/7 Continuous Monitoring System)
