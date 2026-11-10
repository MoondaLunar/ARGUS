# IRGC & Monica Witt Intelligence Crawler Guide

## Overview

This specialized crawler is designed for **in-depth investigation of Monica Witt** (aliases: Fatemah Zahra, Narges Witt, Monica Elfriede Witt, Fatmah Zahra) and **IRGC (Islamic Revolutionary Guard Corps)** connections. The system automates discovery and analysis of court documents, indictments, and public records related to this espionage case.

**Primary Objectives:**
1. **Monica Witt Case** - Former U.S. Air Force officer, alleged IRGC intelligence operative
2. **IRGC Connections** - Islamic Revolutionary Guard Corps relationships and operations
3. **Co-conspirators** - Related individuals and organizations
4. **Evidence Trail** - Documents linking Monica Witt to IRGC activities

---

## Quick Start

### Basic Crawl (5-10 minutes)
```bash
python examples_irgc_monica_witt.py
```

This runs all 8 analysis examples:
- Intelligence summary (documents found)
- Monica Witt case analysis
- IRGC connection analysis
- Timeline of events
- Co-conspirators identification
- Report export (JSON, CSV)
- Search parameters verification
- Network connection analysis

### Minimal Crawl
```python
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler

crawler = IRGCMonicaWittCrawler()
report = crawler.crawl()

# Print findings
print(f"Monica Witt documents found: {len(report['monica_witt_case']['records'])}")
print(f"IRGC documents found: {len(report['irgc_connections']['records'])}")
```

---

## Understanding the Architecture

### Target Configuration

#### Primary Target #1: Monica Witt
```python
{
    "name": "Monica Witt",
    "aliases": [
        "Monica Witt",
        "Fatemah Zahra",
        "Narges Witt",
        "Monica Elfriede Witt",
        "Fatmah Zahra",
        "Fatemah Zahra Witt"
    ],
    "significance": "ESPIONAGE",
    "type": "PERSON"
}
```

**Background:** Former U.S. Air Force officer, convicted of sharing classified information with IRGC. Case appears in multiple federal indictments and court records.

**Why aliases matter:** Iranian operatives often use multiple identities. Using all aliases increases document matching accuracy.

#### Primary Target #2: IRGC
```python
{
    "name": "Iranian Revolutionary Guard Corps",
    "aliases": [
        "IRGC",
        "Islamic Revolutionary Guard Corps",
        "IRGC-Quds Force",
        "IRGC-QF",
        "Quds Force",
        "Revolutionary Guards"
    ],
    "significance": "TERRORIST_SUPPORT / ESPIONAGE",
    "type": "ORGANIZATION"
}
```

**Background:** IRGC is Iran's military organization. Quds Force is its special operations and extraterritorial operations unit. Both involved in espionage against foreign governments.

### Search Strategy

The crawler uses **multiple-layer matching**:

1. **Seed URLs** - Targets federal courts, FBI, DOJ, and relevant national security databases
2. **Search Terms** - 25+ targeted search queries across Monica Witt, IRGC, aliases
3. **Document Filtering** - Automatically filters for relevant documents
4. **Target Extraction** - Identifies and categorizes each mention

---

## Data Categories

### Monica Witt Case Documents

Documents that mention Monica Witt or any of her aliases:
- Federal indictments
- Court motions and filings
- Sentencing documents
- Appeal records
- News/press releases from DOJ

**Example documents:**
- "United States v. Monica Elfriede Witt" (indictment)
- Sentencing memoranda
- Character reference letters
- Appeal briefs

### IRGC Connection Documents

Documents linking IRGC to espionage or intelligence operations:
- Counterintelligence indictments
- Foreign intelligence operations disclosures
- Sanctions and designations documents
- Related espionage cases

### Network Documents

Documents mentioning BOTH Monica Witt AND IRGC (strongest evidence of connections):
- Co-conspirator documents
- Intelligence agency reports
- National security briefings

---

