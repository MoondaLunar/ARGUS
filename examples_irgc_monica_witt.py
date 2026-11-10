"""
IRGC & Monica Witt Intelligence Analysis Examples
Comprehensive examples for investigating Monica Witt espionage case
"""

import json
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler


# Example 1: Basic Intelligence Crawl
def example_basic_crawl():
    """Execute basic intelligence crawl for Monica Witt and IRGC"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Intelligence Crawl")
    print("=" * 80)

    crawler = IRGCMonicaWittCrawler()
    report = crawler.crawl()

    print(f"\n📊 INTELLIGENCE SUMMARY")
    print(f"{'─' * 80}")
    print(f"Documents reviewed:         {report['intelligence_summary']['total_documents_reviewed']}")
    print(f"Target-related documents:   {report['intelligence_summary']['target_related_documents']}")
    print(f"Monica Witt documents:      {report['intelligence_summary']['monica_witt_documents']}")
    print(f"IRGC documents:             {report['intelligence_summary']['irgc_documents']}")

    print(f"\n👤 MONICA WITT CASE")
    print(f"{'─' * 80}")
    print(f"Known aliases:")
    for alias in report['monica_witt_case']['aliases']:
        print(f"  • {alias}")
    print(f"\nDocuments found: {len(report['monica_witt_case']['records'])}")

    print(f"\n🏢 IRGC / QUDS FORCE")
    print(f"{'─' * 80}")
    print(f"Organization identifiers:")
    for name in report['irgc_connections']['organization_names']:
        print(f"  • {name}")
    print(f"\nDocuments found: {len(report['irgc_connections']['records'])}")

    return report


# Example 2: Monica Witt Document Analysis
def example_monica_witt_documents(report):
    """Analyze all Monica Witt case documents"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Monica Witt Document Analysis")
    print("=" * 80)

    records = report['monica_witt_case']['records']
    print(f"\nTotal documents related to Monica Witt: {len(records)}")

    if not records:
        print("No documents found.")
        return

    # Group by document type
    by_type = {}
    for record in records:
        doc_type = record.get('doc_type', 'UNKNOWN')
        if doc_type not in by_type:
            by_type[doc_type] = []
        by_type[doc_type].append(record)

    print(f"\nDocuments by type:")
    for doc_type, docs in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {doc_type:15} : {len(docs):2} documents")

    # Group by court
    by_court = {}
    for record in records:
        court = record.get('court', 'UNKNOWN')
        if court not in by_court:
            by_court[court] = []
        by_court[court].append(record)

    print(f"\nDocuments by court:")
    for court, docs in sorted(by_court.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {court:20} : {len(docs):2} documents")

    # Show sample documents
    print(f"\nSample documents:")
    for i, record in enumerate(records[:5], 1):
        print(f"\n  [{i}] {record.get('title', 'Unknown')}")
        print(f"      Case: {record.get('case_number', 'N/A')}")
        print(f"      Court: {record.get('court', 'N/A')}")
        print(f"      Date: {record.get('date_filed', 'N/A')}")
        print(f"      URL: {record.get('url', 'N/A')}")


# Example 3: IRGC Connection Analysis
def example_irgc_connections(report):
    """Analyze IRGC and Quds Force connections"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: IRGC / Quds Force Connection Analysis")
    print("=" * 80)

    records = report['irgc_connections']['records']
    print(f"\nTotal documents mentioning IRGC: {len(records)}")

    if not records:
        print("No IRGC documents found.")
        return

    # Find co-occurrences with Monica Witt
    monica_irgc_overlap = []
    monica_witt_records = {r['url'] for r in report['monica_witt_case']['records']}

    for record in records:
        if record['url'] in monica_witt_records:
            monica_irgc_overlap.append(record)

    print(f"\nDocuments mentioning BOTH Monica Witt AND IRGC: {len(monica_irgc_overlap)}")
    if monica_irgc_overlap:
        print("  (These are key connections)")
        for record in monica_irgc_overlap[:5]:
            print(f"    • {record.get('title', 'Unknown')}")


# Example 4: Case Timeline
def example_case_timeline(report):
    """Build timeline of Monica Witt case"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Monica Witt Case Timeline")
    print("=" * 80)

    records = report['monica_witt_case']['records']

    # Sort by date
    dated_records = [r for r in records if r.get('date_filed')]
    dated_records.sort(key=lambda r: r.get('date_filed', ''))

    print(f"\nTimeline of events ({len(dated_records)} dated documents):")
    for record in dated_records:
        date = record.get('date_filed', 'Unknown date')
        doc_type = record.get('doc_type', 'Document')
        title = record.get('title', 'Unknown')[:60]

        print(f"  {date:20} [{doc_type:15}] {title}")


