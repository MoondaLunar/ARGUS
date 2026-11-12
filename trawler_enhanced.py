from legacy_policy import blocked
blocked(__name__)

"""Enhanced trawler with multi-document support and metadata tracking"""

import json
import logging
import re
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from metadata_extractor import MetadataExtractor, ImageMetadata, PDFMetadata, GPSCoordinate

logging.basicConfig(level=logging.INFO, format="%(message)s")


@dataclass
class DocumentReference:
    """Reference to a discovered document"""
    doc_type: str  # 'html', 'pdf', 'image', 'archive'
    url: str
    file_path: Optional[str] = None
    metadata: Optional[Dict] = None
    discovered_from: str = ""


@dataclass
class LinkEdge:
    entityA: str
    entityB: str
    confidence: float
    rationale: str
    sourceUrl: str
    link_type: str = "entity_co-occurrence"  # 'entity_co-occurrence', 'gps_proximity', 'metadata_match'
    metadata_evidence: Optional[Dict] = None


@dataclass
class DataSource:
    """Represents a data source with its metadata and discovered entities"""
    source_type: str  # 'web', 'local', 'archive'
    identifier: str
    url: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict] = None
    extracted_text: Optional[str] = None
    entities_found: List[str] = None
    discovered_documents: List[DocumentReference] = None

    def __post_init__(self):
        if self.entities_found is None:
            self.entities_found = []
        if self.discovered_documents is None:
            self.discovered_documents = []


