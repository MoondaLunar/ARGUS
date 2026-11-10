# IRGC & Monica Witt Intelligence System - Integration Guide

## System Overview

You now have a **complete intelligence gathering system** focused on Monica Witt and IRGC connections. This guide explains how all components work together.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│          IRGC & Monica Witt Intelligence System             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├─────────────────────┐
                            │                     │
                    ┌───────▼────────┐    ┌──────▼────────┐
                    │   Configuration│    │    Crawler    │
                    │  (irgc_config) │    │ (trawler_irg  │
                    └────────────────┘    │      c)       │
                            │             └───────┬────────┘
                            │                     │
                    ┌───────▼─────────────────────▼────────┐
                    │  Public Records Parser               │
                    │  (trawler_public_records.py)        │
                    └───────┬─────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼─────┐    ┌────────▼────────┐  ┌──────▼─────┐
   │ Metadata  │    │ Entity Extract. │  │   Analysis │
   │ Extractor │    │ & Linking       │  │   Engine   │
   └───────────┘    └─────────────────┘  └────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────▼───────────────────┐
        │         Output & Reporting            │
        │  • JSON reports                       │
        │  • CSV exports                        │
        │  • Knowledge graphs                   │
        └───────────────────────────────────────┘
```

---

## Component Files

### 1. Configuration Layer
**File:** `irgc_monica_witt_config.py` (10 KB)

**Purpose:** Centralized configuration for all targets, aliases, and search terms

**Key sections:**
- `PRIMARY_TARGETS` - Monica Witt and IRGC definitions
- `RELATED_TARGETS` - Secondary entities (Quds Force, MOIS, etc.)
- `SEARCH_TERMS` - Keywords for matching
- `SEED_URLS` - Federal court/FBI databases
- `CRAWLER_PARAMS` - Performance settings

**Usage:**
```python
from irgc_monica_witt_config import (
    get_monica_witt_aliases,
    get_all_search_terms,
    get_all_seed_urls
)
```

### 2. Main Crawler
**File:** `trawler_irgc_monica_witt.py` (13 KB)

**Purpose:** Intelligent crawler for Monica Witt and IRGC documents

**Key classes:**
- `IRGCIntelligenceTarget` - Target definition
- `IRGCMonicaWittCrawler` - Main crawler with intelligence filtering

**Key methods:**
- `crawl()` - Execute intelligence crawl
- `is_target_related()` - Filter for relevant documents
- `extract_target_mentions()` - Find mentions with context
- `build_intelligence_report()` - Compile findings

**Outputs:**
- Monica Witt case records
- IRGC connection records
- Connection network
- Full intelligence report

### 3. Examples & Testing
**File:** `examples_irgc_monica_witt.py` (11 KB)

**Purpose:** 8 complete, runnable examples

**Examples:**
1. Basic intelligence crawl
2. Monica Witt document analysis
3. IRGC connection analysis
4. Case timeline
5. Related entities extraction
6. Intelligence export
7. Search parameters verification
8. Network analysis

**Run all examples:**
```bash
python examples_irgc_monica_witt.py
```

### 4. Supporting Components (Already Installed)

**Public Records Crawler:**
- `trawler_public_records.py` - Base crawler for federal documents
- `PublicRecordExtractor` - Extracts entities, case numbers, dates

**Analysis Engine:**
- `analysis_engine.py` - Fuzzy matching, correlation, export

**Metadata Extraction:**
- `metadata_extractor.py` - EXIF, PDF, GPS data

---

## Data Flow

### Step 1: Configuration
```python
config = irgc_monica_witt_config
targets = [config.PRIMARY_TARGETS['monica_witt'],
           config.PRIMARY_TARGETS['irgc']]
search_terms = config.get_all_search_terms()
seed_urls = config.get_all_seed_urls()
```

### Step 2: Crawling
```python
crawler = IRGCMonicaWittCrawler()
# Uses seed_urls to start
# Follows links up to max_depth
# Extracts text from PDFs
# Caches results
raw_results = crawler.crawler.crawl()
```

### Step 3: Filtering
```python
# For each document:
for doc in raw_results:
    if crawler.is_target_related(doc.text):
        # Extract mentions
        mentions = crawler.extract_target_mentions(doc.text)
        # Categorize
        if mentions['monica_witt']:
            monica_witt_records.append(doc)
        if mentions['irgc']:
            irgc_records.append(doc)
