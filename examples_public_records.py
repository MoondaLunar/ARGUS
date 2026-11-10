"""
Public Records Intelligence Analysis System
Advanced examples for FBI documents, indictments, and court records
"""

import json
import requests
from trawler_public_records import PublicRecordsCrawler, PublicRecordExtractor
from analysis_engine import FuzzyMatcher, CorrelationAnalyzer, ExportFormatter


# Example 1: Crawl FBI Documents & Indictments
def example_fbi_indictments():
    """Search for and analyze FBI indictments"""
    print("=" * 70)
    print("EXAMPLE 1: FBI Indictments & Court Records")
    print("=" * 70)

    crawler = PublicRecordsCrawler(
        seed_urls=[
            "https://www.fbi.gov/investigate/public-corruption",
            "https://www.fbi.gov/investigate/white-collar-crime",
            "https://www.justice.gov/criminal-vcs/recent-cases",
        ],
        search_terms=["indictment", "fraud", "conspiracy", "corruption"],
        max_pages=15,
        max_depth=2,
    )

    print("\nCrawling public records...")
    result = crawler.crawl()

    print(f"\n✓ Found {result['crawl_summary']['records_found']} documents")
    print(f"✓ Discovered {result['crawl_summary']['connections_found']} connections")
    print(f"✓ Extracted {result['crawl_summary']['unique_entities']} unique entities")

    # Show entity types found
    print("\nEntities by type:")
    for entity_type, entities in result['entities_by_type'].items():
        print(f"  {entity_type}: {len(entities)} unique")
        if entities:
            print(f"    Examples: {', '.join(entities[:3])}")

    # Show connections
    if result['connections']:
        print(f"\nTop connections found:")
        for conn in result['connections'][:5]:
            print(f"  {conn['entity']} ({conn['entity_type']}) appears in 2+ documents")

    return result


# Example 2: Entity Network Analysis
def example_entity_network_analysis(records):
    """Analyze network of connected entities across records"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Entity Network Analysis")
    print("=" * 70)

    # Build entity co-occurrence graph
    entity_pairs = {}
    
    for record in records:
        entities = [e.name for e in record['entities_found']]
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                pair = tuple(sorted([entity1, entity2]))
                if pair not in entity_pairs:
                    entity_pairs[pair] = 0
                entity_pairs[pair] += 1

    # Sort by frequency
    sorted_pairs = sorted(entity_pairs.items(), key=lambda x: x[1], reverse=True)

    print(f"\nTop entity pairs (appear together):")
    for (entity1, entity2), count in sorted_pairs[:10]:
        print(f"  {entity1:30} <-> {entity2:30} ({count} times)")


# Example 3: Case Number Tracking
def example_case_tracking(records):
    """Track specific cases across documents"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Case Number Tracking")
    print("=" * 70)

    case_docs = {}
    
    for record in records:
        if record['case_number']:
            case_id = record['case_number']
            if case_id not in case_docs:
                case_docs[case_id] = []
            case_docs[case_id].append({
                'doc_type': record['doc_type'],
                'url': record['url'],
                'date': record['date_filed'],
                'parties': record['parties']
            })

    print(f"\nFound {len(case_docs)} unique cases")
    
    # Show most referenced cases
    sorted_cases = sorted(case_docs.items(), key=lambda x: len(x[1]), reverse=True)
    
    print("\nMost referenced cases:")
    for case_id, docs in sorted_cases[:10]:
        print(f"\n  Case: {case_id}")
        print(f"  Documents: {len(docs)}")
        print(f"  Types: {', '.join(set(d['doc_type'] for d in docs))}")
        if docs[0]['parties']:
            print(f"  Parties: {', '.join(docs[0]['parties'][:3])}")


# Example 4: Pattern Detection - Document Types
def example_document_patterns(records):
    """Detect patterns in document types and outcomes"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Document Pattern Analysis")
    print("=" * 70)

    doc_types = {}
    courts = {}
    
    for record in records:
        doc_type = record['doc_type']
        if doc_type not in doc_types:
            doc_types[doc_type] = 0
        doc_types[doc_type] += 1

        if record['court']:
            court = record['court']
            if court not in courts:
                courts[court] = 0
            courts[court] += 1

    print(f"\nDocument types found:")
    for doc_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {doc_type:15} : {count:3} documents")

    print(f"\nCourts/Sources:")
    for court, count in sorted(courts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {court:15} : {count:3} documents")


# Example 5: Timeline Construction
def example_timeline_analysis(records):
    """Build timeline of events from filing dates"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Timeline Construction")
    print("=" * 70)

    timeline = {}
    
    for record in records:
        if record['date_filed']:
            date = record['date_filed']
            if date not in timeline:
                timeline[date] = []
            timeline[date].append({
                'case': record['case_number'],
                'type': record['doc_type'],
                'title': record['title'][:60]
            })

    print(f"\nTimeline ({len(timeline)} unique dates):")
    
    for date in sorted(timeline.keys())[:10]:
        events = timeline[date]
        print(f"\n  {date}: {len(events)} events")
        for event in events[:3]:
            print(f"    - [{event['type']}] {event['title']}")