class EnhancedMemoryWebTrawler:
    """
    Enhanced web trawler with:
    - Multi-document type support (PDF, images, archives)
    - Metadata extraction (EXIF, document properties, GPS)
    - GPS-based proximity detection
    - Document fingerprinting
    - Cross-source correlation
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

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "EnhancedMemoryWebTrawler/2.0",
            "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,image/*;q=0.8,*/*;q=0.7",
        })
        self.session.max_redirects = 5

    def is_same_domain(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.netloc == self.domain

    def normalize_url(self, base: str, url: str) -> Optional[str]:
        if url.startswith("javascript:") or url.startswith("mailto:"):
            return None
        joined = urljoin(base, url)
        parsed = urlparse(joined)
        if parsed.scheme not in {"http", "https"}:
            return None
        return joined.split("#")[0].rstrip("/")

    def fetch_content(self, url: str) -> Optional[tuple]:
        """Fetch and return (content_bytes, content_type)"""
        try:
            head = self.session.head(url, timeout=12, allow_redirects=True)
            content_length = int(head.headers.get("Content-Length", 0) or 0)
            content_type = head.headers.get("Content-Type", "").lower()

            if content_length > self.max_content_bytes:
                logging.info(f"[skip] {url} content size {content_length} exceeds limit")
                return None

            response = self.session.get(url, timeout=20)
            if response.status_code != 200:
                logging.info(f"[skip] {url} status {response.status_code}")
                return None

            if len(response.content) > self.max_content_bytes:
                logging.info(f"[skip] {url} after download size {len(response.content)} exceeds limit")
                return None

            return response.content, content_type
        except requests.RequestException as exc:
            logging.info(f"[error] {url} fetch failed: {exc}")
            return None

    def fetch_text(self, url: str) -> Optional[str]:
        """Fetch and return text content"""
        result = self.fetch_content(url)
        if result:
            content, content_type = result
            if "text/html" in content_type or "application/xhtml+xml" in content_type:
                return content.decode('utf-8', errors='ignore')
        return None

    def clean_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag_name in ["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript", "svg", "link"]:
            for node in soup.select(tag_name):
                node.decompose()
        return re.sub(r"\s+", " ", soup.get_text(separator=" ", strip=True))

    def discover_links(self, html: str, base_url: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        urls = []
        for anchor in soup.find_all("a", href=True):
            normalized = self.normalize_url(base_url, anchor["href"])
            if normalized and normalized not in self.visited:
                urls.append(normalized)
        return urls

    def discover_assets(self, html: str, base_url: str) -> List[tuple]:
        """Discover images, PDFs, and other assets"""
        soup = BeautifulSoup(html, "html.parser")
        assets = []

        # Images
        if self.enable_image_extraction:
            for img in soup.find_all("img", src=True):
                asset_url = self.normalize_url(base_url, img["src"])
                if asset_url and asset_url not in self.visited:
                    assets.append((asset_url, "image", img.get("alt", "")))

        # Links to PDFs and documents
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
        """Download and process image asset"""
        try:
            result = self.fetch_content(url)
            if not result or "image" not in result[1]:
                return None

            content, _ = result
            temp_path = Path("/tmp") / f"temp_{hash(url) % 1000000}.tmp"
            temp_path.write_bytes(content)

            metadata = MetadataExtractor.extract_image_metadata(str(temp_path))
            if metadata:
                metadata.file_path = url
                logging.info(f"[asset] Image: {url} | Size: {metadata.width}x{metadata.height}")
                if metadata.gps:
                    geohash = metadata.gps.geohash
                    if geohash not in self.images_by_geohash:
                        self.images_by_geohash[geohash] = []
                    self.images_by_geohash[geohash].append(metadata)
                    logging.info(f"[gps] Found image at {metadata.gps.latitude:.4f}, {metadata.gps.longitude:.4f}")

            temp_path.unlink(missing_ok=True)
            return metadata
        except Exception as e:
            logging.debug(f"Failed to process image asset {url}: {e}")
            return None

    def process_pdf_asset(self, url: str, source_page: str) -> Optional[PDFMetadata]:
        """Download and process PDF asset"""
        try:
            result = self.fetch_content(url)
            if not result or "pdf" not in result[1]:
                return None

            content, _ = result
            temp_path = Path("/tmp") / f"temp_{hash(url) % 1000000}.pdf"
            temp_path.write_bytes(content)

            metadata = MetadataExtractor.extract_pdf_metadata(str(temp_path))
            if metadata:
                metadata.file_path = url
                logging.info(f"[asset] PDF: {url} | Pages: {metadata.pages} | Author: {metadata.author}")

            temp_path.unlink(missing_ok=True)
            return metadata
        except Exception as e:
            logging.debug(f"Failed to process PDF asset {url}: {e}")
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
                            if ent_a in img1.file_name or ent_a in img1.exif_data.get('Make', '') if img1.exif_data else False:
                                if ent_b in img2.file_name or ent_b in img2.exif_data.get('Make', '') if img2.exif_data else False:
                                    link = LinkEdge(
                                        entityA=ent_a,
                                        entityB=ent_b,
                                        confidence=0.7,
                                        rationale=f"Co-located via GPS proximity (geohash: {geohash})",
                                        sourceUrl=f"gps://{geohash}",
                                        link_type="gps_proximity",
                                        metadata_evidence={"images": [img1.file_name, img2.file_name]}
                                    )
                                    proximity_links.append(link)
                                    logging.info(f"[gps-link] {ent_a} <-> {ent_b} at {geohash}")

        return proximity_links

    def make_chunks(self, text: str, size: int = 2400, step: int = 1800) -> List[str]:
        return [text[i : i + size] for i in range(0, max(len(text) - 1, 0), step)] or [text]

    def prompt_for_link(self, ent_a: str, ent_b: str, context: str) -> Dict[str, object]:
        system = (
            "You are a fact-based analyst. Analyze the context and determine whether Entity A and Entity B are linked. "
            "Respond only with valid JSON containing keys: link_detected (true/false), confidence (0.0-1.0), rationale (string)."
        )
        prompt = (
            f"Entity A: {ent_a}\n"
            f"Entity B: {ent_b}\n"
            f"Context:\n{context}\n"
            "If a meaningful factual connection exists, set link_detected to true. "
            "Otherwise set it to false. "
            "Use confidence to quantify how strongly the evidence supports the link."
        )
        return {
            "model": self.ollama_model,
            "prompt": prompt,
            "system": system,
            "format": "json",
            "options": {"temperature": 0.0},
            "stream": False,
        }

    def parse_response(self, raw: str) -> Optional[Dict[str, object]]:
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

    def query_ollama(self, ent_a: str, ent_b: str, context: str) -> Optional[Dict[str, object]]:
        payload = self.prompt_for_link(ent_a, ent_b, context)
        try:
            response = self.session.post(self.ollama_url, json=payload, timeout=25)
            if response.status_code != 200:
                logging.info(f"[ollama] status {response.status_code}")
                return None
            data = response.json()
            raw = None
            if isinstance(data, dict):
                raw = data.get("response") or data.get("output") or data.get("text")
            if raw is None:
                raw = response.text
            return self.parse_response(raw)
        except requests.RequestException as exc:
            logging.info(f"[ollama] request failed: {exc}")
            return None

    def fallback_score(self, ent_a: str, ent_b: str, context: str) -> Dict[str, object]:
        found_a = bool(re.search(rf"\b{re.escape(ent_a)}\b", context, re.IGNORECASE))
        found_b = bool(re.search(rf"\b{re.escape(ent_b)}\b", context, re.IGNORECASE))
        if not found_a or not found_b:
            return {"link_detected": False, "confidence": 0.0, "rationale": "Entities do not appear together."}

        distance = min(
            [abs(m.start() - n.start()) for m in re.finditer(re.escape(ent_a), context, re.IGNORECASE) for n in re.finditer(re.escape(ent_b), context, re.IGNORECASE)]
            or [len(context)]
        )
        score = max(0.35, min(1.0, 1.0 - (distance / max(len(context), 1)) * 0.9))
        return {
            "link_detected": score >= 0.45,
            "confidence": round(score, 3),
            "rationale": f"Entities appear in passage. Proximity score: {distance}."
        }

    def add_link(self, ent_a: str, ent_b: str, score: float, rationale: str, source: str, link_type: str = "entity_co-occurrence", metadata: Optional[Dict] = None) -> None:
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

    def evaluate_page(self, text: str, source_url: str) -> None:
        chunks = self.make_chunks(text)
        for chunk in chunks:
            for i in range(len(self.entities)):
                for j in range(i + 1, len(self.entities)):
                    ent_a = self.entities[i]
                    ent_b = self.entities[j]
                    if not re.search(rf"\b{re.escape(ent_a)}\b", chunk, re.IGNORECASE) or not re.search(rf"\b{re.escape(ent_b)}\b", chunk, re.IGNORECASE):
                        continue

                    result = self.query_ollama(ent_a, ent_b, chunk)
                    if result is None:
                        result = self.fallback_score(ent_a, ent_b, chunk)

                    if result.get("link_detected"):
                        score = float(result.get("confidence", 0.0))
                        if score >= 0.35:
                            self.add_link(ent_a, ent_b, score, result.get("rationale", ""), source_url)
                            logging.info(f"[link] {ent_a} <-> {ent_b} ({score}) from {source_url}")

    def crawl(self) -> Dict[str, object]:
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

            # Discover and process assets
            assets = self.discover_assets(html, url)
            for asset_url, asset_type, asset_title in assets:
                if asset_type == "image":
                    self.process_image_asset(asset_url, url)
                elif asset_type == "pdf":
                    self.process_pdf_asset(asset_url, url)

            if depth < self.max_depth:
                for discovered in self.discover_links(html, url):
                    if discovered not in self.visited and len(self.visited) + len(self.queue) < self.max_pages * 2:
                        self.queue.append({"url": discovered, "depth": depth + 1})

            time.sleep(0.8)

        # Detect GPS-based proximity links
        gps_links = self.detect_gps_proximity_links()
        self.edges.extend(gps_links)

        return self.build_output()

    def build_output(self) -> Dict[str, object]:
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


if __name__ == "__main__":
    TARGET_URL = "https://example.com"
    TARGET_ENTITIES = ["Asset_Alpha", "Location_Node_4", "Operator_Identity", "System_Log_7"]

    trawler = EnhancedMemoryWebTrawler(
        seed_url=TARGET_URL,
        entities=TARGET_ENTITIES,
        ollama_model="dolphin-mixtral:8x7b",
        ollama_url="http://127.0.0.1:11434/api/generate",
        max_pages=8,
        max_content_bytes=1_500_000,
        max_depth=2,
        enable_image_extraction=True,
        enable_pdf_extraction=True,
    )

    result = trawler.crawl()
    print(json.dumps(result, indent=2))