## Key Search Terms

### Monica Witt Specific
- "Monica Witt" - Direct name
- "Fatemah Zahra" - Primary alias
- "Narges Witt" - Secondary alias
- "Air Force officer" - Occupational identifier
- "classified information" - Core charge

### IRGC Specific
- "IRGC" - Direct acronym
- "Quds Force" - Special operations unit
- "Iranian intelligence" - Broader context
- "Revolutionary Guard" - Organization name
- "Soleimani" - Notable IRGC figure

### Case Indicators
- "espionage" - Primary crime
- "counterintelligence" - Investigation type
- "sanctions violation" - Secondary charges
- "export control" - Technology transfer
- "co-conspirator" - Related individuals

---

## Output Files

### irgc_monica_witt_intelligence_report.json
**Full, detailed intelligence report** containing:
- Complete document records (all fields)
- Target mentions with context
- Full text extracts
- Document metadata
- Connection information

**Size:** Typically 2-10 MB depending on documents found
**Use:** Deep analysis, evidence compilation, expert review

**Structure:**
```json
{
  "intelligence_summary": {
    "total_documents_reviewed": 1000,
    "target_related_documents": 50,
    "monica_witt_documents": 35,
    "irgc_documents": 28
  },
  "monica_witt_case": {
    "aliases": [...],
    "documents_found": 35,
    "records": [...]
  },
  "irgc_connections": {
    "organization_names": [...],
    "documents_found": 28,
    "records": [...]
  }
}
```

### irgc_monica_witt_summary.json
**Executive summary** for quick review:
- Key statistics
- Top 10 documents
- Alias and identifier lists
- Document counts by category

**Size:** 50-200 KB
**Use:** Quick briefing, overview, sharing with team

### monica_witt_documents.csv
**Spreadsheet-friendly export** with columns:
- Date Filed
- Document Type (INDICTMENT, MOTION, etc.)
- Case Number
- Court
- Title
- URL

**Size:** 20-100 KB
**Use:** Excel analysis, sorting, pivot tables, timeline visualization

---

## Usage Examples

### Example 1: Quick Status Check
```python
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler

crawler = IRGCMonicaWittCrawler()
report = crawler.crawl()

# Show findings
print(f"Monica Witt documents: {report['intelligence_summary']['monica_witt_documents']}")
print(f"IRGC documents: {report['intelligence_summary']['irgc_documents']}")
print(f"Total relevant: {report['intelligence_summary']['target_related_documents']}")
```

### Example 2: Timeline Analysis
```python
report = crawler.crawl()
records = report['monica_witt_case']['records']

# Sort by date
dated = sorted([r for r in records if r.get('date_filed')], 
               key=lambda x: x.get('date_filed', ''))

for doc in dated:
    print(f"{doc['date_filed']:20} - {doc['title']}")
```

### Example 3: Connection Network
```python
report = crawler.crawl()

# Find docs mentioning BOTH Monica Witt and IRGC
connections = [r for r in report['all_target_documents'] 
               if 'target_mentions' in r 
               and r['target_mentions'].get('monica_witt')
               and r['target_mentions'].get('irgc')]

print(f"Documents linking Monica Witt to IRGC: {len(connections)}")
for doc in connections:
    print(f"  • {doc['title']}")
```

### Example 4: Defendant/Party Extraction
```python
report = crawler.crawl()

# Extract all parties mentioned
parties = {}
for record in report['monica_witt_case']['records']:
    for party in record.get('parties', []):
        parties[party] = parties.get(party, 0) + 1

# Top parties
for party, count in sorted(parties.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{party:40} - {count} documents")
```

---

## Advanced Features

### 1. Alias Matching
The crawler automatically recognizes all Monica Witt aliases:
- Direct name matches
- Fuzzy matching (typos, variations)
- Contextual matching (mentions in same paragraph)

### 2. Document Type Recognition
Automatically identifies:
- INDICTMENT
- COMPLAINT  
- MOTION
- AFFIDAVIT
- SENTENCING
- APPEAL
- etc.

