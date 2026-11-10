# 24/7 CONTINUOUS CRAWLER - QUICK START

## 60-Second Setup

```bash
# 1. Navigate to crawler directory
cd "C:\Users\Moon\OneDrive\Desktop\data crawler"

# 2. Run the continuous crawler (default: 10-minute checks)
python trawler_24_7_continuous.py

# 3. See it monitor Monica Witt & IRGC continuously
# (Press Ctrl+C to stop gracefully)
```

✅ **That's it! It's now running 24/7.**

---

## What's Happening?

Every 10 minutes (600 seconds), the crawler:

1. **Checks 45+ federal data sources**
   - Federal courts, FBI, DoJ, intelligence agencies
   - PACER, FOIA databases, sanctions lists

2. **Searches for 60+ tracked identifiers**
   - Monica Witt (16+ aliases)
   - IRGC & Quds Force (15+ variations)
   - Known associates

3. **Looks for 200+ key phrases**
   - Espionage indicators
   - Legal document types
   - Case-specific terminology

4. **Detects NEW findings**
   - New entity mentions
   - New court documents
   - New relationships
   - **Alerts you immediately**

5. **Sleeps 10 minutes**, then repeats

---

## Different Monitoring Modes

### Standard (Recommended)
```bash
python trawler_24_7_continuous.py
# 10-minute checks, balanced resource usage
```

### Intensive (Active Investigations)
```bash
python trawler_24_7_continuous.py --interval 300
# 5-minute checks, more sensitive
```

### Background (Overnight)
```bash
python trawler_24_7_continuous.py --interval 1800 --no-ai
# 30-minute checks, lower resource usage
```

### With Alerts
```bash
python trawler_24_7_continuous.py --webhook https://your-server.com/alerts
# Send critical findings to your alert system
```

---

## Output Example

```
════════════════════════════════════════════════════════════════════════════════
🕷️  24/7 CONTINUOUS INTELLIGENCE CRAWLER STARTED
════════════════════════════════════════════════════════════════════════════════
Session ID: 20240518_193649
Check Interval: 600 seconds (10 minutes)
🌐 MONITORING 45 sources
🔑 TRACKING 60 identifiers
🔍 USING 200+ search terms

════════════════════════════════════════════════════════════════════════════════
🔄 CYCLE #1 START
   Time: 2024-05-18 19:36:49
   Uptime: 0s
   Accumulated: 0 entities, 0 documents
════════════════════════════════════════════════════════════════════════════════

✓ Cycle #1 complete (0.8s)
   Next check in 600 seconds

💤 Sleeping 600s until next check...

[10 minutes later...]

════════════════════════════════════════════════════════════════════════════════
🔄 CYCLE #2 START
   Time: 2024-05-18 19:46:49
   Uptime: 10m 0s
   Accumulated: 5 entities, 12 documents
════════════════════════════════════════════════════════════════════════════════

🎯 NEW FINDINGS: 2 discoveries
   ✓ NEW_ENTITY_MENTION: New mention of 'Monica Witt'
   ✓ NEW_DOCUMENT: New document discovered

✓ Cycle #2 complete (1.2s)
```

---

## Where's the Data?

### Session State
```
./crawler_state/session_YYYYMMDD_HHMMSS.json
```

Contains: Cycle count, entities found, documents discovered, uptime, alerts

### Log File
```
crawler_24_7.log
```

Contains: All crawl activity, new findings, errors, statistics

### Example Query
```bash
# Check current session status
cat ./crawler_state/session_*.json | tail -1 | python -m json.tool

# View recent discoveries
grep "NEW_FINDING\|NEW_ENTITY\|NEW_DOCUMENT" crawler_24_7.log | tail -10

# Count alerts so far
grep "ALERT\|CRITICAL\|WARNING" crawler_24_7.log | wc -l
```

---

## Stopping the Crawler

Press `Ctrl+C` at any time. It will:

```
✓ Stop current cycle gracefully
✓ Save final statistics
✓ Report total findings
✓ Clean up resources
```

Example shutdown:
```
════════════════════════════════════════════════════════════════════════════════
⚠️  SHUTDOWN SIGNAL RECEIVED
════════════════════════════════════════════════════════════════════════════════

🛑 SHUTDOWN: Finalizing...

📊 FINAL STATISTICS:
   Total Cycles: 144
   Uptime: 24h 0m 15s
   Entities Found: 248
   Documents Discovered: 1543
   Alerts Triggered: 23
   Last Finding: 2024-05-18T21:15:30

✅ Crawler session ended: 20240518_193649
   State saved to: ./crawler_state/session_20240518_193649.json
```

---

## What Gets Monitored?

### Primary Target 1: Monica Witt
- All known aliases (16+ variations)
- Case files and court documents
- Associated individuals
- Timeline analysis

### Primary Target 2: IRGC & Quds Force
- Organizational structure
- Personnel changes
- Operations updates
- Sanctions/designations

### Secondary: Known Associates
- Qasem Soleimani
- Esmail Qaani
- Ahmad Vahidi
- MOIS, Basij Force

### Data Sources: 45+ URLs
- Federal courts (1-11 circuits + DC)
- FBI counterintelligence
- DoJ National Security Division
- Intelligence agencies
- FOIA databases
- Sanctions lists

