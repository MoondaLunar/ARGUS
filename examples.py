"""
Example usage scenarios for the enhanced data crawler system
"""

import json
from trawler_enhanced import EnhancedMemoryWebTrawler
from metadata_extractor import MetadataExtractor
from analysis_engine import (
    FuzzyMatcher, LocationIntelligence, CorrelationAnalyzer, ExportFormatter
)


# Example 1: Basic web crawl with asset discovery
def example_web_crawl():
    """Crawl a website for entity relationships and assets"""
    print("=" * 60)
    print("EXAMPLE 1: Web Crawl with Asset Discovery")
    print("=" * 60)

    trawler = EnhancedMemoryWebTrawler(
        seed_url="https://example-intelligence.local",
        entities=["TARGET_PERSON_A", "LOCATION_ALPHA", "ASSET_BETA"],
        max_pages=10,
        max_depth=2,
        enable_image_extraction=True,
        enable_pdf_extraction=True,
        gps_proximity_threshold_km=1.0
    )

    result = trawler.crawl()

    print(f"Crawled {result['scannedPages']} pages")
    print(f"Found {result['linkCount']} entity relationships")
    print(f"Discovered {result['assetsDiscovered']['total']} assets")

    # Print top confidence links
    links = sorted(result['links'], key=lambda x: x['confidence'], reverse=True)[:5]
    print("\nTop Entity Connections:")
    for link in links:
        print(f"  {link['entityA']} <-> {link['entityB']} ({link['confidence']:.2f})")

    return result


# Example 2: Local file metadata extraction
def example_metadata_extraction():
    """Extract metadata from local files"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Metadata Extraction")
    print("=" * 60)

    # Image extraction
    img_path = "sample_image.jpg"
    print(f"\nExtracting image metadata from {img_path}...")
    img_metadata = MetadataExtractor.extract_image_metadata(img_path)
    if img_metadata:
        print(f"  Dimensions: {img_metadata.width}x{img_metadata.height}")
        print(f"  Camera: {img_metadata.camera_make} {img_metadata.camera_model}")
        if img_metadata.gps:
            print(f"  GPS: {img_metadata.gps.latitude:.4f}, {img_metadata.gps.longitude:.4f}")
            print(f"  Geohash: {img_metadata.gps.geohash}")

    # PDF extraction
    pdf_path = "sample_document.pdf"
    print(f"\nExtracting PDF metadata from {pdf_path}...")
    pdf_metadata = MetadataExtractor.extract_pdf_metadata(pdf_path)
    if pdf_metadata:
        print(f"  Title: {pdf_metadata.title}")
        print(f"  Author: {pdf_metadata.author}")
        print(f"  Pages: {pdf_metadata.pages}")


# Example 3: Fuzzy entity matching
def example_fuzzy_matching():
    """Find similar entities across sources"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Fuzzy Entity Matching")
    print("=" * 60)

    # Candidates from different sources
    source1 = ["John Smith", "Jane Doe", "Robert Johnson"]
    source2 = ["Jon Smith", "Jayne Dough", "Bob Johnson", "James Smith"]

    print(f"\nMatching entities from Source 1 to Source 2...")
    matches = FuzzyMatcher.match_across_sources(source1, source2, threshold=70)

    for ent1, ent2, score in matches:
        print(f"  {ent1:20} <-> {ent2:20} ({score}%)")


# Example 4: Location intelligence and clustering
def example_location_intelligence():
    """Cluster GPS coordinates and analyze locations"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Location Intelligence")
    print("=" * 60)

    # Sample GPS data
    locations = [
        {'latitude': 40.7128, 'longitude': -74.0060, 'entity': 'PERSON_A', 'timestamp': '2024-01-01'},
        {'latitude': 40.7135, 'longitude': -74.0059, 'entity': 'PERSON_B', 'timestamp': '2024-01-01'},
        {'latitude': 40.7580, 'longitude': -73.9855, 'entity': 'PERSON_A', 'timestamp': '2024-01-02'},
        {'latitude': 34.0522, 'longitude': -118.2437, 'entity': 'PERSON_C', 'timestamp': '2024-01-03'},
    ]

    print(f"\nClustering {len(locations)} GPS coordinates (1km radius)...")
    clusters = LocationIntelligence.cluster_locations(locations, radius_km=1.0)
    print(f"Found {len(clusters)} clusters")

    for i, cluster in enumerate(clusters):
        avg_lat = sum(loc['latitude'] for loc in cluster) / len(cluster)
        avg_lon = sum(loc['longitude'] for loc in cluster) / len(cluster)
        entities = [loc['entity'] for loc in cluster]
        print(f"  Cluster {i+1}: {len(cluster)} points at ({avg_lat:.4f}, {avg_lon:.4f})")
        print(f"    Entities: {', '.join(set(entities))}")

    # Generate timeline
    print("\nEntity Timeline:")
    timeline = LocationIntelligence.timeline_from_locations(locations)
    for timestamp, entries in sorted(timeline.items()):
        print(f"  {timestamp}: {len(entries)} sightings")


# Example 5: Co-occurrence analysis
def example_cooccurrence_analysis():
    """Find entities that appear together in documents"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Co-occurrence Analysis")
    print("=" * 60)

    # Sample documents
    documents = [
        {'id': 'doc1', 'text': 'PERSON_A met with LOCATION_X and ASSET_B was mentioned.'},
        {'id': 'doc2', 'text': 'At LOCATION_X, PERSON_A and PERSON_C were observed together.'},
        {'id': 'doc3', 'text': 'ASSET_B was transported from LOCATION_X.'},
        {'id': 'doc4', 'text': 'PERSON_B visited LOCATION_Y.'},
    ]

    entities = ['PERSON_A', 'PERSON_B', 'PERSON_C', 'LOCATION_X', 'LOCATION_Y', 'ASSET_B']

    print(f"\nAnalyzing co-occurrences in {len(documents)} documents...")
    coocs = CorrelationAnalyzer.find_co_occurrences(documents, entities, min_docs=1)

    print(f"Found {len(coocs)} co-occurrence patterns:")
    for cooc in coocs:
        print(f"  {cooc['entity_a']:15} <-> {cooc['entity_b']:15} ({cooc['co_occurrence_count']} docs, strength: {cooc['strength']:.2f})")