```

### Step 4: Analysis
```python
# Build connections
connections = find_documents_with_both_targets(records)

# Timeline
timeline = sort_by_date(monica_witt_records)

# Network
network = build_entity_network(all_records)
```

### Step 5: Export
```python
# Save findings
save_json_report(report)
save_csv_export(documents)
save_knowledge_graph(network)
```

---

## Common Workflows

### Workflow 1: Quick Status Check (2 minutes)
```python
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler

crawler = IRGCMonicaWittCrawler()
report = crawler.crawl()

# Print summary
summary = report['intelligence_summary']
print(f"Monica Witt documents: {summary['monica_witt_documents']}")
print(f"IRGC documents: {summary['irgc_documents']}")
print(f"Total relevant: {summary['target_related_documents']}")
```

### Workflow 2: Full Investigation (15 minutes)
```bash
# Run complete analysis
python examples_irgc_monica_witt.py

# Files generated:
# - irgc_monica_witt_intelligence_report.json (full details)
# - irgc_monica_witt_summary.json (quick summary)
# - monica_witt_documents.csv (spreadsheet analysis)
```

### Workflow 3: Add New Target (10 minutes)
```python
# Edit irgc_monica_witt_config.py

RELATED_TARGETS['new_person'] = {
    "name": "Person Name",
    "aliases": ["alias1", "alias2"],
    "entity_type": "PERSON",
    "significance": "ESPIONAGE",
}

# Crawler automatically includes new targets
crawler = IRGCMonicaWittCrawler()
report = crawler.crawl()  # Will find new target
```

### Workflow 4: Deep Connection Analysis (20 minutes)
```python
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler
import json

crawler = IRGCMonicaWittCrawler()
report = crawler.crawl()

# Find documents mentioning BOTH Monica Witt and IRGC
all_docs = report['all_target_documents']
connections = [d for d in all_docs 
               if 'target_mentions' in d
               and d['target_mentions'].get('monica_witt')
               and d['target_mentions'].get('irgc')]

print(f"Direct connections: {len(connections)}")
for doc in connections:
    print(f"  • {doc['title']}")

# Export for further analysis
with open('connections.json', 'w') as f:
    json.dump(connections, f, indent=2)
```

---

## Integration with Other Systems

### Use with Java Spring Backend
The system generates JSON that integrates with the existing Java backend:

```bash
# Generate data
python examples_irgc_monica_witt.py

# Import into Java backend
# POST /api/document-artifacts with records
# POST /api/intelligence-links with connections
# POST /api/entity-gps-clusters with locations
```

### Use with Analysis Engine
```python
from analysis_engine import FuzzyMatcher, CorrelationAnalyzer
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler

crawler = IRGCMonicaWittCrawler()
report = crawler.crawl()

# Fuzzy match Monica Witt variants
matcher = FuzzyMatcher()
for doc in report['monica_witt_case']['records']:
    text = doc.get('full_text', '')
    matches = matcher.fuzzy_match_entities(text, 
                                          matcher.ENTITY_PATTERNS)
    print(f"Fuzzy matches: {matches}")

# Correlate records
analyzer = CorrelationAnalyzer()
timeline = analyzer.build_timeline(report['all_target_documents'])
```

### Use with Metadata Extraction
```python
from metadata_extractor import MetadataExtractor
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler

crawler = IRGCMonicaWittCrawler()
report = crawler.crawl()

extractor = MetadataExtractor()

# Extract GPS from any images found
for doc in report['all_target_documents']:
    if doc.get('attachments'):
        for attachment in doc['attachments']:
            if attachment.endswith(('.jpg', '.png', '.gif')):
                metadata = extractor.extract_image_metadata(attachment)
                if metadata.get('gps'):
                    print(f"Found GPS location: {metadata['gps']}")
```

---

## Performance Optimization

### For Large Crawls
```python
# Increase resources
crawler = IRGCMonicaWittCrawler()
crawler.crawler.max_pages = 500      # More pages
crawler.crawler.max_depth = 8        # Deeper crawl
crawler.crawler.timeout = 60         # Longer timeout

report = crawler.crawl()  # Will take 30-45 minutes
```

### For Quick Crawls
```python
# Reduce scope
crawler = IRGCMonicaWittCrawler()
crawler.crawler.max_pages = 25       # Fewer pages
crawler.crawler.max_depth = 2        # Shallow crawl
crawler.crawler.use_cache = True     # Use cached results

