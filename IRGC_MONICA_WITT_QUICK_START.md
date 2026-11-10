# IRGC & Monica Witt Intelligence Crawler - Quick Start

## 30-Second Overview

Specialized crawler for investigating Monica Witt (aliases: Fatemah Zahra, Narges Witt, Monica Elfriede Witt, Fatmah Zahra) and IRGC connections through public court records, FBI documents, and federal databases.

**Status:** ✓ Ready to use
**Time to run:** 5-15 minutes
**Output:** JSON reports, CSV export, analysis files

---

## Quick Commands

### Run Full Analysis (Recommended)
```bash
python examples_irgc_monica_witt.py
```
Generates:
- `irgc_monica_witt_intelligence_report.json` (full details)
- `irgc_monica_witt_summary.json` (quick summary)
- `monica_witt_documents.csv` (spreadsheet)

### Run Minimal Test
```python
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler

crawler = IRGCMonicaWittCrawler()
report = crawler.crawl()

print(f"Monica Witt docs: {len(report['monica_witt_case']['records'])}")
print(f"IRGC docs: {len(report['irgc_connections']['records'])}")
```

---

## What It Searches For

### Monica Witt
All known aliases:
- Monica Witt
- Fatemah Zahra
- Narges Witt
- Monica Elfriede Witt
- Fatmah Zahra
- Fatemah Zahra Witt

### IRGC
All organizational names:
- IRGC
- Islamic Revolutionary Guard Corps
- IRGC-Quds Force
- Quds Force
- Revolutionary Guards
- Iranian intelligence agencies

### Locations
- Federal courts (all jurisdictions)
- FBI databases
- DOJ records
- Court records archives
- Public records databases

---

## Output Files

| File | Size | Use | Format |
|------|------|-----|--------|
| `irgc_monica_witt_intelligence_report.json` | 2-10 MB | Deep analysis, legal review | Full JSON |
| `irgc_monica_witt_summary.json` | 50-200 KB | Quick briefing | Compact JSON |
| `monica_witt_documents.csv` | 20-100 KB | Excel analysis | CSV table |

### Sample Output
```json
{
  "intelligence_summary": {
    "total_documents_reviewed": 1000,
    "target_related_documents": 42,
    "monica_witt_documents": 28,
    "irgc_documents": 18
  },
  "monica_witt_case": {
    "documents_found": 28,
    "records": [...]
  }
}
```

---

## 5 Minute Examples

### 1. See what was found
```python
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler

crawler = IRGCMonicaWittCrawler()
report = crawler.crawl()

# Summary
print(f"Total target documents: {report['intelligence_summary']['target_related_documents']}")
print(f"Monica Witt case: {len(report['monica_witt_case']['records'])} documents")
print(f"IRGC mentions: {len(report['irgc_connections']['records'])} documents")
```

### 2. View Monica Witt case documents
```python
records = report['monica_witt_case']['records']
for doc in records[:5]:
    print(f"\n{doc.get('date_filed', 'N/A')} - {doc.get('title')}")
    print(f"  Case: {doc.get('case_number')}")
    print(f"  Court: {doc.get('court')}")
    print(f"  URL: {doc.get('url')}")
```

### 3. Find Monica Witt + IRGC connections
```python
# Documents mentioning BOTH
all_docs = report['all_target_documents']
connections = [r for r in all_docs 
               if 'target_mentions' in r 
               and r['target_mentions'].get('monica_witt')
               and r['target_mentions'].get('irgc')]

print(f"Direct Monica Witt + IRGC connections: {len(connections)}")
```

### 4. Export for investigation
```python
import json

# Save full report
with open("investigation.json", "w") as f:
    json.dump(report, f, indent=2)

# Save CSV for Excel
import csv
with open("monica_witt_case.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Date", "Type", "Case", "Title", "URL"])
    for rec in report['monica_witt_case']['records']:
        writer.writerow([
            rec.get('date_filed', ''),
            rec.get('doc_type', ''),
            rec.get('case_number', ''),
            rec.get('title', ''),
            rec.get('url', '')
        ])
```

### 5. Check Monica Witt's aliases
```python
aliases = report['monica_witt_case']['aliases']
print("Monica Witt Known Aliases:")
for alias in aliases:
    print(f"  • {alias}")
```

---

## Customization

### Add New Targets

```python
# In trawler_irgc_monica_witt.py, add to RELATED_TARGETS:

NEW_TARGET = IRGCIntelligenceTarget(
    primary_name="New Person/Organization",
    aliases=["alias1", "alias2"],
    entity_type="PERSON",  # or "ORGANIZATION"
    significance="ESPIONAGE",  # or other category
    search_terms=["search term 1", "search term 2"]
)

# Then update crawler to use it
```

### Modify Search Scope

```python
crawler = IRGCMonicaWittCrawler()
# Increase search depth
crawler.crawler.max_pages = 200  # default: 100
crawler.crawler.max_depth = 7    # default: 5
report = crawler.crawl()
```

---

## Understanding Results

### Monica Witt Documents
Court filings, indictments, and records mentioning Monica Witt or her aliases directly.

**Expected content:**
- Federal indictments
- Court motions
- Sentencing documents
- Appeal briefs

### IRGC Documents
Records mentioning IRGC, Quds Force, or Iranian intelligence operations.

**Expected content:**
- Counterintelligence cases
- Foreign intelligence designations
- Related espionage indictments

### Connection Documents
Records mentioning BOTH Monica Witt AND IRGC (strongest evidence).

**These are the most important** - they show direct connections.

---

## Next Steps

1. **Run the crawler**
   ```bash
   python examples_irgc_monica_witt.py
   ```

2. **Review findings**
   - Open `irgc_monica_witt_summary.json` in any text editor
   - Open `monica_witt_documents.csv` in Excel

3. **Deep analysis**
   - Load `irgc_monica_witt_intelligence_report.json`
   - Analyze connections and relationships

4. **Customize for new targets**
   - Edit `trawler_irgc_monica_witt.py`
   - Add new aliases, search terms, or seed URLs

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No documents found" | Check internet, wait for crawl to complete (5-15 min) |
| Slow crawl | Normal! 1 sec per request = respectful crawling |
| Missing specific document | Try adding new seed URLs for that court |
| Want more documents | Increase `max_pages` and `max_depth` |

---

## Key Files

- **trawler_irgc_monica_witt.py** - Main crawler (12 KB)
- **examples_irgc_monica_witt.py** - 8 complete examples (11 KB)
- **IRGC_MONICA_WITT_GUIDE.md** - Full documentation (12 KB)

---

## Monica Witt Aliases Reference

| Primary | Aliases |
|---------|---------|
| Monica Witt | Fatemah Zahra, Narges Witt, Monica Elfriede Witt, Fatmah Zahra, Fatemah Zahra Witt |

---

**Ready to start?** → `python examples_irgc_monica_witt.py`

**Want details?** → Read `IRGC_MONICA_WITT_GUIDE.md`

**Need help?** → Check code comments in `trawler_irgc_monica_witt.py`