# Example 6: Metadata pattern detection
def example_metadata_patterns():
    """Detect patterns in document metadata"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Metadata Pattern Detection")
    print("=" * 60)

    # Sample documents with metadata
    documents = [
        {
            'id': 'doc1',
            'metadata': {
                'camera_make': 'Canon',
                'camera_model': 'EOS 5D',
                'gps': '40.7128,-74.0060',
                'date_taken': '2024-01-01'
            }
        },
        {
            'id': 'doc2',
            'metadata': {
                'camera_make': 'Canon',
                'camera_model': 'EOS 5D',
                'gps': '40.7130,-74.0061',
                'date_taken': '2024-01-01'
            }
        },
        {
            'id': 'doc3',
            'metadata': {
                'camera_make': 'Nikon',
                'camera_model': 'D850',
                'gps': '34.0522,-118.2437',
                'date_taken': '2024-01-02'
            }
        },
    ]

    print(f"\nAnalyzing {len(documents)} documents for metadata patterns...")
    patterns = CorrelationAnalyzer.detect_metadata_patterns(documents)

    if patterns['common_cameras']:
        print("\nCommon Cameras:")
        for camera, count in sorted(patterns['common_cameras'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {camera}: {count} documents")

    if patterns['common_locations']:
        print("\nCommon GPS Locations:")
        for location, count in sorted(patterns['common_locations'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {location}: {count} documents")


# Example 7: Knowledge graph export
def example_knowledge_graph_export():
    """Export relationship data as knowledge graph"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Knowledge Graph Export")
    print("=" * 60)

    # Sample links
    links = [
        {'entityA': 'PERSON_A', 'entityB': 'PERSON_B', 'confidence': 0.85, 'link_type': 'entity_co-occurrence', 'rationale': 'Met in document'},
        {'entityA': 'PERSON_A', 'entityB': 'LOCATION_X', 'confidence': 0.92, 'link_type': 'gps_proximity', 'rationale': 'Same GPS cluster'},
        {'entityA': 'PERSON_B', 'entityB': 'ASSET_A', 'confidence': 0.65, 'link_type': 'metadata_match', 'rationale': 'Same camera'},
    ]
    entities = ['PERSON_A', 'PERSON_B', 'LOCATION_X', 'ASSET_A']

    print(f"\nExporting knowledge graph with {len(entities)} entities and {len(links)} links...")
    kg = ExportFormatter.export_knowledge_graph(links, entities)

    print(f"\nNodes: {len(kg['nodes'])}")
    print(f"Edges: {len(kg['edges'])}")
    print(f"Average Confidence: {kg['metadata']['avg_confidence']:.2f}")

    # Print as JSON
    print("\nKnowledge Graph JSON (truncated):")
    print(json.dumps(kg, indent=2)[:500] + "...")


# Example 8: Entity relationship report
def example_entity_report():
    """Generate detailed report for a single entity"""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Entity Relationship Report")
    print("=" * 60)

    connections = [
        {'entityA': 'PERSON_A', 'entityB': 'PERSON_B', 'confidence': 0.95, 'link_type': 'entity_co-occurrence'},
        {'entityA': 'PERSON_A', 'entityB': 'LOCATION_X', 'confidence': 0.88, 'link_type': 'gps_proximity'},
        {'entityA': 'PERSON_A', 'entityB': 'ASSET_A', 'confidence': 0.72, 'link_type': 'metadata_match'},
        {'entityA': 'PERSON_A', 'entityB': 'PERSON_C', 'confidence': 0.45, 'link_type': 'entity_co-occurrence'},
    ]

    print(f"\nGenerating report for PERSON_A...")
    report = ExportFormatter.export_entity_relationship_report('PERSON_A', connections)

    print(f"\nTotal Connections: {report['total_connections']}")
    print(f"High Confidence (≥0.7): {report['high_confidence']['count']}")
    print(f"Medium Confidence (0.5-0.7): {report['medium_confidence']['count']}")
    print(f"Low Confidence (<0.5): {report['low_confidence']['count']}")
    print(f"Evidence Diversity: {report['summary']['evidence_diversity']} types")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " ENHANCED DATA CRAWLER - USAGE EXAMPLES ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")

    # Run examples (some may require actual data)
    try:
        # example_web_crawl()  # Requires valid seed URL
        pass
    except Exception as e:
        print(f"Web crawl example skipped: {e}")

    try:
        # example_metadata_extraction()  # Requires actual files
        pass
    except Exception as e:
        print(f"Metadata extraction example skipped: {e}")

    example_fuzzy_matching()
    example_location_intelligence()
    example_cooccurrence_analysis()
    example_metadata_patterns()
    example_knowledge_graph_export()
    example_entity_report()

    print("\n" + "=" * 60)
    print("Examples Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
