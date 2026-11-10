# Quick Reference Guide

## 📋 File Structure

### Python Analysis & Crawling
- `trawler_enhanced.py` - Enhanced web crawler with multi-document support
- `metadata_extractor.py` - EXIF, GPS, PDF metadata extraction
- `analysis_engine.py` - Correlation, fuzzy matching, timeline analysis
- `examples.py` - 8 practical usage examples
- `config_template.py` - Configuration reference
- `requirements.txt` - Python dependencies

### Java/Spring Backend
- `IntelligenceLinkEnhanced.java` - Enhanced link entity model
- `IntelligenceLinkRepositoryEnhanced.java` - Link queries (40+ methods)
- `DocumentArtifact.java` - Document artifact model
- `DocumentArtifactRepository.java` - Document queries
- `EntityGpsCluster.java` - Location cluster model
- `EntityGpsClusterRepository.java` - Cluster queries
- `CrawlerController.java` - REST API (40+ endpoints)

### Documentation
- `README.md` - Complete system documentation
- `IMPLEMENTATION_SUMMARY.md` - High-level overview
- This file - Quick reference

## 🔥 Quick Start (5 min)

### 1. Install Python Dependencies
```bash
cd "C:\Users\Moon\OneDrive\Desktop\data crawler"
pip install -r requirements.txt
```

### 2. Basic Web Crawl
```python
from trawler_enhanced import EnhancedMemoryWebTrawler
import json

trawler = EnhancedMemoryWebTrawler(
    seed_url="https://target-site.com",
    entities=["PERSON_A", "LOCATION_B", "ASSET_C"],
    max_pages=10
)

result = trawler.crawl()
print(json.dumps(result, indent=2))
```

### 3. Extract Image Metadata
```python
from metadata_extractor import MetadataExtractor

meta = MetadataExtractor.extract_image_metadata("photo.jpg")
if meta and meta.gps:
    print(f"GPS: {meta.gps.latitude}, {meta.gps.longitude}")
    print(f"Geohash: {meta.gps.geohash}")
```

### 4. Fuzzy Entity Matching
```python
from analysis_engine import FuzzyMatcher

matches = FuzzyMatcher.match_across_sources(
    ["John Smith", "Jane Doe"],
    ["Jon Smyth", "Janet Do"],
    threshold=70
)
```

### 5. Export Knowledge Graph
```python
from analysis_engine import ExportFormatter
import json

kg = ExportFormatter.export_knowledge_graph(links, entities)
with open("graph.json", "w") as f:
    json.dump(kg, f, indent=2)
```

## 🎯 Common Use Cases

### Scenario 1: Intelligence Web Crawl
**Goal:** Find relationships between entities on a website

```python
from trawler_enhanced import EnhancedMemoryWebTrawler

trawler = EnhancedMemoryWebTrawler(
    seed_url="https://intelligence-portal.local",
    entities=["TARGET_PERSON", "LOCATION_X", "ASSET_ID"],
    enable_image_extraction=True,
    enable_pdf_extraction=True
)

result = trawler.crawl()

# Filter high-confidence links
strong_links = [l for l in result['links'] if l['confidence'] >= 0.7]
for link in strong_links:
    print(f"{link['entityA']} -- {link['entityB']} ({link['confidence']})")
```

### Scenario 2: Location-Based Analysis
**Goal:** Track entity movements and find co-locations

```python
from analysis_engine import LocationIntelligence, ExportFormatter

# GPS points with metadata
locations = [
    {'latitude': 40.7128, 'longitude': -74.0060, 'entity': 'PERSON_A'},
    {'latitude': 40.7135, 'longitude': -74.0059, 'entity': 'PERSON_B'},
    {'latitude': 34.0522, 'longitude': -118.2437, 'entity': 'PERSON_A'},
]

# Find clusters
clusters = LocationIntelligence.cluster_locations(locations, radius_km=1.0)
print(f"Found {len(clusters)} location clusters")

# Generate timeline
timeline = LocationIntelligence.timeline_from_locations(locations)
print("Timeline:", timeline)

# Export heat map
heatmap = ExportFormatter.export_location_heat_map(clusters)
```

### Scenario 3: Multi-Source Correlation
**Goal:** Match entities across different sources

```python
from analysis_engine import FuzzyMatcher, CorrelationAnalyzer

# Find similar entities
matches = FuzzyMatcher.match_across_sources(
    ["PERSON_A", "PERSON_B"],
    ["PERSON_C", "PERSON_D"],
    threshold=75
)

# Find co-occurrences in documents
coocs = CorrelationAnalyzer.find_co_occurrences(
    documents=[
        {'id': 'd1', 'text': 'PERSON_A and PERSON_B met at LOCATION_X'},
        {'id': 'd2', 'text': 'At LOCATION_X, PERSON_A conducted meeting'},
    ],
    entities=["PERSON_A", "PERSON_B", "LOCATION_X"]
)
```

### Scenario 4: PDF & Image Analysis
**Goal:** Extract and correlate metadata from documents

