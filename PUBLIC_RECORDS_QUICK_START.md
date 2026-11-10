╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║           PUBLIC RECORDS INTELLIGENCE CRAWLER - QUICK START               ║
║                                                                            ║
║              FBI Documents | Indictments | Court Records                 ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝


🎯 WHAT THIS DOES
════════════════════════════════════════════════════════════════════════════

Specialized crawler for public records:
  ✓ Crawls FBI documents, DOJ records, court filings
  ✓ Extracts case numbers, defendant names, dates
  ✓ Finds connections between documents
  ✓ Builds entity networks and timelines
  ✓ Exports knowledge graphs for visualization


🚀 QUICK START (5 MINUTES)
════════════════════════════════════════════════════════════════════════════

Step 1: Test the examples
─────────────────────────────────────────────────────────────────────────────
  python examples_public_records.py

Step 2: Create your first crawl
─────────────────────────────────────────────────────────────────────────────
  from trawler_public_records import PublicRecordsCrawler
  
  crawler = PublicRecordsCrawler(
      seed_urls=[
          "https://www.fbi.gov/investigate/public-corruption",
      ],
      search_terms=["indictment"],
      max_pages=10,
  )
  
  result = crawler.crawl()
  print(result['crawl_summary'])

Step 3: Analyze results
─────────────────────────────────────────────────────────────────────────────
  # Find all defendants
  for record in result['records']:
      print(f"Case: {record['case_number']}")
      print(f"Defendants: {record['parties']}")


📊 SUPPORTED DATA SOURCES
════════════════════════════════════════════════════════════════════════════

Primary:
  ✓ FBI.gov - Documents, FOIA, vault
  ✓ Justice.gov - DOJ, criminal cases, press releases
  ✓ USCOURTS.gov - Federal courts, PACER dockets
  ✓ Court documents - Indictments, complaints, warrants, affidavits
  ✓ SEC.gov - Corporate documents, enforcement actions

Secondary:
  ✓ NARA - National Archives
  ✓ Public databases with linked records
  ✓ News archives with document references


🔎 ENTITY EXTRACTION
════════════════════════════════════════════════════════════════════════════

Automatically extracts:
  CASE_NUMBER    → 23-CR-12345, 2023-CV-89012
  DEFENDANT      → Individual and organization names
  DATE           → Filing dates, judgment dates, etc.
  PHONE          → (555) 123-4567
  EMAIL          → john.doe@example.com
  SSN            → 123-45-6789
  LOCATION       → Courts, incident locations
  ORGANIZATION   → Companies, agencies


💡 COMMON USE CASES
════════════════════════════════════════════════════════════════════════════

Case Tracking:
  # Find all documents for a specific case
  case_docs = [r for r in results if r['case_number'] == "23-CR-12345"]

Defendant Network:
  # Find who's been prosecuted together
  defendants = set()
  for record in results:
      defendants.update(record['parties'])

Corruption Investigation:
  # Track corruption cases
  crawler = PublicRecordsCrawler(
      seed_urls=["https://www.fbi.gov/investigate/public-corruption"],
      search_terms=["bribery", "extortion", "corruption"],
      max_pages=50,
  )

Timeline Building:
  # Order documents chronologically
  timeline = sorted(results, key=lambda r: r['date_filed'])


📈 OUTPUT EXAMPLES
════════════════════════════════════════════════════════════════════════════

Crawl Summary:
  {
    "pages_visited": 25,
    "records_found": 18,
    "connections_found": 42,
    "unique_entities": 87
  }

Single Record:
  {
    "case_number": "23-CR-12345",
    "doc_type": "INDICTMENT",
    "court": "SDNY",
    "date_filed": "January 15, 2024",
    "parties": ["John Doe", "Jane Smith", "Acme Corp"],
    "entities_found": [
      {"name": "John Doe", "entity_type": "PERSON", "confidence": 0.95},
      {"name": "(555) 123-4567", "entity_type": "PHONE", "confidence": 0.9}
    ]
  }

Connections:
  {
    "entity": "John Doe",
    "entity_type": "PERSON",
    "document_a": "doc_id_1",
    "document_b": "doc_id_2",
    "connection_type": "entity_co-occurrence",
    "strength": 0.8
  }


⚙️ CONFIGURATION
════════════════════════════════════════════════════════════════════════════

Basic Setup:
  crawler = PublicRecordsCrawler(
      seed_urls=["https://..."],      # Starting URLs
      search_terms=["indictment"],    # Filter keywords
      max_pages=20,                   # Pages to crawl
      max_depth=2,                    # Link depth
  )

Advanced Setup:
  crawler = PublicRecordsCrawler(
      seed_urls=["https://..."],
      search_terms=["term1", "term2"],
      ollama_model="dolphin-mixtral:8x7b",  # Model to use
      ollama_url="http://127.0.0.1:11434",  # LLM server
      max_pages=50,
      max_depth=4,
      extract_pdfs=True,  # Parse PDFs
  )


🔗 FINDING CONNECTIONS
════════════════════════════════════════════════════════════════════════════

Method 1: Same entity in multiple documents
  results = crawler.crawl()
  connections = crawler.find_connections_between_records()
  
