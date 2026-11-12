from legacy_policy import blocked
blocked(__name__)

"""
IRGC & Monica Witt Intelligence Crawler
Specialized for Monica Witt espionage case and IRGC connections
Searches all aliases: Monica Witt, Fatemah Zahra, Narges Witt, Monica Elfriede Witt, Fatmah Zahra
"""

import json
import logging
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

    def __init__(self):
        self.crawler = PublicRecordsCrawler(
            seed_urls=self._get_seed_urls(),
            search_terms=self._get_search_terms(),
            max_pages=100,
            max_depth=5,
            extract_pdfs=True,
        )
        self.relevant_records = []
        self.monica_witt_records = []
        self.irgc_records = []
        self.connection_map = {}

    @staticmethod
    def _get_seed_urls() -> List[str]:
        """Get federal court and FBI URLs for Monica Witt case"""
        return [
            # Federal Courts - General
            "https://www.uscourts.gov/",
            "https://pacer.uscourts.gov/",

            # Relevant District Courts
            "https://www.sdtx.uscourts.gov/",  # Southern District of Texas
            "https://www.txd.uscourts.gov/",   # District of Texas
            "https://www.ca5.uscourts.gov/",   # 5th Circuit

            # FBI & DOJ
            "https://www.fbi.gov/investigate/counterintelligence",
            "https://www.fbi.gov/investigate/counterintelligence/foreign-interference",
            "https://www.justice.gov/nsd/",  # National Security Division
            "https://www.justice.gov/criminal-nsd/",

            # Public Databases
            "https://www.justice.gov/criminal-vcs/recent-cases",
            "https://www.justice.gov/opa/",  # Office of Public Affairs

            # Indictments & Court Records
            "https://www.justice.gov/usao-sdtx/",  # USAO Southern District Texas
            "https://www.justice.gov/usao-ndia/",  # National Dist Attorney
        ]

    @staticmethod
    def _get_search_terms() -> List[str]:
        """Get all search terms for Monica Witt and IRGC"""
        terms = set()

        # Monica Witt aliases
        for alias in IRGCMonicaWittCrawler.MONICA_WITT.aliases:
            terms.add(alias)
        terms.update(IRGCMonicaWittCrawler.MONICA_WITT.search_terms)

        # IRGC
        for alias in IRGCMonicaWittCrawler.IRGC.aliases:
            terms.add(alias)
        terms.update(IRGCMonicaWittCrawler.IRGC.search_terms)

        # Related organizations
        for target in IRGCMonicaWittCrawler.RELATED_TARGETS:
            terms.update(target.search_terms)

        # Case-specific terms
        terms.update([
            "espionage",
            "classified information",
            "Air Force",
            "intelligence operation",
            "Iranian",
            "sanctions violation",
            "export control",
            "terrorist organization",
            "co-conspirator",
            "indictment",
        ])

        return list(terms)

    def is_target_related(self, text: str) -> bool:
        """Check if document is related to Monica Witt or IRGC targets"""
        text_lower = text.lower()

        # Monica Witt
        for alias in self.MONICA_WITT.aliases:
            if alias.lower() in text_lower:
                return True

        # IRGC
        for alias in self.IRGC.aliases:
            if alias.lower() in text_lower:
                return True

        # Related
        for target in self.RELATED_TARGETS:
            for alias in target.aliases:
                if alias.lower() in text_lower:
                    return True

        return False

    def extract_target_mentions(self, text: str) -> Dict[str, List[Dict]]:
        """Extract all mentions of Monica Witt, aliases, and IRGC"""
        mentions = {
            'monica_witt': [],
            'irgc': [],
            'related': [],
            'supporting_entities': []
        }

        text_lower = text.lower()

        # Find Monica Witt mentions
        for alias in self.MONICA_WITT.aliases:
            if alias.lower() in text_lower:
                context_start = max(0, text_lower.find(alias.lower()) - 100)
                context_end = min(len(text), text_lower.find(alias.lower()) + len(alias) + 100)
                mentions['monica_witt'].append({
                    'name': alias,
                    'context': text[context_start:context_end],
                    'confidence': 0.95
                })

        # Find IRGC mentions
        for alias in self.IRGC.aliases:
            if alias.lower() in text_lower:
                context_start = max(0, text_lower.find(alias.lower()) - 100)
                context_end = min(len(text), text_lower.find(alias.lower()) + len(alias) + 100)
                mentions['irgc'].append({
                    'name': alias,
                    'context': text[context_start:context_end],
                    'confidence': 0.95
                })

        # Find related targets
        for target in self.RELATED_TARGETS:
            for alias in target.aliases:
                if alias.lower() in text_lower:
                    context_start = max(0, text_lower.find(alias.lower()) - 100)
                    context_end = min(len(text), text_lower.find(alias.lower()) + len(alias) + 100)
                    mentions['related'].append({
                        'name': alias,
                        'target': target.primary_name,
                        'context': text[context_start:context_end],
                        'confidence': 0.95
                    })

        return mentions

    def crawl(self) -> Dict:
        """Execute intelligence crawl"""
        logging.info("=" * 80)
        logging.info("IRGC & Monica Witt Intelligence Crawler")
        logging.info("=" * 80)
        logging.info("\nPrimary Objectives:")
        logging.info("  1. Monica Witt (Fatemah Zahra, Narges Witt, Monica Elfriede Witt, Fatmah Zahra)")
        logging.info("  2. IRGC / Quds Force connections")
        logging.info("  3. Related espionage cases and co-conspirators")
        logging.info("  4. Court documents and indictments\n")

        # Execute public records crawl
        logging.info("Starting crawl...")
        result = self.crawler.crawl()

        # Filter for relevant records
        logging.info(f"\nTotal documents found: {len(result['records'])}")
        logging.info("Filtering for target-related documents...")

        for record in result['records']:
            text = record.get('full_text', '') + ' ' + record.get('title', '')

            if self.is_target_related(text):
                self.relevant_records.append(record)

                # Categorize by target
                text_lower = text.lower()
                if any(alias.lower() in text_lower for alias in self.MONICA_WITT.aliases):
                    self.monica_witt_records.append(record)

                if any(alias.lower() in text_lower for alias in self.IRGC.aliases):
                    self.irgc_records.append(record)

                # Extract target mentions
                mentions = self.extract_target_mentions(text)
                if mentions['monica_witt'] or mentions['irgc']:
                    record['target_mentions'] = mentions

        return self.build_intelligence_report()

    def build_intelligence_report(self) -> Dict:
        """Build comprehensive intelligence report"""
        return {
            "intelligence_summary": {
                "total_documents_reviewed": len(self.crawler.records),
                "target_related_documents": len(self.relevant_records),
                "monica_witt_documents": len(self.monica_witt_records),
                "irgc_documents": len(self.irgc_records),
            },
            "monica_witt_case": {
                "aliases": self.MONICA_WITT.aliases,
                "significance": self.MONICA_WITT.significance,
                "documents_found": len(self.monica_witt_records),
                "records": self.monica_witt_records,
            },
            "irgc_connections": {
                "organization_names": self.IRGC.aliases,
                "significance": self.IRGC.significance,
                "documents_found": len(self.irgc_records),
                "records": self.irgc_records,
            },
            "all_target_documents": self.relevant_records,
            "search_parameters": {
                "targets": ["Monica Witt", "IRGC", "Related Entities"],
                "aliases": self.MONICA_WITT.aliases + self.IRGC.aliases,
                "search_terms": self._get_search_terms(),
            }
        }


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

