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
from itertools import combinations

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
    text_length: int = 0
    # Where this record came from: source, query, and the hit that pointed here
    found_by: Optional[Dict] = None
    # Exact lines in the text that made each entity count, kept for evidence
    text_excerpt: str = ""


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

        entities.extend(PublicRecordExtractor.extract_names(text))
        return entities

    # Capitalised name sequences catch people and organisations, which the
    # pattern table above never did: it only knew case numbers, dates, phones,
    # emails and SSNs. Two-token minimum, stopwords and months excluded.
    NAME_STOPWORDS = {
        'The', 'This', 'That', 'These', 'Those', 'United', 'States', 'District',
        'Court', 'Case', 'No', 'Page', 'Filed', 'Date', 'January', 'February',
        'March', 'April', 'May', 'June', 'July', 'August', 'September',
        'October', 'November', 'December', 'Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday', 'Sunday', 'Department', 'Justice',
    }

    @staticmethod
    def extract_names(text: str) -> List[EntityMention]:
        mentions = []
        seen = set()
        for match in re.finditer(r"\b([A-Z][a-z'\-]{1,20}(?:\s+(?:[A-Z]\.|[A-Z][a-z'\-]{1,20})){1,2})\b", text):
            name = match.group(1)
            tokens = name.split()
            if tokens[0] in PublicRecordExtractor.NAME_STOPWORDS:
                continue
            if len(tokens) < 2 or len(name) > 40:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            sentence = text[max(0, text.rfind('.', 0, match.start()) + 1): text.find('.', match.end()) + 1 or len(text)]
            mentions.append(EntityMention(
                name=name,
                entity_type='PERSON',
                context=sentence.strip()[:300],
                confidence=0.6,
            ))
        return mentions

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
        sources: Optional[List] = None,
    ):
        self.seed_urls = seed_urls
        self.search_terms = search_terms
        self.sources = sources  # None -> search_sources.default_sources()
        self.search_report: Optional[Dict] = None
        self.hits_by_url: Dict[str, Dict] = {}
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
            'govinfo.gov',
            'sec.gov',
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

    def fetch_document(self, url: str):
        """Fetch a document. Returns (body, mime_type) where body is bytes for
        PDFs and text for HTML. The old version returned response.text for both,
        which mangled every PDF on the way to the parser."""
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

            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                return None

            ctype = (response.headers.get("Content-Type") or content_type or "").lower()
            if "pdf" in ctype:
                return response.content, ctype
            return response.text, ctype
        except Exception as e:
            logging.debug(f"Error fetching {url}: {e}")
            return None

    def extract_pdf_text(self, raw: bytes, max_chars: int = 200_000) -> Optional[str]:
        """Full text from a PDF's bytes. The old path kept only 500 characters
        of page one (metadata_extractor's preview), so correlation over a court
        order ran on a title block."""
        try:
            import io
            from pypdf import PdfReader
        except ImportError:
            logging.debug("pypdf not installed; cannot read PDF text")
            return None
        try:
            reader = PdfReader(io.BytesIO(raw))
            chunks = []
            total = 0
            for page in reader.pages:
                got = page.extract_text() or ""
                chunks.append(got)
                total += len(got)
                if total >= max_chars:
                    break
            text = "\n".join(chunks).strip()
            logging.info(f"[pdf] {len(reader.pages)} pages, {len(text)} chars")
            return text or None
        except Exception as e:
            logging.debug(f"PDF parse failed: {e}")
            return None

    def extract_from_pdf(self, url: str) -> Optional[str]:
        """Backwards-compatible wrapper: fetch then extract."""
        result = self.fetch_document(url)
        if not result:
            return None
        body, ctype = result
        if not isinstance(body, (bytes, bytearray)) or "pdf" not in str(ctype).lower():
            return None
        return self.extract_pdf_text(bytes(body))

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

    def parse_document_as_record(self, text: str, url: str, found_by: Optional[Dict] = None) -> Optional[PublicRecord]:
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
            text_length=len(text),
            found_by=found_by,
            text_excerpt=text[:600],
        )

        return record

    def find_connections_between_records(self) -> List[Dict]:
        """Every connection used to be strength 0.8, a number with nothing
        behind it. Now each one carries the two lines that produced it, the
        document each line came from, and a confidence derived from what
        actually matched."""
        index: Dict[Tuple[str, str], List[Tuple[PublicRecord, EntityMention]]] = {}
        settled: Dict[str, str] = {}
        for record in self.records:
            for entity in record.entities_found:
                key = (self._canonical_name(entity, settled), entity.entity_type)
                index.setdefault(key, []).append((record, entity))

        connections = []
        for (name, entity_type), hits in index.items():
            by_doc: Dict[str, List[Tuple[PublicRecord, EntityMention]]] = {}
            for record, mention in hits:
                by_doc.setdefault(record.doc_id, []).append((record, mention))
            if len(by_doc) < 2:
                continue

            if not self._is_specific(entity_type, name):
                continue

            doc_ids = sorted(by_doc)
            for doc_a, doc_b in combinations(doc_ids, 2):
                rec_a0, _ = by_doc[doc_a][0]
                rec_b0, _ = by_doc[doc_b][0]
                # A docket number only means something inside its own court.
                # Two different courts sharing "03-cv-225" is two cases, not one.
                if entity_type == 'CASE_NUMBER' and rec_a0.source != rec_b0.source:
                    continue
                rec_a, men_a = by_doc[doc_a][0]
                rec_b, men_b = by_doc[doc_b][0]
                evidence = [
                    {
                        'document': rec_a.doc_id,
                        'title': rec_a.title,
                        'url': rec_a.url,
                        'matched_text': men_a.name,
                        'quote': men_a.context,
                        'mention_confidence': men_a.confidence,
                    },
                    {
                        'document': rec_b.doc_id,
                        'title': rec_b.title,
                        'url': rec_b.url,
                        'matched_text': men_b.name,
                        'quote': men_b.context,
                        'mention_confidence': men_b.confidence,
                    },
                ]
                confidence, basis = self._connection_confidence(name, entity_type, men_a, men_b, len(by_doc))
                connections.append({
                    'entity': men_a.name,
                    'entity_type': entity_type,
                    'document_a': doc_a,
                    'document_b': doc_b,
                    'connection_type': 'entity_co-occurrence',
                    'confidence': confidence,
                    'strength': confidence,  # kept for older consumers
                    'basis': basis,
                    'supporting_documents': len(by_doc),
                    'evidence': evidence,
                })

        connections.sort(key=lambda c: c['confidence'], reverse=True)
        return connections

    # Near-duplicate names are grouped, conservatively: a spelling drift
    # (Witt / Witte, a middle initial) should not hide a real link, but a loose
    # match on a person's name in an OSINT tool is how innocent people end up
    # in a graph. Same surname plus 92% string similarity, nothing looser.
    @staticmethod
    def _canonical_name(entity: EntityMention, settled: Dict[str, str]) -> str:
        import difflib

        raw = entity.name.strip()
        low = raw.lower()
        if entity.entity_type != 'PERSON':
            return low
        surname = low.split()[-1]
        best, best_score = low, 0.0
        for seen, canonical in settled.items():
            other = seen.split()[-1]
            if other != surname and difflib.SequenceMatcher(None, other, surname).ratio() < 0.85:
                continue
            score = difflib.SequenceMatcher(None, low, seen).ratio()
            if score > best_score:
                best, best_score = canonical, score
        if best_score >= 0.92:
            return best
        settled[low] = low
        return low

    @staticmethod
    def _is_specific(entity_type: str, name: str) -> bool:
        """Reject identifiers too thin to identify anything. 'Case Number 3'
        matched across two unrelated Tennessee filings and produced a
        connection with a 0.9 confidence and nothing behind it."""
        nm = name.strip()
        if entity_type == 'CASE_NUMBER':
            digits = sum(ch.isdigit() for ch in nm)
            return digits >= 4 and len(nm) >= 6
        if entity_type in ('PHONE', 'SSN', 'EMAIL'):
            return len(nm) >= 7
        if entity_type == 'DATE':
            return len(nm) >= 8 and any(ch.isdigit() for ch in nm)
        if entity_type == 'PERSON':
            return ' ' in nm and len(nm) >= 6
        return True

    @staticmethod
    def _connection_confidence(name: str, entity_type: str, a: EntityMention, b: EntityMention, doc_count: int) -> Tuple[float, str]:
        """Confidence from the match itself, not a house number.

        Agreement between the two matched strings is the first factor: an exact
        string match on a case number is worth more than two names that merely
        look alike. Each additional document that carries the same entity is
        weak corroboration, so it nudges rather than doubles.
        """
        import difflib

        na, nb = a.name.strip().lower(), b.name.strip().lower()
        if na == nb:
            agreement, agreement_note = 1.0, 'exact string match'
        else:
            ratio = difflib.SequenceMatcher(None, na, nb).ratio()
            ta, tb = set(na.split()), set(nb.split())
            overlap = len(ta & tb) / max(1, len(ta | tb))
            agreement = max(0.5, round(max(ratio, overlap), 3))
            agreement_note = f'name similarity {agreement:.2f} ({a.name!r} vs {b.name!r})'

        base = min(a.confidence, b.confidence)
        corroboration = 1.0 + 0.05 * min(doc_count - 2, 4)
        confidence = round(min(0.99, base * agreement * corroboration), 3)
        basis = f'{entity_type.lower()} match, {agreement_note}, base {base}, {doc_count} documents'
        return confidence, basis

    def run_searches(self) -> Dict:
        """Turn the search terms into a real frontier instead of starting the
        queue at a homepage and hoping. Every URL keeps the query that found
        it, so a record can say why ARGUS ever looked at that page."""
        try:
            from search_sources import search_all
        except ImportError:
            logging.warning("[search] search_sources.py not available; crawling seeds only")
            self.search_report = {'sources': [], 'hits': [], 'unavailable': [], 'errors': []}
            return self.search_report

        report = search_all(self.search_terms, sources=self.sources, limit=8)
        self.search_report = report
        for hit in report['hits']:
            url = hit.get('url') or ''
            if not url:
                continue
            self.hits_by_url[url] = hit
            if not any(item['url'] == url for item in self.queue):
                self.queue.append({
                    'url': url,
                    'fetch_url': (hit.get('extra') or {}).get('fetch_url'),
                    'depth': 0,
                    'found_by': {
                        'source': hit['source'],
                        'query': hit['query'],
                        'title': hit.get('title'),
                        'doc_id': hit.get('doc_id'),
                    },
                })
        for miss in report['unavailable']:
            logging.info(f"[search] {miss['source']} unavailable: {miss['reason']}")
        for err in report['errors']:
            logging.warning(f"[search] {err['source']} failed on {err['term']!r}: {err['error']}")
        return report

    def crawl(self) -> Dict:
        """Execute crawl of public records"""
        # Search results enter first (depth 0), seeds after them
        self.run_searches()
        for seed_url in self.seed_urls:
            self.queue.append({'url': seed_url, 'depth': 0})

        page_count = 0

        while self.queue and len(self.visited) < self.max_pages:
            item = self.queue.pop(0)
            url = item['url']
            depth = item['depth']
            found_by = item.get('found_by') or self.hits_by_url.get(url)
            fetch_url = item.get('fetch_url') or url

            if url in self.visited or depth > self.max_depth:
                continue

            logging.info(f"[crawl] {url} (depth {depth})")
            self.visited.add(url)

            result = self.fetch_document(fetch_url)
            if not result:
                logging.info(f"[skip] unreadable: {url}")
                continue

            body, content_type = result
            if isinstance(body, (bytes, bytearray)):
                text = self.extract_pdf_text(bytes(body)) or ''
            else:
                text = body

            if not text.strip():
                logging.info(f"[skip] no text: {url}")
                continue

            record = self.parse_document_as_record(text, url, found_by=found_by)
            if record:
                self.records.append(record)
                logging.info(f"[record] {record.doc_type}: {record.case_number or record.title[:50]}")

            # Discover links to follow (HTML only; a PDF has no anchor graph)
            if not isinstance(body, (bytes, bytearray)):
                discovered_urls = self.discover_links_in_document(text, url)
                for discovered_url, is_priority in discovered_urls:
                    if discovered_url not in self.visited and len(self.visited) + len(self.queue) < self.max_pages * 2:
                        new_item = {
                            'url': discovered_url,
                            'depth': depth + 1,
                            'found_by': {'source': 'link', 'query': None, 'parent': url},
                        }
                        if is_priority:
                            self.queue.insert(0, new_item)
                        else:
                            self.queue.append(new_item)

            page_count += 1
            time.sleep(1.0)

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
            "search": self.search_report or {"sources": [], "hits": [], "unavailable": [], "errors": []},
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
        seed_urls=[],
        search_terms=["Monica Witt"],
        max_pages=6,
        max_depth=1,
        sources=None,  # search_sources.default_sources()
    )

    result = crawler.crawl()
    print(json.dumps(result, indent=2, default=str))