Method 2: Same case number across documents
  case_docs = [r for r in results if r['case_number'] == case_num]
  
Method 3: Party relationships
  # Find parties that appear together
  party_pairs = {}
  for record in results:
      parties = record['parties']
      for i, p1 in enumerate(parties):
          for p2 in parties[i+1:]:
              key = tuple(sorted([p1, p2]))
              party_pairs[key] = party_pairs.get(key, 0) + 1


📊 ANALYSIS EXAMPLES
════════════════════════════════════════════════════════════════════════════

Entity Network:
  from examples_public_records import example_entity_network_analysis
  example_entity_network_analysis(result['records'])

Case Tracking:
  from examples_public_records import example_case_tracking
  example_case_tracking(result['records'])

Timeline:
  from examples_public_records import example_timeline_analysis
  example_timeline_analysis(result['records'])

Knowledge Graph:
  from examples_public_records import example_export_knowledge_graph
  kg = example_export_knowledge_graph(result)
  # Use with Gephi, vis.js, or other graph tools


🎓 EXAMPLE: Complete Workflow
════════════════════════════════════════════════════════════════════════════

from trawler_public_records import PublicRecordsCrawler
import json

# 1. Create crawler
crawler = PublicRecordsCrawler(
    seed_urls=[
        "https://www.fbi.gov/investigate/public-corruption",
        "https://www.justice.gov/criminal-vcs/recent-cases",
    ],
    search_terms=["fraud", "conspiracy"],
    max_pages=15,
)

# 2. Execute crawl
print("Crawling public records...")
result = crawler.crawl()

# 3. Show summary
print(f"\nFound {result['crawl_summary']['records_found']} documents")
print(f"Discovered {result['crawl_summary']['connections_found']} connections")

# 4. Analyze results
for record in result['records'][:5]:
    print(f"\n{record['case_number']}: {record['doc_type']}")
    print(f"  Court: {record['court']}")
    print(f"  Defendants: {', '.join(record['parties'])}")

# 5. Export
with open("results.json", "w") as f:
    json.dump(result, f, indent=2, default=str)


🛠️ DOCUMENT TYPE RECOGNITION
════════════════════════════════════════════════════════════════════════════

Automatically identifies:
  INDICTMENT   → Criminal charges filed by grand jury
  COMPLAINT    → Initial filing in case
  WARRANT      → Search or arrest warrant
  AFFIDAVIT    → Sworn statement by agent/official
  PLEA         → Plea agreement between parties
  JUDGMENT     → Court's final decision
  DOCUMENT     → Other document types


⚡ PERFORMANCE
════════════════════════════════════════════════════════════════════════════

With Dolphin-Mixtral-8x7b:
  • Pages/minute: 2-3 (respectful crawling)
  • Entities per page: 20-50
  • Entity extraction: ~1 second per page
  • Full 10-page crawl: 5-10 minutes

Tips:
  ✓ Start small (max_pages=5) for testing
  ✓ Increase gradually to production runs
  ✓ 1 second delay between pages (respectful)
  ✓ Results cached after first crawl


🔍 TROUBLESHOOTING
════════════════════════════════════════════════════════════════════════════

No documents found:
  → Check seed URLs are correct
  → Verify is_relevant_url() includes your domain
  → Try broader search_terms
  → Increase max_depth

Few entities extracted:
  → Check document is text-based (not scanned PDF)
  → Add custom patterns to PATTERNS dict
  → Use extract_from_pdf() for PDF text

Slow crawling:
  → Normal - 2-3 pages/minute is expected
  → Check network connection
  → Reduce max_pages for testing


📚 FILES
════════════════════════════════════════════════════════════════════════════

Main:
  trawler_public_records.py    → Core public records crawler
  examples_public_records.py   → 8 usage examples
  PUBLIC_RECORDS_GUIDE.md      → Complete documentation

Integration:
  trawler_enhanced.py          → Regular web crawler (can use together)
  analysis_engine.py           → Correlation analysis
  metadata_extractor.py        → PDF metadata extraction


🚀 NEXT STEPS
════════════════════════════════════════════════════════════════════════════

1. Run examples:
   python examples_public_records.py

2. Test your first crawl:
   Create script with PublicRecordsCrawler
   Start with max_pages=5

3. Analyze results:
   Build timelines
   Find connections
   Export knowledge graphs

4. Scale up:
   Increase max_pages to 50+
   Add more seed URLs
   Set up database for persistence


💡 TIPS FOR SUCCESS
════════════════════════════════════════════════════════════════════════════

✓ Use specific case numbers for targeted research
✓ Follow page links to find related documents
✓ Cross-reference entities across multiple sources
✓ Build timelines by sorting on date_filed
✓ Export knowledge graphs for visualization
✓ Start small, validate results, then scale
✓ Save results to JSON for later analysis
✓ Use connection strength to prioritize relationships


═════════════════════════════════════════════════════════════════════════════

For detailed documentation: Read PUBLIC_RECORDS_GUIDE.md
For examples: Run examples_public_records.py
For usage: See trawler_public_records.py code comments

═════════════════════════════════════════════════════════════════════════════
