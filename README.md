# Enhanced Data Crawler System

## Overview

This system provides advanced data trawling, metadata extraction, and multi-source correlation capabilities for intelligence gathering. It combines web crawling, document analysis, GPS tracking, and AI-powered entity relationship detection.

## Architecture

### Python Components

#### 1. **trawler_enhanced.py** - Core Web Trawler
Enhanced web crawler with:
- Multi-document type support (HTML, PDF, images, archives)
- Asset discovery and downloading
- Metadata extraction and storage
- GPS coordinate tracking and clustering
- Entity relationship detection

**Key Classes:**
- `EnhancedMemoryWebTrawler` - Main crawling engine
- `LinkEdge` - Entity relationship representation
- `DocumentReference` - Document asset tracking
- `DataSource` - Unified data source model

**Usage:**
```python
trawler = EnhancedMemoryWebTrawler(
    seed_url="https://example.com",
    entities=["Entity_A", "Entity_B", "Entity_C"],
    enable_image_extraction=True,
    enable_pdf_extraction=True,
    gps_proximity_threshold_km=1.0
)
result = trawler.crawl()
```

#### 2. **metadata_extractor.py** - Metadata Extraction Engine
Specialized extractors for:
- **Images**: EXIF data, GPS coordinates, camera information
- **PDFs**: Document properties, text preview, metadata
- **Documents**: File hashing, timestamps, sizing

**Key Classes:**
- `MetadataExtractor` - Auto-detection and extraction
- `ImageMetadata` - Image-specific metadata model
- `PDFMetadata` - PDF-specific metadata model
- `GPSCoordinate` - GPS location model with geohashing

**Usage:**
```python
img_meta = MetadataExtractor.extract_image_metadata("photo.jpg")
pdf_meta = MetadataExtractor.extract_pdf_metadata("document.pdf")

# Detect file type and extract
meta = MetadataExtractor.extract_file_metadata("any_file.ext")
```

#### 3. **analysis_engine.py** - Advanced Analytics
Multi-source correlation and analysis:
- Fuzzy entity matching across sources
- Geospatial clustering and timeline generation
- Co-occurrence detection
- Metadata pattern recognition
- Relationship strength calculation

**Key Classes:**
- `FuzzyMatcher` - Entity matching with fuzzy logic
- `LocationIntelligence` - GPS clustering and timeline analysis
- `CorrelationAnalyzer` - Multi-document correlation
- `ExportFormatter` - Knowledge graph and report generation

**Usage:**
```python
# Find similar entities
matches = FuzzyMatcher.find_similar_entities("John Smith", candidates)

# Cluster nearby locations
clusters = LocationIntelligence.cluster_locations(gps_points, radius_km=1.0)

# Find co-occurrences
coocs = CorrelationAnalyzer.find_co_occurrences(documents, entities)

# Export knowledge graph
kg = ExportFormatter.export_knowledge_graph(links, entities)
```

### Java Backend Components

#### 1. **IntelligenceLinkEnhanced.java** - Link Model
Enhanced entity relationship storage with:
- Multiple link types (entity_co-occurrence, gps_proximity, metadata_match)
- Metadata evidence storage
- GPS geohash tracking
- Audit trail via Hibernate Envers

**Fields:**
- `linkType`: Classification of connection
- `metadataEvidence`: JSON evidence details
- `gpsGeohash`: For proximity queries
- Timestamps for temporal analysis

#### 2. **DocumentArtifact.java** - Asset Storage
Unified document artifact model:
- Multiple source types (web, local, archive)
- Full metadata storage
- GPS information with geohashing
- Image and PDF-specific fields

**Key Fields:**
- `sourceType`, `documentType`: Classification
- `hashMd5`: Deduplication
- GPS fields for location tracking
- `metadata`: Flexible JSON storage

#### 3. **EntityGpsCluster.java** - Location Intelligence
Entity-location cluster model:
- GPS coordinate aggregation
- Sighting tracking and corroboration
- Confidence scoring
- Timeline tracking (first_seen, last_seen)

#### 4. **Repositories** - Data Access
Enhanced JPA repositories with custom queries:
- `IntelligenceLinkRepository`: Link queries by type, confidence, geohash
- `DocumentArtifactRepository`: Document discovery by hash, type, GPS
- `EntityGpsClusterRepository`: Location-based entity clustering

#### 5. **CrawlerController.java** - REST API
Comprehensive REST endpoints:
- Link management and querying
- Document artifact storage and retrieval
- GPS cluster operations
- Analytics and summary endpoints

**API Endpoints:**
```
POST   /api/links                          - Create/update link
GET    /api/links/entity/{entity}          - Get all connections
GET    /api/links/type/{linkType}          - Filter by type
GET    /api/links/confidence/{threshold}   - Confidence filtering
GET    /api/links/gps/{geohash}            - GPS proximity

POST   /api/documents                      - Store document
GET    /api/documents/hash/{hash}          - Dedup check
GET    /api/documents/gps/{geohash}        - Location search
GET    /api/documents/images               - All images
GET    /api/documents/pdfs                 - All PDFs

POST   /api/clusters/gps                   - Create cluster
GET    /api/clusters/gps/{geohash}         - Find clusters
GET    /api/clusters/confidence/{threshold}

GET    /api/analytics/summary              - Overview stats
```