### 3. Target Mention Context
Extracts surrounding text (±100 characters) for each mention:
```python
{
  "name": "Monica Witt",
  "context": "...Monica Witt was charged with espionage and sharing classified...",
  "confidence": 0.95
}
```

### 4. Multi-Source Correlation
Tracks mentions across multiple documents to identify:
- Co-conspirators (mentioned together)
- Organization relationships
- Temporal patterns
- Geographic clusters

---

## Seed URLs (Target Databases)

The crawler targets these public federal databases:

**Federal Courts:**
- PACER (https://pacer.uscourts.gov/) - Court case information
- Southern District of Texas - Relevant jurisdiction
- Appeals courts (5th Circuit)

**Law Enforcement:**
- FBI Counterintelligence (https://www.fbi.gov/investigate/counterintelligence)
- DOJ National Security Division
- DOJ Criminal Division

**Intelligence:**
- ODNI (Director of National Intelligence)
- CIA public records
- Congressional oversight documents

**Public Records:**
- Justice Department press releases
- Federal register notices
- Congressional testimony archives

---

## Performance & Rate Limiting

- **Rate Limit:** 1 second between requests (respectful crawling)
- **Max Pages:** 100 documents per crawl (adjustable)
- **Max Depth:** 5 link levels (prevents infinite loops)
- **PDF Processing:** Automatically extracts text and metadata
- **Typical Runtime:** 5-15 minutes depending on network and document volume

---

## Customization

### Modify Search Targets

Add new aliases or organizations:
```python
# In trawler_irgc_monica_witt.py

# Add to Monica Witt aliases
MONICA_WITT.aliases.append("New Alias")

# Add new related target
NEW_TARGET = IRGCIntelligenceTarget(
    primary_name="Name",
    aliases=["alias1", "alias2"],
    entity_type="PERSON",
    significance="ESPIONAGE",
    search_terms=["term1", "term2"]
)
RELATED_TARGETS.append(NEW_TARGET)
```

### Add New Seed URLs

```python
# In _get_seed_urls()
return [
    "https://new.court.gov/",
    "https://another.database.gov/",
    # ... existing URLs
]
```

### Adjust Crawl Parameters

```python
crawler = IRGCMonicaWittCrawler()
crawler.crawler.max_pages = 200  # Increase from 100
crawler.crawler.max_depth = 7     # Increase from 5
report = crawler.crawl()
```

---

## Troubleshooting

### No documents found
- Check internet connectivity
- Verify seed URLs are accessible
- Increase `max_pages` and `max_depth`
- Check for 403/404 errors in crawler logs

### Slow crawl
- Expected: 5-15 minutes is normal
- 1-second rate limiting ensures respectful crawling
- Reduce `max_pages` if in hurry (less thorough)

### Missing documents
- Monica Witt case may have limited online availability
- PACER requires login for some documents
- Add new seed URLs if specific courts not covered

---

## Legal and Ethical Considerations

This system uses **only publicly available information**:
- Federal court documents (public record)
- DOJ press releases (public)
- FBI/intelligence agency disclosures
- Published court cases

No private, classified, or restricted information is accessed. All data is from official government sources available to the public.

---

## See Also

- `trawler_public_records.py` - Base public records crawler
- `analysis_engine.py` - Entity correlation and analysis
- `metadata_extractor.py` - Image and document metadata
- `examples_public_records.py` - General examples
- `PUBLIC_RECORDS_GUIDE.md` - Public records documentation

---

## Support

For issues or questions:
1. Check this guide (detailed examples above)
2. Review `examples_irgc_monica_witt.py` source code
3. Check crawler logs (printed to console)
4. Verify seed URLs are accessible
5. Increase log verbosity for debugging

---

**Last Updated:** 2024
**System:** IRGC & Monica Witt Intelligence Crawler v1.0
**Status:** Production Ready
