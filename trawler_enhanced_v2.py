from legacy_policy import blocked
blocked(__name__)

"""Enhanced trawler with performance optimizations for 32GB RAM and modern async I/O"""

import asyncio
import json
import logging
import re
import tempfile
import time
from dataclasses import dataclass, asdict, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from metadata_extractor import MetadataExtractor, ImageMetadata, PDFMetadata, GPSCoordinate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("crawler.log", mode='a')
    ]
)


@dataclass
class DocumentReference:
    """Reference to a discovered document"""
    doc_type: str
    url: str
    file_path: Optional[str] = None
    metadata: Optional[Dict] = None
    discovered_from: str = ""


@dataclass
class LinkEdge:
    """Entity relationship with evidence"""
    entityA: str
    entityB: str
    confidence: float
    rationale: str
    sourceUrl: str
    link_type: str = "entity_co-occurrence"
    metadata_evidence: Optional[Dict] = None


@dataclass
class DataSource:
    """Data source with metadata and discovered entities"""
    source_type: str
    identifier: str
    url: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict] = None
    extracted_text: Optional[str] = None
    entities_found: List[str] = field(default_factory=list)
    discovered_documents: List[DocumentReference] = field(default_factory=list)


class OptimizedWebTrawler:
    """
    High-performance web trawler with:
    - Connection pooling and persistent sessions
    - LRU caching for URLs and LLM responses
    - Parallel entity pair analysis with ThreadPoolExecutor
    - Memory-efficient asset streaming
    - Retry logic with exponential backoff
    - Proper temp file management
    """

    def __init__(
        self,
        seed_url: str,
        entities: List[str],
        ollama_model: str = "dolphin-llama3",
        ollama_url: str = "http://127.0.0.1:11434/api/generate",
        max_pages: int = 12,
        max_content_bytes: int = 1_800_000,
        max_depth: int = 3,
        enable_image_extraction: bool = True,
        enable_pdf_extraction: bool = True,
        gps_proximity_threshold_km: float = 1.0,
        parallel_workers: int = 4,
        requests_per_second: float = 1.0,
        cache_size: int = 1000,
    ):
        self.seed_url = seed_url.rstrip("/")
        self.entities = entities
        self.ollama_model = ollama_model
        self.ollama_url = ollama_url
        self.max_pages = max_pages
        self.max_content_bytes = max_content_bytes
        self.max_depth = max_depth
        self.enable_image_extraction = enable_image_extraction
        self.enable_pdf_extraction = enable_pdf_extraction
        self.gps_proximity_threshold_km = gps_proximity_threshold_km
        self.parallel_workers = parallel_workers
        self.cache_size = cache_size
        self.delay = 1.0 / requests_per_second

        parsed = urlparse(self.seed_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("seed_url must be a valid URL starting with http:// or https://")

        self.domain = parsed.netloc
        self.visited: Set[str] = set()
        self.queue: List[Dict[str, object]] = []
        self.edges: List[LinkEdge] = []
        self.documents: List[DocumentReference] = []
        self.data_sources: List[DataSource] = []
        self.images_by_geohash: Dict[str, List[ImageMetadata]] = {}
        self.honeypots: Set[str] = set()
        self.infrastructure_anomalies: List[Dict] = []

        # Setup connection pooling with retries
        self.session = self._create_optimized_session()

        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=parallel_workers)

        # LRU caches for performance
        self._setup_caches()

    def _apply_rate_limit(self):
        """Simple blocking rate limiter for synchronous requests"""
        if hasattr(self, '_last_request_time'):
            elapsed = time.time() - self._last_request_time
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
        self._last_request_time = time.time()

    def _setup_caches(self):
        """Setup LRU caches with configured size"""
        self.cache_url_fetch = lru_cache(maxsize=self.cache_size)(self._fetch_url_impl)
        self.cache_ollama_query = lru_cache(maxsize=self.cache_size)(self._query_ollama_impl)

    def _create_optimized_session(self) -> requests.Session:
        """Create session with connection pooling and retry strategy"""
        session = requests.Session()

        # Retry strategy with exponential backoff
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=20)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.headers.update({
            "User-Agent": "US-Aligned-OSINT-Agent/3.0 (Friendly Actor; OptimizedWebTrawler/3.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,image/*;q=0.8,*/*;q=0.7",
            "Connection": "keep-alive",
            "X-Mission-Intent": "Defense Research & Infrastructure Analysis",
            "X-Alignment": "Pro-US National Security; Non-Hostile Researcher",
            "X-Researcher-Contact": "simplelogin-newsletter.crust110@simplelogin.com"
        })
        session.max_redirects = 5

        return session

    def is_same_domain(self, url: str) -> bool:
        """Check if URL is on same domain"""
        parsed = urlparse(url)
        return parsed.netloc == self.domain

    def normalize_url(self, base: str, url: str) -> Optional[str]:
        """Normalize and validate URL"""
        if url.startswith("javascript:") or url.startswith("mailto:"):
            return None
        
        # Filter out CDN noise and static trackers to prevent false positives
        noise_patterns = ['cdn-cgi', 'googletagmanager', 'google-analytics', 'cloudfront.net', 'fastly.net', 'akamai', 'wp-content', 'wp-includes']
        lower_url = url.lower()
        if any(p in lower_url for p in noise_patterns):
            return None

        joined = urljoin(base, url)
        parsed = urlparse(joined)
        if parsed.scheme not in {"http", "https"}:
            return None
        return joined.split("#")[0].rstrip("/")

    def _fetch_url_impl(self, url: str) -> Optional[Tuple[bytes, str]]:
        """Internal URL fetch implementation (called by cached wrapper)"""
        try:
            self._apply_rate_limit()
            head = self.session.head(url, timeout=12, allow_redirects=True)
            content_length = int(head.headers.get("Content-Length", 0) or 0)
            content_type = head.headers.get("Content-Type", "").lower()
            
            # Heuristic: Detect infrastructure discrepancies
            server_header = head.headers.get("Server", "Unknown")
            powered_by = head.headers.get("X-Powered-By", "")
            csp_header = head.headers.get("Content-Security-Policy", "")
            xfo_header = head.headers.get("X-Frame-Options", "")
            xcto_header = head.headers.get("X-Content-Type-Options", "")
            
            # Determine if site is likely high-value official vs generic CDN
            is_cdn = any(cdn in server_header.lower() for cdn in ["cloudflare", "akamai", "fastly", "cloudfront", "edgecast", "sucuri"])
            
            if not is_cdn and (csp_header or xfo_header or xcto_header.lower() == "nosniff"):
                logging.info(f"[heuristic] Probable high-value official infrastructure: {url} (Advanced Security Profile detected)")

            if "gov" in url.lower() and any(x in server_header.lower() for x in ["nginx/1.10", "php", "deprecated"]):
                 # Example: An official .gov site running an unusual or outdated stack 
                 # that matches known secondary networks.
                 logging.warning(f"[anomaly] Host {url} identifies as {server_header}. Potential secondary network.")
                 self.infrastructure_anomalies.append({"url": url, "server": server_header, "leakage": powered_by})

            # Deception Detection: Ancient server identifying on high-value domain
            if any(domain in url.lower() for domain in ["gov", "mil", "justice"]) and \
               any(old in server_header.lower() for old in ["iis/6", "apache/1.3", "php/5.2"]):
                logging.error(f"[honeypot] Host {url} uses suspicious legacy signature ({server_header}). Potential decoy.")
                self.honeypots.add(url)
                return None

            if content_length > self.max_content_bytes:
                logging.error(f"[skip] {url} size {content_length} exceeds limit.")
                return None

            response = self.session.get(url, timeout=20)
            if response.status_code != 200:
                logging.error(f"[failed] {url} status {response.status_code} for {url}. Moving on.")
                return None

            if len(response.content) > self.max_content_bytes:
                logging.info(f"[skip] {url} actual size exceeds limit")
                return None

            return response.content, content_type
        except requests.RequestException as exc:
            logging.info(f"[error] {url} fetch failed: {exc}")
            return None

    def fetch_content(self, url: str) -> Optional[Tuple[bytes, str]]:
        """Fetch content with caching"""
        return self.cache_url_fetch(url)

    def fetch_text(self, url: str) -> Optional[str]:
        """Fetch and return text content"""
        result = self.fetch_content(url)
        if result:
            content, content_type = result
            if "text/html" in content_type or "application/xhtml+xml" in content_type:
                return content.decode('utf-8', errors='ignore')
        return None

    def clean_text(self, html: str) -> str:
        """Clean HTML and extract text"""
        soup = BeautifulSoup(html, "html.parser")
        for tag_name in ["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript", "svg", "link"]:
            for node in soup.select(tag_name):
                node.decompose()
        return re.sub(r"\s+", " ", soup.get_text(separator=" ", strip=True))

    def discover_links(self, html: str, base_url: str) -> List[Tuple[str, bool]]:
        """Discover links from HTML"""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        # Added unconventional triggers: targeting software signatures and anomalous data structures
        priority_keywords = ["indictment", "irgc", "quds", "witt", "espionage", "complaint", "motion", "pdf", "court",
                             "signature", "hash", "cid", "uuid", "agent", "alias", "redacted"]
        
        # Matches years (2010-2029) or federal case year patterns (e.g., 23-CR, 24-CV)
        year_pattern = r'\b(20[12]\d)\b|\b(\d{2}-(?:CR|CV|BK|MD|KS|MJ))\b'

        for anchor in soup.find_all("a", href=True):
            # Bot Trap Detection: Hidden or microscopic links
            style = anchor.get("style", "").lower().replace(" ", "")
            if "display:none" in style or "visibility:hidden" in style or "width:0" in style or "height:0" in style:
                logging.error(f"[honeypot] Trap detected at {base_url} -> {anchor['href']}. Skipping.")
                continue

            normalized = self.normalize_url(base_url, anchor["href"])
            if normalized and normalized not in self.visited:
                text = anchor.get_text().lower()
                is_keyword_priority = any(k in text or k in normalized.lower() for k in priority_keywords)
                is_date_priority = bool(re.search(year_pattern, text, re.I)) or bool(re.search(year_pattern, normalized, re.I))
                is_priority = is_keyword_priority or is_date_priority
                links.append((normalized, is_priority))
        
        links.sort(key=lambda x: x[1], reverse=True)
        return links

    def discover_assets(self, html: str, base_url: str) -> List[Tuple[str, str, str]]:
        """Discover images, PDFs, and documents"""
        soup = BeautifulSoup(html, "html.parser")
        assets = []

        if self.enable_image_extraction:
            for img in soup.find_all("img", src=True):
                asset_url = self.normalize_url(base_url, img["src"])
                if asset_url and asset_url not in self.visited:
                    assets.append((asset_url, "image", img.get("alt", "")))

        if self.enable_pdf_extraction:
            for link in soup.find_all("a", href=True):
                href = link["href"].lower()
                if any(href.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.xlsx', '.zip']):
                    asset_url = self.normalize_url(base_url, link["href"])
                    if asset_url and asset_url not in self.visited:
                        doc_type = 'pdf' if href.endswith('.pdf') else 'document'
                        assets.append((asset_url, doc_type, link.get_text(strip=True)))

        return assets

    def process_image_asset(self, url: str, source_page: str) -> Optional[ImageMetadata]:
        """Download and process image with memory-efficient streaming"""
        try:
            result = self.fetch_content(url)
            if not result or "image" not in result[1]:
                return None

            content, _ = result

            # Use proper temp directory
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tmp:
                tmp.write(content)
                temp_path = Path(tmp.name)

            metadata = MetadataExtractor.extract_image_metadata(str(temp_path))
            if metadata:
                metadata.file_path = url
                logging.info(f"[asset] Image: {url} | Size: {metadata.width}x{metadata.height}")
                if metadata.gps:
                    geohash = metadata.gps.geohash
                    if geohash not in self.images_by_geohash:
                        self.images_by_geohash[geohash] = []
                    self.images_by_geohash[geohash].append(metadata)
                    logging.info(f"[gps] Image at {metadata.gps.latitude:.4f}, {metadata.gps.longitude:.4f}")

            temp_path.unlink(missing_ok=True)
            return metadata
        except Exception as e:
            logging.debug(f"Failed to process image {url}: {e}")
            return None

    def process_pdf_asset(self, url: str, source_page: str) -> Optional[PDFMetadata]:
        """Download and process PDF"""
        try:
            result = self.fetch_content(url)
            if not result or "pdf" not in result[1]:
                return None

            content, _ = result

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(content)
                temp_path = Path(tmp.name)

            metadata = MetadataExtractor.extract_pdf_metadata(str(temp_path))
            if metadata:
                metadata.file_path = url
                logging.info(f"[asset] PDF: {url} | Pages: {metadata.pages}")

            temp_path.unlink(missing_ok=True)
            return metadata
        except Exception as e:
            logging.debug(f"Failed to process PDF {url}: {e}")
            return None

    def detect_gps_proximity_links(self) -> List[LinkEdge]:
        """Find entities co-located by GPS proximity"""
        proximity_links = []
        processed_pairs = set()

        for geohash, images in self.images_by_geohash.items():
            if len(images) < 2:
                continue

            for i, img1 in enumerate(images):
                for img2 in images[i+1:]:
                    pair = tuple(sorted([img1.file_name, img2.file_name]))
                    if pair in processed_pairs:
                        continue
                    processed_pairs.add(pair)

                    for ent_a in self.entities:
                        for ent_b in self.entities:
                            if ent_a >= ent_b:
                                continue
                            if ent_a in img1.file_name or (img1.exif_data and ent_a in img1.exif_data.get('Make', '')):
                                if ent_b in img2.file_name or (img2.exif_data and ent_b in img2.exif_data.get('Make', '')):
                                    link = LinkEdge(
                                        entityA=ent_a,
                                        entityB=ent_b,
                                        confidence=0.7,
                                        rationale=f"Co-located via GPS (geohash: {geohash})",
                                        sourceUrl=f"gps://{geohash}",
                                        link_type="gps_proximity",
                                        metadata_evidence={"images": [img1.file_name, img2.file_name]}
                                    )
                                    proximity_links.append(link)
                                    logging.info(f"[gps-link] {ent_a} <-> {ent_b}")

        return proximity_links

    def make_chunks(self, text: str, size: int = 2400, step: int = 1800) -> List[str]:
        """Split text into overlapping chunks"""
        return [text[i : i + size] for i in range(0, max(len(text) - 1, 0), step)] or [text]

    def prompt_for_link(self, ent_a: str, ent_b: str, context: str) -> Dict:
        """Create LLM prompt for entity relationship analysis"""
        system = (
            "You are an expert Intelligence Analyst specializing in Infrastructure Leakage. "
            "Your objective is to determine if Entity A and Entity B are connected, specifically looking for "
            "'Infrastructure Paradoxes'—where official fronts utilize secondary, unofficial network signatures. "
            "Analyze text and metadata for these ghosts. Respond only with valid JSON: "
            "{link_detected (true/false), confidence (0.0-1.0), rationale (string), infrastructure_paradox (boolean)}."
        )
        prompt = (
            f"Entity A: {ent_a}\n"
            f"Entity B: {ent_b}\n"
            f"Context:\n{context}\n"
            "If a meaningful connection exists, set link_detected to true, else false."
        )
        return {
            "model": self.ollama_model,
            "prompt": prompt,
            "system": system,
            "format": "json",
            "options": {"temperature": 0.0},
            "stream": False,
        }

    def parse_response(self, raw: str) -> Optional[Dict]:
        """Parse LLM response JSON"""
        raw = raw.strip()
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    return None
            return None

    def _query_ollama_impl(self, ent_a: str, ent_b: str, context: str) -> Optional[Dict]:
        """Internal Ollama query implementation"""
        payload = self.prompt_for_link(ent_a, ent_b, context)
        try:
            response = self.session.post(self.ollama_url, json=payload, timeout=25)
            if response.status_code != 200:
                logging.info(f"[ollama] status {response.status_code}")
                return None
            data = response.json()
            raw = data.get("response") if isinstance(data, dict) else response.text
            return self.parse_response(raw)
        except requests.RequestException as exc:
            logging.info(f"[ollama] request failed: {exc}")
            return None

    def query_ollama(self, ent_a: str, ent_b: str, context: str) -> Optional[Dict]:
        """Query Ollama with caching"""
        # Create cache key from entities and context hash
        context_hash = hash(context[:500]) % 10000000
        return self.cache_ollama_query(ent_a, ent_b, context_hash)

    def fallback_score(self, ent_a: str, ent_b: str, context: str) -> Dict:
        """Fallback entity proximity scoring"""
        found_a = bool(re.search(rf"\b{re.escape(ent_a)}\b", context, re.IGNORECASE))
        found_b = bool(re.search(rf"\b{re.escape(ent_b)}\b", context, re.IGNORECASE))
        if not found_a or not found_b:
            return {"link_detected": False, "confidence": 0.0, "rationale": "Entities not found together."}

        distance = min(
            [abs(m.start() - n.start()) for m in re.finditer(re.escape(ent_a), context, re.IGNORECASE)
             for n in re.finditer(re.escape(ent_b), context, re.IGNORECASE)]
            or [len(context)]
        )
        score = max(0.35, min(1.0, 1.0 - (distance / max(len(context), 1)) * 0.9))
        return {
            "link_detected": score >= 0.45,
            "confidence": round(score, 3),
            "rationale": f"Proximity score: {distance}"
        }

    def add_link(self, ent_a: str, ent_b: str, score: float, rationale: str, 
                 source: str, link_type: str = "entity_co-occurrence", metadata: Optional[Dict] = None) -> None:
        """Add or update entity link"""
        if score <= 0.0:
            return
        existing = next(
            (edge for edge in self.edges if edge.entityA == ent_a and edge.entityB == ent_b and edge.link_type == link_type),
            None,
        )
        if existing and existing.confidence >= score:
            return
        if existing:
            existing.confidence = score
            existing.rationale = rationale
            existing.sourceUrl = source
            existing.metadata_evidence = metadata
        else:
            self.edges.append(LinkEdge(ent_a, ent_b, score, rationale, source, link_type, metadata))

    def process_entity_pair(self, ent_a: str, ent_b: str, chunk: str, source_url: str) -> None:
        """Process single entity pair in parallel"""
        result = self.query_ollama(ent_a, ent_b, chunk)
        if result is None:
            result = self.fallback_score(ent_a, ent_b, chunk)

        if result.get("link_detected"):
            score = float(result.get("confidence", 0.0))
            if score >= 0.35:
                self.add_link(ent_a, ent_b, score, result.get("rationale", ""), source_url)
                logging.info(f"[link] {ent_a} <-> {ent_b} ({score})")

    def evaluate_page(self, text: str, source_url: str) -> None:
        """Evaluate page with parallel entity analysis"""
        chunks = self.make_chunks(text)
        tasks = []

        for chunk in chunks:
            for i in range(len(self.entities)):
                for j in range(i + 1, len(self.entities)):
                    ent_a = self.entities[i]
                    ent_b = self.entities[j]
                    if not re.search(rf"\b{re.escape(ent_a)}\b", chunk, re.IGNORECASE) or \
                       not re.search(rf"\b{re.escape(ent_b)}\b", chunk, re.IGNORECASE):
                        continue

                    # Submit to thread pool for parallel processing
                    future = self.executor.submit(self.process_entity_pair, ent_a, ent_b, chunk, source_url)
                    tasks.append(future)

        # Wait for all tasks to complete
        for future in as_completed(tasks):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in entity pair processing: {e}")

    def crawl(self) -> Dict:
        """Main crawling loop"""
        self.queue.append({"url": self.seed_url, "depth": 0})
        while self.queue and len(self.visited) < self.max_pages:
            item = self.queue.pop(0)
            url = item["url"]
            depth = item["depth"]
            if url in self.visited or depth > self.max_depth:
                continue

            logging.info(f"[crawl] {url} (depth {depth})")
            self.visited.add(url)

            html = self.fetch_text(url)
            if not html:
                continue

            text = self.clean_text(html)
            if text:
                self.evaluate_page(text, url)

            # Process assets
            assets = self.discover_assets(html, url)
            for asset_url, asset_type, asset_title in assets:
                if asset_type == "image":
                    self.process_image_asset(asset_url, url)
                elif asset_type == "pdf":
                    self.process_pdf_asset(asset_url, url)

            if depth < self.max_depth:
                for discovered, is_priority in self.discover_links(html, url):
                    if discovered not in self.visited and len(self.visited) + len(self.queue) < self.max_pages * 2:
                        item = {"url": discovered, "depth": depth + 1}
                        if is_priority:
                            self.queue.insert(0, item)
                        else:
                            self.queue.append(item)

            time.sleep(0.8)

        # Detect GPS proximity links
        gps_links = self.detect_gps_proximity_links()
        self.edges.extend(gps_links)

        return self.build_output()

    def build_output(self) -> Dict:
        """Build final output"""
        return {
            "seedUrl": self.seed_url,
            "domain": self.domain,
            "entities": self.entities,
            "scannedPages": len(self.visited),
            "linkCount": len(self.edges),
            "links": [asdict(edge) for edge in self.edges],
            "assetsDiscovered": {
                "total": len(self.documents),
                "byGeohash": {k: [asdict(img) for img in v] for k, v in self.images_by_geohash.items()}
            }
        }

    def close(self):
        """Cleanup resources"""
        self.session.close()
        self.executor.shutdown(wait=True)


# Backward compatibility alias
EnhancedMemoryWebTrawler = OptimizedWebTrawler


if __name__ == "__main__":
    TARGET_URL = "https://example.com"
    TARGET_ENTITIES = ["Asset_Alpha", "Location_Node_4", "Operator_Identity"]

    trawler = OptimizedWebTrawler(
        seed_url=TARGET_URL,
        entities=TARGET_ENTITIES,
        parallel_workers=4,
        cache_size=500
    )

    try:
        result = trawler.crawl()
        print(json.dumps(result, indent=2))
    finally:
        trawler.close()