## Data Models

### Link Types
- **entity_co-occurrence**: Entities appear in same document/passage
- **gps_proximity**: Entities/assets at same GPS location
- **metadata_match**: Matching metadata (camera, author, etc)
- **document_co-occurrence**: Entities in same document

### Confidence Scoring
- Based on LLM analysis, co-occurrence frequency, metadata corroboration
- Ranges 0.0-1.0
- Updated across multiple crawl runs
- Audited via Hibernate Envers

### Geohashing
- Uses precision geohashing for GPS clustering
- Default precision: 5 decimal places (≈1.1m accuracy)
- Enables fast proximity queries
- Supports radius-based search

## Workflow Examples

### Example 1: Web Crawl with Asset Discovery
```python
from trawler_enhanced import EnhancedMemoryWebTrawler
import json

trawler = EnhancedMemoryWebTrawler(
    seed_url="https://intelligence-portal.local",
    entities=["TARGET_PERSON", "LOCATION_X", "ASSET_ID"],
    max_pages=20,
    max_depth=3,
    enable_image_extraction=True
)

result = trawler.crawl()
print(json.dumps(result, indent=2))

# Result includes:
# - Entity relationships with confidence scores
# - Discovered images with EXIF/GPS data
# - PDFs with extracted metadata
# - GPS clustering results
```

### Example 2: Fuzzy Entity Matching
```python
from analysis_engine import FuzzyMatcher, CorrelationAnalyzer

# Find variations of same entity across sources
matches = FuzzyMatcher.match_across_sources(
    source1_entities=["John Smith", "J. Smith"],
    source2_entities=["John Smyth", "Jon Smith"],
    threshold=75
)

# Find co-occurrences
coocs = CorrelationAnalyzer.find_co_occurrences(
    documents=crawled_docs,
    entities=["TARGET_A", "TARGET_B"],
    min_docs=2
)
```

### Example 3: Location Intelligence
```python
from analysis_engine import LocationIntelligence

# Cluster GPS coordinates
clusters = LocationIntelligence.cluster_locations(
    gps_points,
    radius_km=1.0
)

# Generate timeline
timeline = LocationIntelligence.timeline_from_locations(locations)

# Export heat map data
heatmap = ExportFormatter.export_location_heat_map(clusters)
```

### Example 4: Relationship Analysis
```python
from analysis_engine import CorrelationAnalyzer, ExportFormatter

# Detect patterns
patterns = CorrelationAnalyzer.detect_metadata_patterns(documents)

# Generate relationship report
report = ExportFormatter.export_entity_relationship_report(
    entity="TARGET_ENTITY",
    connections=all_connections
)

# Export knowledge graph
kg_json = ExportFormatter.export_knowledge_graph(links, entities)
```

## Configuration

### Environment Variables
```
OLLAMA_MODEL=dolphin-llama3
OLLAMA_URL=http://127.0.0.1:11434/api/generate
MAX_CRAWL_PAGES=12
MAX_CONTENT_BYTES=1800000
GPS_PROXIMITY_THRESHOLD_KM=1.0
```

### Database Requirements
- PostgreSQL 12+ (or compatible)
- Hibernate with Envers for audit trails
- Schema auto-creation via JPA

## Installation

### Python
```bash
pip install -r requirements.txt
```

**Requirements:**
- requests
- beautifulsoup4
- lxml
- Pillow (image processing)
- PyPDF2 (PDF extraction)
- python-Levenshtein (fuzzy matching)
- fuzzywuzzy (fuzzy matching)

### Java/Spring Boot
```bash
mvn clean install
mvn spring-boot:run
```

**Dependencies:**
- Spring Boot 3.x
- Spring Data JPA
- Hibernate with Envers
- PostgreSQL JDBC driver
- Lombok

## Advanced Features

### GPS Proximity Detection
- Automatic EXIF GPS extraction from images
- Geohash-based clustering
- Configurable proximity radius
- Entity co-location link generation

### Metadata Evidence
- Structured metadata storage in links
- EXIF data correlation
- PDF property matching
- Document hash-based deduplication

### Multi-Source Correlation
- Fuzzy entity name matching
- Timeline alignment across sources
- Metadata pattern detection
- Cross-source confidence scoring

### Audit Trails
- All changes tracked via Hibernate Envers
- Historical confidence evolution
- Source URL tracking
- Temporal relationship analysis

## Limitations & Considerations

1. **LLM Dependency**: Requires Ollama or compatible service
2. **Memory**: Large crawls may require adjustment of max_content_bytes
3. **Rate Limiting**: Respects 0.8s delay between requests
4. **GPS Precision**: Limited by EXIF data availability
5. **PDF Extraction**: Works best with text-based PDFs

## Future Enhancements

- Neo4j integration for graph visualization
- Streaming analysis for large datasets
- Automated cluster invalidation rules
- Advanced NLP entity extraction
- Real-time update pipelines
- Distributed crawling support
