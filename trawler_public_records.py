"""
Public Records Intelligence Crawler
Specialized for FBI documents, indictments, court records, and linked public data
"""

import json
import logging
import re
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from metadata_extractor import MetadataExtractor
from analysis_engine import FuzzyMatcher, CorrelationAnalyzer

logging.basicConfig(level=logging.INFO, format="%(message)s")


@dataclass
class EntityMention:
    """Entity found in a document"""
    name: str
    entity_type: str  # PERSON, ORGANIZATION, LOCATION, CASE_NUMBER, DATE, PHONE, EMAIL
    context: str
    confidence: float


@dataclass
class PublicRecord:
    """Structured representation of a public record"""
    doc_id: str
    doc_type: str  # INDICTMENT, COMPLAINT, WARRANT, AFFIDAVIT, PLEA, JUDGMENT
    title: str
    url: str
    source: str  # FBI, USDC, SDNY, etc.
    date_filed: Optional[str]
    case_number: Optional[str]
    court: Optional[str]
    parties: List[str]  # Defendants, plaintiffs
    entities_found: List[EntityMention]
    full_text: Optional[str]
    pdf_path: Optional[str]
    extracted_links: List[str]  # Links to related documents


class PublicRecordExtractor:
    """Extract structured data from public records documents"""

    # Common entity patterns
    PATTERNS = {
        'CASE_NUMBER': [
            r'(?:Case|Docket)\s*(?:No\.?|Number)\s*[\d\-]+',
            r'\d{2}[-\s]cv[-\s]\d+',
            r'\d{2}[-\s]cr[-\s]\d+',
            r'[A-Z]{2}\s+\d+\s+(?:CV|CR)\s+\d+',
        ],
        'DATE': [
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'\d{1,2}/\d{1,2}/\d{2,4}',
        ],
        'PHONE': [
            r'\(?[\d]{3}\)?[\s\.\-]?[\d]{3}[\s\.\-]?[\d]{4}',
        ],
        'EMAIL': [
            r'[\w\.\-]+@[\w\.\-]+\.\w{2,}',
        ],
        'SSN': [
            r'\d{3}-\d{2}-\d{4}',
        ],
    }

    @staticmethod
    def extract_defendant_names(text: str) -> List[str]:
        """Extract defendant/plaintiff names from text"""
        names = []
        
        # Look for "v." or "versus" patterns
        patterns = [
            r'(?:Defendant|Plaintiff)s?:?\s*([A-Z][a-zA-Z\s\-\.]+?)(?:,|and|\n|$)',
            r'(?:United States|U\.S\.)\s+(?:v\.|versus)\s+([A-Z][a-zA-Z\s\-\.]+?)(?:,|;|$)',
            r'^([A-Z][a-zA-Z\s\-\.]+?)\s+(?:v\.|versus)\s+([A-Z][a-zA-Z\s\-\.]+?)$',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                for group in match.groups():
                    if group:
                        name = group.strip().title()
                        if 4 < len(name) < 100:
                            names.append(name)
        
        return list(set(names))  # Deduplicate

    @staticmethod
    def extract_entities(text: str) -> List[EntityMention]:
        """Extract named entities from text"""
        entities = []

        for entity_type, patterns in PublicRecordExtractor.PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    mention = EntityMention(
                        name=match.group(0),
                        entity_type=entity_type,
                        context=text[max(0, match.start() - 50):min(len(text), match.end() + 50)],
                        confidence=0.9 if entity_type in ['CASE_NUMBER', 'SSN'] else 0.7
                    )
                    entities.append(mention)

        return entities

    @staticmethod
    def extract_case_number(text: str) -> Optional[str]:
        """Extract primary case number"""
        for pattern in PublicRecordExtractor.PATTERNS['CASE_NUMBER']:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    @staticmethod
    def extract_court_from_url(url: str) -> Optional[str]:
        """Infer court from URL"""
        url_lower = url.lower()
        
        court_patterns = {
            'SDNY': ['sdny', 'south.district.new.york'],
            'NDNY': ['ndny', 'north.district.new.york'],
            'EDNY': ['edny', 'east.district.new.york'],
            'WDNY': ['wdny', 'west.district.new.york'],
            'SCOTUS': ['supreme', 'supremecourt'],
            'FBI': ['fbi.gov', 'vault.fbi'],
            'DOJ': ['justice.gov', 'doj.gov'],
        }
        
        for court, keywords in court_patterns.items():
            for keyword in keywords:
                if keyword in url_lower:
                    return court
        
        return None


class PublicRecordsCrawler:
    """
    Specialized crawler for public records, FBI documents, court filings, indictments
    """

    def __init__(
        self,
        seed_urls: List[str],
        search_terms: List[str],
        ollama_model: str = "dolphin-llama3",
        ollama_url: str = "http://127.0.0.1:11434/api/generate",
        max_pages: int = 50,
        max_depth: int = 4,
        extract_pdfs: bool = True,
    ):
        self.seed_urls = seed_urls
        self.search_terms = search_terms
        self.ollama_model = ollama_model
        self.ollama_url = ollama_url
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.extract_pdfs = extract_pdfs

        self.visited: Set[str] = set()
        self.queue: List[Dict] = []
        self.records: List[PublicRecord] = []
        self.entity_mentions: Dict[str, List[EntityMention]] = {}
        self.relationships: List[Dict] = []

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "US-Aligned-OSINT-Agent/3.0 (Friendly Actor; Defense Research)",
            "X-Mission-Intent": "Public Records Analysis (Target: IRGC/Monica Witt)",
            "X-Alignment": "Pro-US National Security; Non-Hostile Researcher",
            "X-Researcher-Contact": "your_email@example.com", # <--- ADD YOUR CONTACT INFO HERE
            "Accept": "text/html,application/pdf,*/*",
        })

    def is_relevant_url(self, url: str) -> bool:
        """Check if URL is likely to contain relevant public records"""
        relevant_domains = [
            'fbi.gov',
            'justice.gov',
            'doj.gov',
            'uscourts.gov',
            'pacer.uscourts.gov',
            'ca9.uscourts.gov',
            'sdny.uscourts.gov',
            'edny.uscourts.gov',
            'docket.sec.gov',
            'regulations.gov',
            'archives.gov',
            'publicintegrity.org',
            'documenting-the-now',
        ]
        
        url_lower = url.lower()
        
        # Check domain
        if not any(domain in url_lower for domain in relevant_domains):
            return False
        
        # Exclude non-document URLs
        excluded = ['login', 'auth', 'payment', 'ad', 'tracking', 'cdn-cgi', 'wp-content', 'wp-includes', 'googletagmanager']
        if any(term in url_lower for term in excluded):
            return False
        
        return True

    def fetch_document(self, url: str) -> Optional[Tuple[str, str]]:
        """Fetch document (HTML or PDF) and return (content, mime_type)"""
        try:
            head = self.session.head(url, timeout=12, allow_redirects=True)
            content_type = head.headers.get("Content-Type", "").lower()
            content_length = int(head.headers.get("Content-Length", 0) or 0)

            # Heuristic: Check for high-value official site vs generic CDN
            server_header = head.headers.get("Server", "Unknown")
            csp_header = head.headers.get("Content-Security-Policy", "")
            xfo_header = head.headers.get("X-Frame-Options", "")
            xcto_header = head.headers.get("X-Content-Type-Options", "")
            
            is_cdn = any(cdn in server_header.lower() for cdn in ["cloudflare", "akamai", "fastly", "cloudfront", "edgecast", "sucuri"])
            
            if not is_cdn and (csp_header or xfo_header or xcto_header.lower() == "nosniff"):
                logging.info(f"[heuristic] High-value record source identified: {url} (Strict Security Headers detected)")

            # Skip if too large
            if content_length > 50_000_000:  # 50MB limit
                logging.info(f"[skip] {url} too large ({content_length/1e6:.1f}MB)")
                return None

            response = self.session.get(url, timeout=20)
            if response.status_code != 200:
                return None

            return response.text, content_type
        except Exception as e:
            logging.debug(f"Error fetching {url}: {e}")
            return None

    def extract_from_pdf(self, url: str) -> Optional[str]:
        """Download and extract text from PDF"""
        try:
            result = self.fetch_document(url)
            if not result or "pdf" not in result[1]:
                return None

            content, _ = result
            temp_path = Path(f"/tmp/temp_{hash(url) % 1000000}.pdf")
            temp_path.write_bytes(content.encode() if isinstance(content, str) else content)

            metadata = MetadataExtractor.extract_pdf_metadata(str(temp_path))
            if metadata and metadata.text_preview:
                text = metadata.text_preview
                temp_path.unlink(missing_ok=True)
                return text

            temp_path.unlink(missing_ok=True)
            return None
        except Exception as e:
            logging.debug(f"PDF extraction failed for {url}: {e}")
            return None

    def discover_links_in_document(self, html: str, base_url: str) -> List[Tuple[str, bool]]:
        """Discover links to other public records"""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        priority_keywords = ["indictment", "irgc", "quds", "witt", "espionage", "complaint", "motion", "pdf", "court"]
        # Matches years (2010-2029) or federal case year patterns (e.g., 23-CR, 24-CV)
        year_pattern = r'\b(20[12]\d)\b|\b(\d{2}-(?:CR|CV|BK|MD))\b'

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            text = anchor.get_text().lower()
            if not href.startswith("http"):
                href = urljoin(base_url, href)

            # Only follow relevant URLs
            if self.is_relevant_url(href) and href not in self.visited:
                is_keyword_priority = any(k in text or k in href.lower() for k in priority_keywords)
                is_date_priority = bool(re.search(year_pattern, text, re.I)) or bool(re.search(year_pattern, href, re.I))
                is_priority = is_keyword_priority or is_date_priority
                links.append((href, is_priority))

        # Return list sorted so priority links are discovered first
        links.sort(key=lambda x: x[1], reverse=True)
        return links[:15]

    def parse_document_as_record(self, text: str, url: str) -> Optional[PublicRecord]:
        """Parse document text into structured PublicRecord"""
        
        # Extract entities
        entities = PublicRecordExtractor.extract_entities(text)
        defendants = PublicRecordExtractor.extract_defendant_names(text)
        case_number = PublicRecordExtractor.extract_case_number(text)
        court = PublicRecordExtractor.extract_court_from_url(url)

        # Infer document type
        doc_type = "DOCUMENT"
        for term in ['indictment', 'complaint', 'warrant', 'affidavit', 'plea', 'judgment']:
            if term.lower() in text.lower():
                doc_type = term.upper()
                break

        # Extract date
        date_match = re.search(r'(?:Filed|Dated|Date):\s*(\w+\s+\d+,?\s+\d{4})', text)
        date_filed = date_match.group(1) if date_match else None

        # Create title from first meaningful line
        lines = text.split('\n')
        title = next((line.strip() for line in lines if 20 < len(line) < 200), "Public Record")

        record = PublicRecord(
            doc_id=f"{url}#{hash(text) % 1000000}",
            doc_type=doc_type,
            title=title,
            url=url,
            source=court or "PUBLIC_RECORDS",
            date_filed=date_filed,
            case_number=case_number,
            court=court,
            parties=defendants,
            entities_found=entities,
            full_text=text[:5000],  # Store preview
            pdf_path=url if url.endswith('.pdf') else None,
            extracted_links=[],
        )

        return record

    def find_connections_between_records(self) -> List[Dict]:
        """Find relationships between records using entity matching"""
        connections = []

        # Extract all mentioned entities
        all_entities = {}
        for record in self.records:
            for entity in record.entities_found:
                key = (entity.name, entity.entity_type)
                if key not in all_entities:
                    all_entities[key] = []
                all_entities[key].append(record.doc_id)

        # Find co-occurrences (same entity in multiple records = connection)
        for (entity_name, entity_type), doc_ids in all_entities.items():
            if len(doc_ids) > 1:
                for i, doc_id_a in enumerate(doc_ids):
                    for doc_id_b in doc_ids[i+1:]:
                        connection = {
                            'entity': entity_name,
                            'entity_type': entity_type,
                            'document_a': doc_id_a,
                            'document_b': doc_id_b,
                            'connection_type': 'entity_co-occurrence',
                            'strength': 0.8,
                        }
                        connections.append(connection)

        return connections

    def crawl(self) -> Dict:
        """Execute crawl of public records"""
        # Initialize queue with seed URLs
        for seed_url in self.seed_urls:
            self.queue.append({"url": seed_url, "depth": 0})

        page_count = 0

        while self.queue and len(self.visited) < self.max_pages:
            item = self.queue.pop(0)
            url = item["url"]
            depth = item["depth"]

            if url in self.visited or depth > self.max_depth:
                continue

            logging.info(f"[crawl] {url} (depth {depth})")
            self.visited.add(url)

            # Fetch document
            result = self.fetch_document(url)
            if not result:
                continue

            content, content_type = result
            text = content

            # If PDF, extract text
            if "pdf" in content_type.lower():
                pdf_text = self.extract_from_pdf(url)
                if pdf_text:
                    text = pdf_text

            # Parse as public record
            record = self.parse_document_as_record(text, url)
            if record:
                self.records.append(record)
                logging.info(f"[record] {record.doc_type}: {record.case_number or record.title[:50]}")

            # Discover links to follow
            discovered_urls = self.discover_links_in_document(text, url)
            for discovered_url, is_priority in discovered_urls:
                if discovered_url not in self.visited and len(self.visited) + len(self.queue) < self.max_pages * 2:
                    item = {"url": discovered_url, "depth": depth + 1}
                    if is_priority:
                        self.queue.insert(0, item) # Jump to front
                    else:
                        self.queue.append(item)

            page_count += 1
            time.sleep(1.0)  # Respectful crawling

        # Find connections
        self.relationships = self.find_connections_between_records()

        return self.build_output()

    def build_output(self) -> Dict:
        """Build final output"""
        return {
            "crawl_summary": {
                "pages_visited": len(self.visited),
                "records_found": len(self.records),
                "connections_found": len(self.relationships),
                "unique_entities": len(set((e.name, e.entity_type) for r in self.records for e in r.entities_found)),
            },
            "records": [asdict(r) for r in self.records],
            "connections": self.relationships,
            "entities_by_type": self._group_entities_by_type(),
        }

    def _group_entities_by_type(self) -> Dict[str, List[str]]:
        """Group all entities by type"""
        grouped = {}
        for record in self.records:
            for entity in record.entities_found:
                if entity.entity_type not in grouped:
                    grouped[entity.entity_type] = []
                grouped[entity.entity_type].append(entity.name)

        # Deduplicate
        for entity_type in grouped:
            grouped[entity_type] = list(set(grouped[entity_type]))

        return grouped


# Example usage
if __name__ == "__main__":
    # Example: Search for specific case
    crawler = PublicRecordsCrawler(
        seed_urls=[
            "https://www.fbi.gov/investigate/public-corruption",
            "https://www.justice.gov/criminal-vcs/recent-cases",
        ],
        search_terms=["indictment", "fraud", "conspiracy"],
        max_pages=20,
        max_depth=2,
    )

    result = crawler.crawl()
    print(json.dumps(result, indent=2, default=str))
