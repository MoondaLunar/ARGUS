# Public Records Intelligence Crawler

## Overview

This is a specialized crawler designed to dig through public databases including FBI documents, court indictments, federal records, and any interconnected public data sources. It's built for intelligence gathering, research, and data correlation.

## Use Cases

**Legal Research:**
- Track specific cases across multiple courts
- Find all documents related to a defendant/plaintiff
- Build timelines of legal proceedings
- Identify patterns in case outcomes

**Investigative Journalism:**
- Find connections between individuals in public records
- Trace funding and corporate relationships
- Build networks from indictments and complaints
- Cross-reference with other public sources

**Academic Research:**
- Analyze patterns in federal prosecution
- Study corruption cases across jurisdictions
- Build datasets for statistical analysis
- Track legal precedents

**Corporate Due Diligence:**
- Find regulatory actions against companies
- Identify connected parties in legal documents
- Track compliance histories
- Monitor potential partners/acquisitions

## Supported Data Sources

### Primary Sources:
- **FBI**: fbi.gov documents, vault, FOIA releases
- **DOJ**: justice.gov, criminal cases, press releases
- **Federal Courts**: uscourts.gov, PACER, dockets
- **Court Documents**: 
  - Indictments
  - Complaints
  - Warrants
  - Affidavits
  - Plea agreements
  - Judgments
  - Sentencing memoranda

### Secondary Sources:
- SEC documents and regulatory filings
- NARA (National Archives)
- Public Integrity databases
- News archives with linked records

## Features

### Document Extraction
- **Case Numbers**: Extracts and normalizes case numbers (e.g., 23-CR-12345)
- **Defendants/Plaintiffs**: Identifies and extracts party names
- **Dates**: Parses filing dates, sentencing dates, etc.
- **Contact Info**: Extracts phone numbers, emails, addresses
- **Identifiers**: Finds SSNs, Federal IDs, etc.

### Entity Recognition
- **PERSON**: Defendant, plaintiff, witness names
- **ORGANIZATION**: Companies, agencies involved
- **LOCATION**: Court locations, incident locations
- **CASE_NUMBER**: Federal case identifiers
- **DATE**: All temporal references
- **PHONE/EMAIL/SSN**: Direct contact information

### Connection Discovery
- **Co-occurrence**: Same entity in multiple documents = connection
- **Case linking**: Documents for same case number
- **Party networks**: Who sues/prosecutes whom
- **Timeline alignment**: Events that correlate temporally

### Export Capabilities
- Knowledge graph (JSON for visualization)
- Timeline reports
- Entity networks
- Case summaries
- Statistical analysis exports

## Installation

```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Additional dependency for advanced PDF:
pip install pdfplumber
```

## Basic Usage

### Simple Public Records Crawl

```python
from trawler_public_records import PublicRecordsCrawler
import json

# Create crawler targeting specific sources
crawler = PublicRecordsCrawler(
    seed_urls=[
        "https://www.fbi.gov/investigate/public-corruption",
        "https://www.justice.gov/criminal-vcs/recent-cases",
    ],
    search_terms=["indictment", "fraud", "conspiracy"],
    max_pages=20,
    max_depth=2,
)

# Execute crawl
result = crawler.crawl()

# Process results
print(f"Found {result['crawl_summary']['records_found']} documents")
print(f"Discovered {result['crawl_summary']['connections_found']} connections")

# Save results
with open("public_records.json", "w") as f:
    json.dump(result, f, indent=2, default=str)
```

### Advanced: Specific Case Tracking

```python
from trawler_public_records import PublicRecordsCrawler

# Track a specific case
crawler = PublicRecordsCrawler(
    seed_urls=[
        "https://www.justice.gov/usao-sdny",  # Southern District NY
    ],
    search_terms=["23-CR-12345"],  # Specific case number
    max_pages=50,  # More pages for one case
    max_depth=4,
)

result = crawler.crawl()

# Analyze results
for record in result['records']:
    if record['case_number'] == "23-CR-12345":
        print(f"Found: {record['doc_type']} - {record['date_filed']}")
```

