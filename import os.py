import os
import re
import json
import requests
import hashlib
import io
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import networkx as nx
from pyvis.network import Network
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import PyPDF2
from PIL import Image
from PIL.ExifTags import TAGS
import pgpy

class IntelligenceGraphPipeline:
    def __init__(self, target_domain, ollama_model="dolphin-llama3", pgp_key_path="private_key.asc"):
        self.base_url = target_domain
        self.domain = urlparse(target_domain).netloc
        self.model = ollama_model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.checkpoint_path = "crawler_state.json"
        # Utilize 1TB SSD for persistent caching to mitigate dial-up bandwidth costs
        self.cache_dir = "intelligence_cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # Threshold for moderate speeds (20MB). Adjustable for dial-up vs 20mbps.
        self.max_file_size = 20 * 1024 * 1024 

        self.visited_urls = set()
        self.graph = nx.Graph()
        
        # Setup robust session for slow/unstable internet
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        self.load_state()

        # Initialize PGP signing key if it exists locally
        self.pgp_key = None
        if os.path.exists(pgp_key_path):
            try:
                self.pgp_key, _ = pgpy.PGPKey.from_file(pgp_key_path)
            except Exception as e:
                print(f"[!] Failed to load PGP signing key: {e}")

        # Add friendly actor headers
        self.session.headers.update({
            "User-Agent": "US-Aligned-OSINT-Agent/3.0 (Friendly Actor; Defense Research)",
            "X-Mission-Intent": "Intelligence Graph Pipeline (Friendly Research)",
            "X-Alignment": "Pro-US National Security; Non-Hostile Researcher",
            "X-Researcher-Contact": "simplelogin-newsletter.crust110@simplelogin.com" # <--- ADD YOUR CONTACT INFO HERE
        })

    def save_state(self):
        """Serializes the current graph and progress to a local JSON file."""
        state = {
            "visited_urls": list(self.visited_urls),
            "graph": nx.node_link_data(self.graph)
        }
        with open(self.checkpoint_path, "w") as f:
            json.dump(state, f, indent=4)

    def load_state(self):
        """Resumes progress from a previous run if a checkpoint exists."""
        if os.path.exists(self.checkpoint_path):
            with open(self.checkpoint_path, "r") as f:
                state = json.load(f)
                self.visited_urls = set(state.get("visited_urls", []))
                self.graph = nx.node_link_graph(state.get("graph", {"nodes": [], "links": []}))
            print(f"[*] Resumed from checkpoint: {len(self.visited_urls)} pages visited.")

    def extract_exif(self, image_url):
        """Attempts to extract EXIF metadata from an image URL."""
        # SSD Cache Filter: Check if we already processed this image to save bandwidth
        url_hash = hashlib.md5(image_url.encode()).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"exif_{url_hash}.json")
        
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                return json.load(f)

        try:
            # Connection Filter: Perform a HEAD request to check size before committing to a full download
            head = self.session.head(image_url, timeout=10)
            content_length = int(head.headers.get('Content-Length', 0))
            
            # Use the global max_file_size threshold
            if content_length > self.max_file_size:
                return None

            response = self.session.get(image_url, timeout=25, stream=True)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                exif_data = img._getexif()
                if exif_data:
                    result = {TAGS.get(k, k): str(v) for k, v in exif_data.items() if k in TAGS}
                    # Persist to SSD
                    with open(cache_path, "w") as f:
                        json.dump(result, f)
                    return result
        except Exception:
            pass # Silent failure to keep crawler moving on bad connections
        return None

    def extract_pdf_text(self, pdf_bytes):
        """Extracts text and metadata from PDF bytes in memory."""
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            text_content = []
            # Extract metadata (Author, Creator, etc.)
            meta = reader.metadata
            if meta:
                text_content.append(f"[PDF Metadata: {json.dumps(dict(meta))}]")
            
            for page in reader.pages:
                text_content.append(page.extract_text())
            return " ".join(text_content)
        except Exception as e:
            return f"[!] PDF Extraction Error: {e}"

    def extract_clean_text(self, html_content, base_url):
        """Strips out structural web clutter and extracts image metadata/EXIF."""
        soup = BeautifulSoup(html_content, 'html.parser')
        metadata_snippets = []
        for img in soup.find_all('img', src=True):
            img_url = urljoin(base_url, img['src'])
            # Only process likely image extensions to save bandwidth on dial-up speeds
            if any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.tiff']):
                exif = self.extract_exif(img_url)
                if exif:
                    metadata_snippets.append(f"[Image EXIF for {img_url}: {json.dumps(exif)}]")
            if img.get('alt'):
                metadata_snippets.append(f"[Image Alt-Tag: {img.get('alt')}]")

        # Remove all "fancy" structural elements and style-related tags
        for element in soup(["script", "style", "link", "nav", "footer", "header", "aside", "svg", "noscript", "iframe"]):
            element.decompose()
        
        clean_text = " ".join(soup.get_text().split())
        return f"{clean_text} {' '.join(metadata_snippets)}"

    def trawl_and_analyze(self, current_url=None, target_entities=None, max_pages=15):
        """Recursively crawls domains and passes text windows to the local model."""
        if current_url is None:
            current_url = self.base_url
        if target_entities is None or len(target_entities) < 2:
            print("[!] Error: You must provide at least two entities to cross-reference.")
            return

        if len(self.visited_urls) >= max_pages or current_url in self.visited_urls:
            return
        if urlparse(current_url).netloc != self.domain:
            return

        print(f"[*] Analyzing node: {current_url}")
        self.visited_urls.add(current_url)
        self.save_state() # Save visited URL progress

        try:
            # Pre-check file size and type via HEAD request to save bandwidth
            head = self.session.head(current_url, timeout=10, allow_redirects=True)
            content_size = int(head.headers.get('Content-Length', 0))
            content_type = head.headers.get('Content-Type', '').lower()

            if content_size > self.max_file_size:
                print(f"[!] Skipping {current_url} (Size: {content_size} bytes exceeds limit)")
                return

            # Increased timeout for slow connections
            response = self.session.get(current_url, timeout=25, headers={"User-Agent": "DataCompiler/1.0"})
            if response.status_code != 200:
                return

            # Route content based on type
            if 'application/pdf' in content_type:
                clean_text = self.extract_pdf_text(response.content)
            else:
                clean_text = self.extract_clean_text(response.text, current_url)
            
            self.evaluate_entity_matrix(clean_text, target_entities, source_url=current_url)
            
            # Removed .pdf from blacklist to allow discovery
            blacklist_ext = ('.css', '.js', '.zip', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.mp4', '.avi', '.exe')

            # Discover internal paths to crawl next
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href'].split('?')[0].split('#')[0] # Strip queries and fragments
                if not href.lower().endswith(blacklist_ext):
                    next_url = urljoin(self.base_url, link['href'])
                    self.trawl_and_analyze(next_url, target_entities, max_pages)

        except Exception as e:
            print(f"[!] Error processing {current_url}: {e}")

    def evaluate_entity_matrix(self, text, entities, source_url):
        """Pairs every entity together to test proximity and run local model inference."""
        # Simple sliding chunk window to protect local model context length limits
        chunks = [text[i:i+2500] for i in range(0, len(text), 1800)]
        
        for chunk in chunks:
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    ent_a, ent_b = entities[i], entities[j]
                    
                    # Regex pre-filter saves computational power before spinning up the GPU
                    if re.search(rf"\b{re.escape(ent_a)}\b", chunk, re.IGNORECASE) and \
                       re.search(rf"\b{re.escape(ent_b)}\b", chunk, re.IGNORECASE):
                        
                        self.query_local_inference(chunk, ent_a, ent_b, source_url)

    def query_local_inference(self, context, ent_a, ent_b, source):
        """Forces the local Dolphin model to evaluate link probabilities in pure JSON."""
        system_instruction = (
            "You are an expert multi-modal data analyst. Your task is to analyze the provided context, "
            "which includes both webpage text and structured image metadata (EXIF/Alt-tags), to determine "
            "if a factual relationship exists between Entity A and Entity B. "
            "Treat technical metadata—such as GPS coordinates, timestamps, and camera serialization—as "
            "high-fidelity evidence for location or temporal proximity. "
            "Ignore visual styling and focus on semantic and technical data points. "
            "Assign a confidence score (0.0 to 1.0) based on evidence strength. "
            "Respond ONLY in JSON using these exact keys:\n"
            '{"link_detected": boolean, "confidence": float, "rationale": "string"}'
        )

        user_prompt = f"Context Material:\n{context}\n\nEntity A: {ent_a}\nEntity B: {ent_b}"

        payload = {
            "model": self.model,
            "prompt": user_prompt,
            "system": system_instruction,
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.0}  # Complete deterministic tracking
        }

        try:
            res = requests.post(self.ollama_url, json=payload, timeout=20)
            data = json.loads(res.json()['response'])
            
            if data.get("link_detected") and data.get("confidence", 0.0) >= 0.5:
                score = data["confidence"]
                reason = data["rationale"]
                print(f"    [!] Connected: [{ent_a}] <-> [{ent_b}] (Confidence: {score})")
                
                # Sync to Spring Boot Backend
                self.sync_to_spring_boot({
                    "entityA": ent_a,
                    "entityB": ent_b,
                    "confidence": score,
                    "rationale": reason,
                    "sourceUrl": source
                })

                # Update or insert connections into our mathematical array
                if self.graph.has_edge(ent_a, ent_b):
                    if self.graph[ent_a][ent_b]['weight'] < score:
                        self.graph[ent_a][ent_b]['weight'] = score
                        self.graph[ent_a][ent_b]['title'] = f"Source: {source} | Reason: {reason}"
                else:
                    self.graph.add_edge(ent_a, ent_b, weight=score, title=f"Source: {source} | {reason}")
        except Exception as e:
            pass
        finally:
            self.save_state() # Save graph changes immediately after inference

    def sync_to_spring_boot(self, data):
        """Pushes data to the Spring Boot / Hibernate Envers backend."""
        try:
            # Serialize with sort_keys=True to ensure the string is identical for signing/verification
            payload_str = json.dumps(data, sort_keys=True)
            headers = {"Content-Type": "application/json"}
            
            if self.pgp_key:
                # If your key has a passphrase, you would unlock it here:
                # with self.pgp_key.unlock("YOUR_PASSPHRASE"):
                #     signature = self.pgp_key.sign(payload_str)
                signature = self.pgp_key.sign(payload_str)
                headers["X-PGP-Signature"] = str(signature)
                print(f"[*] Signed data packet for authenticity.")

            # Point this to your local Spring Boot instance
            self.session.post(
                "http://localhost:8080/api/links", 
                data=payload_str, 
                headers=headers,
                timeout=5
            )
        except Exception as e:
            print(f"[!] Spring Boot Sync Failed: {e}")

    def build_visual_map(self, filename="intelligence_map.html"):
        """Transforms the network structure into an interactive physical network visualization."""
        if len(self.graph.nodes) == 0:
            print("[-] Map generation bypassed: No entity relationships crossed the confidence threshold.")
            return

        net = Network(height="800px", width="100%", bgcolor="#1a1a1a", font_color="#ffffff")
        
        for node in self.graph.nodes():
            net.add_node(node, label=node, color="#00ffcc", value=12)
            
        for edge in self.graph.edges(data=True):
            # Line thickness is directly mapped to the model's confidence value
            line_thickness = edge[2]['weight'] * 10
            net.add_edge(
                edge[0], edge[1], 
                value=line_thickness, 
                title=edge[2]['title'], 
                color="#ff3366"
            )
            
        net.toggle_physics(True)
        net.write_html(filename)
        print(f"\n[+] Success! Interactive network chart generated at: ./{filename}")

# --- Target Launch Matrix ---
if __name__ == "__main__":
    # Point the pipeline to your local reference mirror or document domain
    TARGET_DOMAIN = "https://example.com" 
    
    # Define the precise string assets you want the engine to scan for
    SEARCH_MATRIX = ["Asset_Alpha", "Location_Node_4", "Operator_Identity", "System_Log_7"]
    
    engine = IntelligenceGraphPipeline(target_domain=TARGET_DOMAIN, ollama_model="dolphin-llama3")
    
    print("[*] Launching ingestion crawler sequence...")
    engine.trawl_and_analyze(target_entities=SEARCH_MATRIX, max_pages=5)
    engine.build_visual_map()