# Example 6: Export for Visualization
def example_export_knowledge_graph(result):
    """Export data for knowledge graph visualization"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Knowledge Graph Export")
    print("=" * 70)

    # Extract entities and connections
    all_entities = set()
    connections = []

    for record in result['records']:
        for entity in record['entities_found']:
            all_entities.add(entity['name'])

    for conn in result['connections']:
        connections.append({
            'source': conn['entity'],
            'target': conn['document_a'],
            'weight': conn['strength'],
            'type': 'entity_mention'
        })

    kg = {
        'nodes': [{'id': e, 'type': 'entity'} for e in all_entities],
        'edges': connections[:100],  # Limit for visualization
        'metadata': {
            'total_entities': len(all_entities),
            'total_connections': len(connections)
        }
    }

    print(f"\nKnowledge graph:")
    print(f"  Nodes: {len(kg['nodes'])} entities")
    print(f"  Edges: {len(kg['edges'])} connections")
    print(f"\nExport to graph.json for visualization")

    return kg


# Example 7: Defendant/Plaintiff Network
def example_party_network(records):
    """Build network of defendants and plaintiffs"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Party Network Analysis")
    print("=" * 70)

    party_connections = {}
    party_cases = {}

    for record in records:
        for party in record['parties']:
            if party not in party_cases:
                party_cases[party] = []
            party_cases[party].append(record['case_number'])

    # Find parties in multiple cases
    print(f"\nParties appearing in multiple cases:")
    multi_case_parties = sorted(
        [(p, len(c)) for p, c in party_cases.items() if len(c) > 1],
        key=lambda x: x[1],
        reverse=True
    )

    for party, case_count in multi_case_parties[:15]:
        print(f"  {party:40} : {case_count:2} cases")

    print(f"\nTotal unique parties: {len(party_cases)}")


# Example 8: PDF-Specific Extraction
def example_pdf_analysis():
    """Advanced PDF extraction from indictments"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: PDF Document Analysis")
    print("=" * 70)

    # Example PDF content (would be actual PDF text)
    sample_indictment = """
    UNITED STATES DISTRICT COURT
    SOUTHERN DISTRICT OF NEW YORK
    
    Case No. 23-CR-12345
    
    UNITED STATES OF AMERICA
    v.
    JOHN DOE, JANE SMITH, and ACME CORPORATION
    
    INDICTMENT
    
    Filed: January 15, 2024
    
    The Grand Jury charges:
    1. CONSPIRACY
    Defendants John Doe, Jane Smith, and Acme Corporation
    conspired to commit wire fraud...
    
    Phone: (555) 123-4567
    Email: john.doe@acmecorp.com
    SSN: 123-45-6789
    """

    # Extract entities
    entities = PublicRecordExtractor.extract_entities(sample_indictment)
    defendants = PublicRecordExtractor.extract_defendant_names(sample_indictment)
    case_num = PublicRecordExtractor.extract_case_number(sample_indictment)

    print(f"\nExtracted from document:")
    print(f"  Case Number: {case_num}")
    print(f"  Defendants: {defendants}")
    print(f"  Entities found: {len(entities)}")

    for entity in entities[:10]:
        print(f"    - [{entity['entity_type']}] {entity['name']}")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " PUBLIC RECORDS INTELLIGENCE CRAWLER - EXAMPLES ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")

    # Example 1: Main crawl (may take time with real sources)
    # result = example_fbi_indictments()
    # Commented out - uses real sources
    
    # Instead, show capability examples with mock data
    print("\n✓ Public Records Crawler Capabilities:")
    print("  - Crawl FBI documents, court records, indictments")
    print("  - Extract structured data from PDFs")
    print("  - Identify entities (defendants, locations, case numbers)")
    print("  - Find connections between documents")
    print("  - Build knowledge graphs and timelines")
    print("  - Analyze party networks")
    print("  - Export for visualization")

    # Example 8: PDF extraction (no network needed)
    example_pdf_analysis()

    print("\n" + "=" * 70)
    print("Examples Complete!")
    print("=" * 70)
    print("\nTo use the Public Records Crawler:")
    print("  1. Create crawler with seed URLs")
    print("  2. Run: result = crawler.crawl()")
    print("  3. Analyze results with example functions")


if __name__ == "__main__":
    main()