report = crawler.crawl()  # Will take 2-5 minutes
```

### Cache Management
```python
import os
import shutil

# Clear cache
if os.path.exists('crawler_cache'):
    shutil.rmtree('crawler_cache')

# Crawler will rebuild cache
crawler = IRGCMonicaWittCrawler()
report = crawler.crawl()
```

---

## Customization Examples

### Add New Aliases
```python
# In irgc_monica_witt_config.py
PRIMARY_TARGETS['monica_witt']['aliases'].append('New Alias')

# Or programmatically:
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler
crawler = IRGCMonicaWittCrawler()
crawler.MONICA_WITT.aliases.append('New Alias')
report = crawler.crawl()
```

### Add New Court/Database
```python
# In irgc_monica_witt_config.py
SEED_URLS['new_source'] = [
    'https://new.court.gov/',
    'https://new.database.gov/'
]

# Or programmatically:
crawler = IRGCMonicaWittCrawler()
crawler.crawler.seed_urls.extend([
    'https://new.court.gov/',
    'https://new.database.gov/'
])
report = crawler.crawl()
```

### Custom Analysis
```python
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler

crawler = IRGCMonicaWittCrawler()
report = crawler.crawl()

# Custom filtering
urgent_docs = [d for d in report['monica_witt_case']['records']
               if d.get('doc_type') == 'INDICTMENT'
               and '2020' in d.get('date_filed', '')]

print(f"2020+ indictments: {len(urgent_docs)}")
for doc in urgent_docs:
    print(f"  • {doc['title']}")
```

---

## Testing & Validation

### Test 1: Configuration Loading
```bash
python irgc_monica_witt_config.py
```
Should print all aliases, search terms, and seed URLs.

### Test 2: Crawler Initialization
```python
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler

crawler = IRGCMonicaWittCrawler()
print(f"Seed URLs: {len(crawler.crawler.seed_urls)}")
print(f"Search terms: {len(crawler.crawler.search_terms)}")
print(f"Monica Witt aliases: {len(crawler.MONICA_WITT.aliases)}")
print(f"IRGC aliases: {len(crawler.IRGC.aliases)}")
```

### Test 3: Target Matching
```python
test_text = """
The defendant, Monica Witt, is accused of sharing classified information 
with the Iranian Revolutionary Guard Corps (IRGC) Quds Force.
"""

crawler = IRGCMonicaWittCrawler()
is_relevant = crawler.is_target_related(test_text)
print(f"Text is relevant: {is_relevant}")  # Should be True

mentions = crawler.extract_target_mentions(test_text)
print(f"Monica Witt mentions: {len(mentions['monica_witt'])}")  # Should be 1
print(f"IRGC mentions: {len(mentions['irgc'])}")  # Should be 1
```

### Test 4: Full Crawl
```bash
python examples_irgc_monica_witt.py
```
Should generate three output files:
- irgc_monica_witt_intelligence_report.json
- irgc_monica_witt_summary.json
- monica_witt_documents.csv

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ImportError for trawler_public_records | Run: `pip install -r requirements.txt` |
| No documents found | Wait longer (5-15 min normal), check internet connectivity |
| JSON export fails | Check disk space, verify JSON is valid with `json.tool` |
| Slow crawl | Normal (1 sec/request). Use `max_pages=25` for quick test |
| Memory error on large crawl | Reduce `max_pages` and `max_depth` |

---

## Next Steps

1. **Quick Test:** `python examples_irgc_monica_witt.py`
2. **Review Output:** Open `monica_witt_documents.csv` in Excel
3. **Deep Analysis:** Study `irgc_monica_witt_intelligence_report.json`
4. **Customize:** Edit `irgc_monica_witt_config.py` to add targets
5. **Integrate:** Use output with Java backend or other systems

---

## Support Files

- **IRGC_MONICA_WITT_QUICK_START.md** - 5-minute overview
- **IRGC_MONICA_WITT_GUIDE.md** - Complete reference
- **trawler_irgc_monica_witt.py** - Main source code
- **examples_irgc_monica_witt.py** - Working examples
- **irgc_monica_witt_config.py** - Configuration reference

---

**System Status:** ✓ Ready for deployment

**Components:** ✓ All integrated

**Documentation:** ✓ Complete

**Ready to investigate Monica Witt and IRGC connections!**