---

## Advanced Options

### Running Multiple Sessions

```bash
# Terminal 1: Intensive Monica Witt tracking
python trawler_24_7_continuous.py --interval 300 --state-dir ./monica_witt

# Terminal 2: Standard IRGC monitoring
python trawler_24_7_continuous.py --interval 600 --state-dir ./irgc

# Terminal 3: Background related cases
python trawler_24_7_continuous.py --interval 1800 --state-dir ./related
```

### Custom Check Interval

```bash
# 5 minutes (intensive)
python trawler_24_7_continuous.py --interval 300

# 15 minutes
python trawler_24_7_continuous.py --interval 900

# 30 minutes (background)
python trawler_24_7_continuous.py --interval 1800

# 1 minute (emergency)
python trawler_24_7_continuous.py --interval 60
```

### Webhook Notifications

```bash
python trawler_24_7_continuous.py \
  --webhook https://your-server.com/api/intelligence-alerts
```

The crawler sends JSON alerts like:
```json
{
  "timestamp": "2024-05-18T19:56:50",
  "level": "CRITICAL",
  "type": "NEW_ENTITY_MENTION",
  "description": "New mention of Monica Witt",
  "entity": "Monica Witt",
  "source": "https://www.justice.gov/opa/"
}
```

---

## Performance

### Resource Usage
- **CPU**: 5-15% during checks
- **Memory**: 50-200MB
- **Network**: 2-5 Mbps per cycle
- **Disk**: ~10-50MB for state/logs

### Per Cycle (10 minutes)
- 45 HTTP requests (concurrent)
- ~500KB downloaded
- ~2-5 seconds processing
- ~200 entities analyzed

### Over 24 Hours
- 144 cycles
- 6,480 requests
- ~72MB downloaded
- Average 3.5s per cycle

---

## Troubleshooting

### Q: Nothing happening?
**A:** Check the log file:
```bash
tail -20 crawler_24_7.log
```

### Q: Too slow?
**A:** Disable AI analysis:
```bash
python trawler_24_7_continuous.py --no-ai
```

### Q: Out of memory?
**A:** Run in background mode:
```bash
python trawler_24_7_continuous.py --interval 1800 --no-ai
```

### Q: Network errors?
**A:** Run with longer timeout:
```bash
# Edit continuous_monitoring_config.py
PERFORMANCE_CONFIG = {
    "request_timeout": 60,  # Increase from 30
}
```

### Q: Want to check progress without stopping?
**A:** In another terminal:
```bash
# View latest status
tail -5 crawler_24_7.log

# Count total discoveries
grep -c "NEW_FINDING\|NEW_ENTITY\|NEW_DOCUMENT" crawler_24_7.log
```

---

## Next Steps

1. **Let it run overnight**
   - Get 6 hours of baseline data
   - See what it finds

2. **Check the results**
   ```bash
   cat ./crawler_state/session_*.json | python -m json.tool
   ```

3. **Review discoveries**
   ```bash
   grep "NEW_" crawler_24_7.log
   ```

4. **Set up webhooks** (optional)
   - Route critical alerts to your system
   - See real-time notifications

5. **Deploy to server** (optional)
   - Run 24/7 on cloud instance
   - Keep monitoring going

---

## Command Cheat Sheet

```bash
# Start with default settings
python trawler_24_7_continuous.py

# Start with 5-minute checks
python trawler_24_7_continuous.py --interval 300

# Start with 30-minute checks (background)
python trawler_24_7_continuous.py --interval 1800

# Disable AI (faster)
python trawler_24_7_continuous.py --no-ai

# With webhooks
python trawler_24_7_continuous.py --webhook https://your-server.com/alerts

# Custom state directory
python trawler_24_7_continuous.py --state-dir ./my_state

# All options combined
python trawler_24_7_continuous.py \
  --interval 600 \
  --state-dir ./my_crawler \
  --webhook https://alerts.example.com \
  --no-ai
```

---

## 24/7 Monitoring Targets

### 🎯 Monica Witt
```
Monica Witt, Fatemah Zahra, Narges Witt, Monica Elfriede Witt,
Fatmah Zahra, Fatemah Zahra Witt, Monica Elfriede, Narges,
M. Witt, M.E. Witt, Agent Witt, and more variations
```

### 🏢 IRGC & Quds Force
```
IRGC, Islamic Revolutionary Guard Corps, IRGC-Quds Force,
Quds Force, IRGC-QF, IRGC-E, Revolutionary Guards,
IRGC Aerospace, IRGC Navy, IRGC Cyber, and more
```

### 🔗 Associates
```
Qasem Soleimani, Esmail Qaani, Ahmad Vahidi, MOIS, Basij
```

---

## Status: ✅ Ready to Go

Your continuous crawler is ready. Just run it and let it monitor 24/7.

```bash
python trawler_24_7_continuous.py
```

Monitor Monica Witt, IRGC, and related espionage cases continuously with periodic 10-minute checks (configurable).

---

**For detailed documentation**: See `CONTINUOUS_24_7_README.md`

**For examples**: Run `python examples_24_7_continuous.py`
