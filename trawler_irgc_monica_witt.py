"""Case research view over the passive public-record pipeline.

Only central active queries are matched. Historical declarations are preserved
for comparison and do not establish identity, affiliation or wrongdoing.
"""

import json
import logging
import re
from research_config import active_search_terms, verified_aliases
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from trawler_public_records import PublicRecordsCrawler, PublicRecordExtractor

logging.basicConfig(level=logging.INFO, format="%(message)s")


@dataclass
class IRGCIntelligenceTarget:
    """Primary intelligence target"""
    primary_name: str
    aliases: List[str]
    entity_type: str  # PERSON, ORGANIZATION
    significance: str  # ESPIONAGE, TERRORIST_SUPPORT, SANCTIONS_VIOLATION
    search_terms: List[str]


class IRGCMonicaWittCrawler:
    """
    Specialized crawler for Monica Witt / IRGC case
    Primary objectives:
    1. Monica Witt (all aliases)
    2. IRGC connections
    3. Co-conspirators
    4. Related cases and charges
    """

    # PRIMARY TARGET: Monica Witt
    MONICA_WITT = IRGCIntelligenceTarget(
        primary_name="Monica Witt",
        aliases=[
            "Monica Witt",
            "Fatemah Zahra",
            "Narges Witt",
            "Monica Elfriede Witt",
            "Fatmah Zahra",
            "Fatemah Zahra Witt",
            "Agent Witt",
        ],
        entity_type="PERSON",
        significance="ESPIONAGE",
        search_terms=[
            "Monica Witt",
            "Fatemah Zahra",
            "Narges Witt",
            "IRGC",
            "espionage",
            "IRGC-Quds Force",
            "Iranian Revolutionary Guard",
            "Air Force officer",
            "classified information",
            "Iran intelligence",
            "defector",
        ]
    )

    # PRIMARY TARGET: IRGC
    IRGC = IRGCIntelligenceTarget(
        primary_name="Iranian Revolutionary Guard Corps",
        aliases=[
            "IRGC",
            "Islamic Revolutionary Guard Corps",
            "IRGC-Quds Force",
            "IRGC-QF",
            "Quds Force",
            "Revolutionary Guards",
            "Sepah",
        ],
        entity_type="ORGANIZATION",
        significance="TERRORIST_SUPPORT",
        search_terms=[
            "IRGC",
            "Quds Force",
            "Revolutionary Guard",
            "Iranian intelligence",
            "Soleimani",
            "espionage",
            "sanctions",
            "terrorist organization",
        ]
    )

    # RELATED INDIVIDUALS & ORGANIZATIONS
    RELATED_TARGETS = [
        IRGCIntelligenceTarget(
            primary_name="IRGC-Quds Force",
            aliases=["Quds Force", "IRGC-QF"],
            entity_type="ORGANIZATION",
            significance="ESPIONAGE",
            search_terms=["Quds Force", "espionage operations"]
        ),
        IRGCIntelligenceTarget(
            primary_name="MOIS",
            aliases=["Ministry of Intelligence", "VAJA"],
            entity_type="ORGANIZATION",
            significance="ESPIONAGE",
            search_terms=["MOIS", "Iranian intelligence", "Ministry of Intelligence"]
        ),
    ]

    def __init__(self, **crawler_options):
        self.crawler = PublicRecordsCrawler(seed_urls=[], search_terms=active_search_terms(), **crawler_options)
        self.relevant_records = []
        self.monica_witt_records = []
        self.irgc_records = []
        self.connection_map = {}
        self.last_result = {}

    @staticmethod
    def _get_seed_urls():
        return []

    @staticmethod
    def _get_search_terms():
        return active_search_terms()

    def is_target_related(self, text):
        return any(re.search(r'(?<!\w)' + re.escape(term) + r'(?!\w)', text, re.IGNORECASE)
                   for term in active_search_terms())

    def extract_target_mentions(self, text):
        mentions = {'monica_witt': [], 'irgc': [], 'related': [], 'supporting_entities': []}
        for term in active_search_terms():
            for match in re.finditer(r'(?<!\w)' + re.escape(term) + r'(?!\w)', text, re.IGNORECASE):
                group = 'monica_witt' if term.title() in {'Monica Witt', 'Monica Elfriede Witt'} else 'related'
                mentions[group].append({'name': term,
                    'context': text[max(0,match.start()-100):match.end()+100],
                    'match_type': 'literal_research_query', 'identity_verified': False})
        return mentions

    def crawl(self):
        self.last_result = self.crawler.crawl()
        self.relevant_records = []
        self.monica_witt_records = []
        self.irgc_records = []
        for record in self.last_result['records']:
            text = (record.get('full_text') or '') + ' ' + (record.get('title') or '')
            if self.is_target_related(text):
                self.relevant_records.append(record)
                record['target_mentions'] = self.extract_target_mentions(text)
                if record['target_mentions']['monica_witt']:
                    self.monica_witt_records.append(record)
        return self.build_intelligence_report()

    def build_intelligence_report(self) -> Dict:
        """Build comprehensive intelligence report"""
        return {
            "assessment": "research-query matches; identity unverified",
            "all_records": self.last_result.get("records", []),
            "errors": self.last_result.get("errors", []),
            "connections": self.last_result.get("connections", []),
            "intelligence_summary": {
                "total_documents_reviewed": len(self.last_result.get("records", [])),
                "target_related_documents": len(self.relevant_records),
                "monica_witt_documents": len(self.monica_witt_records),
                "irgc_documents": len(self.irgc_records),
            },
            "monica_witt_case": {
                "aliases": verified_aliases(),
                "significance": "unassessed research context",
                "documents_found": len(self.monica_witt_records),
                "records": self.monica_witt_records,
            },
            "irgc_connections": {
                "organization_names": [],
                "significance": "unassessed research context",
                "documents_found": len(self.irgc_records),
                "records": self.irgc_records,
            },
            "all_target_documents": self.relevant_records,
            "search_parameters": {
                "targets": ["Monica Witt", "IRGC", "Related Entities"],
                "aliases": verified_aliases(),
                "search_terms": self._get_search_terms(),
            }
        }


# The static historical target declarations above are retained for research history,
# not consumed by active matching. Queries come exclusively from research_config.

# Example usage
if __name__ == "__main__":
    crawler = IRGCMonicaWittCrawler()
    report = crawler.crawl()

    print("\n" + "=" * 80)
    print("INTELLIGENCE REPORT")
    print("=" * 80)

    print(f"\n📊 Summary:")
    print(f"  Documents reviewed: {report['intelligence_summary']['total_documents_reviewed']}")
    print(f"  Target-related documents: {report['intelligence_summary']['target_related_documents']}")
    print(f"  Monica Witt case documents: {report['intelligence_summary']['monica_witt_documents']}")
    print(f"  IRGC documents: {report['intelligence_summary']['irgc_documents']}")

    print(f"\n👤 Monica Witt Case:")
    print(f"  Aliases: {', '.join(report['monica_witt_case']['aliases'])}")
    print(f"  Documents found: {len(report['monica_witt_case']['records'])}")

    print(f"\n🏢 IRGC Connections:")
    print(f"  Organization names: {', '.join(report['irgc_connections']['organization_names'])}")
    print(f"  Documents found: {len(report['irgc_connections']['records'])}")

    # Save full report
    with open("irgc_monica_witt_intelligence_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n✓ Full report saved to: irgc_monica_witt_intelligence_report.json")