### PDF Extraction

```python
from trawler_public_records import PublicRecordExtractor

# Extract from known document URL
text = crawler.extract_from_pdf("https://example.com/indictment.pdf")

# Parse into structured data
record = crawler.parse_document_as_record(text, url)
print(f"Case: {record.case_number}")
print(f"Defendants: {record.parties}")
print(f"Entities found: {len(record.entities_found)}")
```

### Entity Analysis

```python
from trawler_public_records import PublicRecordExtractor

document_text = "... indictment text ..."

# Extract all entities
entities = PublicRecordExtractor.extract_entities(document_text)
for entity in entities:
    print(f"{entity['entity_type']}: {entity['name']}")

# Extract specific types
defendants = PublicRecordExtractor.extract_defendant_names(document_text)
case_number = PublicRecordExtractor.extract_case_number(document_text)
```

## Advanced Usage

### Build Complete Entity Network

```python
from trawler_public_records import PublicRecordsCrawler
from analysis_engine import ExportFormatter

crawler = PublicRecordsCrawler(
    seed_urls=["https://www.fbi.gov/investigate/public-corruption"],
    search_terms=["corruption"],
    max_pages=50,
)

result = crawler.crawl()

# Find all connections
connections = crawler.find_connections_between_records()

# Export as knowledge graph
records = result['records']
entities = [e['name'] for r in records for e in r['entities_found']]
kg = ExportFormatter.export_knowledge_graph(connections, entities)

# Visualize with Gephi or similar tool
import json
with open("knowledge_graph.json", "w") as f:
    json.dump(kg, f, indent=2)
```

### Case Timeline Analysis

```python
# Group documents by case
case_timelines = {}

for record in result['records']:
    case_id = record['case_number']
    if case_id not in case_timelines:
        case_timelines[case_id] = []
    
    case_timelines[case_id].append({
        'date': record['date_filed'],
        'type': record['doc_type'],
        'document': record['url']
    })

# Sort by date for each case
for case_id, events in case_timelines.items():
    events.sort(key=lambda x: x['date'])
    print(f"\n{case_id}:")
    for event in events:
        print(f"  {event['date']}: {event['type']}")
```

### Party Network Analysis

```python
# Find people/organizations in multiple cases
party_cases = {}

for record in result['records']:
    for party in record['parties']:
        if party not in party_cases:
            party_cases[party] = []
        party_cases[party].append(record['case_number'])

# Find the most connected parties
connected = sorted(
    [(p, cases) for p, cases in party_cases.items() if len(cases) > 1],
    key=lambda x: len(x[1]),
    reverse=True
)

for party, cases in connected[:10]:
    print(f"{party}: {len(cases)} cases")
```

## Entity Types

### Extracted by Default:

| Type | Pattern | Example |
|------|---------|---------|
| **CASE_NUMBER** | Federal case ID format | 23-CR-12345, 2023-CV-89012 |
| **DATE** | Filing/document dates | January 15, 2024 |
| **PHONE** | Telephone numbers | (555) 123-4567 |
| **EMAIL** | Email addresses | john.doe@example.com |
| **SSN** | Social security | 123-45-6789 |
| **PERSON** | Names of individuals | John Doe (via NLP) |
| **ORGANIZATION** | Company/agency names | Acme Corporation |
| **LOCATION** | Locations mentioned | Southern District of New York |

## Document Types Recognized

- **INDICTMENT** - Criminal charges
- **COMPLAINT** - Initial complaint in civil/criminal case
- **WARRANT** - Search or arrest warrant
- **AFFIDAVIT** - Sworn statement by agent
- **PLEA** - Plea agreement
- **JUDGMENT** - Court judgment
- **DOCUMENT** - Generic document

## Configuration Options