```python
from metadata_extractor import MetadataExtractor
from analysis_engine import CorrelationAnalyzer

# Extract all metadata
documents = []
for file in ["doc1.pdf", "photo1.jpg", "photo2.jpg"]:
    meta = MetadataExtractor.extract_file_metadata(file)
    if meta:
        documents.append({'id': file, 'metadata': meta})

# Find patterns
patterns = CorrelationAnalyzer.detect_metadata_patterns(documents)
print("Common cameras:", patterns['common_cameras'])
print("Common locations:", patterns['common_locations'])
```

## 📊 REST API Quick Reference

### Link Endpoints
```bash
# Create/update link
curl -X POST http://localhost:8080/api/links \
  -H "Content-Type: application/json" \
  -d '{"entityA":"PERSON_A","entityB":"PERSON_B","confidence":0.85}'

# Find all connections for entity
curl http://localhost:8080/api/links/entity/PERSON_A

# Find high-confidence links
curl http://localhost:8080/api/links/confidence/0.7

# Find links by GPS proximity
curl http://localhost:8080/api/links/gps/40.7128,-74.0060
```

### Document Endpoints
```bash
# Store document
curl -X POST http://localhost:8080/api/documents \
  -H "Content-Type: application/json" \
  -d '{"sourceType":"web","identifier":"url","documentType":"image"}'

# Get all images
curl http://localhost:8080/api/documents/images

# Check for duplicates
curl http://localhost:8080/api/documents/hash/abc123def456

# Find by location
curl http://localhost:8080/api/documents/gps/40.7128,-74.0060
```

### Analytics Endpoints
```bash
# Get summary stats
curl http://localhost:8080/api/analytics/summary

# Response:
# {
#   "totalLinks": 1500,
#   "totalDocuments": 450,
#   "totalGpsClusters": 23,
#   "linksByType": {...}
# }
```

## 🔧 Configuration Guide

### Enable/Disable Features
```python
trawler = EnhancedMemoryWebTrawler(
    # Crawling limits
    max_pages=12,
    max_depth=3,
    max_content_bytes=1_800_000,
    
    # Feature flags
    enable_image_extraction=True,      # Extract EXIF/GPS
    enable_pdf_extraction=True,        # Parse PDFs
    
    # GPS clustering
    gps_proximity_threshold_km=1.0,
    
    # LLM settings
    ollama_model="dolphin-llama3",
    ollama_url="http://127.0.0.1:11434/api/generate"
)
```

### Tuning Analysis
```python
from analysis_engine import FuzzyMatcher, CorrelationAnalyzer

# More strict fuzzy matching
strict_matches = FuzzyMatcher.find_similar_entities(
    entity="John Smith",
    candidates=candidates,
    threshold=90  # Very strict
)

# Require more evidence
coocs = CorrelationAnalyzer.find_co_occurrences(
    documents=docs,
    entities=entities,
    min_docs=3  # Must appear in 3+ docs
)
```

## 📈 Key Metrics to Track

### Crawler Metrics
- `scannedPages` - Total pages visited
- `linkCount` - Entity relationships found
- `assetsDiscovered.total` - Documents/images found

### Quality Metrics
- Confidence score distribution (0.0-1.0)
- Link type breakdown (co-occurrence vs GPS vs metadata)
- Deduplication rate (hash matches)

### Performance Metrics
- Pages per second
- Metadata extraction time
- LLM query latency
- Database query times

## 🚨 Troubleshooting

### No Links Found
- Check entities are spelled correctly
- Verify LLM is running: `curl http://127.0.0.1:11434/api/generate`
- Lower confidence threshold temporarily
- Check logs: `tail -f logs/crawler.log`

### GPS Coordinates Not Extracted
- File must have EXIF data
- Check permissions to read files
- Some cameras strip EXIF by default

### Slow Crawling
- Increase `max_content_bytes` to skip large files
- Reduce `max_pages` to smaller sample
- Use separate thread pool for assets
- Check network connectivity

### Database Connection Issues
- Verify PostgreSQL is running
- Check credentials in config
- Ensure database exists
- Run migrations: `mvn flyway:migrate`

## 📚 Documentation Navigation

| Need | File |
|------|------|
| **Full API Reference** | README.md |
| **Architecture Details** | IMPLEMENTATION_SUMMARY.md |
| **Python Examples** | examples.py |
| **Configuration Reference** | config_template.py |
| **This Quick Guide** | This file |

## 🎓 Learning Path

1. **Start Here:** Read this file (5 min)
2. **Understand:** Review README.md architecture (15 min)
3. **Explore:** Run examples.py (10 min)
4. **Build:** Create custom crawler (30 min)
5. **Deploy:** Set up Java backend (20 min)
6. **Integrate:** Connect Python to REST API (20 min)

## 💡 Pro Tips

1. **Batch Processing:** Process 50+ documents at once for efficiency
2. **Confidence Filtering:** Start with 0.7+ confidence, lower for exploratory
3. **GPS Clustering:** Use geohash for fast proximity queries
4. **Entity Aliases:** Use fuzzy matching to find name variations
5. **Knowledge Export:** Export as JSON for visualization tools
6. **Timeline Analysis:** Group events by date for temporal correlation

## 🚀 Next Steps

1. Configure target URL and entities
2. Install dependencies: `pip install -r requirements.txt`
3. Start Ollama: `ollama serve`
4. Run crawler: `python examples.py`
5. Review results in output files
6. Deploy Java backend for persistence
7. Query via REST API

---

**Remember:** Start small, validate results, then scale up!