# Example 5: Co-Conspirators and Related Entities
def example_related_entities(report):
    """Find co-conspirators and related entities"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Co-conspirators and Related Entities")
    print("=" * 80)

    all_records = report['all_target_documents']
    print(f"\nTotal target-related documents: {len(all_records)}")

    # Extract defendants/parties
    all_parties = set()
    for record in all_records:
        for party in record.get('parties', []):
            all_parties.add(party)

    print(f"\nPeople/organizations mentioned in documents:")
    for party in sorted(all_parties):
        count = sum(1 for r in all_records if party in r.get('parties', []))
        print(f"  • {party:40} ({count} documents)")


# Example 6: Intelligence Export
def example_export_intelligence(report):
    """Export intelligence report for analysis"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Intelligence Report Export")
    print("=" * 80)

    # Save full report
    with open("irgc_monica_witt_intelligence_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    print("\n✓ Full report saved: irgc_monica_witt_intelligence_report.json")

    # Create summary for quick reference
    summary = {
        "objectives": [
            "Monica Witt (all aliases)",
            "IRGC / Quds Force",
            "Related espionage cases"
        ],
        "monica_witt_aliases": report['monica_witt_case']['aliases'],
        "irgc_identifiers": report['irgc_connections']['organization_names'],
        "documents_found": {
            "total_target_related": report['intelligence_summary']['target_related_documents'],
            "monica_witt_specific": report['intelligence_summary']['monica_witt_documents'],
            "irgc_specific": report['intelligence_summary']['irgc_documents'],
        },
        "key_documents": [
            {
                "title": r.get('title'),
                "case_number": r.get('case_number'),
                "type": r.get('doc_type'),
                "date": r.get('date_filed'),
                "url": r.get('url')
            }
            for r in report['monica_witt_case']['records'][:10]
        ]
    }

    with open("irgc_monica_witt_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("✓ Summary saved: irgc_monica_witt_summary.json")

    # Create CSV for spreadsheet analysis
    import csv
    with open("monica_witt_documents.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Document Type", "Case Number", "Court", "Title", "URL"])
        for record in report['monica_witt_case']['records']:
            writer.writerow([
                record.get('date_filed', ''),
                record.get('doc_type', ''),
                record.get('case_number', ''),
                record.get('court', ''),
                record.get('title', ''),
                record.get('url', '')
            ])
    print("✓ CSV export: monica_witt_documents.csv")


# Example 7: Search Verification
def example_search_parameters(report):
    """Show search parameters and targets"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Intelligence Search Parameters")
    print("=" * 80)

    params = report['search_parameters']

    print(f"\nPrimary Targets:")
    for target in params['targets']:
        print(f"  • {target}")

    print(f"\nMonica Witt Aliases:")
    for alias in params['aliases'][:8]:  # First 8 are Monica Witt
        print(f"  • {alias}")

    print(f"\nIRGC Identifiers:")
    for identifier in params['aliases'][8:]:  # Rest are IRGC
        print(f"  • {identifier}")

    print(f"\nSearch Terms ({len(params['search_terms'])} total):")
    for term in sorted(params['search_terms'])[:20]:  # Show first 20
        print(f"  • {term}")
    if len(params['search_terms']) > 20:
        print(f"  ... and {len(params['search_terms']) - 20} more")


# Example 8: Network Analysis
def example_network_analysis(report):
    """Build network of connections"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Connection Network Analysis")
    print("=" * 80)

    all_records = report['all_target_documents']

    # Find documents that mention both Monica Witt and IRGC
    connection_docs = []
    for record in all_records:
        if 'target_mentions' in record:
            mentions = record['target_mentions']
            if mentions.get('monica_witt') and mentions.get('irgc'):
                connection_docs.append(record)

    print(f"\nDocuments mentioning BOTH Monica Witt and IRGC: {len(connection_docs)}")
    print("(These indicate direct connections)")

    if connection_docs:
        print("\nKey connection documents:")
        for doc in connection_docs[:5]:
            print(f"  • {doc.get('title', 'Unknown')}")
            print(f"    {doc.get('url', 'No URL')}")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " IRGC & MONICA WITT INTELLIGENCE ANALYSIS ".center(78) + "║")
    print("╚" + "=" * 78 + "╝")

    # Run main crawl
    print("\nLaunching intelligence crawler...")
    report = example_basic_crawl()

    # Run analyses
    example_monica_witt_documents(report)
    example_irgc_connections(report)
    example_case_timeline(report)
    example_related_entities(report)
    example_search_parameters(report)
    example_network_analysis(report)

    # Export results
    example_export_intelligence(report)

    print("\n" + "=" * 80)
    print("Intelligence Analysis Complete")
    print("=" * 80)
    print("\nGenerated files:")
    print("  • irgc_monica_witt_intelligence_report.json (Full report)")
    print("  • irgc_monica_witt_summary.json (Quick summary)")
    print("  • monica_witt_documents.csv (Spreadsheet format)")


if __name__ == "__main__":
    main()