```python
crawler = PublicRecordsCrawler(
    seed_urls=["url1", "url2"],           # Starting URLs
    search_terms=["term1", "term2"],      # Keywords to filter
    
    # Performance
    max_pages=50,                          # Maximum pages to crawl
    max_depth=3,                           # Maximum link depth
    
    # Model settings
    ollama_model="dolphin-mixtral:8x7b",  # LLM model
    ollama_url="http://127.0.0.1:11434",  # Ollama server
    
    # Features
    extract_pdfs=True,                     # Parse PDFs
)
```

## Output Format

### Crawl Result Structure

```json
{
  "crawl_summary": {
    "pages_visited": 25,
    "records_found": 18,
    "connections_found": 42,
    "unique_entities": 87
  },
  "records": [
    {
      "doc_id": "...",
      "doc_type": "INDICTMENT",
      "title": "United States v. John Doe",
      "url": "https://...",
      "case_number": "23-CR-12345",
      "court": "SDNY",
      "date_filed": "January 15, 2024",
      "parties": ["John Doe", "Jane Smith"],
      "entities_found": [
        {
          "name": "John Doe",
          "entity_type": "PERSON",
          "confidence": 0.95,
          "context": "..."
        }
      ],
      "extracted_links": ["url1", "url2"]
    }
  ],
  "connections": [
    {
      "entity": "John Doe",
      "entity_type": "PERSON",
      "document_a": "doc_id_1",
      "document_b": "doc_id_2",
      "connection_type": "entity_co-occurrence",
      "strength": 0.8
    }
  ],
  "entities_by_type": {
    "PERSON": ["John Doe", "Jane Smith", ...],
    "ORGANIZATION": ["Acme Corp", ...],
    "CASE_NUMBER": ["23-CR-12345", ...]
  }
}
```

## Performance Tips

### Crawling Speed
1. Start with smaller max_pages for testing
2. Increase max_depth gradually (each level multiplies requests)
3. Use specific search_terms to filter results
4. Monitor with Dolphin-Mixtral: 2-3 pages/minute

### Data Quality
1. Filter out irrelevant domains early
2. Use case_number confirmation for accuracy
3. Cross-reference entity names (fuzzy matching)
4. Validate party names against databases

### Resource Usage
1. Stream large result sets to file
2. Batch process records (100 at a time)
3. Cache PDF extractions
4. Use pagination for large datasets

## Limitations & Considerations

1. **Legal**: Always check Terms of Service for each data source
2. **Rate Limiting**: Respectfully space requests (1s between pages)
3. **PDF Quality**: Scanned PDFs may require OCR
4. **Entity Accuracy**: NLP matching is 85-95% accurate
5. **Data Freshness**: Some sources update daily, others quarterly

## Examples

See `examples_public_records.py` for:
- FBI indictments crawl
- Entity network analysis
- Case tracking
- Document pattern detection
- Timeline construction
- Knowledge graph export
- Party network analysis
- PDF extraction

## Integration with Main System

Runs alongside existing crawler:

```python
# Use regular trawler for websites
from trawler_enhanced import EnhancedMemoryWebTrawler

# Use public records crawler for legal documents
from trawler_public_records import PublicRecordsCrawler

# Combine results
web_result = trawler.crawl()
records_result = pub_crawler.crawl()

# Correlate entities
from analysis_engine import FuzzyMatcher
matches = FuzzyMatcher.match_across_sources(
    web_entities=web_result['links'],
    record_parties=records_result['entities_by_type']['PERSON']
)
```

## Next Steps

1. Run `python examples_public_records.py` to see capabilities
2. Configure for your target sources
3. Start with `max_pages=5` for testing
4. Review extracted records
5. Adjust entity patterns as needed
6. Scale up to production crawls

## Support & Reference

- See README.md for base system
- Check COMMANDS_REFERENCE.txt for usage
- Review examples_public_records.py for patterns
- Test with verify_setup.py first
